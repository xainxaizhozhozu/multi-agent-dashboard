"""
项目一：Multi-Agent 智能数据分析与自动化报表系统
FastAPI 主入口文件

这个文件做了三件事：
1. 注册所有路由（API 接口）
2. 配置跨域中间件（CORS），让前端可以访问后端
3. 提供 Swagger 文档（http://localhost:8000/docs）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── 数据库初始化（应用启动时执行一次）────────────────────
def init_db():
    """
    在应用启动时调用，负责：
    1. 创建 SQLite 数据库表
    2. 注入示例数据（如果没有数据的话）
    
    你不需要修改这个函数，但建议读一遍理解它在做什么。
    """
    from schema.database import create_tables, seed_sample_data
    logger.info("正在初始化数据库...")
    create_tables()
    seed_sample_data()
    logger.info("数据库初始化完成 ✓")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 的生命周期管理器。
    lifespan 是 "enter" 和 "exit" 的组合——
    应用启动时执行 init_db，关闭时做清理工作。
    """
    init_db()
    yield  # ← 这里应用开始正常运行
    logger.info("应用关闭中...")


# ── 创建 FastAPI 实例 ───────────────────────────────────
app = FastAPI(
    title="AI Multi-Agent Data Dashboard",
    description="基于多智能体协作的智能化数据分析平台",
    version="1.0.0",
    lifespan=lifespan,  # ← 绑定生命周期
)

# ── 允许前端跨域访问 ─────────────────────────────────────
# 开发环境允许 Vite 默认的 localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 导入并注册路由 ───────────────────────────────────────
from routers.dashboard import router as dashboard_router
from routers.agent import router as agent_router

app.include_router(dashboard_router)   # 看板相关接口（统计、趋势）
app.include_router(agent_router)       # Agent 交互接口（对话→生成图表）


# ── 健康检查接口 ─────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    """根路径，用于验证服务是否正常运行"""
    return {
        "message": "欢迎使用 AI Multi-Agent 智能数据分析系统",
        "status": "running",
        "docs": "/docs",           # Swagger 文档页面
        "agent_api": "/api/v1/agent/chat",
    }


# ── 如果直接运行此文件 ───────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",     # 模块名:变量名
        host="0.0.0.0", # 监听所有网络接口
        port=8000,      # 端口号
        reload=True,    # 代码修改后自动重启（开发用）
    )
