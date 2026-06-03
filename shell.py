import os
import sys
import getpass
from utils import parse_line

# --- ANSI True Color Escape Codes ---
COLOR_LOGO = "\033[38;2;19;175;215m"                # Cyan (#13AFD7)
COLOR_OS_INFO = "\033[38;2;19;175;215m\033[1m"      # Cyan + Bold
COLOR_TAGLINE = "\033[38;2;29;90;104m"              # Dark Cyan (#1D5A68)
COLOR_LABEL = "\033[38;2;19;175;215m"               # Cyan
COLOR_VALUE = "\033[38;2;42;138;158m"               # Mid Cyan (#2A8A9E)
COLOR_DIVIDER = "\033[38;2;26;58;69m"               # Deep Cyan (#1A3A45)
COLOR_RESET = "\033[0m"

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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_splash_banner():
    # 1. Logo CYANIX OS
    print()
    print(COLOR_LOGO + ASCII_LOGO.strip("\n") + COLOR_RESET)
    print()

    # 2. Nama & Tagline
    print(COLOR_OS_INFO + "∞ CyanSh — Cyanix CLI Shell v1.0.0" + COLOR_RESET)
    print(COLOR_TAGLINE + '"Security at the Core, Performance at the Edge"' + COLOR_RESET)
    print()

    # Divider
    print(COLOR_DIVIDER + DIVIDER + COLOR_RESET)

    # 3. Tabel Info Sistem
    for label, value in SYSTEM_INFO:
        print(f"{COLOR_LABEL}  {label:<14}{COLOR_VALUE}{value}{COLOR_RESET}")

    # Divider
    print(COLOR_DIVIDER + DIVIDER + COLOR_RESET)

def main():
    clear_screen()

    print_splash_banner()

    print("  Ketik 'help' untuk daftar perintah, 'exit' untuk keluar.\n")

    username = getpass.getuser()

    while True:
        try:
            raw_input = input(f"{username}@cynix:~$ ").strip()
            
            if not raw_input:
                continue

            try:
                args = parse_line(raw_input)
            except ValueError as e:
                print(e)
                continue

            if not args:
                continue

            cmd = args[0]

            if cmd == "exit":
                break
            
            elif cmd == "help":
                print()
                print("Cynix-CLI-Shell (CyanSh) - Panduan Perintah:")
                print("  help  - Menampilkan menu bantuan ini.")
                print("  exit  - Keluar dari program shell.")
                print()
            
            else:
                print(f"cynix: command not found: {cmd}")

        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print()
            break

    sys.exit(0)

if __name__ == "__main__":
    main()