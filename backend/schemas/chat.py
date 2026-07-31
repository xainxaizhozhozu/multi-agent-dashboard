"""
Agent 聊天相关请求/响应模型

覆盖端点：
  POST /api/v1/agent/chat  — ChatRequest / ChatResponse
  GET  /api/v1/agent/status — AgentStatusResponse
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any


# ── 请求 ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Agent 对话请求体"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="用户的自然语言查询",
        examples=["各地区销售额对比", "月度销售趋势"],
    )
    session_id: Optional[str] = Field(
        None,
        description="会话 ID，用于上下文关联（可选）",
    )

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("查询内容不能为空白")
        return v


# ── 响应 ──────────────────────────────────────────────

class ChatResponse(BaseModel):
    """Agent 对话响应体"""
    success: bool
    chart_type: Optional[str] = None
    chart_title: Optional[str] = None
    chart_config: Optional[dict[str, Any]] = None
    raw_data: Optional[list] = None
    columns: Optional[list[str]] = None
    sql: Optional[str] = None
    explanation: Optional[str] = None
    review_passed: Optional[bool] = None
    message: Optional[str] = None
    agent_timeline: Optional[dict[str, str]] = None
    elapsed_seconds: Optional[float] = None
    error: Optional[str] = None


class AgentInfo(BaseModel):
    """单个 Agent 信息"""
    name: str
    status: str
    description: Optional[str] = None


class AgentStatusResponse(BaseModel):
    """Agent 系统状态响应"""
    status: str
    agents: list[AgentInfo]
    ready: bool
