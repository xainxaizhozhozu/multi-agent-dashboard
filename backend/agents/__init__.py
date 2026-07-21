"""
Agent 包初始化。

这里定义了四个 Agent，它们是系统的"大脑"：

┌─────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐
│ Router  │ ──► │ SQL      │ ──► │ Chart      │ ──► │ Review   │
│(规划)    │     │(取数)     │     │(画图)       │     │(审核)     │
└─────────┘     └──────────┘     └────────────┘     └──────────┘
   拆解任务          生成SQL           选择图表           校验输出
"""

from agents.router_agent import RouterAgent
from agents.sql_agent import SQLAgent
from agents.chart_agent import ChartAgent
from agents.reviewer_agent import ReviewerAgent

__all__ = [
    "RouterAgent",
    "SQLAgent", 
    "ChartAgent",
    "ReviewerAgent",
]
