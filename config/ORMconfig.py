import os
import sys
from pathlib import Path

# 获取当前文件的目录
god_path = Path(__file__).parent.parent

# 获取数据库模型目录
models_path = os.path.join(god_path, "models")

# 将项目根目录添加到 Python 路径
sys.path.append(models_path)

# ORM系统配置
# TODO: 需要开放为接口供用户配置数据库连接信息
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": "3306",
                "user": "root",
                "password": "Happyzyz1225",
                "database": "dataguardian",
                "minsize": 1,
                "maxsize": 5,
                "charset": "utf8mb4",
                "echo": True,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],  # 与模型文件名相同
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "Asia/Shanghai",
}
