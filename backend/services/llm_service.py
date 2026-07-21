"""
LLM 服务模块：封装与大模型的交互。

支持两种模式：
1. Mock 模式（默认）— 返回模拟响应，无需 API Key
2. 真实模式 — 调用 OpenAI/DashScope API

切换方式：在 .env 中设置 USE_MOCK_MODE=true/false
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class LLMService:
    """
    LLM 服务类
    
    设计思路：统一接口，底层可以切换不同的模型提供商。
    目前实现了 MockProvider 和 OpenAIProvider 两种实现。
    """

    def __init__(self):
        # 检查是否使用 Mock 模式
        self.mock_mode = os.getenv("USE_MOCK_MODE", "true").lower() == "true"

        if self.mock_mode:
            print("ℹ [LLM Service] 处于 Mock 模式，无需 API Key")
            self.provider = MockProvider()
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.getenv("MODEL_NAME", "gpt-4o-mini")

            if not api_key:
                raise ValueError(
                    "请在 .env 文件中配置 OPENAI_API_KEY，或设置 USE_MOCK_MODE=true"
                )

            from langchain_openai import ChatOpenAI
            self.provider = OpenAIProvider(
                api_key=api_key,
                base_url=base_url,
                model=model,
            )

    async def chat(self, messages: list[dict]) -> str:
        """
        发送对话请求到 LLM
        
        参数:
            messages: 消息列表，格式 [{"role": "user/system/assistant", "content": "..."}]
        
        返回:
            LLM 的回复文本
            
        示例:
            result = await llm_service.chat([
                {"role": "system", "content": "你是一个数据分析专家"},
                {"role": "user", "content": "帮我看看华东区销售额"}
            ])
        """
        return await self.provider.chat(messages)

    async def chat_json(self, messages: list[dict]) -> dict:
        """
        发送对话请求并期望返回 JSON 格式的回复
        
        参数同上
        
        返回:
            解析后的字典对象
            
        注意：会在消息末尾追加要求返回 JSON 的提示词
        """
        text = await self.chat(messages + [
            {"role": "system", "content": "请只返回纯 JSON 数据，不要包含 Markdown 代码块标记（```json）。确保 JSON 格式合法。"}
        ])

        # 清理可能的 Markdown 标记
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠ JSON 解析失败，原始回复: {text}")
            return {"error": f"JSON解析失败: {str(e)}", "raw": text}


# ── Mock 提供者（不需要 API Key）───────────────────────────
class MockProvider:
    """
    模拟 LLM 响应。
    
    在项目开发和演示阶段非常有用——你可以看到完整的系统流程，
    而不需要支付 API 费用。
    
    当你在 .env 中设置 USE_MOCK_MODE=false 并提供 API Key 后，
    这部分代码会自动被 OpenAIProvider 替换。
    """

    async def chat(self, messages: list[dict]) -> str:
        # 从消息中提取用户问题（最后一条 user 消息）
        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        return self._generate_response(last_user_msg)

    def _generate_response(self, user_query: str) -> str:
        """根据用户问题智能匹配对应的模拟数据"""
        query = user_query.lower()
        
        # ── 员工薪资查询 ──────────────────────────────
        if any(k in query for k in ["员工", "薪资", "工资", "部门", "salary", "employee"]):
            return json.dumps({
                "sql": "SELECT department, ROUND(AVG(salary), 0) as avg_salary, COUNT(*) as emp_count FROM employees GROUP BY department ORDER BY avg_salary DESC",
                "suggested_sql": "SELECT department, ROUND(AVG(salary), 0) as avg_salary, COUNT(*) as emp_count FROM employees GROUP BY department ORDER BY avg_salary DESC",
                "explanation": "按部门统计平均薪资和人数分布，直观对比各部门薪酬水平差异",
                "chart_type": "bar",
                "chart_title": "各部门平均薪资对比",
            }, ensure_ascii=False)
        
        # ── 产品销售占比（饼图）───────────────────────────
        elif any(k in query for k in ["产品类别", "销售占比", "品类", "category", "product"]):
            return json.dumps({
                "sql": "SELECT product_category, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY product_category ORDER BY total_amount DESC",
                "suggested_sql": "SELECT product_category, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY product_category ORDER BY total_amount DESC",
                "explanation": "各产品品类的销售额及订单量统计，帮助了解业务重心分布",
                "chart_type": "pie",
                "chart_title": "各产品品类销售占比",
            }, ensure_ascii=False)
        
        # ── 趋势查询（折线图）────────────────────────────
        elif any(k in query for k in ["趋势", "趋势怎么样", "变化", "trend", "month", "月"]):
            return json.dumps({
                "sql": "SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue, COUNT(*) as orders FROM sales GROUP BY month ORDER BY month",
                "suggested_sql": "SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue, COUNT(*) as orders FROM sales GROUP BY month ORDER BY month",
                "explanation": "按月聚合销售额和订单数，观察收入变化趋势",
                "chart_type": "line",
                "chart_title": "月度销售趋势",
            }, ensure_ascii=False)
        
        # ── 默认：地区对比（柱状图）────────────────────────
        else:
            return json.dumps({
                "sql": "SELECT region, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY region ORDER BY total_amount DESC",
                "suggested_sql": "SELECT region, SUM(amount) as total_amount, COUNT(*) as order_count FROM sales GROUP BY region ORDER BY total_amount DESC",
                "explanation": "按地区聚合销售总额和订单数量，帮助了解各区域业绩表现",
                "chart_type": "bar",
                "chart_title": "各地区销售总额对比",
            }, ensure_ascii=False)


# ── OpenAI 提供者（真实 API 调用）───────────────────────────
class OpenAIProvider:
    """
    通过 LangChain 调用 OpenAI 兼容的 LLM API。
    
    可以对接：
    - OpenAI (gpt-4o, gpt-4o-mini)
    - 阿里云通义千问 (DashScope)
    - DeepSeek
    - 任何其他 OpenAI 兼容接口
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        self.llm = None  # 延迟初始化，避免不必要的导入
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
                temperature=0,     # 低温度 = 更确定性的输出
                max_tokens=2048,   # 最大输出 token 数
            )

        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

        # 将 dict 格式的 messages 转为 LangChain 的 Message 对象
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
