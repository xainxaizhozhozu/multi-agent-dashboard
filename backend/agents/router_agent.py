"""
Router Agent（路由/规划智能体）

职责：理解用户的自然语言问题，将其拆解为可执行的任务计划。

工作流程：
1. 接收用户输入（如"帮我看看华东区上个月的销售额趋势"）
2. 分析意图：识别关键维度（地区、时间、指标）
3. 输出结构化任务计划供下游 Agent 使用
"""

import json
from services.llm_service import LLMService
from agents.base_agent import BaseAgent


class RouterAgent(BaseAgent):
    """路由 Agent — 系统的第一道关卡"""

    SYSTEM_PROMPT = """你是一个智能化的数据分析路由专家。你的任务是理解用户的自然语言查询需求，并将其转化为结构化的任务计划。

你需要完成以下工作：
1. **意图识别**：判断用户想看什么类型的数据（销售分析、员工统计、产品概览等）
2. **维度提取**：找出关键分析维度（时间范围、地区、类别等）
3. **SQL 建议**：基于以下数据库 Schema 生成 SQL 查询建议
4. **图表推荐**：根据数据类型推荐最合适的图表类型

### 数据库表结构说明：

**sales 表（销售记录）**
- date: TEXT — 销售日期 (YYYY-MM-DD)
- amount: REAL — 销售金额
- region: TEXT — 地区 (华东/华南/华北/西南/华中)
- product_category: TEXT — 产品类别 (电子产品/办公用品/软件服务/咨询服务/硬件设备)
- quantity: INTEGER — 数量
- customer_type: TEXT — 客户类型 (企业客户/个人客户)

**employees 表（员工信息）**
- name: TEXT — 姓名
- department: TEXT — 部门
- position: TEXT — 职位
- salary: REAL — 月薪
- join_date: TEXT — 入职日期
- status: TEXT — 状态 (active/resigned)

**products 表（产品信息）**
- name: TEXT — 产品名称
- category: TEXT — 分类
- cost_price: REAL — 成本价
- sell_price: REAL — 销售价
- stock: INTEGER — 库存

### 图表类型映射规则：
- time_series / trend → "line" （趋势图用折线图）
- comparison / ranking → "bar"   （对比图用柱状图）
- distribution / proportion → "pie" （占比图用饼图）
- overview / stats → "combo"    （综合概览用组合面板）
- employee / salary / department → "bar"   （员工统计用柱状图）
- product / category → "pie"    （产品分类用饼图）

### 返回格式（必须是合法 JSON，不要包含 Markdown 标记）：
{
    "intent": "简要描述用户意图",
    "dimensions": ["region", "date"],      // 分析的维度
    "metrics": ["amount"],                 // 要聚合的指标
    "suggested_sql": "SELECT ... ",        // SQL 查询语句草稿
    "chart_type": "bar|line|pie|combo",   // 推荐的图表类型
    "chart_title": "图表标题",
    "filters": {"region": "华东"}          // 条件过滤（可选）
}

如果用户的请求不清晰，返回：
{
    "intent": "clarification_needed",
    "response_text": "请明确您想分析的具体维度...",
    "chart_type": null,
    "suggested_sql": null
}"""

    async def process(self, input_data: dict) -> dict:
        user_query = input_data.get("query", "")

        if not user_query.strip():
            return {
                "error": "请输入您要分析的问题",
                "needs_clarification": True,
                "response_text": "请问您想了解哪方面的数据？例如：" + 
                    "\n- '华东区上个月的销售额是多少'" +
                    "\n- '各产品线利润排行'" +
                    "\n- '最近三个月的销售趋势'",
            }

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]

        result = await self._call_llm(messages)

        try:
            plan = json.loads(result)
        except json.JSONDecodeError:
            # Mock 模式下可能直接返回了文本描述
            return {
                "intent": "unclear",
                "response_text": result,
                "chart_type": None,
                "suggested_sql": None,
            }

        return plan
