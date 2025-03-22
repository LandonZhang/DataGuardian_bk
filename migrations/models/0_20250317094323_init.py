from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `rule_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `project_name` VARCHAR(100) NOT NULL COMMENT '项目名称',
    `table_name` VARCHAR(100) NOT NULL COMMENT '表格名称',
    `feature_name` VARCHAR(100) NOT NULL COMMENT '特征名称',
    `rule_content` VARCHAR(500) NOT NULL COMMENT '对应规则',
    `error_type` VARCHAR(50) NOT NULL COMMENT '错误类型',
    `issue_details` LONGTEXT COMMENT '问题详情',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='规则导入数据表';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
