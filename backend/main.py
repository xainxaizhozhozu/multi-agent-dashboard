import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    from schema.database import create_tables, seed_sample_data
    logger.info("initializing database...")
    create_tables()
    seed_sample_data()
    logger.info("database ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    logger.info("shutting down...")


app = FastAPI(
    title="AI Multi-Agent Data Dashboard",
    description="Multi-agent data analysis: natural language -> SQL -> chart",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers.dashboard import router as dashboard_router
from routers.agent import router as agent_router

app.include_router(dashboard_router)
app.include_router(agent_router)


@app.get("/", tags=["health"])
async def root():
    return {
        "message": "AI Multi-Agent Data Dashboard",
        "status": "running",
        "docs": "/docs",
        "agent_api": "/api/v1/agent/chat",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
