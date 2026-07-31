"""
API 请求/响应模型

Pydantic 模型为所有 API 端点提供：
  - 请求参数校验（类型、必填、长度限制）
  - 响应结构文档化（自动生成 OpenAPI Schema）
  - 序列化/反序列化
"""

from schemas.chat import ChatRequest, ChatResponse, AgentInfo, AgentStatusResponse
from schemas.dashboard import (
    DashboardStats,
    MonthlyTrend,
    DailyTrend,
    RegionAnalysis,
    CategoryAnalysis,
)

__all__ = [
    "ChatRequest", "ChatResponse", "AgentInfo", "AgentStatusResponse",
    "DashboardStats", "MonthlyTrend", "DailyTrend",
    "RegionAnalysis", "CategoryAnalysis",
]
