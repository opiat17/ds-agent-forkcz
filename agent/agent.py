from loguru import logger

from .llm_wrapper import LLMFactory


class SimpleAgent:
    def __init__(self, provider_type: str = None):
        llm_factory = LLMFactory(provider_type)
        self.llm = llm_factory.get_llm()

    async def handle_input(self, user_message: str) -> str | None:
        try:
            response = await self.llm.ainvoke(user_message)
            return response.content
        except Exception as e:
            logger.error(f"Agent handler error: {e}")
            return
