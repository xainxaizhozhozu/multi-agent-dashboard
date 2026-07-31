"""
数据模型：Sales / Employee / Product

用 dataclass 定义三张核心表的结构，提供类型安全的行数据表示。
每个模型都有 from_row() 方法，可以从 sqlite3.Row 直接转换。
"""

from models.sales import Sales, SalesRow
from models.employee import Employee, EmployeeRow
from models.product import Product, ProductRow

__all__ = [
    "Sales", "SalesRow",
    "Employee", "EmployeeRow",
    "Product", "ProductRow",
]
