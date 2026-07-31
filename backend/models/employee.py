"""
员工数据模型

对应数据库 employees 表：
  id, name, department, position, salary, join_date, status
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    """员工完整模型"""
    id: int
    name: str
    department: str
    position: str
    salary: float
    join_date: str
    status: str = "active"

    @classmethod
    def from_row(cls, row) -> "Employee":
        """从 sqlite3.Row 构建实例"""
        return cls(
            id=row["id"],
            name=row["name"],
            department=row["department"],
            position=row["position"],
            salary=row["salary"],
            join_date=row["join_date"],
            status=row["status"] if "status" in row.keys() else "active",
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "position": self.position,
            "salary": self.salary,
            "join_date": self.join_date,
            "status": self.status,
        }


@dataclass
class EmployeeRow:
    """轻量员工行模型（不含 id），用于聚合统计返回"""
    name: str
    department: str
    position: str
    salary: float
    join_date: str
    status: str = "active"
