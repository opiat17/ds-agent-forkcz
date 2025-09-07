import asyncio
import random
from typing import Dict, Any, List, Union

from loguru import logger

from agent.agent import SimpleAgent
from agent.nous import NousResearch
from config.config import settings
from discord.client import DiscordUserClient
from utils.helpers import get_media_files


def _summarize_messages_for_prompt(
    messages: list[dict[str, str]], max_chars: int = 1500
) -> str:
    """
    messages: [{ "author": "Nick", "content": "text", "ts": "..." }, ...]
    Hard-trims content to max_chars while keeping the gist.
    """
    lines: list[str] = []
    for m in messages:
        content = (m.get("content") or "").strip().replace("\n", " ")
        if not content:
            continue
        author = m.get("author") or "user"
        lines.append(f"{author}: {content}")
        if sum(len(x) for x in lines) > max_chars:
            break
    return "\n".join(lines[-50:])  # the most recent part matters


def _build_ai_prompt(
    system_prompt: str, summary: str, recent_tail: str, locale_hint: str
) -> str:
    """
    Concatenates everything into a single string prompt to keep SimpleAgent unchanged.
    """
    return (
        f"{system_prompt.strip()}\n\n"
        f"CONTEXT (short summary):\n{summary.strip()}\n\n"
        f"RECENT MESSAGES:\n{recent_tail.strip()}\n\n"
        f"Requirement: reply in the channel language ({locale_hint}), briefly (1–3 sentences), strictly based on the context."
    )


class MessageSender:
    def __init__(self, mode: str = "always_mode", account: str = None, proxy: str = None):
        self.mode = mode
        self.account = account
        self.proxy = proxy
        self.media_files = get_media_files()
        self.active_tasks = {}

    @staticmethod
    def _parse_range_value(value: Union[int, str, List]) -> int:
        if isinstance(value, list) and len(value) == 2:
            min_val = int(value[0])
            max_val = int(value[1])
            return random.randint(min_val, max_val)
        elif isinstance(value, (int, str)):
            return int(value)
        else:
            return 1

    async def start(self):
        all_tasks = []
        for server_name, server_config in settings.SERVERS.items():
            if not server_config.get('ENABLED', False):
                continue

            for chat_config in server_config.get('CHATS', []):
                message_type = chat_config.get('message_type')

                if message_type in ['1', '2', '3']:
                    task_info = {
                        'server_name': server_name,
                        'chat_config': chat_config
                    }
                    all_tasks.append(task_info)

        if not all_tasks:
            logger.error("No message tasks (type 1, 2 or 3) found in config")
            return

        tasks = []
        for task_info in all_tasks:
            task = asyncio.create_task(
                self._message_loop(
                    task_info['server_name'],
                    task_info['chat_config']
                )
            )
            tasks.append(task)

            task_id = f"{task_info['server_name']}_{task_info['chat_config']['chat_id']}_{task_info['chat_config']['message_type']}"
            self.active_tasks[task_id] = task

        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, SystemExit):
            logger.error("Stopping message sender...")
            for task in self.active_tasks.values():
                task.cancel()
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)

    async def _delayed_start(self, server_name: str, chat_config: Dict[str, Any], delay: float):
        if delay > 0:
            await asyncio.sleep(delay)
        await self._message_loop(server_name, chat_config)

    async def _message_loop(self, server_name: str, chat_config: Dict[str, Any]):
        channel_id = chat_config['chat_id']
        message_type = int(chat_config['message_type'])

        delay_value = chat_config.get('delay', 15)

        chats_delay = settings.SETTINGS.get('CHATS_DELAY', [0, 30])
        initial_delay = self._parse_range_value(chats_delay)

        if initial_delay > 0:
            logger.info(
                f"[{self.account[:8]}] [{server_name}] Channel {channel_id}: "
                f"Starting in {initial_delay} seconds..."
            )
            await asyncio.sleep(initial_delay)

        if self.mode == "always_mode":
            message_count = float('inf')
        else:
            count_value = chat_config.get('message_count', 1)
            message_count = self._parse_range_value(count_value)

        sent_count = 0
        while sent_count < message_count:
            try:
                if message_type == 1:
                    await self._send_ai_message(channel_id)
                elif message_type == 2:
                    await self._send_media_message(channel_id)
                elif message_type == 3:
                    await self._send_random_message(channel_id)

                sent_count += 1

                if message_count != float('inf'):
                    logger.info(
                        f"[{self.account[:8]}] [{server_name}] Channel {channel_id}: "
                        f"Sent {sent_count}/{message_count} messages"
                    )

                if sent_count < message_count:
                    delay_minutes = self._parse_range_value(delay_value)
                    logger.info(
                        f"[{self.account[:8]}] [{server_name}] Channel {channel_id}: "
                        f"Waiting {delay_minutes} minutes..."
                    )
                    await asyncio.sleep(delay_minutes * 60)

            except Exception as e:
                logger.error(f"[{self.account[:8]}] [{server_name}] Error send message to channel {channel_id}")
                return

    async def _send_ai_message(self, channel_id: str):
        async with DiscordUserClient(token=self.account, proxy=self.proxy) as dc:
            raw = await dc.get_channel_messages(channel_id, limit=100)
            if raw is None:
                raise Exception

            history: list[dict[str, str]] = []
            for msg in reversed(raw or []):
                content = (getattr(msg, "content", "") or "").strip()
                if not content:
                    continue
                author = getattr(msg, "author_username", "user")
                history.append({"author": author, "content": content})

            if not history:
                message = (
                    "Could someone summarize the last question? I'd like to reply on-topic."
                )
            else:
                recent_tail = _summarize_messages_for_prompt(history, max_chars=1500)
                topic_hint = history[-1]["content"][:140]
                summary = f"Recent discussions revolve around: '{topic_hint}'."
                locale_hint = (
                    "ru"
                    if sum(
                        c.isalpha() and ("а" <= c <= "я" or "А" <= c <= "Я")
                        for c in recent_tail
                    )
                    > 10
                    else "en"
                )
                prompt = _build_ai_prompt(
                    settings.AI.system_prompt, summary, recent_tail, locale_hint
                )

                if settings.AI.provider == "nous":
                    async with NousResearch(self.account, self.proxy) as nous:
                        message = await nous.invoke(prompt)
                else:
                    agent = SimpleAgent(settings.AI.provider)
                    message = await agent.handle_input(prompt)

            if not message:
                message = "I can chime in once you clarify the question or details."

            result = await dc.send_message(channel_id, message)
            if result is None:
                raise Exception

            logger.info(
                f"[{self.account[:8]}] Sent AI message to channel {channel_id}"
            )

    async def _send_media_message(self, channel_id: str):
        if not self.media_files:
            logger.error(f"Warning: No media files found in media/ directory")
            return

        media_file = random.choice(self.media_files)

        async with DiscordUserClient(token=self.account, proxy=self.proxy) as client:
            if self.proxy:
                pass

            result = await client.send_media_message(channel_id, media_file)
            if result is None:
                raise Exception

            logger.info(
                f"[{self.account[:8]}] Sent media file '{media_file}' to channel {channel_id}"
            )

    async def _send_random_message(self, channel_id: str):
        if len(settings.SETTINGS.RANDOM_MESSAGES) == 0:
            logger.error(f"Warning: random messages list is empty")
            return

        message = random.choice(settings.SETTINGS.RANDOM_MESSAGES)

        async with DiscordUserClient(token=self.account, proxy=self.proxy) as client:
            result = await client.send_message(channel_id, message)
            if result is None:
                raise Exception

            logger.info(
                f"[{self.account[:8]}] Sent random message '{message}' to channel {channel_id}"
            )


async def run_message_sender(mode: str = "always_mode", account: str = None, proxy: str = None):
    if mode not in ["always_mode", "one_time_mode"]:
        raise ValueError(f"Invalid mode: {mode}. Use 'always_mode' or 'one_time_mode'")

    sender = MessageSender(mode=mode, account=account, proxy=proxy)
    await sender.start()
