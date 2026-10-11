"""
Discord Token Retriever — UI Engine
Styled with rich gradients, box drawing, and terminal aesthetics inspired by GhoSty OwO V4.1.

Author: @jijaghosty • Async Development
"""

import sys
import os
import re
import shutil
import ctypes
import subprocess
import time

# Reconfigure standard output for UTF-8 compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def _enable_windows_vt():
    """Enable Windows 10+ Virtual Terminal Sequences for ANSI escape code support."""
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                mode.value |= 0x0004
                kernel32.SetConsoleMode(handle, mode)
        except Exception:
            pass

_enable_windows_vt()

# ANSI Style Constants
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
ITALIC = "\033[3m"

# Curated RGB Color Palette (Matching GhoSty OwO V4.1 Theme)
CYAN_ELECTRIC = (0, 245, 255)
CYAN_MID      = (0, 195, 255)
BLUE_ELECTRIC = (30, 144, 255)
BLUE_NEON     = (59, 130, 246)
PURPLE_NEON   = (168, 85, 247)
PURPLE_LIGHT  = (192, 132, 252)
GREEN_NEON    = (52, 211, 153)
GREEN_EMERALD = (16, 185, 129)
YELLOW_GOLD   = (250, 204, 21)
RED_CRIMSON   = (248, 113, 113)
RED_BRIGHT    = (239, 68, 68)
GRAY_TEXT     = (148, 163, 184)
GRAY_MUTED    = (100, 116, 139)
GRAY_BORDER   = (51, 65, 85)
WHITE_BRIGHT  = (248, 250, 252)

def fg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"

def strip_ansi(text: str) -> str:
    return re.sub(r'\033\[[0-9;]*[a-zA-Z]', '', text)

def get_term_width(default: int = 86) -> int:
    try:
        w = shutil.get_terminal_size((default, 24)).columns
        return max(w, 64)
    except Exception:
        return default

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H\033[3J")
        sys.stdout.flush()

def center(text: str, width: int = None) -> str:
    if width is None:
        width = get_term_width()
    plain_len = len(strip_ansi(text))
    if plain_len >= width:
        return text
    pad = (width - plain_len) // 2
    return " " * pad + text

def center_block(lines: list, width: int = None) -> list:
    if width is None:
        width = get_term_width()
    clean_lines = [strip_ansi(l) for l in lines]
    non_empty = [l for l in clean_lines if l.strip()]
    if not non_empty:
        return lines
    max_len = max(len(l) for l in non_empty)
    pad = max(0, (width - max_len) // 2)
    return [(" " * pad + line) if line.strip() else "" for line in lines]

def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def multi_gradient_color(colors: list, t: float) -> tuple:
    if not colors:
        return (255, 255, 255)
    if len(colors) == 1 or t <= 0.0:
        return colors[0]
    if t >= 1.0:
        return colors[-1]
    seg_len = 1.0 / (len(colors) - 1)
    seg_idx = min(int(t / seg_len), len(colors) - 2)
    local_t = (t - (seg_idx * seg_len)) / seg_len
    return lerp_color(colors[seg_idx], colors[seg_idx + 1], local_t)

def colorize_gradient(text: str, colors: list = None) -> str:
    if colors is None:
        colors = [CYAN_ELECTRIC, CYAN_MID, BLUE_ELECTRIC, PURPLE_NEON, PURPLE_LIGHT]
    clean = strip_ansi(text)
    if not clean:
        return text
    n = len(clean)
    result = []
    clean_idx = 0
    in_ansi = False
    ansi_buf = []

    for ch in text:
        if ch == '\033':
            in_ansi = True
            ansi_buf.append(ch)
            continue
        if in_ansi:
            ansi_buf.append(ch)
            if ch.isalpha():
                in_ansi = False
                result.append("".join(ansi_buf))
                ansi_buf = []
            continue

        t = clean_idx / max(n - 1, 1)
        r, g, b = multi_gradient_color(colors, t)
        result.append(f"{fg_rgb(r, g, b)}{ch}")
        clean_idx += 1

    result.append(RESET)
    return "".join(result)

def make_badge(text: str, bg_tuple: tuple, fg_tuple: tuple = (0, 0, 0), width: int = 10) -> str:
    padded = f" {text} ".center(width)
    return f"{bg_rgb(*bg_tuple)}{fg_rgb(*fg_tuple)}{BOLD}{padded}{RESET}"

# Banner Logo copied exactly from GhoSty OwO V4.1 reference file
LOGO_GHOSTY_OWO = [
    '   ▄▄▄▄▄▄ ▄▄▄            ▄▄▄▄▄             ',
    ' ██▀▀  ▀█  ██           ▄██ ▀█  ▄█         ',
    '███        ██▀██  ██▀█▄  ▀██▄▄ ▀██▀▀██▀▀█▀ ',
    '▀██   ▀██▀ ██ ██ ███ ██ ▄  ▀▀██ ██  ▀███   ',
    ' ▀▀█▄▄▄█▀ ▄██▄██▄ ██▄█▀ █▀█▄▄█▀ ██▄  ▀█    ',
    '                                   ▄▄▄▀',
    '                                   ▀▀▀',
]

def render_header(device_id: str = None, width: int = None):
    """Render the full GhoSty styled banner, status badges, and configuration card."""
    if width is None:
        width = get_term_width()

    lines_out = [""]
    
    # 1. Gradient ASCII Banner (exact copy from reference)
    grad_colors = [CYAN_ELECTRIC, (45, 190, 255), BLUE_ELECTRIC, PURPLE_NEON]
    banner_grad = [colorize_gradient(l, grad_colors) for l in LOGO_GHOSTY_OWO]
    lines_out.extend(center_block(banner_grad, width))
    lines_out.append("")

    # 2. Version & Brand Tag
    v_tag = (
        f"{fg_rgb(*CYAN_MID)}{BOLD}GhoSty Token Retriever{RESET} "
        f"{fg_rgb(*GRAY_MUTED)}•{RESET} {fg_rgb(*PURPLE_LIGHT)}Safe Alpha Build V2{RESET} "
        f"{fg_rgb(*GRAY_MUTED)}•{RESET} {fg_rgb(*GREEN_NEON)}{BOLD}Bypass Active{RESET}"
    )
    lines_out.append(center(v_tag, width))
    lines_out.append("")

    # 3. Environment & Configuration Matrix
    box_w = min(width - 4, 82)
    if box_w < 64:
        box_w = 64

    side_pad = " " * max(0, (width - box_w) // 2)

    b_col = fg_rgb(*CYAN_MID)
    t_white = fg_rgb(*WHITE_BRIGHT)
    t_muted = fg_rgb(*GRAY_TEXT)
    t_accent = fg_rgb(*CYAN_ELECTRIC)

    top_border = f"{side_pad}{b_col}╭{'─' * (box_w - 2)}╮{RESET}"
    bot_border = f"{side_pad}{b_col}╰{'─' * (box_w - 2)}╯{RESET}"
    mid_border = f"{side_pad}{b_col}├{'─' * (box_w - 2)}┤{RESET}"

    lines_out.append(top_border)

    title = f"{BOLD}{t_white}SECURITY & ENGINE PROFILE{RESET}"
    pad_l = (box_w - 2 - len(strip_ansi(title))) // 2
    pad_r = box_w - 2 - len(strip_ansi(title)) - pad_l
    lines_out.append(f"{side_pad}{b_col}│{RESET}{' ' * pad_l}{title}{' ' * pad_r}{b_col}│{RESET}")
    lines_out.append(mid_border)

    dev_str = (device_id[:18] + "...") if (device_id and len(device_id) > 21) else (device_id or "Auto-Generated")

    rows = [
        ("TARGET API", "Discord v9 [Chrome 124]", "ENGINE", "curl_cffi (JA3/TLS Evasion)"),
        ("FINGERPRINT", "Akamai & Experiments v2", "DEVICE ID", dev_str),
        ("TELEMETRY", "Science Pipeline Emulated", "STATUS", f"{fg_rgb(*GREEN_NEON)}READY FOR AUTH{RESET}"),
    ]

    col_w = (box_w - 4) // 2
    for r1_k, r1_v, r2_k, r2_v in rows:
        left_txt = f"{t_muted}{r1_k:<12}: {t_accent}{r1_v}{RESET}"
        right_txt = f"{t_muted}{r2_k:<10}: {t_accent}{r2_v}{RESET}"

        pad_left = max(0, col_w - len(strip_ansi(left_txt)))
        pad_right = max(0, col_w - len(strip_ansi(right_txt)))

        content = f" {left_txt}{' ' * pad_left}{b_col}│{RESET} {right_txt}{' ' * pad_right}"
        fill_pad = max(0, box_w - 2 - len(strip_ansi(content)))
        lines_out.append(f"{side_pad}{b_col}│{RESET}{content}{' ' * fill_pad}{b_col}│{RESET}")

    lines_out.append(bot_border)
    lines_out.append("")

    # 4. Author Attribution
    author_line = (
        f"{fg_rgb(*GRAY_MUTED)}< Made With {RESET}{fg_rgb(*RED_CRIMSON)}❤️{RESET}{fg_rgb(*GRAY_MUTED)} in India By {RESET}"
        f"{fg_rgb(*CYAN_MID)}{BOLD}@jijaghosty{RESET}{fg_rgb(*GRAY_MUTED)} • {RESET}"
        f"{fg_rgb(*PURPLE_NEON)}Async Development{RESET}{fg_rgb(*GRAY_MUTED)} >{RESET}"
    )
    lines_out.append(center(author_line, width))
    lines_out.append("")

    # 5. Section Divider for Pipeline Logs
    div_title = f" {BOLD}{fg_rgb(*CYAN_ELECTRIC)}[ AUTHENTICATION PIPELINE ]{RESET} "
    div_plain_len = len(strip_ansi(div_title))
    left_line_len = 4
    right_line_len = max(0, box_w - left_line_len - div_plain_len)
    section_div = f"{fg_rgb(*GRAY_BORDER)}{'─' * left_line_len}{RESET}{div_title}{fg_rgb(*GRAY_BORDER)}{'─' * right_line_len}{RESET}"
    lines_out.append(f"{side_pad}{section_div}")
    lines_out.append("")

    print("\n".join(lines_out))

def log_step(badge_label: str, msg: str, bg_color: tuple = (14, 165, 233), fg_color: tuple = (0, 0, 0)):
    badge = make_badge(badge_label, bg_color, fg_color, width=11)
    arrow = f"{fg_rgb(*CYAN_MID)}───›{RESET}"
    print(f"   {badge} {arrow} {fg_rgb(*WHITE_BRIGHT)}{msg}{RESET}")

def log_info(msg: str):
    log_step("INFO", msg, bg_color=(14, 165, 233), fg_color=(0, 0, 0))

def log_success(msg: str):
    badge = make_badge("SUCCESS", (16, 185, 129), (0, 0, 0), width=11)
    arrow = f"{fg_rgb(*GREEN_NEON)}───›{RESET}"
    print(f"   {badge} {arrow} {fg_rgb(*GREEN_NEON)}{BOLD}{msg}{RESET}")

def log_warn(msg: str):
    badge = make_badge("SECURITY", (217, 119, 6), (0, 0, 0), width=11)
    arrow = f"{fg_rgb(*YELLOW_GOLD)}───›{RESET}"
    print(f"   {badge} {arrow} {fg_rgb(*YELLOW_GOLD)}{msg}{RESET}")

def log_error(msg: str):
    badge = make_badge("FAILED", (220, 38, 38), (255, 255, 255), width=11)
    arrow = f"{fg_rgb(*RED_BRIGHT)}───›{RESET}"
    print(f"   {badge} {arrow} {fg_rgb(*RED_CRIMSON)}{msg}{RESET}")

def log_support_prompt(width: int = None):
    if width is None:
        width = get_term_width()
    b_col = fg_rgb(*CYAN_ELECTRIC)
    t_col = fg_rgb(*WHITE_BRIGHT)
    l_col = fg_rgb(*PURPLE_NEON)
    
    print("")
    print(center(f"{b_col}╭────────────── [ ASYNC DEVELOPMENT COMMUNITY SUPPORT ] ──────────────╮{RESET}", width))
    print(center(f"{b_col}│{RESET} {fg_rgb(239, 68, 68)}{BOLD}[!] Encountered an issue during account authentication.{RESET}               {b_col}│{RESET}", width))
    print(center(f"{b_col}│{RESET} {t_col}Join our official Discord server for instant help & updates:{RESET}           {b_col}│{RESET}", width))
    print(center(f"{b_col}│{RESET} {l_col}{BOLD}https://discord.gg/asMJGgDA7u{RESET}                                         {b_col}│{RESET}", width))
    print(center(f"{b_col}│{RESET} {fg_rgb(*GRAY_MUTED)}Made With ❤️ By @jijaghosty • Async Development Support{RESET}                {b_col}│{RESET}", width))
    print(center(f"{b_col}╰──────────────────────────────────────────────────────────────────────╯{RESET}", width))
    print("")

def prompt_input(label: str) -> str:
    """Styled input prompt with badge and clean styling."""
    badge = make_badge("INPUT", (0, 245, 255), (0, 0, 0), width=11)
    arrow = f"{fg_rgb(*CYAN_ELECTRIC)}───›{RESET}"
    prompt_str = f"   {badge} {arrow} {fg_rgb(*WHITE_BRIGHT)}{label}: {RESET}"
    try:
        val = input(prompt_str).strip()
        return val
    except KeyboardInterrupt:
        print(f"\n{fg_rgb(*YELLOW_GOLD)}[!] Operation cancelled by user.{RESET}")
        sys.exit(0)

def render_token_card(token: str, user_data: dict = None, device_id: str = None, width: int = None):
    """Render a showcase card presenting the retrieved token and extracted profile."""
    if width is None:
        width = get_term_width()

    box_w = min(width - 4, 82)
    if box_w < 64:
        box_w = 64

    side_pad = " " * max(0, (width - box_w) // 2)

    b_col = fg_rgb(*GREEN_NEON)
    t_white = fg_rgb(*WHITE_BRIGHT)
    t_label = fg_rgb(*CYAN_MID)
    t_tok = fg_rgb(*GREEN_NEON)

    lines = [""]
    lines.append(f"{side_pad}{b_col}╭{'─' * (box_w - 2)}╮{RESET}")
    
    title = f"{BOLD}{fg_rgb(*GREEN_EMERALD)}✨ DISCORD TOKEN ACQUIRED SUCCESSFULLY ✨{RESET}"
    pad_l = (box_w - 2 - len(strip_ansi(title))) // 2
    pad_r = box_w - 2 - len(strip_ansi(title)) - pad_l
    lines.append(f"{side_pad}{b_col}│{RESET}{' ' * pad_l}{title}{' ' * pad_r}{b_col}│{RESET}")
    lines.append(f"{side_pad}{b_col}├{'─' * (box_w - 2)}┤{RESET}")

    # Profile Rows with sanitized strings to prevent multiline disruptions
    display_name = "Unknown"
    user_id = "N/A"
    email = "N/A"
    phone = "None"
    mfa_str = "Disabled"
    nitro_str = "None"

    if user_data:
        uname = str(user_data.get("username", "")).replace("\n", "").replace("\r", "").strip()
        disc = str(user_data.get("discriminator", "0")).strip()
        raw_gname = user_data.get("global_name")
        gname = str(raw_gname).replace("\n", "").replace("\r", "").strip() if raw_gname else uname
        display_name = f"{gname} (@{uname})" if (disc == "0" or not disc) else f"{uname}#{disc}"
        user_id = str(user_data.get("id", "N/A")).strip()
        email = str(user_data.get("email") or "N/A").strip()
        phone = str(user_data.get("phone") or "None").strip()
        mfa_str = "Enabled (2FA Active)" if user_data.get("mfa_enabled") else "Disabled"
        ptype = user_data.get("premium_type", 0)
        nitro_map = {0: "None", 1: "Nitro Classic", 2: "Nitro Boost", 3: "Nitro Basic"}
        nitro_str = nitro_map.get(ptype, "None")

    fields = [
        ("USER", display_name),
        ("USER ID", user_id),
        ("EMAIL", email),
        ("PHONE", phone),
        ("MFA 2FA", mfa_str),
        ("NITRO", nitro_str),
    ]

    for label, val in fields:
        content = f" {t_label}{label:<10}{RESET} {b_col}│{RESET} {t_white}{val}{RESET}"
        pad = max(0, box_w - 2 - len(strip_ansi(content)))
        lines.append(f"{side_pad}{b_col}│{RESET}{content}{' ' * pad}{b_col}│{RESET}")

    lines.append(f"{side_pad}{b_col}├{'─' * (box_w - 2)}┤{RESET}")

    # Token Field Box
    token_label = f" {t_label}{'TOKEN':<10}{RESET} {b_col}│{RESET} "
    token_str = f"{t_tok}{BOLD}{token}{RESET}"
    token_plain = f" TOKEN      │ {token}"
    
    if len(strip_ansi(token_plain)) <= box_w - 2:
        pad = max(0, box_w - 2 - len(strip_ansi(token_label + token_str)))
        lines.append(f"{side_pad}{b_col}│{RESET}{token_label}{token_str}{' ' * pad}{b_col}│{RESET}")
    else:
        avail = box_w - 16
        t1 = token[:avail]
        t2 = token[avail:]
        pad1 = max(0, box_w - 2 - len(strip_ansi(token_label + f"{t_tok}{BOLD}{t1}{RESET}")))
        lines.append(f"{side_pad}{b_col}│{RESET}{token_label}{t_tok}{BOLD}{t1}{RESET}{' ' * pad1}{b_col}│{RESET}")
        line2 = f" {' ' * 10} {b_col}│{RESET} {t_tok}{BOLD}{t2}{RESET}"
        pad2 = max(0, box_w - 2 - len(strip_ansi(line2)))
        lines.append(f"{side_pad}{b_col}│{RESET}{line2}{' ' * pad2}{b_col}│{RESET}")

    lines.append(f"{side_pad}{b_col}╰{'─' * (box_w - 2)}╯{RESET}")
    lines.append("")
    print("\n".join(lines))

def copy_to_clipboard(text: str) -> bool:
    """Copy text to Windows clipboard natively using clip."""
    try:
        subprocess.run("clip", input=text.strip(), text=True, shell=True, check=True)
        return True
    except Exception:
        return False

def save_token_to_file(token: str, user_data: dict = None, filepath: str = "token.txt"):
    """Save token and timestamp to local file."""
    try:
        uname = user_data.get("username", "unknown") if user_data else "unknown"
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {uname} | Token: {token}\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)
        return True
    except Exception:
        return False
