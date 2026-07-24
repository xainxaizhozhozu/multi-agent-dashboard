"""Agent 对话接口：POST /api/v1/agent/chat 接收用户问题，启动多 Agent 流程"""

import uuid
from fastapi import APIRouter, HTTPException
from services.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/v1/agent", tags=["AI Agent"])
orchestrator = AgentOrchestrator()


@router.post("/chat")
async def agent_chat(request: dict):
    query = request.get("query", "").strip()
    session_id = request.get("session_id", str(uuid.uuid4())[:8])

    if not query:
        raise HTTPException(status_code=400, detail="请输入您要分析的问题")

    try:
        result = await orchestrator.process_query(query, session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def agent_status():
    return {
        "status": "running",
        "agents": [
            {"name": "Router", "role": "意图识别与任务规划"},
            {"name": "SQL_Agent", "role": "数据查询与提取"},
            {"name": "Chart_Agent", "role": "可视化配置生成"},
            {"name": "Reviewer", "role": "质量审查"},
        ],
        "mock_mode": orchestrator.llm.mock_mode,
    }
