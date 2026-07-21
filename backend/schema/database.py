"""
数据库模块：负责 SQLite 建表和示例数据注入。

SQLite 是一个轻量级文件数据库，不需要安装额外服务——
数据直接存在一个 .db 文件里。对于这个项目完全够用。

核心函数：
  create_tables()       — 创建所有需要的表
  seed_sample_data()    — 填充示例数据（只在空表时执行）
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

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
    创建四张核心表：
    
    1. sales         — 销售记录（金额、地区、产品类别）
    2. employees     — 员工信息（部门、职级、薪资）
    3. products      — 产品信息（分类、成本、售价）
    4. chart_config  — 缓存 Agent 生成的图表配置
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

    # ── 图表配置缓存表 ───────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,        -- 会话 ID
            query_text TEXT NOT NULL,        -- 用户原始问题
            chart_type TEXT NOT NULL,        -- 图表类型
            config_json TEXT NOT NULL,       -- ECharts 配置 JSON
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("  ✓ 数据库表已就绪")


# ── 示例数据生成器 ────────────────────────────────────────
REGIONS = ["华东", "华南", "华北", "西南", "华中"]
CATEGORIES = ["电子产品", "办公用品", "软件服务", "咨询服务", "硬件设备"]
CUSTOMER_TYPES = ["企业客户", "个人客户"]
DEPARTMENTS = ["技术部", "销售部", "市场部", "财务部", "人力资源部"]
POSITIONS = {
    "技术部": ["工程师", "高级工程师", "架构师", "技术总监"],
    "销售部": ["销售代表", "销售经理", "销售总监"],
    "市场部": ["市场专员", "市场经理", "市场总监"],
    "财务部": ["会计", "财务经理", "财务总监"],
    "人力资源部": ["HR专员", "HR经理", "HR总监"],
}

def seed_sample_data():
    """
    如果数据库为空，自动填充示例数据。
    
    数据说明：
    - 销售记录：最近 90 天的随机销售数据（~500 条）
    - 员工：每个部门随机生成 5-10 人
    - 产品：5 个品类各 8 个产品
    
    这些数据只是为了让看板有内容可展示。
    实际项目中你会接真实数据库。
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] > 0:
        print("  ℹ 数据库中已有数据，跳过种子注入")
        conn.close()
        return

    print("  🌱 正在注入示例数据...")

    # ── 生成销售记录 ─────────────────────────────────
    today = datetime.now()
    for i in range(500):
        days_ago = random.randint(0, 90)
        sale_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO sales (date, amount, region, product_category, quantity, customer_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sale_date,
            round(random.uniform(500, 50000), 2),   # 金额 500 ~ 50000
            random.choice(REGIONS),
            random.choice(CATEGORIES),
            random.randint(1, 100),
            random.choice(CUSTOMER_TYPES),
        ))

    # ── 生成员工记录 ────────────────────────────────
    names_first = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
                   "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    names_last = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "洋", "勇",
                  "艳", "杰", "涛", "明", "超", "秀英", "浩", "鑫", "建军", "婷"]

    for dept in DEPARTMENTS:
        count = random.randint(5, 10)
        for _ in range(count):
            name = random.choice(names_first) + random.choice(names_last)
            pos = random.choice(POSITIONS[dept])
            base_salary = {"技术部": 15000, "销售部": 12000, "市场部": 11000,
                           "财务部": 13000, "人力资源部": 11000}[dept]
            salary = base_salary + random.randint(-3000, 8000)
            join_days = random.randint(30, 1800)
            join_date = (today - timedelta(days=join_days)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO employees (name, department, position, salary, join_date)
                VALUES (?, ?, ?, ?, ?)
            """, (name, dept, pos, salary, join_date))

    # ── 生成产品记录 ────────────────────────────────
    product_names = {
        "电子产品": ["笔记本电脑", "显示器", "键盘", "鼠标", "硬盘", "路由器", "摄像头", "音箱"],
        "办公用品": ["打印纸", "钢笔", "笔记本", "文件夹", "订书机", "白板", "剪刀", "胶水"],
        "软件服务": ["CRM系统订阅", "ERP系统订阅", "云存储套餐", "安全防护套件", "开发工具许可", "设计软件许可", "监控工具", "协作平台"],
        "咨询服务": ["战略咨询", "IT审计", "系统集成", "培训服务", "运维支持", "安全评估"],
        "硬件设备": ["服务器", "交换机", "UPS电源", "机柜", "光纤模块", "AP接入点", "防火墙", "NAS存储"],
    }

    for category, names in product_names.items():
        for name in names:
            cost = round(random.uniform(50, 30000), 2)
            margin = random.uniform(1.2, 2.5)  # 利润率 20% ~ 150%
            cursor.execute("""
                INSERT INTO products (name, category, cost_price, sell_price, stock)
                VALUES (?, ?, ?, ?, ?)
            """, (name, category, cost, round(cost * margin, 2), random.randint(10, 500)))

    conn.commit()
    conn.close()
    print(f"  ✓ 示例数据注入完成（500条销售 + {len(DEPARTMENTS)}个部门员工 + 40个产品）")
