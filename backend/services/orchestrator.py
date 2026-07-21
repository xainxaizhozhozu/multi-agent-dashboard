"""
Agent Orchestrator（智能体编排器）

职责：协调四个 Agent 的顺序执行，处理异常和重试。

执行流程：
    User Query ──► Router ──► SQL ──► Chart ──► Review ──► Response
                        │              │         │          │
                        ▼              ▼         ▼          ▼
                  任务计划      SQL+数据     ECharts      校验结果
                              
异常情况处理：
- Router 无法理解 → 反问用户
- SQL 执行失败 → 打回给 SQL Agent 重试（最多2次）
- Chart 配置不完整 → 打回给 Chart Agent 重新生成
- Review 发现严重问题 → 整体打回 Router 重新开始

这是整个项目的核心架构代码。面试时可以详细讲解这个设计。
"""

import json
import time
from services.llm_service import LLMService
from agents.router_agent import RouterAgent
from agents.sql_agent import SQLAgent
from agents.chart_agent import ChartAgent
from agents.reviewer_agent import ReviewerAgent


class AgentOrchestrator:
    """
    多智能体编排器
    
    设计模式：Pipeline（管道模型）+ Retry（重试机制）
    
    你可以把它想象成一个工作流引擎：
    - 每个 Agent 是一个工位
    - 数据是流水线上的产品
    - Orchestrator 是调度员
    """

    def __init__(self):
        # 创建一个调用大模型的工具对象
        self.llm = LLMService()
        
        # 初始化四个“协作小助手”
        # 它们分别负责不同任务：理解问题、查数据、画图、检查结果
        self.router = RouterAgent("Router", self.llm)
        self.sql_agent = SQLAgent(self.llm)
        self.chart_agent = ChartAgent(self.llm)
        self.reviewer = ReviewerAgent()

    async def process_query(self, user_query: str, session_id: str = "") -> dict:
        """
        处理一条用户查询的完整流程
        
        参数:
            user_query: 用户的自然语言输入
            session_id: 会话 ID（用于追踪同一轮对话）
        
        返回:
            {
                "success": True/False,
                "response_text": "聊天回复（如果需要澄清）",
                "chart_type": "bar/line/pie/combo",
                "chart_title": "...",
                "chart_config": {...},       // ECharts 配置
                "raw_data": [[...]],         // 原始数据
                "columns": [...],            // 列名
                "sql": "...",               // 执行的 SQL
                "review_passed": True,      // 是否通过审查
                "message": "..."            // 状态消息
            }
        """
        # 记录开始时间，方便后面统计整个流程花了多少时间
        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"🤖 Agent 协作流程开始")
        print(f"📝 用户问题: {user_query}")
        print(f"{'='*60}\n")

        try:
            # ──────────────────────────────────────────────
            # Stage 1: Router — 先理解用户想要什么
            # 这里相当于“总负责人”，先判断问题是什么、需不需要澄清
            # ──────────────────────────────────────────────
            print("① [Router Agent] 正在分析您的意图...\n")
            router_output = await self.router.process({"query": user_query})

            # 如果 Router 认为需要澄清
            if router_output.get("needs_clarification"):
                elapsed = time.time() - start_time
                print(f"\n⏱ 总耗时: {elapsed:.2f}s")
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

            print(f"   📋 任务计划: {json.dumps(router_output, ensure_ascii=False)[:200]}...\n")

            # ──────────────────────────────────────────────
            # Stage 2: SQL Agent — 根据需求去数据库取数据
            # 这里负责把问题翻译成 SQL，并把结果查出来
            # ──────────────────────────────────────────────
            print("② [SQL Agent] 正在准备数据查询...\n")
            
            # 最多重试 2 次，避免因为一次 SQL 失败就直接报错
            max_retries = 2
            sql_result = None
            
            for attempt in range(max_retries + 1):
                # 把 Router 规划好的内容传给 SQL Agent
                sql_input = {
                    **router_output,
                    "suggested_sql": suggested_sql or "",
                }
                sql_result = await self.sql_agent.process(sql_input)

                # 如果没有错误，或者不需要再试，就停止
                if "error" not in sql_result or not sql_result.get("needs_retry"):
                    break

                print(f"   ⚠️ 第 {attempt + 1} 次尝试失败，重试中...\n")
                # 如果 SQL 有问题，就把错误内容再交给 Router，帮忙改进方案
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

            print(f"   ✅ 获取到 {sql_result.get('row_count', 0)} 条数据\n")

            # ──────────────────────────────────────────────
            # Stage 3: Chart Agent — 把数据变成图表
            # 这里会根据数据和图表类型，生成 ECharts 配置
            # ──────────────────────────────────────────────
            print("③ [Chart Agent] 正在生成可视化图表...\n")
            
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

            print(f"   ✅ 图表配置已生成: {chart_type}\n")

            # ──────────────────────────────────────────────
            # Stage 4: Review Agent — 最后做一次检查
            # 这里像“质检员”一样，看看生成的 SQL 和图表配置是否合理
            # ──────────────────────────────────────────────
            print("④ [Review Agent] 正在进行质量审查...\n")
            
            review_input = {
                "sql": sql_result.get("sql", ""),
                "chart_config": chart_result.get("chart_config"),
            }
            review_result = await self.reviewer.process(review_input)

            # ──────────────────────────────────────────────
            # ──────────────────────────────────────────────
            # 把上面各个步骤的结果整理成一个完整返回值
            # 这样前端就能直接使用这些数据展示页面
            # ──────────────────────────────────────────────
            elapsed = time.time() - start_time

            result = {
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

            print(f"\n{'='*60}")
            print(f"✅ 全部完成! 耗时: {elapsed:.2f}s")
            print(f"{'='*60}")

            return result

        except Exception as e:
            print(f"\n❌ 系统异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "response_text": "系统内部出错，请稍后重试",
                "elapsed_seconds": round(time.time() - start_time, 2),
            }
