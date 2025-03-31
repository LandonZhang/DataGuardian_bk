from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import pymysql
import os
from pathlib import Path
import json
from fastapi.responses import JSONResponse

# 获取当前文件的目录
god_path = Path(__file__).parent.parent

# 创建一个APIRouter实例
linkDatabaseRouter = APIRouter()


# 数据库连接参数模型
class DatabaseConnectionParams(BaseModel):
    host: str = Field(..., description="数据库主机地址")
    port: int = Field(3306, description="数据库端口，默认为3306")
    user: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    database: str = Field(..., description="数据库名称")
    charset: str = Field("utf8mb4", description="字符集，默认为utf8mb4")


# 数据库连接响应模型
class ConnectionResponse(BaseModel):
    status: str = "success"
    message: str
    connection_info: Optional[dict] = None


# 获取配置文件路径
def get_config_path() -> str:
    """
    获取数据库配置文件的路径

    Returns:
        str: 配置文件路径
    """
    config_dir = os.path.join(god_path, "config")
    return os.path.join(config_dir, "database_config.json")


# 保存连接配置的函数
async def save_connection_config(config: dict) -> bool:
    """
    保存数据库连接配置到配置文件

    Args:
        config: 数据库连接配置

    Returns:
        bool: 保存是否成功
    """
    try:
        # 创建配置目录（如果不存在）
        config_dir = os.path.join(god_path, "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 使用JSON形式保存配置到文件
        config_path = os.path.join(config_dir, "database_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存数据库配置时出错: {str(e)}")
        return False


# 读取保存的配置信息
async def get_saved_config() -> Dict[str, Any]:
    """
    读取保存的数据库配置信息

    Returns:
        Dict[str, Any]: 保存的配置信息，如果不存在则返回空字典
    """
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"读取数据库配置时出错: {str(e)}")
        return {}


# 测试数据库连接
def test_database_connection(params: dict) -> bool:
    """
    测试数据库连接是否成功

    Args:
        params: 数据库连接参数

    Returns:
        bool: 连接是否成功
    """
    try:
        # 创建连接
        connection = pymysql.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
            charset=params["charset"],
        )

        # 使用句柄测试连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        # 关闭连接
        connection.close()

        # 检查结果
        return result and result[0] == 1  # type: ignore

    except Exception as e:
        # print(f"测试数据库连接时出错: {str(e)}")
        return False


# 数据库连接接口
@linkDatabaseRouter.post(
    "/", summary="连接MySQL数据库", response_model=ConnectionResponse
)
async def connect_database(params: DatabaseConnectionParams = Body(...)):
    """
    连接MySQL数据库并保存连接配置

    Args:
        params: 数据库连接参数

    Returns:
        ConnectionResponse: 包含连接状态和信息的响应对象

    Raises:
        HTTPException: 当连接失败时抛出相应错误
    """
    try:
        # 转换为字典以方便操作
        db_params = params.model_dump()

        # 测试数据库连接
        if not test_database_connection(db_params):
            raise HTTPException(
                status_code=400, detail="无法连接到数据库，请检查连接参数是否正确"
            )

        # 保存连接配置
        await save_connection_config(db_params)

        # 返回成功信息
        return {
            "status": "success",
            "message": "成功连接到数据库",
            "connection_info": {
                "host": db_params["host"],
                "port": db_params["port"],
                "user": db_params["user"],
                "database": db_params["database"],
                "charset": db_params["charset"],
            },
        }

    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500, detail=f"处理数据库连接请求时出错: {str(e)}"
        )


# 测试数据库连接接口
@linkDatabaseRouter.post(
    "/test", summary="测试MySQL数据库连接", response_model=ConnectionResponse
)
async def test_connection(params: DatabaseConnectionParams = Body(...)):
    """
    测试MySQL数据库连接，但不保存配置，用户应先测试后保存

    Args:
        params: 数据库连接参数

    Returns:
        ConnectionResponse: 包含连接测试结果的响应对象
    """
    try:
        # 转换为字典以方便操作
        db_params = params.model_dump()

        # 测试数据库连接
        if test_database_connection(db_params):
            return {
                "status": "success",
                "message": "数据库连接测试成功",
                "connection_info": {
                    "host": db_params["host"],
                    "port": db_params["port"],
                    "user": db_params["user"],
                    "database": db_params["database"],
                    "charset": db_params["charset"],
                },
            }
        else:
            return {
                "status": "error",
                "message": "数据库连接测试失败，请检查连接参数",
                "connection_info": None,
            }

    except Exception as e:
        # 处理异常
        return {
            "status": "error",
            "message": f"测试数据库连接时出错: {str(e)}",
            "connection_info": None,
        }


# 用于返回config文件中数据的接口
@linkDatabaseRouter.get("/config", summary="获取已保存的数据库配置")
async def get_database_config():
    """
    获取已保存的数据库配置信息

    如果配置文件不存在，则返回空对象

    Returns:
        包含配置信息的JSON响应
    """
    try:
        # 获取保存的配置
        config = await get_saved_config()

        if not config:
            return {
                "status": "info",
                "message": "未找到保存的数据库配置",
                "config": None,
            }

        return {
            "status": "success",
            "message": "成功获取保存的数据库配置",
            "config": config,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取数据库配置时出错: {str(e)}",
            "config": None,
        }
