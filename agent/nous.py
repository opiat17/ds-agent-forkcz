import asyncio
import random
from typing import Optional

import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from loguru import logger

from config.config import settings
from utils.exceptions import APIError


class NousResearch:
    def __init__(self, account: str = None, proxy: Optional[str] = None):
        self.model = settings.AI.model
        self.api_key = random.choice(settings.AI.api_key)
        self.user = account
        self.proxy = proxy
        self.session: Optional[aiohttp.ClientSession] = None
        self._ua = UserAgent()
        if self.model not in [
            'Hermes-3-Llama-3.1-70B', 'DeepHermes-3-Llama-3-8B-Preview',
            'DeepHermes-3-Mistral-24B-Preview', 'Hermes-3-Llama-3.1-405B'
        ]:
            raise ValueError(
                "Не указан провайдер LLM: передайте 'Hermes-3-Llama-3.1-70B' или 'DeepHermes-3-Llama-3-8B-Preview' "
                "'DeepHermes-3-Mistral-24B-Preview' 'Hermes-3-Llama-3.1-405B' "
                "в качестве параметра или установите переменную окружения LLM_PROVIDER."
            )

    async def __aenter__(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self._ua.random,
        }
        if self.proxy:
            connector = ProxyConnector.from_url("socks5://" + self.proxy)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers=headers
            )
        else:
            self.session = aiohttp.ClientSession(
                headers=headers
            )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def invoke(self, prompt: str) -> str | None:
        url = f"https://inference-api.nousresearch.com/v1/completions"

        for attempt in range(settings.SETTINGS.RETRY_COUNT):
            try:
                payload = {"model": self.model, "prompt": prompt}

                async with self.session.post(url, json=payload) as resp:
                    data = await resp.json()

                    if resp.status != 200:
                        raise APIError(resp.status, "ERROR")

                    return data["choices"][0]["text"]
            except APIError as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{settings.SETTINGS.RETRY_COUNT} "
                    f"failed for {self.user[:8]}...: {e.payload}"
                )
                await asyncio.sleep(
                    random.randint(settings.SETTINGS.RETRY_DELAY[0], settings.SETTINGS.RETRY_DELAY[1])
                )
        return None
