from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
import os
import sys
from pathlib import Path
import pandas as pd
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

# 获取当前文件的目录
god_path = Path(__file__).parent.parent
# 获取模板文件的路径
template_path = os.path.join(god_path, "static", "ruleTemplate.xlsx")
# 获取模型文件的路径
model_path = os.path.join(god_path, "models")
sys.path.append(model_path)

from models import RuleData  # type: ignore


# 创建一个APIRouter实例
ruleRouter = APIRouter()


# w文件上传响应模型
class RuleUploadResponse(BaseModel):
    status: str = "success"
    message: str
    total_records: int
    success_count: int
    error_count: int
    error_details: Optional[List[dict]] = None


# 下载模板文件
@ruleRouter.get("/", summary="下载模板文件")
async def download_rule_file():
    file_path = template_path

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename="ruleTemplate.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# 上传规则文件并保存到数据库, file为必填项
@ruleRouter.post(
    "/", summary="上传规则文件并保存到数据库", response_model=RuleUploadResponse
)
async def upload_rule_file(file: UploadFile = File(...)):
    try:
        # 验证文件类型
        if not file.filename.endswith(".xlsx"):  # type: ignore
            raise HTTPException(status_code=400, detail="只支持.xlsx格式的文件")

        # 读取Excel文件内容
        df = pd.read_excel(await file.read())

        # 打印df的列名
        print(df.columns)

        # 验证必要的列是否存在
        required_columns = ["项目名称", "表格名称", "特征名称", "对应规则", "错误类型"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        print(missing_columns)
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件缺少必要的列: {', '.join(missing_columns)}",
            )

        # 保存数据到数据库
        success_count = 0
        error_records = []

        for index, row in df.iterrows():
            try:
                # 验证必填字段
                if any(pd.isna(row[col]) for col in required_columns):
                    error_records.append(
                        {
                            "行号": int(index) + 2,  # type: ignore # Excel行号从1开始，标题占据第1行
                            "错误": "必填字段不能为空",
                        }
                    )
                    continue

                # 创建数据库记录
                await RuleData.create(
                    project_name=str(row["项目名称"]),
                    table_name=str(row["表格名称"]),
                    feature_name=str(row["特征名称"]),
                    rule_content=str(row["对应规则"]),
                    error_type=str(row["错误类型"]),
                    issue_details=str(row["问题详情"])
                    if "问题详情" in df.columns and not pd.isna(row["问题详情"])
                    else None,
                )
                success_count += 1

            except Exception as e:
                error_records.append({"行号": index + 2, "错误": str(e)})  # type: ignore

        # 返回处理结果
        return JSONResponse(
            {
                "status": "success",
                "message": f"成功导入 {success_count} 条规则",
                "total_records": len(df),
                "success_count": success_count,
                "error_count": len(error_records),
                "error_details": error_records if error_records else None,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文件时发生错误: {str(e)}")
