"""
ID 分配工具

实现"删除后自动填补空缺"的 ID 分配策略：
新建记录时返回表中最小的未被占用的正整数 ID。

注意：
该策略仅适用于本学习项目（数据库未设置物理外键约束）。
在生产环境中，主键 ID 应保持单调递增、永不复用，
以避免审计追溯、外键关联混乱等问题。
"""

from sqlalchemy import select
from sqlalchemy.orm import Session


def next_available_id(db: Session, model) -> int:
    """
    返回指定表中最小的未被占用的正整数 ID。

    例如表中已有 ID [1, 2, 4, 5]，则返回 3；表为空则返回 1。

    :param db: 数据库会话
    :param model: SQLAlchemy 模型类（需含主键列 id）
    :return: 可用于新记录的最小正整数 ID
    """
    existing = {row[0] for row in db.execute(select(model.id)).all()}
    candidate = 1
    while candidate in existing:
        candidate += 1
    return candidate
