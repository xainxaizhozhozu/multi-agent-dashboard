from abc import ABC, abstractmethod
from services.llm_service import LLMService


class BaseAgent(ABC):
    """所有 Agent 的基类，子类必须实现 process()"""

    def __init__(self, name: str, llm_service: LLMService | None = None):
        self.name = name
        self.llm = llm_service or LLMService()

    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        pass

    async def _call_llm(self, messages: list[dict]) -> str:
        return await self.llm.chat(messages)
