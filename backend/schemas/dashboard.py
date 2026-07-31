"""
Dashboard 看板相关响应模型

覆盖端点：
  GET /api/v1/dashboard/stats            — DashboardStats
  GET /api/v1/dashboard/trends/monthly   — MonthlyTrend
  GET /api/v1/dashboard/trends/daily     — DailyTrend
  GET /api/v1/dashboard/analysis/by-region   — RegionAnalysis
  GET /api/v1/dashboard/analysis/by-category — CategoryAnalysis
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── 总览统计 ──────────────────────────────────────────

class DashboardStats(BaseModel):
    """看板核心指标"""
    total_revenue: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    avg_order_value: float = Field(..., description="平均订单金额")
    employee_count: int = Field(..., description="员工总数")
    this_month_revenue: float = Field(..., description="本月销售额")
    mom_change: Optional[float] = Field(None, description="环比变化率（%），None 表示无上月数据")


# ── 趋势分析 ──────────────────────────────────────────

class MonthlyTrend(BaseModel):
    """月度趋势数据点"""
    month: str = Field(..., description="月份 (YYYY-MM)")
    revenue: float = Field(..., description="当月销售额")
    orders: int = Field(..., description="当月订单数")
    avg_order: float = Field(..., description="当月平均订单金额")


class DailyTrend(BaseModel):
    """日度趋势数据点"""
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    revenue: float = Field(..., description="当日销售额")
    orders: int = Field(..., description="当日订单数")


# ── 多维分析 ──────────────────────────────────────────

class RegionAnalysis(BaseModel):
    """地区维度分析"""
    region: str = Field(..., description="地区名称")
    total_amount: float = Field(..., description="地区总销售额")
    order_count: int = Field(..., description="订单数")
    avg_amount: float = Field(..., description="平均订单金额")
    customer_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="客户类型分布，如 {'企业客户': 15, '个人客户': 8}",
    )


class CategoryAnalysis(BaseModel):
    """产品类别维度分析"""
    product_category: str = Field(..., description="产品类别")
    total_revenue: float = Field(..., description="类别总销售额")
    order_count: int = Field(..., description="订单数")
    avg_amount: float = Field(..., description="平均订单金额")
