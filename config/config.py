import os
import json
import random
from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[
        "config.yaml",
    ],
    environments=True,
    load_dotenv=True,
    env_switcher="ENV_FOR_DYNACONF",
    merge_enabled=True,
)


with open("accounts.txt", "r") as file:
    ACCOUNTS = [row.strip() for row in file]

with open("proxy.txt", "r") as file:
    PROXIES = [row.strip() for row in file]
