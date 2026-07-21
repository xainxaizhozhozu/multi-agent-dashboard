"""
看板数据接口：为前端 Dashboard 提供聚合统计数据。

这些接口不需要 LLM，直接从数据库读取并聚合数据，响应速度快。
用于渲染前端的静态统计卡片和趋势图表。
"""

from fastapi import APIRouter
import sqlite3
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


def get_db():
    """获取数据库连接"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "dashboard.db"
    )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/stats")
async def get_overall_stats():
    """
    获取整体统计摘要
    
    返回数据用于前端展示：
    - 总销售额
    - 总订单数  
    - 员工总数
    - 平均客单价
    """
    db = get_db()

    # 总销售额和订单数
    result = db.execute("""
        SELECT 
            SUM(amount) as total_revenue,
            COUNT(*) as total_orders,
            ROUND(AVG(amount), 2) as avg_order_value,
            MIN(date) as first_sale_date,
            MAX(date) as last_sale_date
        FROM sales
    """).fetchone()

    # 员工总数
    employee_count = db.execute(
        "SELECT COUNT(*) as cnt FROM employees WHERE status = 'active'"
    ).fetchone()["cnt"]

    # 本月销售额 vs 上月（计算环比）
    today = datetime.now()
    this_month = today.strftime("%Y-%m")
    last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    this_month_sales = db.execute(
        "SELECT SUM(amount) as total FROM sales WHERE date LIKE ? || '%'",
        (this_month,)
    ).fetchone()["total"] or 0

    last_month_sales = db.execute(
        "SELECT SUM(amount) as total FROM sales WHERE date LIKE ? || '%'",
        (last_month,)
    ).fetchone()["total"] or 0

    mom_change = round((this_month_sales - last_month_sales) / max(last_month_sales, 1) * 100, 2)

    db.close()

    return {
        "total_revenue": round(result["total_revenue"] or 0, 2),
        "total_orders": result["total_orders"] or 0,
        "avg_order_value": result["avg_order_value"] or 0,
        "employee_count": employee_count,
        "this_month_revenue": round(this_month_sales, 2),
        "mom_change": mom_change,  # Month-over-Month 环比变化百分比
    }


@router.get("/trends/monthly")
async def get_monthly_trend():
    """
    按月销售趋势
    
    返回最近6个月的数据，用于折线图展示收入变化趋势
    """
    db = get_db()
    rows = db.execute("""
        SELECT strftime('%Y-%m', date) as month,
               SUM(amount) as revenue,
               COUNT(*) as orders,
               ROUND(AVG(amount), 2) as avg_order
        FROM sales
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """).fetchall()
    db.close()

    # 反转顺序，让时间从左到右递增
    result = [{"month": r["month"], "revenue": round(r["revenue"], 2),
               "orders": r["orders"], "avg_order": r["avg_order"]} for r in reversed(rows)]

    return result


@router.get("/trends/daily")
async def get_daily_trend():
    """
    按日销售趋势（最近30天）
    
    用于展示短期波动，粒度更细
    """
    db = get_db()
    rows = db.execute("""
        SELECT date,
               SUM(amount) as revenue,
               COUNT(*) as orders
        FROM sales
        WHERE date >= date('now', '-30 days')
        GROUP BY date
        ORDER BY date
    """).fetchall()
    db.close()

    return [
        {"date": r["date"], "revenue": round(r["revenue"], 2), "orders": r["orders"]}
        for r in rows
    ]


@router.get("/analysis/by-region")
async def analysis_by_region():
    """
    地区分析
    
    按地区统计销售额、订单数和客户类型分布
    """
    db = get_db()
    rows = db.execute("""
        SELECT region,
               SUM(amount) as total_amount,
               COUNT(*) as order_count,
               ROUND(AVG(amount), 2) as avg_amount
        FROM sales
        GROUP BY region
        ORDER BY total_amount DESC
    """).fetchall()

    # 每个地区的客户类型分布
    customer_types = db.execute("""
        SELECT region, customer_type, COUNT(*) as count
        FROM sales
        GROUP BY region, customer_type
        ORDER BY region, count DESC
    """).fetchall()

    db.close()

    regions = [dict(r) for r in rows]
    for r in regions:
        r["total_amount"] = round(r["total_amount"], 2)
        r["customer_distribution"] = {
            r2["customer_type"]: r2["count"]
            for r2 in customer_types if r2["region"] == r["region"]
        }

    return regions


@router.get("/analysis/by-category")
async def analysis_by_category():
    """
    产品类别分析
    
    各产品线的营收贡献和利润估算
    """
    db = get_db()
    rows = db.execute("""
        SELECT product_category,
               SUM(amount) as total_revenue,
               COUNT(*) as order_count,
               ROUND(AVG(amount), 2) as avg_amount
        FROM sales
        GROUP BY product_category
        ORDER BY total_revenue DESC
    """).fetchall()
    db.close()

    return [dict(r) for r in rows]
