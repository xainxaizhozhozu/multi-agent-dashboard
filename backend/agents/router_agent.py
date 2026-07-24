"""Router Agent: 理解用户问题，输出结构化任务计划（意图、维度、SQL建议、图表类型）"""

import json
from agents.base_agent import BaseAgent


class RouterAgent(BaseAgent):

    SYSTEM_PROMPT = """你是一个数据分析路由专家。理解用户的自然语言查询，输出结构化任务计划。

工作：
1. 意图识别：判断用户想看什么数据
2. 维度提取：时间、地区、类别等
3. SQL 建议：基于下面的 Schema 生成 SQL
4. 图表推荐：根据数据特征选图表类型

### 表结构：

sales: date(TEXT), amount(REAL), region(TEXT), product_category(TEXT), quantity(INTEGER), customer_type(TEXT)
employees: name(TEXT), department(TEXT), position(TEXT), salary(REAL), join_date(TEXT), status(TEXT)
products: name(TEXT), category(TEXT), cost_price(REAL), sell_price(REAL), stock(INTEGER)

### 图表映射：
- trend/time_series -> "line"
- comparison/ranking -> "bar"
- distribution/proportion -> "pie"
- overview/stats -> "combo"
- employee/department -> "bar"
- product/category -> "pie"

### 返回 JSON（不要 Markdown 标记）：
{
    "intent": "描述",
    "dimensions": ["region", "date"],
    "metrics": ["amount"],
    "suggested_sql": "SELECT ...",
    "chart_type": "bar|line|pie|combo",
    "chart_title": "标题",
    "filters": {}
}

用户请求不清时返回：
{
    "intent": "clarification_needed",
    "response_text": "请明确分析维度...",
    "chart_type": null,
    "suggested_sql": null
}"""

    async def process(self, input_data: dict) -> dict:
        user_query = input_data.get("query", "")

        if not user_query.strip():
            return {
                "error": "请输入您要分析的问题",
                "needs_clarification": True,
                "response_text": "请问您想了解哪方面的数据？例如：\n- '华东区上个月的销售额'\n- '各产品线利润排行'\n- '最近三个月趋势'",
            }

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]

        result = await self._call_llm(messages)

        try:
            plan = json.loads(result)
        except json.JSONDecodeError:
            return {
                "intent": "unclear",
                "response_text": result,
                "chart_type": None,
                "suggested_sql": None,
            }

        return plan
