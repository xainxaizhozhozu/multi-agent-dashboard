"""
Agent Pipeline 类型契约

定义 Agent 之间传递数据的结构类型（TypedDict），
用于 IDE 自动补全、静态分析（mypy）和运行时文档。

Pipeline 数据流：
  User Query → Router → SQL Agent → Chart Agent → Reviewer → Frontend

每个 TypedDict 标注了必填/可选字段，与实际代码保持一致。
"""

from typing import TypedDict, Optional


# ── Router Agent 输出 ─────────────────────────────────

class RouterOutput(TypedDict, total=False):
    """
    RouterAgent.process() 返回值。

    成功时必须包含 intent, chart_type, chart_title, suggested_sql。
    需要用户澄清时包含 needs_clarification + response_text。
    失败时包含 error。
    """
    intent: str              # 查询意图，如 "regional_comparison", "trend_analysis"
    dimensions: list[str]    # 分析维度，如 ["region"]
    metrics: list[str]       # 度量指标，如 ["total_amount", "order_count"]
    suggested_sql: str       # 推荐的 SQL 查询（供 SQL Agent 参考或直接使用）
    chart_type: str          # 推荐图表类型：bar / line / pie / combo
    chart_title: str         # 图表标题
    filters: dict            # 过滤条件，如 {"date_range": "last_90_days"}
    needs_clarification: bool  # 是否需要用户进一步澄清
    response_text: str       # 澄清/错误时的人可读文本
    error: str               # 处理异常时的错误信息


# ── SQL Agent 输出 ────────────────────────────────────

class SQLAgentOutput(TypedDict, total=False):
    """
    SQLAgent.process() 返回值。

    成功时必须包含 sql, data, columns, row_count, explanation。
    失败时包含 error + needs_retry。
    """
    sql: str                 # 最终执行的 SQL
    data: list[list]         # 查询结果行，如 [["华东", 12345], ["华南", 9876]]
    columns: list[str]       # 列名，如 ["region", "total_amount"]
    row_count: int           # 返回行数
    explanation: str         # SQL 的自然语言解释
    error: str               # 错误信息
    needs_retry: bool        # 是否需要 Router 重新规划


# ── Chart Agent 输出 ──────────────────────────────────

class ChartConfig(TypedDict, total=False):
    """ECharts / Recharts 配置对象"""
    type: str                # bar / line / pie / combo
    title: str
    xAxis: Optional[dict]
    yAxis: Optional[dict]
    series: list[dict]
    tooltip: Optional[dict]
    legend: Optional[dict]


class ChartAgentOutput(TypedDict, total=False):
    """
    ChartAgent.process() 返回值。

    成功时包含 chart_config, chart_type, chart_title, raw_data, columns。
    """
    chart_config: dict       # ECharts option 对象
    chart_type: str          # 图表类型
    chart_title: str         # 图表标题
    raw_data: list           # 原始数据行（前端用于表格展示）
    columns: list[str]       # 列名


# ── Reviewer Agent 输出 ──────────────────────────────

class ValidationResult(TypedDict):
    """单项校验结果"""
    passed: bool
    issues: list[str]
    severity: str            # "info" / "warning" / "error"


class ReviewerOutput(TypedDict, total=False):
    """
    ReviewerAgent.process() 返回值。

    包含 SQL 校验和图表校验两个维度的结果。
    """
    review_passed: bool      # 总体是否通过
    sql_validation: ValidationResult
    chart_validation: ValidationResult
    message: str             # 审查总结信息


# ── Pipeline 最终输出（Orchestrator → Frontend）────────

class PipelineResult(TypedDict, total=False):
    """
    AgentOrchestrator.process_query() 返回值。
    前端 AgentResponse 组件直接消费此结构。
    """
    success: bool
    chart_type: str
    chart_title: str
    chart_config: dict
    raw_data: list
    columns: list[str]
    sql: str
    explanation: str
    review_passed: bool
    message: str
    agent_timeline: dict[str, str]   # {"Router": "0.2s", "SQL_Agent": "0.5s", ...}
    elapsed_seconds: float
    error: str
