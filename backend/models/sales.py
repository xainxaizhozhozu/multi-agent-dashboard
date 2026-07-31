"""
销售记录数据模型

对应数据库 sales 表：
  id, date, amount, region, product_category, quantity, customer_type, created_at
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Sales:
    """销售记录完整模型（包含 id 和 created_at）"""
    id: int
    date: str
    amount: float
    region: str
    product_category: str
    quantity: int
    customer_type: str
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Sales":
        """从 sqlite3.Row 构建实例"""
        return cls(
            id=row["id"],
            date=row["date"],
            amount=row["amount"],
            region=row["region"],
            product_category=row["product_category"],
            quantity=row["quantity"],
            customer_type=row["customer_type"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "region": self.region,
            "product_category": self.product_category,
            "quantity": self.quantity,
            "customer_type": self.customer_type,
            "created_at": self.created_at,
        }


@dataclass
class SalesRow:
    """
    轻量销售行模型（不含 id 和审计字段）。
    用于 API 响应中的聚合数据返回。
    """
    date: str
    amount: float
    region: str
    product_category: str
    quantity: int
    customer_type: str

    @classmethod
    def from_row(cls, row) -> "SalesRow":
        return cls(
            date=row["date"],
            amount=row["amount"],
            region=row["region"],
            product_category=row["product_category"],
            quantity=row["quantity"],
            customer_type=row["customer_type"],
        )
