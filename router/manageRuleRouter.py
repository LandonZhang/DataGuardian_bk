from fastapi import APIRouter, HTTPException, Path, Body
from typing import Optional
from pydantic import BaseModel
import os
import sys
from pathlib import Path as PathLib
from fastapi.responses import JSONResponse

# 获取当前文件的目录
god_path = PathLib(__file__).parent.parent
# 获取模型文件的路径
model_path = os.path.join(god_path, "models")
sys.path.append(model_path)

from models import RuleData  # type: ignore

# 创建一个APIRouter实例
manageRuleRouter = APIRouter()


# 规则数据响应模型
class RuleDetailResponse(BaseModel):
    id: int
    project_name: str
    table_name: str
    feature_name: str
    rule_content: str
    error_type: str
    issue_details: Optional[str] = None
    created_at: str
    updated_at: str


# 规则数据更新模型，都是可选项，如果为空则不更新
class RuleUpdateModel(BaseModel):
    project_name: Optional[str] = None
    table_name: Optional[str] = None
    feature_name: Optional[str] = None
    rule_content: Optional[str] = None
    error_type: Optional[str] = None
    issue_details: Optional[str] = None


# 操作响应模型
class OperationResponse(BaseModel):
    status: str = "success"
    message: str


# 查看单条规则数据详情
@manageRuleRouter.get(
    "/{rule_id}", summary="查看单条规则数据详情", response_model=RuleDetailResponse
)
async def view_rule_detail(rule_id: int = Path(..., description="规则ID", ge=1)):
    """
    根据ID查看单条规则数据的详细信息

    Args:
        rule_id (int): 规则ID

    Returns:
        RuleDetailResponse: 规则详细信息

    Raises:
        HTTPException: 当规则不存在时抛出404错误
    """
    try:
        # 查询单条规则数据
        rule = await RuleData.get_or_none(id=rule_id)

        # 如果规则不存在，返回404错误
        if not rule:
            raise HTTPException(
                status_code=404, detail=f"ID为{rule_id}的规则数据不存在"
            )

        # 返回规则详情
        return {
            "id": rule.id,
            "project_name": rule.project_name,
            "table_name": rule.table_name,
            "feature_name": rule.feature_name,
            "rule_content": rule.rule_content,
            "error_type": rule.error_type,
            "issue_details": rule.issue_details,
            "created_at": rule.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": rule.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"查询规则数据时出错: {str(e)}")


# 更新单条规则数据
@manageRuleRouter.put(
    "/{rule_id}", summary="更新规则数据", response_model=OperationResponse
)
async def update_rule(
    rule_id: int = Path(..., description="规则ID", ge=1),
    rule_data: RuleUpdateModel = Body(..., description="更新的规则数据"),
):
    """
    更新指定ID的规则数据

    Args:
        rule_id (int): 规则ID
        rule_data (RuleUpdateModel): 要更新的规则数据字段

    Returns:
        OperationResponse: 操作结果

    Raises:
        HTTPException: 当规则不存在或更新失败时抛出相应错误
    """
    try:
        # 查询规则数据
        rule = await RuleData.get_or_none(id=rule_id)

        # 如果规则不存在，返回404错误
        if not rule:
            raise HTTPException(
                status_code=404, detail=f"ID为{rule_id}的规则数据不存在"
            )

        # 准备更新字段, 默认为空不更新
        update_data = rule_data.model_dump(exclude_unset=True)

        # 如果没有提供任何字段进行更新，返回错误
        if not update_data:
            raise HTTPException(status_code=400, detail="未提供任何需要更新的字段")

        # 更新数据
        await rule.update_from_dict(update_data)

        # 保存更新
        await rule.save()

        return {"status": "success", "message": f"成功更新ID为{rule_id}的规则数据"}
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"更新规则数据时出错: {str(e)}")


# 删除规则数据
@manageRuleRouter.delete(
    "/{rule_id}", summary="删除规则数据", response_model=OperationResponse
)
async def delete_rule(rule_id: int = Path(..., description="规则ID", ge=1)):
    """
    删除指定ID的规则数据

    Args:
        rule_id (int): 要删除的规则ID

    Returns:
        OperationResponse: 操作结果

    Raises:
        HTTPException: 当规则不存在或删除失败时抛出相应错误
    """
    try:
        # 查询规则数据
        rule = await RuleData.get_or_none(id=rule_id)

        # 如果规则不存在，返回404错误
        if not rule:
            raise HTTPException(
                status_code=404, detail=f"ID为{rule_id}的规则数据不存在"
            )

        # 删除数据
        await rule.delete()

        return {"status": "success", "message": f"成功删除ID为{rule_id}的规则数据"}
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"删除规则数据时出错: {str(e)}")


# 批量删除规则数据
class BatchDeleteModel(BaseModel):
    ids: list[int]


@manageRuleRouter.post(
    "/batch-delete", summary="批量删除规则数据", response_model=OperationResponse
)
async def batch_delete_rules(
    delete_data: BatchDeleteModel = Body(..., description="要删除的规则ID列表"),
):
    """
    批量删除多条规则数据

    Args:
        delete_data (BatchDeleteModel): 包含要删除的规则ID列表

    Returns:
        OperationResponse: 操作结果

    Raises:
        HTTPException: 当删除失败时抛出相应错误
    """
    try:
        # 检查ID列表是否为空
        if not delete_data.ids:
            raise HTTPException(status_code=400, detail="删除ID列表不能为空")

        # 批量删除
        delete_count = await RuleData.filter(id__in=delete_data.ids).delete()

        # 返回结果
        return {"status": "success", "message": f"成功删除{delete_count}条规则数据"}
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"批量删除规则数据时出错: {str(e)}")
