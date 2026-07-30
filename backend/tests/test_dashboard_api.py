"""
Tests for the dashboard API endpoints (routers/dashboard.py + health/root).

All tests use the TestClient backed by the temp_db fixture via
FastAPI dependency_overrides.
"""

import pytest


class TestHealthEndpoints:

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"

    def test_root_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "running"
        assert "docs" in data
        assert "agent_api" in data


class TestDashboardStats:

    def test_stats_status_code(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        assert resp.status_code == 200

    def test_stats_structure(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        data = resp.json()
        expected_keys = {
            "total_revenue", "total_orders", "avg_order_value",
            "employee_count", "this_month_revenue", "mom_change",
        }
        assert expected_keys <= set(data.keys())

    def test_stats_total_revenue(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        data = resp.json()
        # 1500 + 800.50 + 2200 + 650 + 3100 = 8250.50
        assert data["total_revenue"] == pytest.approx(8250.50, abs=0.01)

    def test_stats_total_orders(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        data = resp.json()
        assert data["total_orders"] == 5

    def test_stats_employee_count_active_only(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        data = resp.json()
        assert data["employee_count"] == 2

    def test_stats_avg_order_value(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        data = resp.json()
        assert data["avg_order_value"] > 0


class TestMonthlyTrends:

    def test_monthly_returns_list(self, client):
        resp = client.get("/api/v1/dashboard/trends/monthly")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_monthly_item_keys(self, client):
        resp = client.get("/api/v1/dashboard/trends/monthly")
        data = resp.json()
        for item in data:
            assert "month" in item
            assert "revenue" in item
            assert "orders" in item
            assert "avg_order" in item

    def test_monthly_chronological_order(self, client):
        resp = client.get("/api/v1/dashboard/trends/monthly")
        data = resp.json()
        months = [item["month"] for item in data]
        assert months == sorted(months)


class TestDailyTrends:

    def test_daily_returns_list(self, client):
        resp = client.get("/api/v1/dashboard/trends/daily")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_daily_item_keys(self, client):
        resp = client.get("/api/v1/dashboard/trends/daily")
        data = resp.json()
        for item in data:
            assert "date" in item
            assert "revenue" in item
            assert "orders" in item


class TestAnalysisByRegion:

    def test_by_region_returns_list(self, client):
        resp = client.get("/api/v1/dashboard/analysis/by-region")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_by_region_keys(self, client):
        resp = client.get("/api/v1/dashboard/analysis/by-region")
        data = resp.json()
        for item in data:
            assert "region" in item
            assert "total_amount" in item
            assert "order_count" in item
            assert "avg_amount" in item
            assert "customer_distribution" in item

    def test_by_region_sorted_desc(self, client):
        resp = client.get("/api/v1/dashboard/analysis/by-region")
        data = resp.json()
        amounts = [item["total_amount"] for item in data]
        assert amounts == sorted(amounts, reverse=True)


class TestAnalysisByCategory:

    def test_by_category_returns_list(self, client):
        resp = client.get("/api/v1/dashboard/analysis/by-category")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_by_category_keys(self, client):
        resp = client.get("/api/v1/dashboard/analysis/by-category")
        data = resp.json()
        for item in data:
            assert "product_category" in item
            assert "total_revenue" in item
            assert "order_count" in item

    def test_by_category_sorted_desc(self, client):
        resp = client.get("/api/v1/dashboard/analysis/by-category")
        data = resp.json()
        revenues = [item["total_revenue"] for item in data]
        assert revenues == sorted(revenues, reverse=True)
