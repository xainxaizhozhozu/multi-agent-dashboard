"""
数据库连接与表定义

职责：
  - 管理 SQLite 连接（get_connection）
  - 创建数据表（create_tables）
  - 导出数据库路径常量（DB_PATH）

种子数据已拆分至 schema/seed_data.py
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

# 数据库文件路径（和 main.py 同级目录的 data/ 文件夹下）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "dashboard.db")


def get_connection():
    """获取数据库连接（每次调用创建新连接）"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # ← 让查询结果可以用列名访问
    return conn


def create_tables():
    """
    创建三张核心表：

    1. sales         — 销售记录（金额、地区、产品类别）
    2. employees     — 员工信息（部门、职级、薪资）
    3. products      — 产品信息（分类、成本、售价）
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── 销售记录表 ───────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,              -- 销售日期
            amount REAL NOT NULL,            -- 销售金额
            region TEXT NOT NULL,            -- 地区（华东/华南/华北）
            product_category TEXT NOT NULL,  -- 产品类别
            quantity INTEGER NOT NULL,       -- 数量
            customer_type TEXT NOT NULL,     -- 客户类型（企业/个人）
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── 员工表 ───────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,        -- 部门
            position TEXT NOT NULL,          -- 职位
            salary REAL NOT NULL,            -- 月薪
            join_date TEXT NOT NULL,         -- 入职日期
            status TEXT DEFAULT 'active'     -- active/resigned
        )
    """)

    # ── 产品表 ───────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            cost_price REAL NOT NULL,        -- 成本价
            sell_price REAL NOT NULL,        -- 销售价
            stock INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info("数据库表已就绪")
