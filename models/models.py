from tortoise import fields
from tortoise.models import Model


# 规则导入数据表
class RuleData(Model):
    id = fields.IntField(pk=True)
    project_name = fields.CharField(max_length=100, null=False, description="项目名称")
    table_name = fields.CharField(max_length=100, null=False, description="表格名称")
    feature_name = fields.CharField(max_length=100, null=False, description="特征名称")
    rule_content = fields.CharField(max_length=500, null=False, description="对应规则")
    error_type = fields.CharField(max_length=50, null=False, description="错误类型")
    issue_details = fields.TextField(null=True, description="问题详情")
    class_name = fields.CharField(
        max_length=100, null=False, description="所属域名", default=""
    )

    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:  # type: ignore
        table = "rule_data"
        table_description = "规则导入数据表"

    # 调试函数，打印模型实例信息时使用
    def __str__(self):
        return f"{self.project_name} - {self.table_name} - {self.feature_name}"


# 需求确认记录表
class RequestConfirmation(Model):
    id = fields.IntField(pk=True)
    uid = fields.CharField(max_length=100, null=False, index=True, description="用户ID")
    init_request = fields.TextField(null=False, description="初始请求")
    final_request = fields.TextField(null=False, description="最终确认请求")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:  # type: ignore
        table = "request_confirmation"
        table_description = "需求确认记录表"

    def __str__(self):
        return f"用户 {self.uid} 的需求确认记录 ID: {self.id}"
