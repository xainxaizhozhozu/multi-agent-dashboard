"""Agent 对话接口：POST /api/v1/agent/chat 接收用户问题，启动多 Agent 流程"""

import uuid
import logging
from fastapi import APIRouter, HTTPException, Request
from services.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent", tags=["AI Agent"])

# 延迟初始化：在第一次请求时创建，避免 import 时崩溃
_orchestrator: AgentOrchestrator | None = None


def get_orchestrator() -> AgentOrchestrator:
    """懒加载 orchestrator，首次调用时初始化"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


@router.post("/chat")
async def agent_chat(request: dict):
    query = request.get("query", "").strip()
    session_id = request.get("session_id", str(uuid.uuid4())[:8])

    if not query:
        raise HTTPException(status_code=400, detail="请输入您要分析的问题")
    if len(query) > 500:
        raise HTTPException(status_code=400, detail="问题过长，请控制在 500 字以内")

    try:
        orch = get_orchestrator()
        result = await orch.process_query(query, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=503, detail="AI 服务未就绪，请检查配置")
    except Exception as e:
        logger.error("Agent chat error: %s", e)
        raise HTTPException(status_code=500, detail="AI 分析服务暂时不可用，请稍后重试")


@router.get("/status")
async def agent_status():
    orch = _orchestrator
    return {
        "status": "running",
        "agents": [
            {"name": "Router", "role": "意图识别与任务规划"},
            {"name": "SQL_Agent", "role": "数据查询与提取"},
            {"name": "Chart_Agent", "role": "可视化配置生成"},
            {"name": "Reviewer", "role": "质量审查"},
        ],
        "ready": orch is not None,
    }
