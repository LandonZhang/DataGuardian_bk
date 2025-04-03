from fastapi import APIRouter, HTTPException, Body, Request, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import httpx
import os
import json
import uuid
from datetime import datetime
from pathlib import Path as PathLib
import sys
import re

# 获取当前文件的目录
god_path = PathLib(__file__).parent.parent
# 获取模型文件的路径
model_path = os.path.join(god_path, "models")
sys.path.append(model_path)

from models import RequestConfirmation  # type: ignore

# 创建一个APIRouter实例
llmChatRouter = APIRouter()

# Dify API配置
testMode = True
if testMode:
    DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "app-lHz8NmEHEZRFecdEVelninyt")
    DIFY_API_URL = os.environ.get(
        "DIFY_API_URL", "https://api.dify.ai/v1/chat-messages"
    )
else:
    DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "app-dG3lwUKOqCGKnAZaHffsohKo")
    DIFY_API_URL = os.environ.get(
        "DIFY_API_URL", "https://api.dify.ai/v1/chat-messages"
    )

# 内存中存储用户的对话ID映射 (用户名与对应的对话ID)
user_conversations = {}

# * 如果做一个用户多端对话的话可以考虑使用Redis需求用户ID与对话ID的映射


# 聊天请求模型
class ChatRequest(BaseModel):
    query: str = Field(..., description="用户的问题或输入")
    conversation_id: Optional[str] = Field(
        None, description="对话ID，不提供则使用保存的值，提供空字符串则开始新对话"
    )
    user: str = Field(..., description="用户标识符")


# 完整响应模型(非流式模式下使用)
class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    created_at: int
    id: str


# 获取对话ID的辅助函数
def get_conversation_id(user_id: str, provided_id: Optional[str] = None) -> str:
    """
    获取用户的对话ID

    Args:
        user_id: 用户标识
        provided_id: 用户提供的对话ID

    Returns:
        应该使用的对话ID
    """
    # 如果提供了确切的对话ID (不是None)，就使用它
    if provided_id is not None:
        # 如果提供了空字符串，意味着要开始新对话
        if provided_id == "":
            # 从存储中移除旧的映射
            if user_id in user_conversations:
                del user_conversations[user_id]
            return ""
        # 使用提供的ID，并更新存储
        user_conversations[user_id] = provided_id
        return provided_id

    # 如果没有提供ID，尝试从存储中获取
    return user_conversations.get(user_id, "")


# 更新存储的对话ID
def update_conversation_id(user_id: str, conversation_id: str) -> None:
    """
    更新用户的对话ID

    Args:
        user_id: 用户标识
        conversation_id: 新的对话ID
    """
    if conversation_id:  # 只保存非空ID
        user_conversations[user_id] = conversation_id


# 异步生成Dify流式响应
async def stream_dify_response(query: str, conversation_id: str, user: str):
    """
    从Dify获取流式响应并转发给客户端

    Args:
        query: 用户查询内容
        conversation_id: 对话ID，新对话为空字符串
        user: 用户标识符

    Yields:
        SSE格式的响应数据
    """
    try:
        # 获取正确的对话ID
        effective_conversation_id = get_conversation_id(user, conversation_id)

        # 构建请求数据
        dify_request = {
            "inputs": {},  # 应用中暂时没有需要输入的其他参数
            "query": query,
            "response_mode": "streaming",  # 默认流式返回
            "conversation_id": effective_conversation_id,
            "user": user,
        }

        # 设置请求头
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json",
        }

        # 创建异步HTTP客户端
        async with httpx.AsyncClient() as client:
            # 发送流式请求到Dify
            async with client.stream(
                method="POST",
                url=DIFY_API_URL,
                json=dify_request,
                headers=headers,
                timeout=90.0,  # 90秒Dify不响应则超时
            ) as response:
                # 检查响应状态
                if response.status_code != 200:
                    error_body = await response.aread()
                    error_message = f"Dify API错误: HTTP {response.status_code}"
                    try:
                        error_detail = json.loads(error_body.decode("utf-8"))
                        error_message = (
                            f"{error_message} - {error_detail.get('message', '')}"
                        )
                    except:
                        error_message = (
                            f"{error_message} - {error_body.decode('utf-8')}"
                        )

                    # 返回错误信息
                    yield f"data: {json.dumps({'event': 'error', 'message': error_message})}\n\n"
                    return

                # 标记是否已更新对话ID
                updated_conversation_id = False

                # 正常处理流式响应
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        # 打印原始数据模块
                        # print(f"原始Dify数据块: {repr(chunk)}")

                        # 尝试解析JSON以获取conversation_id
                        if not updated_conversation_id and chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])  # 去掉 'data: ' 前缀
                                if data.get("conversation_id"):
                                    # 更新存储的对话ID
                                    update_conversation_id(
                                        user, data["conversation_id"]
                                    )
                                    updated_conversation_id = True
                            except:
                                pass  # 解析失败则忽略

                        # Dify已经返回了正确的SSE格式，通过 yield 直接转发，返回一个转发一个
                        # 格式: data: {"event": "message", "answer": "部分回答", ...}\n\n
                        yield chunk

                        # 如果是最后一个消息，添加结束标记
                        if chunk.startswith('data: {"event": "message_end"'):
                            yield f"data: {json.dumps({'event': 'done'})}\n\n"

    except httpx.TimeoutException:
        yield f"data: {json.dumps({'event': 'error', 'message': '与Dify通信超时'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'message': f'发生错误: {str(e)}'})}\n\n"


# 聊天接口 - 流式响应
@llmChatRouter.post("/stream", summary="与大模型对话(流式响应)")
async def chat_stream(request: ChatRequest = Body(...)):
    """
    与大模型进行流式对话，适用于实时显示回答

    Args:
        request: 包含查询内容、对话ID和用户标识的请求体

    Returns:
        StreamingResponse: 流式SSE格式的响应
    """
    try:
        # 返回流式响应
        return StreamingResponse(
            stream_dify_response(
                query=request.query,
                conversation_id=request.conversation_id
                or "",  # 可以是None，函数内部会处理
                user=request.user,
            ),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")


# 聊天接口 - 完整响应（非流式）
@llmChatRouter.post("/", summary="与大模型对话(完整响应)")
async def chat_complete(request: ChatRequest = Body(...)):
    """
    与大模型进行对话，返回完整的回答

    Args:
        request: 包含查询内容、对话ID和用户标识的请求体

    Returns:
        完整的响应内容
    """
    try:
        # print("开始处理完整响应请求")
        # 获取正确的对话ID
        effective_conversation_id = get_conversation_id(
            request.user, request.conversation_id
        )
        # print(f"获取到的对话ID: {effective_conversation_id}")
        # print(f"请求体的数据是: {request.model_dump()}")
        # 构建请求数据
        dify_request = {
            "inputs": {},
            "query": request.query,  # 后端需要在这里包装RequestHistory
            "response_mode": "blocking",  # 非流式模式
            "conversation_id": effective_conversation_id,
            "user": request.user,
        }
        # print(f"构建的请求数据是: {dify_request}")

        # 设置请求头
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json",
        }
        # print(f"设置的请求头是: {headers}")

        async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
            # print(f"发送请求到Dify的请求是: {DIFY_API_URL}")
            response = await client.post(
                DIFY_API_URL, json=dify_request, headers=headers, timeout=60.0
            )
            # print(f"发送请求到Dify的响应是: {response}")
            # 检查响应状态
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Dify API错误: {response.text}",
                )

            # 解析响应内容
            result = response.json()

            # 获取返回的对话ID并更新存储
            if result.get("conversation_id"):
                update_conversation_id(request.user, result["conversation_id"])
            answer = result.get("answer", "")
            # print(answer)
            answer = answer.strip()
            # print(answer)

            # 检查是否为"数据稽核开始"请求，需要从固定格式文本中提取信息并保存
            if request.query == "数据稽核开始" and "需求保存完成！" in answer:
                try:
                    # 使用正则表达式从文本中提取初始请求和最终确认请求
                    init_request_match = re.search(
                        r"用户初始请求是：(.+?)(?=\n|$)", answer
                    )
                    final_request_match = re.search(
                        r"最终确认请求是：(.+?)(?=\n|$)", answer
                    )

                    init_request = (
                        init_request_match.group(1).strip()
                        if init_request_match
                        else ""
                    )
                    final_request = (
                        final_request_match.group(1).strip()
                        if final_request_match
                        else ""
                    )

                    # 保存到数据库
                    if init_request:
                        await RequestConfirmation.create(
                            uid=request.user,
                            init_request=init_request,
                            final_request=final_request,
                        )
                        print(f"已成功保存需求确认记录 - 用户ID: {request.user}")

                    # 如果请求是"数据稽核开始"，则需要从删除用户ID与对话ID的映射关系
                    if request.query == "数据稽核开始":
                        del user_conversations[request.user]
                except Exception as e:
                    print(f"提取和保存需求确认数据时出错: {str(e)}")

            # 返回处理后的结果
            return {
                "answer": answer,
                "conversation_id": result.get("conversation_id", ""),
                "created_at": result.get("created_at", int(datetime.now().timestamp())),
                "id": result.get("id", str(uuid.uuid4())),
            }

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="与Dify通信超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")


# 生成用户ID接口
@llmChatRouter.get("/generate-user-id", summary="生成用户ID")
async def generate_user_id():
    """
    生成一个唯一的用户ID，用于标识用户

    Returns:
        包含用户ID的JSON响应
    """
    return {"user_id": str(uuid.uuid4())}


# 开始新对话接口
@llmChatRouter.post("/new-conversation", summary="开始新对话")
async def new_conversation(user: str = Body(..., embed=True)):
    """
    为指定用户开始一个新的对话

    Args:
        user: 用户标识符

    Returns:
        成功消息
    """
    # 从存储中移除用户的对话ID
    if user in user_conversations:
        del user_conversations[user]

    return {"status": "success", "message": "已开始新对话", "user": user}


# 获取当前对话ID接口
@llmChatRouter.get("/conversation-id/{user}", summary="获取当前对话ID")
async def get_current_conversation_id(user: str):
    """
    获取指定用户当前的对话ID

    Args:
        user: 用户标识符

    Returns:
        当前对话ID
    """
    return {"user": user, "conversation_id": user_conversations.get(user, "")}
