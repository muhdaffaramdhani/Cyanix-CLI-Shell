import os
import sys
import ctypes
import subprocess

COLOR_LOGO = "\033[38;5;39m"
COLOR_OS_INFO = "\033[38;5;39m\033[1m"
COLOR_TAGLINE = "\033[38;5;31m"
COLOR_LABEL = "\033[38;5;39m"
COLOR_VALUE = "\033[38;5;73m"
COLOR_DIVIDER = "\033[38;5;24m"
COLOR_RESET = "\033[0m"

COLOR_PROMPT_USER = "\033[1;32m"
COLOR_PROMPT_OS = "\033[1;36m"
COLOR_PROMPT_DIR = "\033[1;33m"
COLOR_PROMPT_SYMBOL = "\033[1;36m"

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ASCII_LOGO = """

 ██████╗██╗   ██╗██████╗ ███╗   ██╗██╗██╗  ██╗     ██████╗ ███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗████╗  ██║██║╚██╗██╔╝    ██╔═══██╗██╔════╝
██║      ╚████╔╝ ███████║██╔██╗ ██║██║ ╚███╔╝     ██║   ██║███████╗
██║       ╚██╔╝  ██╔══██║██║╚██╗██║██║ ██╔██╗     ██║   ██║╚════██║
╚██████╗   ██║   ██║  ██║██║ ╚████║██║██╔╝ ██╗    ╚██████╔╝███████║
 ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝

"""

SYSTEM_INFO = [
    ("Shell Name", "CyanSh (Cyanix CLI Shell)"),
    ("Version", "v1.0.0"),
    ("Contributors", "Fujiono Nur Ikhsan (1313624008)\n"
                     "                Nadine Alysha Maheswari (1313624009)\n"
                     "                Muhammad Daffa Ramdhani (1313624025)\n"
                     "                Fathya Khairani R (1313624056)")
]

IS_GIT_BASH = (os.name == 'nt') and ("MSYSTEM" in os.environ)
old_settings = None

def enable_raw_mode():
    global old_settings
    if os.name == 'nt':
        if IS_GIT_BASH:
            try:
                subprocess.run(["stty", "raw", "-echo"], capture_output=True)
            except Exception:
                pass
        else:
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                pass
    else:
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        except Exception:
            pass

def disable_raw_mode():
    global old_settings
    if os.name == 'nt':
        if IS_GIT_BASH:
            try:
                subprocess.run(["stty", "sane"], capture_output=True)
            except Exception:
                pass
    else:
        if old_settings is not None:
            try:
                import termios
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSANOW, old_settings)
            except Exception:
                pass

def setup_terminal():
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
    else:
        try:
            import termios
            import sys
            fd = sys.stdin.fileno()
            attrs = termios.tcgetattr(fd)
            attrs[3] |= (termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
            attrs[1] |= termios.OPOST
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
        except Exception:
            pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_splash_banner():
    print()
    print(COLOR_LOGO + ASCII_LOGO.strip("\n") + COLOR_RESET)
    print()
    print(COLOR_OS_INFO + "∞ CyanSh — Cyanix CLI Shell v1.0.0" + COLOR_RESET)
    print(COLOR_TAGLINE + '"Security at the Core, Performance at the Edge"' + COLOR_RESET)
    print()
    print(COLOR_DIVIDER + DIVIDER + COLOR_RESET)
    for label, value in SYSTEM_INFO:
        print(f"{COLOR_LABEL}  {label:<14}{COLOR_VALUE}{value}{COLOR_RESET}")
    print(COLOR_DIVIDER + DIVIDER + COLOR_RESET)
