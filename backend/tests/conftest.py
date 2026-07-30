"""
Shared pytest fixtures for all tests.
"""

import pytest
import os
import sys
import sqlite3
import tempfile

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import fastapi
from fastapi.testclient import TestClient
from routers.dashboard import router as dashboard_router, get_db
from routers.agent import router as agent_router


@pytest.fixture()
def temp_db():
    """Create a temporary SQLite database with sample data for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE sales (
        id INTEGER PRIMARY KEY, date TEXT, amount REAL,
        region TEXT, product_category TEXT, quantity INTEGER, customer_type TEXT
    )""")
    conn.execute("""CREATE TABLE employees (
        id INTEGER PRIMARY KEY, name TEXT, department TEXT,
        position TEXT, salary REAL, join_date TEXT, status TEXT
    )""")

    conn.executemany(
        "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "2026-07-01", 1500.00, "\u534e\u4e1c", "\u7535\u5b50\u4ea7\u54c1", 2, "VIP"),
            (2, "2026-07-15",  800.50, "\u534e\u5317", "\u670d\u88c5",     1, "\u666e\u901a"),
            (3, "2026-06-20", 2200.00, "\u534e\u5357", "\u7535\u5b50\u4ea7\u54c1", 3, "VIP"),
            (4, "2026-07-22",  650.00, "\u534e\u4e1c", "\u98df\u54c1",     5, "\u666e\u901a"),
            (5, "2026-05-10", 3100.00, "\u534e\u5317", "\u7535\u5b50\u4ea7\u54c1", 4, "VIP"),
        ],
    )
    conn.executemany(
        "INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "\u5f20\u4e09", "\u6280\u672f\u90e8", "\u5de5\u7a0b\u5e08", 15000, "2024-01-15", "active"),
            (2, "\u674e\u56db", "\u9500\u552e\u90e8", "\u7ecf\u7406",   12000, "2023-06-01", "active"),
            (3, "\u738b\u4e94", "\u6280\u672f\u90e8", "\u67b6\u6784\u5e08", 22000, "2022-03-20", "inactive"),
        ],
    )
    conn.commit()
    conn.close()

    yield path

    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture()
def test_app(temp_db):
    """Build a FastAPI app that uses the temp database and skips the real lifespan."""
    app = fastapi.FastAPI()

    def _override_get_db():
        conn = sqlite3.connect(temp_db, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.include_router(dashboard_router)
    app.include_router(agent_router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "1.0.0"}

    @app.get("/")
    async def root():
        return {
            "message": "AI Multi-Agent Data Dashboard",
            "status": "running",
            "docs": "/docs",
            "agent_api": "/api/v1/agent/chat",
        }

    yield app
    app.dependency_overrides.clear()


@pytest.fixture()
def client(test_app):
    """A TestClient wired to the test_app."""
    with TestClient(test_app) as c:
        yield c
