import os
import sys
import ctypes
import subprocess

# --- ANSI True Color Escape Codes for Splash Banner ---
COLOR_LOGO = "\033[38;2;19;175;215m"                # Cyan (#13AFD7)
COLOR_OS_INFO = "\033[38;2;19;175;215m\033[1m"      # Cyan + Bold
COLOR_TAGLINE = "\033[38;2;29;90;104m"              # Dark Cyan (#1D5A68)
COLOR_LABEL = "\033[38;2;19;175;215m"               # Cyan
COLOR_VALUE = "\033[38;2;42;138;158m"               # Mid Cyan (#2A8A9E)
COLOR_DIVIDER = "\033[38;2;26;58;69m"               # Deep Cyan (#1A3A45)
COLOR_RESET = "\033[0m"

# --- Colorful Prompt Themes ---
COLOR_PROMPT_USER = "\033[1;32m"      # Bold Green
COLOR_PROMPT_OS = "\033[1;35m"        # Bold Magenta/Pink
COLOR_PROMPT_DIR = "\033[1;33m"       # Bold Yellow/Orange
COLOR_PROMPT_SYMBOL = "\033[1;36m"    # Bold Light Blue/Cyan

# --- Constants & Specs ---
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

# Detect Git Bash on Windows
IS_GIT_BASH = (os.name == 'nt') and ("MSYSTEM" in os.environ)
old_settings = None

def enable_raw_mode():
    global old_settings
    if os.name == 'nt':
        if IS_GIT_BASH:
            try:
                # Set raw mode and turn off echo in Git Bash (mintty)
                subprocess.run(["stty", "raw", "-echo"], capture_output=True)
            except Exception:
                pass
        else:
            # Enable VT mode in native Windows console
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                pass
    else:
        # UNIX raw mode
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
                # Restore terminal settings in Git Bash
                subprocess.run(["stty", "sane"], capture_output=True)
            except Exception:
                pass
    else:
        # UNIX restore
        if old_settings is not None:
            try:
                import termios
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

def setup_terminal():
    if os.name == 'nt':
        # Enable virtual terminal processing on Windows to render ANSI colors properly
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
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
