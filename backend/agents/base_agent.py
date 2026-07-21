"""
Agent 基类：所有 Agent 都继承这个类。

设计模式：Chain of Responsibility（责任链）+ Multi-Agent Pattern
每个 Agent 做一件事，通过 output 传递给下一个 Agent。
"""

from abc import ABC, abstractmethod
from services.llm_service import LLMService


class BaseAgent(ABC):
    """
    Agent 抽象基类
    
    所有 Agent 必须实现 process() 方法：
    - 接收 input_data (dict)
    - 返回 result (dict)
    
    子类应该添加 system_prompt 属性来定义该 Agent 的角色和职责。
    """

    def __init__(self, name: str, llm_service: LLMService | None = None):
        self.name = name
        self.llm = llm_service or LLMService()

    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        """
        处理输入数据并返回结果
        
        参数:
            input_data: 上游 Agent 的输出或用户原始输入
        
        返回:
            处理后的字典，可能包含:
            - data: 业务数据
            - error: 错误信息
            - needs_retry: 是否需要重新处理
            - metadata: 额外元数据
        """
        pass

    async def _call_llm(self, messages: list[dict]) -> str:
        """快捷方法：调用 LLM 并返回文本"""
        return await self.llm.chat(messages)
