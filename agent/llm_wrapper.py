import os
import random

from langchain_deepseek import ChatDeepSeek
from langchain_openai.chat_models import ChatOpenAI
from pydantic import SecretStr

from config.config import settings


class LLMFactory:
    def __init__(self, provider: str = None):
        self.provider = provider
        if not self.provider:
            raise ValueError(
                "Не указан провайдер LLM: передайте 'openai' или 'deepseek' "
                "в качестве параметра или установите переменную окружения LLM_PROVIDER."
            )

    def get_llm(self):
        api_key = settings.AI.api_key
        if len(api_key) == 0:
            raise ValueError("Отсутствует переменная окружения DEEPSEEK_API_KEY для провайдера 'deepseek'.")

        if self.provider == "openai":
            return self._get_openai_llm(random.choice(api_key))
        elif self.provider == "deepseek":
            return self._get_deepseek_llm(random.choice(api_key))
        else:
            raise ValueError(
                f"Неизвестный провайдер LLM: '{self.provider}'. Допустимые значения: 'openai', 'deepseek'.")

    @staticmethod
    def _get_openai_llm(api_key: SecretStr):
        os.environ["HTTP_PROXY"] = "socks5://"+settings.AI.proxy
        os.environ["HTTPS_PROXY"] = "socks5://"+settings.AI.proxy

        return ChatOpenAI(
            model=settings.AI.model,
            temperature=float(os.getenv("LLM_TEMPERATURE", 0)),
            timeout=None,
            max_retries=int(os.getenv("LLM_MAX_RETRIES", 2)),
            api_key=api_key,
        )

    @staticmethod
    def _get_deepseek_llm(api_key: SecretStr):
        return ChatDeepSeek(
            model=settings.AI.model,
            temperature=float(os.getenv("LLM_TEMPERATURE", 0)),
            timeout=None,
            max_retries=int(os.getenv("LLM_MAX_RETRIES", 2)),
            api_key=api_key,
        )
