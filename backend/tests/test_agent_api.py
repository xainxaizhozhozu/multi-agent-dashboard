"""
Tests for the agent API endpoints (routers/agent.py).

Covers:
  - POST /api/v1/agent/chat validation (empty, too long, missing query)
  - POST /api/v1/agent/chat with mocked orchestrator (success, errors)
  - GET  /api/v1/agent/status returns agent list
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestAgentChatValidation:

    def test_empty_query_returns_400(self, client):
        resp = client.post("/api/v1/agent/chat", json={"query": ""})
        assert resp.status_code == 400
        assert "detail" in resp.json()

    def test_whitespace_only_query_returns_400(self, client):
        resp = client.post("/api/v1/agent/chat", json={"query": "   "})
        assert resp.status_code == 400

    def test_missing_query_field_returns_400(self, client):
        resp = client.post("/api/v1/agent/chat", json={})
        assert resp.status_code == 400

    def test_query_too_long_returns_400(self, client):
        long_query = "a" * 501
        resp = client.post("/api/v1/agent/chat", json={"query": long_query})
        assert resp.status_code == 400
        assert "500" in resp.json()["detail"] or "\u8fc7\u957f" in resp.json()["detail"]

    def test_query_exactly_500_chars_is_ok(self, client):
        query = "a" * 500
        with patch("routers.agent.get_orchestrator") as mock_get:
            mock_orch = AsyncMock()
            mock_orch.process_query = AsyncMock(return_value={"success": True})
            mock_get.return_value = mock_orch
            resp = client.post("/api/v1/agent/chat", json={"query": query})
            assert resp.status_code != 400


class TestAgentChatWithMockedOrchestrator:

    def test_valid_query_calls_orchestrator(self, client):
        with patch("routers.agent.get_orchestrator") as mock_get:
            mock_orch = AsyncMock()
            mock_orch.process_query = AsyncMock(return_value={
                "success": True,
                "chart_type": "bar",
                "chart_title": "\u6d4b\u8bd5",
                "sql": "SELECT 1",
                "raw_data": [],
                "columns": [],
                "elapsed_seconds": 0.5,
            })
            mock_get.return_value = mock_orch
            resp = client.post(
                "/api/v1/agent/chat",
                json={"query": "\u5404\u5730\u533a\u9500\u552e\u989d"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            mock_orch.process_query.assert_called_once()

    def test_orchestrator_value_error_returns_503(self, client):
        with patch("routers.agent.get_orchestrator") as mock_get:
            mock_orch = AsyncMock()
            mock_orch.process_query = AsyncMock(
                side_effect=ValueError("no api key")
            )
            mock_get.return_value = mock_orch
            resp = client.post(
                "/api/v1/agent/chat", json={"query": "\u6d4b\u8bd5"}
            )
            assert resp.status_code == 503

    def test_orchestrator_generic_error_returns_500(self, client):
        with patch("routers.agent.get_orchestrator") as mock_get:
            mock_orch = AsyncMock()
            mock_orch.process_query = AsyncMock(
                side_effect=RuntimeError("boom")
            )
            mock_get.return_value = mock_orch
            resp = client.post(
                "/api/v1/agent/chat", json={"query": "\u6d4b\u8bd5"}
            )
            assert resp.status_code == 500

    def test_session_id_passed_through(self, client):
        with patch("routers.agent.get_orchestrator") as mock_get:
            mock_orch = AsyncMock()
            mock_orch.process_query = AsyncMock(
                return_value={"success": True}
            )
            mock_get.return_value = mock_orch
            resp = client.post("/api/v1/agent/chat", json={
                "query": "\u6d4b\u8bd5",
                "session_id": "test123",
            })
            assert resp.status_code == 200
            mock_orch.process_query.assert_called_once_with(
                "\u6d4b\u8bd5", "test123"
            )


class TestAgentStatus:

    def test_status_returns_agent_list(self, client):
        resp = client.get("/api/v1/agent/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "agents" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_status_agents_count(self, client):
        resp = client.get("/api/v1/agent/status")
        data = resp.json()
        assert len(data["agents"]) == 4
        agent_names = {a["name"] for a in data["agents"]}
        assert agent_names == {"Router", "SQL_Agent", "Chart_Agent", "Reviewer"}

    def test_status_ready_field_exists(self, client):
        resp = client.get("/api/v1/agent/status")
        data = resp.json()
        assert "ready" in data
        assert isinstance(data["ready"], bool)
