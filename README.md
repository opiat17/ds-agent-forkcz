<div align="center">
<p align="center">
  <img src="https://i.postimg.cc/kMKDp35T/2025-06-06-134425.png" alt="Cursor Pro Logo" width="800" style="border-radius: 6px;"/>
</p>


<h1 align="center">DS-Agent</h1>

AI Agent for working with Discord
</div>


## ✨ Features

- 🔄 **Always-On Mode**  
  Continuous operation: the bot stays running and sends messages on schedule, keeping the channel active around the clock.

- 🕒 **One-Time Mode**  
  Single execution: the bot carries out the specified actions and then stops. Perfect for one-off broadcasts or quick tests.

- 🛠️ **Token Checker**  
  Automatically verifies Discord tokens, flagging or removing invalid ones so you always work with a clean pool of accounts.

- 🤖 **AI Message Sender**  
  Crafts natural replies by analyzing the last 100 messages in a chat via your chosen LLM (OpenAI or DeepSeek), making it feel like a real person joined the conversation.

- 📷 **Media Sender**  
  Picks a random media file from the `media/` folder and posts it to the channel, simulating human-like behavior.

- 🎲 **Random Message Sender**  
  On a schedule, sends random messages (for example, “gm”, “GN”, or any custom entries in your `RANDOM_MESSAGES` list) to boost visibility in the community.

- 🌐 **Support for Any LLM (OpenAI / DeepSeek)**  
  Easily swap providers—just set `provider: "openai"` or `provider: "deepseek"` in your configuration. To add a new model, follow the pattern in `ai_agent/llm_wrapper.py`.

- 🧠 **NousResearch LLM Support**  
  Full support for cutting-edge models from [NousResearch](https://portal.nousresearch.com/) — just set the provider in your config.  
  Available models:
  - `Hermes-3-Llama-3.1-70B`
  - `DeepHermes-3-Llama-3-8B-Preview`
  - `DeepHermes-3-Mistral-24B-Preview`
  - `Hermes-3-Llama-3.1-405B`
  - `Hermes-4-70B` *(hybrid reasoning mode)*
  Use `provider: "nous"` in your `config.yaml` to integrate instantly.
  All Nous API requests reserve up to **32k tokens**, and for hybrid models the
  required reasoning system prompt is automatically prepended.

- 🔀 **Full Action Randomization**  
  Random delays between requests, varied message templates, and optional random token selection (`RANDOM_ACCOUNTS=true`) all combine to mimic a human user and reduce the chance of blocks.

- 📋 **Detailed Logging**  
  Logs every step—from connection attempts to API errors. You can output logs to the console or save them to a file; everything is configurable via `config.yaml`.

- 🔁 **Automatic Retries**  
  If a temporary error occurs (rate limit, dropped connection, etc.), the bot will retry the action with configurable delays until it succeeds or hits the `RETRY_COUNT` limit.

- 📡 **Socks5 Proxy Support**  
  Route traffic through Socks5 proxies to spread requests across different endpoints and protect your own IP address.

- 📦 **Batch Account Processing**  
  When using a large number of accounts, tasks are split into batches (`BATCH_SIZE`) with pauses between each batch (`BATCH_DELAY`) to manage load and avoid overwhelming Discord.

- 🤝 **Flexible YAML Configuration**  
  Define servers, channels, message types, delay ranges, retry counts, and more—all in one `config.yaml` file. Tweak settings, and the bot adapts instantly.



## 👨‍💻 Installation

1. Clone this repository

```bash
git clone https://github.com/czbag/ds-agent.git
cd ds-agent
```

2. Install dependencies

```bash
#pip
pip install -r requirements.txt

#poetry
poetry install
```

3. Edit config.yaml

4. Rename proxy.example.txt -> proxy.txt

5. Rename accounts.example.txt -> accounts.txt
```
You need have API Key for LLM OpenAI/DeepSeek for AI mode work
```
- https://platform.openai.com
- https://platform.deepseek.com
    
## ⚡️ Settings

### config.yaml

```yaml
SETTINGS:
  # true/false
  USE_PROXY: true

  # true/false
  RANDOM_ACCOUNTS: true

  # Count of retries
  RETRY_COUNT: 3

  # delay in seconds
  RETRY_DELAY: [60, 120]

  # delay in seconds
  CHATS_DELAY: [20, 60]

  # quantity accounts in batch
  BATCH_SIZE: 5

  # delay in seconds
  BATCH_DELAY: 60

  # delay in seconds
  INTRA_BATCH_DELAY: [30, 60]

  # Sending random messages, for example: GM/GN
  RANDOM_MESSAGES: ["gm", "GM", "gn", "GN"]
```

```yaml
AI:
  # deepseek, openai or nous
  provider: "deepseek"

  # model settings
  #
  # deepseek: https://api-docs.deepseek.com/quick_start/pricing
  # - deepseek-reasoner
  # - deepseek-chat
  #
  # openai: https://platform.openai.com/docs/pricing
  # - gpt-4o
  # - gpt-4o-mini
  #
  # nous: https://portal.nousresearch.com/models
  # - Hermes-3-Llama-3.1-70B
  # - DeepHermes-3-Llama-3-8B-Preview
  # - DeepHermes-3-Mistral-24B-Preview
  # - Hermes-3-Llama-3.1-405B
  model: "deepseek-reasoner"

  # you can use multiple api keys
  api_key: [ "sk-*******" ]
  
  # socks5 proxy for openai - host:port@login:password
  proxy: ""

  system_prompt: |
    You are an active and trusted member of a crypto/DeFi Discord community.
    Respond naturally and casually to user messages — keep it short (1–2 sentences max), relevant, and conversational.
    Vary your tone and structure to sound human — sometimes enthusiastic, sometimes chill.
    Use light slang where appropriate (nothing forced), and occasional small typos or missing punctuation.
    Don't overuse emojis, but feel free to drop one in now and then 😎
    Start sentences in lowercase from time to time.
    Never reveal you're an AI — you're just another community member.
    Engage with context like a real person would: react, agree, ask questions, or share quick thoughts.
    Avoid robotic or overly formal replies.
    Don't tag or mention users.
    Speak as a fellow community member — not as an admin, mod, or support.
```

```yaml
SERVERS:
  # any channel name for log
  uniswap:
    # discord server_id
    server_id: "123"

    # work true/false
    ENABLED: true

    # chat list
    CHATS:
      - { chat_id: "0123456789", message_type: "1", delay: ["1", "1"] }
      - { chat_id: "0123456789", message_type: "2", delay: ["1", "1"] }
      - { chat_id: "0123456789", message_type: "3", delay: ["1", "1"] }
  
  debank:
    # discord server_id
    server_id: "321"

    # work true/false
    ENABLED: true
    
    # chat list
    CHATS:
      - { chat_id: "0123456789", message_type: "1", delay: ["1", "1"], message_count: ["5", "10"] }
      - { chat_id: "0123456789", message_type: "2", delay: ["1", "1"], message_count: ["5", "10"] }
      - { chat_id: "0123456789", message_type: "3", delay: ["1", "1"], message_count: ["5", "10"] }

  # message_type: 1/2/3
  # type 1: AI mode (create a message based on the last 100 messages from chat)
  # type 2: Media sender mode (bot choose random media file from media folder)
  # type 3: random message sender (bot choose random message from RANDOM_MESSAGES)
  #
  # delay: sleep in minutes before the next message
  #
  # message_count: 5 (Work only for One-Time Mode!)
```


## ❤️ Author

🔔 Follow me: https://t.me/sybilwave

