from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rule_data` ADD `class_name` VARCHAR(100) NOT NULL COMMENT '所属域名' DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `rule_data` DROP COLUMN `class_name`;"""
