"""
SQL 查询执行器：安全地执行 SQL 语句并返回结果。

安全设计（三层防护）：
1. 数据库以只读模式打开 — 即使 SQL 绕过检查，写入也会在引擎层被拒绝
2. 拒绝多语句执行（禁止分号分隔的语句链）
3. 正则词边界匹配危险关键词，避免误判和绕过
"""

import sqlite3
import os
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QueryExecutor:
    """数据库查询执行器"""

    # 危险关键词（使用正则词边界匹配，防止 "EXEC(" 绕过 "EXEC " 的情况）
    _DANGEROUS_PATTERNS = [
        re.compile(r'\bINSERT\b', re.IGNORECASE),
        re.compile(r'\bUPDATE\b', re.IGNORECASE),
        re.compile(r'\bDELETE\b', re.IGNORECASE),
        re.compile(r'\bDROP\b', re.IGNORECASE),
        re.compile(r'\bALTER\b', re.IGNORECASE),
        re.compile(r'\bCREATE\b', re.IGNORECASE),
        re.compile(r'\bEXEC\b', re.IGNORECASE),
        re.compile(r'\bATTACH\b', re.IGNORECASE),
        re.compile(r'\bDETACH\b', re.IGNORECASE),
        re.compile(r'\bPRAGMA\s+\w+\s*=', re.IGNORECASE),  # 禁止写 PRAGMA
    ]

    def __init__(self):
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "dashboard.db"
        )

    def execute(self, sql: str) -> dict:
        """
        执行一条 SQL 查询（只读模式）

        参数:
            sql: SQL 语句（只允许 SELECT）

        返回:
            {"columns": [...], "rows": [[...]], "row_count": N}
            或 {"error": "错误信息"}
        """
        # ── 第 1 层：基本格式检查 ──────────────────────
        cleaned = sql.strip()
        if not cleaned:
            return {"error": "SQL 语句不能为空"}

        # 禁止多语句执行（防止 SELECT 1; DROP TABLE x 这种注入）
        if ";" in cleaned:
            return {"error": "不允许执行多条 SQL 语句（禁止使用分号）"}

        upper = cleaned.upper()
        if not upper.startswith("SELECT") and not upper.startswith("WITH"):
            return {"error": "仅允许执行 SELECT / WITH 查询语句"}

        # ── 第 2 层：正则词边界匹配危险关键词 ────────────
        for pattern in self._DANGEROUS_PATTERNS:
            if pattern.search(cleaned):
                return {"error": f"SQL 中包含不允许的操作"}

        # ── 第 3 层：只读模式连接（终极防线） ────────────
        conn = None
        try:
            # mode=ro 使 SQLite 引擎层面拒绝所有写操作
            conn = sqlite3.connect(
                f"file:{self.db_path}?mode=ro",
                uri=True,
            )
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(cleaned)

            columns = [desc[0] for desc in cursor.description]
            rows = [list(row) for row in cursor.fetchmany(1000)]

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }

        except sqlite3.OperationalError as e:
            logger.warning("SQL 执行失败: %s | SQL: %s", e, cleaned[:200])
            return {"error": f"查询执行失败，请检查 SQL 语法"}

        except Exception as e:
            logger.error("SQL 执行异常: %s | SQL: %s", e, cleaned[:200])
            return {"error": "查询执行时发生未知错误"}

        finally:
            if conn:
                conn.close()
