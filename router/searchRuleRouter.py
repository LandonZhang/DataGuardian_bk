from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
import sys
from pathlib import Path
from pydantic import BaseModel

# 获取当前文件的目录
god_path = Path(__file__).parent.parent
# 获取模板文件的路径
template_path = os.path.join(god_path, "static", "ruleTemplate.xlsx")
# 获取模型文件的路径
model_path = os.path.join(god_path, "models")
sys.path.append(model_path)

from models import RuleData  # type: ignore


# 创建一个APIRouter实例
searchRuleRouter = APIRouter()


# 创建下拉选项响应模型
class DropdownResponse(BaseModel):
    options: List[str]


# 搜索参数模型
class SearchParams(BaseModel):
    project_name: Optional[str] = None
    table_name: Optional[str] = None
    feature_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# 搜索结果模型
class RuleDataResponse(BaseModel):
    id: int
    project_name: str
    table_name: str
    feature_name: str
    rule_content: str
    error_type: str
    issue_details: Optional[str] = None
    created_at: datetime


# 搜索结果列表响应模型
class SearchResponse(BaseModel):
    total: int
    data: List[RuleDataResponse]


# 下拉选项接口
@searchRuleRouter.get(
    "/project", summary="获取项目名称下拉选项", response_model=DropdownResponse
)
async def get_project_options():
    """
    获取所有不重复的项目名称作为下拉选项

    Returns:
        DropdownResponse: 包含项目名称列表的响应对象
    """
    try:
        # 使用 Tortoise ORM 的 values_list 方法获取唯一的项目名称
        projects = (
            await RuleData.all().distinct().values_list("project_name", flat=True)
        )
        return {"options": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目名称选项时出错: {str(e)}")


# 获取表格名称下拉选项
@searchRuleRouter.get(
    "/table", summary="获取表格名称下拉选项", response_model=DropdownResponse
)
async def get_table_options(project_name: Optional[str] = None):
    """
    获取所有不重复的表格名称作为下拉选项，可以通过项目名称筛选

    Args:
        project_name (Optional[str], optional): 项目名称筛选条件. Defaults to None.

    Returns:
        DropdownResponse: 包含表格名称列表的响应对象
    """
    try:
        # 创建一个查询
        query = RuleData.all()

        # 如果提供了项目名称，添加过滤条件
        if project_name:
            query = query.filter(project_name=project_name)

        # 获取唯一的表格名称
        tables = await query.distinct().values_list("table_name", flat=True)
        return {"options": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取表格名称选项时出错: {str(e)}")


# 获取特征名称下拉选项
@searchRuleRouter.get(
    "/feature", summary="获取特征名称下拉选项", response_model=DropdownResponse
)
async def get_feature_options(
    project_name: Optional[str] = None, table_name: Optional[str] = None
):
    """
    获取所有不重复的特征名称作为下拉选项，可以通过项目名称和表格名称筛选

    Args:
        project_name (Optional[str], optional): 项目名称筛选条件. Defaults to None.
        table_name (Optional[str], optional): 表格名称筛选条件. Defaults to None.

    Returns:
        DropdownResponse: 包含特征名称列表的响应对象
    """
    try:
        # 创建一个查询
        query = RuleData.all()

        # 添加过滤条件
        if project_name:
            query = query.filter(project_name=project_name)
        if table_name:
            query = query.filter(table_name=table_name)

        # 获取唯一的特征名称
        features = await query.distinct().values_list("feature_name", flat=True)
        return {"options": features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取特征名称选项时出错: {str(e)}")


# 搜索接口，返回全部结果
@searchRuleRouter.get("/", summary="搜索规则数据", response_model=SearchResponse)
async def search_rules(
    project_name: Optional[str] = Query(None, description="项目名称"),
    table_name: Optional[str] = Query(None, description="表格名称"),
    feature_name: Optional[str] = Query(None, description="特征名称"),
    start_time: Optional[str] = Query(None, description="创建开始时间 (YYYY-MM-DD)"),
    end_time: Optional[str] = Query(None, description="创建结束时间 (YYYY-MM-DD)"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
):
    """
    根据条件搜索规则数据

    Args:
        project_name: 项目名称筛选条件
        table_name: 表格名称筛选条件
        feature_name: 特征名称筛选条件
        start_time: 创建开始日期
        end_time: 创建结束日期
        page: 页码（从1开始）
        page_size: 每页显示的记录数量

    Returns:
        SearchResponse: 包含总数和规则数据列表的响应对象
    """
    try:
        # 创建查询对象
        query = RuleData.all()

        # 添加过滤条件
        if project_name:
            query = query.filter(project_name=project_name)
        if table_name:
            query = query.filter(table_name=table_name)
        if feature_name:
            query = query.filter(feature_name=feature_name)

        # 处理日期筛选条件
        if start_time:
            try:
                # 将字符串转换为日期，并设置为当天开始时间 (00:00:00)
                start_datetime = datetime.strptime(start_time, "%Y-%m-%d")
                query = query.filter(created_at__gte=start_datetime)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="开始时间格式错误，请使用 YYYY-MM-DD 格式"
                )

        if end_time:
            try:
                # 将字符串转换为日期，并设置为当天结束时间 (23:59:59)
                end_datetime = datetime.strptime(end_time, "%Y-%m-%d")
                # 添加一天并减去一微秒，得到当天的最后一刻
                end_datetime = (
                    end_datetime + timedelta(days=1) - timedelta(microseconds=1)
                )
                query = query.filter(created_at__lte=end_datetime)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="结束时间格式错误，请使用 YYYY-MM-DD 格式"
                )

        # 获取总数
        total = await query.count()

        # 计算分页
        offset = (page - 1) * page_size

        # 获取数据列表，数量按照page_size限制
        data = (
            await query.order_by("-created_at").offset(offset).limit(page_size)
        )  # 倒序排序

        # 转换为响应模型格式
        result_data = []

        # 从Queryset中获取模型实例
        for item in data:
            result_data.append(
                {
                    "id": item.id,
                    "project_name": item.project_name,
                    "table_name": item.table_name,
                    "feature_name": item.feature_name,
                    "rule_content": item.rule_content,
                    "error_type": item.error_type,
                    "issue_details": item.issue_details,
                    "created_at": item.created_at,
                }
            )

        return {"total": total, "data": result_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索规则数据时出错: {str(e)}")


# 重置接口（清空搜索条件）
@searchRuleRouter.get("/reset", summary="重置搜索条件", response_model=SearchResponse)
async def reset_search(
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
):
    """
    重置所有搜索条件，返回所有规则数据
    Args:
        page: 页码（从1开始）
        page_size: 每页显示的记录数量

    Returns:
        SearchResponse: 包含总数和规则数据列表的响应对象
    """
    try:
        total = await RuleData.all().count()

        # 计算分页
        offset = (page - 1) * page_size

        # 获取数据列表，数量按照page_size限制
        data = (
            await RuleData.all().order_by("-created_at").offset(offset).limit(page_size)
        )

        # 转换为响应模型格式
        result_data = []
        for item in data:
            result_data.append(
                {
                    "id": item.id,
                    "project_name": item.project_name,
                    "table_name": item.table_name,
                    "feature_name": item.feature_name,
                    "rule_content": item.rule_content,
                    "error_type": item.error_type,
                    "issue_details": item.issue_details,
                    "created_at": item.created_at,
                }
            )

        return {"total": total, "data": result_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置搜索条件时出错: {str(e)}")
