"""
schema 包 — 数据库基础设施

对外暴露核心接口，方便外部统一导入：
  from schema import create_tables, seed_sample_data, get_connection, DB_PATH
"""

from schema.database import get_connection, create_tables, DB_PATH
from schema.seed_data import seed_sample_data

__all__ = [
    "get_connection",
    "create_tables",
    "seed_sample_data",
    "DB_PATH",
]
