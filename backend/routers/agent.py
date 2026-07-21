"""
Agent 交互接口：前端聊天窗口调用的核心 API。

这是用户与多 Agent 系统交互的唯一入口。

接口说明：
    POST /api/v1/agent/chat
    
    Request:
    {
        "query": "帮我看看华东区的销售情况",
        "session_id": "abc123"      // 可选，用于区分不同对话
    }
    
    Response:
    {
        "success": true,
        "chart_type": "bar",
        "chart_title": "各地区销售总额对比",
        "chart_config": {...},         // ECharts 配置对象
        "raw_data": [...],             // 原始数据
        "columns": [...],              // 列名
        "sql": "SELECT ...",           // 执行的 SQL
        "explanation": "...",          // 文字解释
        "review_passed": true,
        "elapsed_seconds": 1.23        // 处理耗时
    }
"""

from fastapi import APIRouter, HTTPException
import uuid

from services.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/v1/agent", tags=["AI Agent"])

# 创建全局编排器实例（单例模式）
orchestrator = AgentOrchestrator()


@router.post("/chat")
async def agent_chat(request: dict):
    """
    AI Agent 对话接口
    
    这是整个系统的核心入口——接收用户问题，启动多 Agent 协作流程。
    """
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
    """
    查看 Agent 系统状态
    
    可用于健康检查或展示当前 Agent 配置信息
    """
    return {
        "status": "running",
        "agents": [
            {"name": "Router", "role": "意图识别与任务规划"},
            {"name": "SQL_Agent", "role": "数据查询与提取"},
            {"name": "Chart_Agent", "role": "可视化配置生成"},
            {"name": "Reviewer", "role": "质量审查与反思"},
        ],
        "mock_mode": orchestrator.llm.mock_mode,
    }
