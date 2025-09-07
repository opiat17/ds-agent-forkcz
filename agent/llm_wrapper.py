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
                "LLM provider not specified: pass 'openai' or 'deepseek' "
                "as a parameter or set the LLM_PROVIDER environment variable."
            )

    def get_llm(self):
        api_key = settings.AI.api_key
        if len(api_key) == 0:
            raise ValueError("Missing DEEPSEEK_API_KEY environment variable for provider 'deepseek'.")

        if self.provider == "openai":
            return self._get_openai_llm(random.choice(api_key))
        elif self.provider == "deepseek":
            return self._get_deepseek_llm(random.choice(api_key))
        else:
            raise ValueError(
                f"Unknown LLM provider: '{self.provider}'. Valid options: 'openai', 'deepseek'.")

    @staticmethod
    def _get_openai_llm(api_key: SecretStr):
        if settings.AI.proxy != "":
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
