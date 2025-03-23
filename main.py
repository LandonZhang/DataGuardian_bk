from fastapi import FastAPI, Request
import uvicorn
from router.ruleRouter import ruleRouter
from router.searchRuleRouter import searchRuleRouter
from router.manageRuleRouter import manageRuleRouter
from router.llmChatRouter import llmChatRouter
from tortoise.contrib.fastapi import register_tortoise
from config.ORMconfig import TORTOISE_ORM
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 一旦启动服务器，那么就会自动通过 tortoise 完成数据库的连接操作 -> 确保数据库信息正确
register_tortoise(
    app=app,
    config=TORTOISE_ORM,
    # generate_schemas=True,  # 如果数据库为空，则直接自动生成表
    # add_exception_handlers=True,  # 生成调试信息
)


# 解决跨域请求问题
@app.middleware("http")
async def CORS(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# 使用FastAPI的CORSMiddleware，它会处理所有CORS相关的头信息
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，可以改为特定域名列表
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)


app.include_router(ruleRouter, prefix="/rule/upload", tags=["稽核规则导入的相关接口"])
app.include_router(
    searchRuleRouter, prefix="/rule/search", tags=["稽核规则搜索的相关接口"]
)
app.include_router(
    manageRuleRouter, prefix="/rule/manage", tags=["稽核规则管理的相关接口"]
)
app.include_router(llmChatRouter, prefix="/llm/chat", tags=["LLM 对话的相关接口"])

if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, reload=True)
