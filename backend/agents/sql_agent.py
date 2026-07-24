"""SQL Agent: 根据 Router 计划生成并执行 SQL，只允许 SELECT，禁止 DDL/DML"""

import json
import logging
from services.llm_service import LLMService
from services.query_executor import QueryExecutor
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SQLAgent(BaseAgent):

    SYSTEM_PROMPT = """你是一个 SQL 工程师。根据分析需求生成准确的 SELECT 查询。

### 表结构：
sales: date, amount, region, product_category, quantity, customer_type
employees: name, department, position, salary, join_date, status
products: name, category, cost_price, sell_price, stock

### 常用查询模式：
-- 按月统计
SELECT strftime('%Y-%m', date) as month, SUM(amount) as total FROM sales GROUP BY month ORDER BY month
-- 按地区
SELECT region, SUM(amount) as total, COUNT(*) as orders FROM sales GROUP BY region ORDER BY total DESC
-- 品类占比
SELECT product_category, SUM(amount) as total FROM sales GROUP BY product_category ORDER BY total DESC

### 输出 JSON：
{
    "sql": "完整 SELECT 语句",
    "explanation": "查询说明（中文）"
}

注意：只生成 SELECT，金额用 ROUND(..., 2)，日期用 SQLite 函数。
"""

    def __init__(self, llm_service: LLMService | None = None):
        super().__init__("SQL_Agent", llm_service)
        self.executor = QueryExecutor()

    async def process(self, input_data: dict) -> dict:
        router_plan = input_data

        if "suggested_sql" in router_plan and router_plan.get("suggested_sql"):
            sql_draft = router_plan["suggested_sql"]
        elif "query" in router_plan:
            user_query = router_plan["query"]
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"请根据以下问题生成 SQL：{user_query}"},
            ]
            result = await self._call_llm(messages)
            try:
                parsed = json.loads(result)
                sql_draft = parsed.get("sql", "")
            except:
                sql_draft = result
        else:
            return {"error": "缺少必要的输入参数", "needs_retry": True}

        logger.debug(f"[SQL] generated: {sql_draft[:100]}...")
        query_result = self.executor.execute(sql_draft)

        if "error" in query_result:
            return {
                "error": query_result["error"],
                "needs_retry": True,
                "sql": sql_draft,
            }

        return {
            "sql": sql_draft,
            "data": query_result["rows"],
            "columns": query_result["columns"],
            "row_count": query_result["row_count"],
            "explanation": router_plan.get("explanation", "查询结果已就绪"),
        }
