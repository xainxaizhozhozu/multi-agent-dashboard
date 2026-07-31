"""
产品数据模型

对应数据库 products 表：
  id, name, category, cost_price, sell_price, stock, created_at
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """产品完整模型"""
    id: int
    name: str
    category: str
    cost_price: float
    sell_price: float
    stock: int = 0
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Product":
        """从 sqlite3.Row 构建实例"""
        return cls(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            cost_price=row["cost_price"],
            sell_price=row["sell_price"],
            stock=row["stock"] if "stock" in row.keys() else 0,
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "cost_price": self.cost_price,
            "sell_price": self.sell_price,
            "stock": self.stock,
            "created_at": self.created_at,
        }


@dataclass
class ProductRow:
    """轻量产品行模型（不含 id），用于列表展示"""
    name: str
    category: str
    cost_price: float
    sell_price: float
    stock: int = 0
