"""
LLM 服务模块 — 封装大模型调用，支持 Mock / 真实两种模式。
通过 .env 中 USE_MOCK_MODE 切换，Mock 模式无需 API Key。
"""

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMService:
    """统一 LLM 接口，底层可切换 MockProvider / OpenAIProvider"""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_MODE", "true").lower() == "true"

        if self.mock_mode:
            logger.info("[LLM] mock mode enabled")
            self.provider = MockProvider()
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.getenv("MODEL_NAME", "gpt-4o-mini")

            if not api_key:
                raise ValueError("请配置 OPENAI_API_KEY 或设置 USE_MOCK_MODE=true")

            self.provider = OpenAIProvider(
                api_key=api_key, base_url=base_url, model=model
            )

    async def chat(self, messages: list[dict]) -> str:
        return await self.provider.chat(messages)

    async def chat_json(self, messages: list[dict]) -> dict:
        text = await self.chat(messages + [
            {"role": "system", "content": "请只返回纯 JSON，不要包含 Markdown 代码块标记。"}
        ])

        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {text[:200]}")
            return {"error": f"JSON解析失败: {str(e)}", "raw": text}


class MockProvider:
    """Mock 模式：根据关键词匹配返回预定义的 JSON 响应"""

    async def chat(self, messages: list[dict]) -> str:
        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        return self._generate_response(last_user_msg)

    def _generate_response(self, user_query: str) -> str:
        query = user_query.lower()

        if any(k in query for k in ["员工", "薪资", "工资", "部门", "salary", "employee"]):
            return json.dumps({
                "sql": "SELECT department, ROUND(AVG(salary), 0) as avg_salary, COUNT(*) as emp_count FROM employees GROUP BY department ORDER BY avg_salary DESC",
                "suggested_sql": "SELECT department, ROUND(AVG(salary), 0) as avg_salary, COUNT(*) as emp_count FROM employees GROUP BY department ORDER BY avg_salary DESC",
                "explanation": "按部门统计平均薪资和人数分布",
                "chart_type": "bar",
                "chart_title": "各部门平均薪资对比",
            }, ensure_ascii=False)

        elif any(k in query for k in ["产品类别", "销售占比", "品类", "category", "product"]):
            return json.dumps({
                "sql": "SELECT product_category, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY product_category ORDER BY total_amount DESC",
                "suggested_sql": "SELECT product_category, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY product_category ORDER BY total_amount DESC",
                "explanation": "各产品品类的销售额及订单量统计",
                "chart_type": "pie",
                "chart_title": "各产品品类销售占比",
            }, ensure_ascii=False)

        elif any(k in query for k in ["趋势", "变化", "trend", "month", "月"]):
            return json.dumps({
                "sql": "SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue, COUNT(*) as orders FROM sales GROUP BY month ORDER BY month",
                "suggested_sql": "SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue, COUNT(*) as orders FROM sales GROUP BY month ORDER BY month",
                "explanation": "按月聚合销售额和订单数",
                "chart_type": "line",
                "chart_title": "月度销售趋势",
            }, ensure_ascii=False)

        else:
            return json.dumps({
                "sql": "SELECT region, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY region ORDER BY total_amount DESC",
                "suggested_sql": "SELECT region, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY region ORDER BY total_amount DESC",
                "explanation": "按地区聚合销售总额和订单数量",
                "chart_type": "bar",
                "chart_title": "各地区销售总额对比",
            }, ensure_ascii=False)


class OpenAIProvider:
    """通过 langchain 调用 OpenAI 兼容 API"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.llm = None
        self._api_key = api_key
        self._base_url = base_url
        self._model = model

    async def chat(self, messages: list[dict]) -> str:
        if self.llm is None:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                model=self._model,
                temperature=0,
                max_tokens=2048,
            )

        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

        response = await self.llm.ainvoke(lc_messages)
        return response.content
