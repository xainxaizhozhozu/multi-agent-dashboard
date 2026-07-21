"""
SQL Agent（数据提取智能体）

职责：根据 Router 的任务计划，生成精确的 SQL 查询并执行。

工作流程：
1. 接收 Router 输出的任务计划（包含 suggested_sql、维度、指标等）
2. 优化和修正 SQL 语句
3. 执行 SQL 查询数据库
4. 返回结构化结果

### SQL Agent 的安全防护：
- 只允许 SELECT 语句
- 禁止 INSERT/UPDATE/DELETE/DROP 等操作
- 限制最大返回行数（1000条）
"""

import json
from services.llm_service import LLMService
from services.query_executor import QueryExecutor
from agents.base_agent import BaseAgent


class SQLAgent(BaseAgent):
    """SQL Agent — 数据的获取者"""

    SYSTEM_PROMPT = """你是一个精通 SQL 的数据工程师。你的任务是根据用户的分析需求，生成准确、高效的 SQL 查询语句。

### 可用表结构：

**sales** (销售记录)
| date | amount | region | product_category | quantity | customer_type |
|------|--------|--------|------------------|----------|---------------|
| 2024-01-15 | 12500 | 华东 | 电子产品 | 5 | 企业客户 |

**employees** (员工信息)
| name | department | position | salary | join_date | status |
|------|------------|----------|--------|-----------|--------|
| 张伟 | 技术部 | 高级工程师 | 18000 | 2022-03-01 | active |

**products** (产品信息)
| name | category | cost_price | sell_price | stock |
|------|----------|------------|------------|-------|
| 笔记本电脑 | 电子产品 | 4500 | 6800 | 150 |

### 常见查询模式：

**按月统计销售额：**
SELECT strftime('%Y-%m', date) as month, SUM(amount) as total 
FROM sales GROUP BY month ORDER BY month

**按地区统计：**
SELECT region, SUM(amount) as total, COUNT(*) as orders 
FROM sales GROUP BY region ORDER BY total DESC

**产品类别占比：**
SELECT product_category, SUM(amount) as total 
FROM sales GROUP BY product_category ORDER BY total DESC

**最近N个月趋势：**
SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue 
FROM sales WHERE date >= date('now', '-6 months')
GROUP BY month ORDER BY month

### 你的输出格式（必须是合法 JSON）：
{
    "sql": "完整的 SELECT 语句",
    "explanation": "这个查询做了什么（中文说明）"
}

注意事项：
1. SQL 必须语法正确
2. 金额字段建议 ROUND(..., 2) 保留两位小数
3. 日期处理注意使用 SQLite 的日期函数
4. 如果不需要过滤条件，不要添加多余的 WHERE 子句
5. 只返回 SQL SELECT 查询，不要返回其他操作
"""

    def __init__(self, llm_service: LLMService | None = None):
        super().__init__("SQL_Agent", llm_service)
        self.executor = QueryExecutor()

    async def process(self, input_data: dict) -> dict:
        router_plan = input_data  # 接收 Router 的输出

        # 如果是从用户直接过来的（没有经过 Router），先做简单分析
        if "suggested_sql" in router_plan and router_plan.get("suggested_sql"):
            sql_draft = router_plan["suggested_sql"]
        elif "query" in router_plan:
            # 没有 Router，直接用 query 生成 SQL
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
            return {
                "error": "缺少必要的输入参数",
                "needs_retry": True,
            }

        print(f"📝 SQL Agent 生成的 SQL:\n{sql_draft}\n")

        # ── 执行 SQL ───────────────────────────────────
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
