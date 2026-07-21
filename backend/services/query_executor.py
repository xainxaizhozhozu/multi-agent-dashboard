"""
SQL 查询执行器：安全地执行 SQL 语句并返回结果。

安全设计：
1. 只允许 SELECT 语句（禁止 INSERT/UPDATE/DELETE）
2. 限制最多返回 1000 条记录
3. 捕获所有异常并返回友好错误信息
"""

import sqlite3
import os
from typing import Optional


class QueryExecutor:
    """数据库查询执行器"""

    def __init__(self):
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "dashboard.db"
        )

    def execute(self, sql: str) -> dict:
        """
        执行一条 SQL 查询
        
        参数:
            sql: SQL 语句（只允许 SELECT）
        
        返回:
            {"columns": [...], "rows": [[...]], "row_count": N}
            或 {"error": "错误信息"}
        """
        # ── 安全检查：只允许 SELECT ────────────────────
        cleaned = sql.strip().upper()
        if not cleaned.startswith("SELECT"):
            return {"error": "⛔ 仅允许执行 SELECT 查询语句"}

        # 检查是否包含危险关键词
        dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "EXEC"]
        for kw in dangerous_keywords:
            if kw in cleaned and kw != "SELECT":
                return {"error": f"⛔ 不允许使用 {kw} 操作"}

        # ── 执行查询 ───────────────────────────────────
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)

            columns = [description[0] for description in cursor.description]
            rows = [list(row) for row in cursor.fetchmany(1000)]  # 限制行数
            conn.close()

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }

        except Exception as e:
            print(f"\n❌ [QueryExecutor] SQL执行失败! SQL:\n{sql}\n错误详情: {str(e)}\n")
            return {"error": f"❌ 查询执行失败: {str(e)}"}
