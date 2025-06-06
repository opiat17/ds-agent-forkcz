import re
from colorama import Fore, Style, init

init(autoreset=True)

def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def get_block_width(block: str) -> int:
    lines = block.split("\n")
    max_width = 0
    for line in lines:
        clean = strip_ansi(line)
        length = len(clean)
        if length > max_width:
            max_width = length
    return max_width


def center_text_within_width(text: str, width: int) -> str:
    lines = text.split("\n")
    centered = []
    for line in lines:
        clean = strip_ansi(line)
        display_len = len(clean)
        padding = max(0, (width - display_len) // 2)
        centered.append(" " * padding + line)
    return "\n".join(centered)


DS_TITLE = f"""{Fore.CYAN}
██████╗ ███████╗       █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██╔══██╗██╔════╝      ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██║  ██║███████╗█████╗███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██║  ██║╚════██║╚════╝██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
██████╔╝███████║      ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
╚═════╝ ╚══════╝      ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
{Style.RESET_ALL}"""

DS_SUBTITLE = f"{Fore.YELLOW}AI Agent for Discord{Style.RESET_ALL}"
DS_AUTHOR = f"{Fore.GREEN}Author: SybilWave (czbag){Style.RESET_ALL}"
DS_CHANNEL = f"{Fore.MAGENTA}Channel: https://t.me/sybilwave{Style.RESET_ALL}"
DS_GITHUB = f"{Fore.BLUE}GitHub: https://github.com/czbag/ds-agent{Style.RESET_ALL}"


def print_startup_window():
    print(DS_TITLE)
    print()

    title_width = get_block_width(DS_TITLE)
    meta_block = "\n".join([DS_SUBTITLE, DS_AUTHOR, DS_CHANNEL])
    centered_meta = center_text_within_width(meta_block, title_width)
    print(centered_meta)
    print()
    print(center_text_within_width(DS_GITHUB, title_width))
    print()
