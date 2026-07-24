"""
Agent 编排器 — 协调 Router/SQL/Chart/Review 四个 Agent 顺序执行。
Pipeline: User Query -> Router -> SQL -> Chart -> Review -> Response
SQL 失败时自动重试（最多2次），Review 发现安全问题则标记不通过。
"""

import json
import time
import logging
from services.llm_service import LLMService
from agents.router_agent import RouterAgent
from agents.sql_agent import SQLAgent
from agents.chart_agent import ChartAgent
from agents.reviewer_agent import ReviewerAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """多 Agent 编排器：Pipeline + Retry"""

    def __init__(self):
        self.llm = LLMService()
        self.router = RouterAgent("Router", self.llm)
        self.sql_agent = SQLAgent(self.llm)
        self.chart_agent = ChartAgent(self.llm)
        self.reviewer = ReviewerAgent()

    async def process_query(self, user_query: str, session_id: str = "") -> dict:
        """
        处理一条用户查询，依次经过 Router -> SQL -> Chart -> Review。
        返回包含 chart_config、raw_data、sql 等字段的完整结果。
        """
        start_time = time.time()
        logger.info(f"[Orchestrator] query={user_query}")

        try:
            # Stage 1: Router — 意图识别
            logger.debug("[Router] analyzing intent...")
            router_output = await self.router.process({"query": user_query})

            if router_output.get("needs_clarification"):
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "needs_clarification": True,
                    "response_text": router_output.get("response_text", "请补充更多信息"),
                    "elapsed_seconds": round(elapsed, 2),
                }

            intent = router_output.get("intent", "unknown")
            chart_type = router_output.get("chart_type")
            chart_title = router_output.get("chart_title", "数据分析图表")
            suggested_sql = router_output.get("suggested_sql", "")

            logger.debug(f"[Router] intent={intent}, chart_type={chart_type}")

            # Stage 2: SQL Agent — 数据查询（带重试）
            logger.debug("[SQL] executing query...")
            max_retries = 2
            sql_result = None

            for attempt in range(max_retries + 1):
                sql_input = {
                    **router_output,
                    "suggested_sql": suggested_sql or "",
                }
                sql_result = await self.sql_agent.process(sql_input)

                if "error" not in sql_result or not sql_result.get("needs_retry"):
                    break

                logger.warning(f"[SQL] attempt {attempt + 1} failed, retrying...")
                error_feedback = f"上一次生成的 SQL 出错了: {sql_result.get('error')}"
                revised_plan = await self.router.process({
                    **router_output,
                    "error_context": error_feedback,
                })
                suggested_sql = revised_plan.get("suggested_sql", "")

            if sql_result is None or "data" not in sql_result:
                return {
                    "success": False,
                    "response_text": f"数据查询失败: {sql_result.get('error', '未知错误')}",
                    "elapsed_seconds": round(time.time() - start_time, 2),
                }

            logger.debug(f"[SQL] got {sql_result.get('row_count', 0)} rows")

            # Stage 3: Chart Agent — 生成图表配置
            logger.debug("[Chart] generating visualization...")
            chart_input = {
                **sql_result,
                "chart_type": chart_type or "bar",
                "chart_title": chart_title,
            }
            chart_result = await self.chart_agent.process(chart_input)

            if "error" in chart_result:
                return {
                    "success": False,
                    "response_text": chart_result["error"],
                    "elapsed_seconds": round(time.time() - start_time, 2),
                }

            # Stage 4: Review Agent — 质量校验
            logger.debug("[Review] validating output...")
            review_input = {
                "sql": sql_result.get("sql", ""),
                "chart_config": chart_result.get("chart_config"),
            }
            review_result = await self.reviewer.process(review_input)

            elapsed = time.time() - start_time
            logger.info(f"[Orchestrator] done in {elapsed:.2f}s")

            return {
                "success": True,
                "chart_type": chart_type or "bar",
                "chart_title": chart_title,
                "chart_config": chart_result.get("chart_config"),
                "raw_data": chart_result.get("raw_data", []),
                "columns": chart_result.get("columns", []),
                "sql": sql_result.get("sql", ""),
                "explanation": sql_result.get("explanation", ""),
                "review_passed": review_result.get("review_passed", True),
                "message": review_result.get("message", "分析完成"),
                "agent_timeline": {
                    "router": "intent parsed",
                    "sql": f"{sql_result.get('row_count', 0)} rows",
                    "chart": f"{chart_type} generated",
                    "review": "passed" if review_result.get("review_passed") else "warnings",
                },
                "elapsed_seconds": round(elapsed, 2),
            }

        except Exception as e:
            logger.error(f"[Orchestrator] unexpected error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "response_text": "系统内部出错，请稍后重试",
                "elapsed_seconds": round(time.time() - start_time, 2),
            }
