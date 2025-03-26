from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `request_confirmation` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `uid` VARCHAR(100) NOT NULL COMMENT '用户ID',
    `init_request` LONGTEXT NOT NULL COMMENT '初始请求',
    `final_request` LONGTEXT NOT NULL COMMENT '最终确认请求',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    KEY `idx_request_con_uid_3ecd39` (`uid`)
) CHARACTER SET utf8mb4 COMMENT='需求确认记录表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `request_confirmation`;"""
