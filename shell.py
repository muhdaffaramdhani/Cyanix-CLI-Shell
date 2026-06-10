import os
import sys
import getpass
import socket
import ctypes
import time
from utils import parse_line, execute_command
from config import (
    setup_terminal,
    clear_screen,
    print_splash_banner,
    enable_raw_mode,
    disable_raw_mode,
    IS_GIT_BASH,
    COLOR_PROMPT_USER,
    COLOR_PROMPT_OS,
    COLOR_PROMPT_DIR,
    COLOR_PROMPT_SYMBOL,
    COLOR_RESET
)

# History file settings
HISTORY_FILE = os.path.expanduser("~/.cyanix_history")

# Cross-platform raw input support
try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False

if not WINDOWS:
    import tty
    import termios
    import select

# Key code definitions (supporting standard e0 and 00 prefixes on Windows, and ANSI escape codes on UNIX/Git Bash)
KEY_UP = (b'\xe0H', b'\x00H', b'\x1b[A')
KEY_DOWN = (b'\xe0P', b'\x00P', b'\x1b[B')
KEY_RIGHT = (b'\xe0M', b'\x00M', b'\x1b[C')
KEY_LEFT = (b'\xe0K', b'\x00K', b'\x1b[D')
KEY_DELETE = (b'\xe0S', b'\x00S', b'\x1b[3~')

def bytes_available_windows() -> int:
    try:
        # Get standard input handle (STD_INPUT_HANDLE = -10)
        handle = ctypes.windll.kernel32.GetStdHandle(-10)
        avail = ctypes.c_ulong(0)
        res = ctypes.windll.kernel32.PeekNamedPipe(handle, None, 0, None, ctypes.byref(avail), None)
        if res != 0:
            return avail.value
    except Exception:
        pass
    return 0

def is_char_available() -> bool:
    start_time = time.time()
    while True:
        if WINDOWS:
            if bytes_available_windows() > 0:
                return True
        else:
            import select
            r, w, x = select.select([sys.stdin], [], [], 0.001)
            if r:
                return True
        if (time.time() - start_time) * 1000 > 10:  # 10ms timeout
            break
        time.sleep(0.001)
    return False

def load_history() -> list[str]:
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        history.append(line)
        except Exception:
            pass
    return history

def save_history(history: list[str]):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            for item in history:
                f.write(item + "\n")
    except Exception:
        pass

def add_to_history(history: list[str], cmd: str):
    if not cmd:
        return
    if not history or history[-1] != cmd:
        history.append(cmd)
        if len(history) > 1000:
            history.pop(0)
        save_history(history)

def get_suggestion(buffer_str: str) -> str:
    if not buffer_str or buffer_str.endswith(" "):
        return ""
    
    idx = buffer_str.rfind(' ')
    last_word = buffer_str[idx+1:]
    is_cd = buffer_str.strip().startswith("cd")
    
    # Strip quotes if they were opened
    clean_last_word = last_word.strip('"\'')
    
    search_dir = "."
    filter_prefix = clean_last_word
    
    if '/' in clean_last_word or '\\' in clean_last_word:
        normalized = clean_last_word.replace('\\', '/')
        dir_idx = normalized.rfind('/')
        dir_part = clean_last_word[:dir_idx]
        filter_prefix = clean_last_word[dir_idx+1:]
        search_dir = dir_part if dir_part else "."
        
    # Prevent automatic suggestion if the prefix for matching is empty
    if not filter_prefix:
        return ""
        
    try:
        if os.path.isdir(search_dir):
            items = os.listdir(search_dir)
            matches = []
            for name in items:
                full_path = os.path.join(search_dir, name)
                if is_cd and not os.path.isdir(full_path):
                    continue
                if name.lower().startswith(filter_prefix.lower()):
                    display_name = name
                    if os.path.isdir(full_path):
                        display_name += "/"
                    matches.append(display_name)
            
            if matches:
                matches.sort()
                best_match = matches[0]
                return best_match[len(filter_prefix):]
    except Exception:
        pass
    return ""

def autocomplete_last_word(buffer_str: str) -> tuple[str, bool]:
    if buffer_str.endswith(" "):
        return buffer_str, False
        
    idx = buffer_str.rfind(' ')
    prefix = buffer_str[:idx+1]
    last_word = buffer_str[idx+1:]
    is_cd = buffer_str.strip().startswith("cd")
    
    # Strip quotes if they were opened
    clean_last_word = last_word.strip('"\'')
    
    search_dir = "."
    filter_prefix = clean_last_word
    dir_prefix = ""
    
    if '/' in clean_last_word or '\\' in clean_last_word:
        normalized = clean_last_word.replace('\\', '/')
        dir_idx = normalized.rfind('/')
        dir_part = clean_last_word[:dir_idx]
        filter_prefix = clean_last_word[dir_idx+1:]
        search_dir = dir_part if dir_part else "."
        dir_prefix = clean_last_word[:dir_idx+1]
        
    try:
        if os.path.isdir(search_dir):
            items = os.listdir(search_dir)
            matches = []
            for name in items:
                full_path = os.path.join(search_dir, name)
                if is_cd and not os.path.isdir(full_path):
                    continue
                if name.lower().startswith(filter_prefix.lower()):
                    display_name = name
                    if os.path.isdir(full_path):
                        display_name += "/"
                    matches.append(display_name)
            
            if matches:
                matches.sort()
                best_match = matches[0]
                completed_word = dir_prefix + best_match
                # Quote completed word if it contains spaces
                if " " in completed_word:
                    completed_word = f'"{completed_word}"'
                return prefix + completed_word, True
    except Exception:
        pass
    return buffer_str, False

def get_char() -> bytes:
    if WINDOWS and not IS_GIT_BASH:
        # Native Windows console using msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            return ch + ch2
        return ch
    else:
        # UNIX or Git Bash using sys.stdin.read(1)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            if is_char_available():
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    if is_char_available():
                        ch3 = sys.stdin.read(1)
                        if ch3 in ('3', '1'):
                            if is_char_available():
                                ch4 = sys.stdin.read(1)
                                return f"\x1b[{ch3}{ch4}".encode('utf-8')
                        return f"\x1b[{ch3}".encode('utf-8')
                return f"\x1b{ch2}".encode('utf-8')
        return ch.encode('utf-8')

def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()

def read_line_interactive(prompt_prefix: str, history: list[str]) -> str:
    if not is_interactive():
        sys.stdout.write(prompt_prefix)
        sys.stdout.flush()
        try:
            return input()
        except (KeyboardInterrupt, EOFError):
            raise
            
    import shutil
    buffer = []
    pos = 0
    history_index = len(history)
    saved_buffer = ""
    start_idx = 0
    
    sys.stdout.write(prompt_prefix)
    sys.stdout.flush()
    
    while True:
        buffer_str = "".join(buffer)
        suggestion = get_suggestion(buffer_str) if pos == len(buffer) else ""
        
        # Get terminal size
        try:
            cols = os.get_terminal_size().columns
        except Exception:
            try:
                cols = shutil.get_terminal_size().columns
            except Exception:
                cols = 80
                
        prompt_len = 2  # Visual length of "$ " is 2
        visible_width = max(10, cols - prompt_len - 4)
        
        # Adjust start_idx to keep pos within visible window
        if pos < start_idx:
            start_idx = pos
        elif pos > start_idx + visible_width:
            start_idx = pos - visible_width
            
        if start_idx + visible_width > len(buffer):
            start_idx = max(0, len(buffer) - visible_width)
            
        if start_idx > pos:
            start_idx = pos
            
        # Get visible slice of buffer
        buffer_visible = buffer[start_idx : start_idx + visible_width]
        buffer_visible_str = "".join(buffer_visible)
        
        # Get visible slice of suggestion
        suggestion_visible = ""
        if suggestion:
            rem = start_idx + visible_width - len(buffer)
            if rem > 0:
                suggestion_visible = suggestion[:rem]
                
        suggestion_rendered = ""
        if suggestion_visible:
            suggestion_rendered = f"\033[90m{suggestion_visible}\033[0m"
            
        sys.stdout.write("\r" + prompt_prefix + buffer_visible_str + suggestion_rendered + "\033[K")
        
        # Calculate move left distance from the end of the printed slice to the cursor pos
        move_left = (len(buffer_visible) + len(suggestion_visible)) - (pos - start_idx)
        if move_left > 0:
            sys.stdout.write(f"\033[{move_left}D")
        sys.stdout.flush()
        
        try:
            ch = get_char()
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise KeyboardInterrupt
            
        if not ch:
            continue
            
        if ch == b'\x03':  # Ctrl+C
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise KeyboardInterrupt
            
        elif ch == b'\x04':  # Ctrl+D
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise EOFError
            
        elif ch in (b'\r', b'\n'):  # Enter
            sys.stdout.write("\r" + prompt_prefix + buffer_str + "\033[K\n")
            sys.stdout.flush()
            return buffer_str
            
        elif ch in (b'\x08', b'\x7f'):  # Backspace
            if pos > 0:
                buffer.pop(pos - 1)
                pos -= 1
                
        elif ch in KEY_DELETE:
            if pos < len(buffer):
                buffer.pop(pos)
                
        elif ch in (b'\t',):  # Tab
            completed_str, ok = autocomplete_last_word(buffer_str)
            if ok:
                buffer = list(completed_str)
                pos = len(buffer)
                
        elif ch in KEY_LEFT:
            if pos > 0:
                pos -= 1
                
        elif ch in KEY_RIGHT:
            if suggestion:
                idx = buffer_str.rfind(' ')
                prefix = buffer_str[:idx+1]
                last_word = buffer_str[idx+1:]
                
                full_word = last_word + suggestion
                if " " in full_word:
                    clean_word = full_word.strip('"\'')
                    completed_word = f'"{clean_word}"'
                else:
                    completed_word = full_word
                    
                buffer = list(prefix + completed_word)
                pos = len(buffer)
            elif pos < len(buffer):
                pos += 1
                
        elif ch in KEY_UP:
            if history:
                if history_index == len(history):
                    saved_buffer = buffer_str
                if history_index > 0:
                    history_index -= 1
                    buffer = list(history[history_index])
                    pos = len(buffer)
                    
        elif ch in KEY_DOWN:
            if history_index < len(history):
                history_index += 1
                if history_index == len(history):
                    buffer = list(saved_buffer)
                else:
                    buffer = list(history[history_index])
                pos = len(buffer)
                
        elif len(ch) == 1 and ch[0] >= 32:
            try:
                char_to_insert = ch.decode('utf-8', errors='replace')
                buffer.insert(pos, char_to_insert)
                pos += 1
            except Exception:
                pass

def main():
    setup_terminal()
    clear_screen()
    print_splash_banner()
    print("  Ketik 'help' untuk daftar perintah, 'exit' untuk keluar.\n")
    
    # Setup global state structure
    state = {
        'debug_mode': "--debug" in sys.argv,
        'running': True
    }
    
    if "--debug" in sys.argv:
        sys.argv.remove("--debug")
        
    history = load_history()
    username = getpass.getuser()
    device = socket.gethostname()
    
    first_prompt = True
    
    enable_raw_mode()
    try:
        while state['running']:
            try:
                # Print blank line between prompts (except the very first one)
                if not first_prompt:
                    print()
                first_prompt = False
                
                # Format path: replace backslash with forward slash and use ~ for home directory
                raw_path = os.getcwd()
                formatted_path = raw_path.replace('\\', '/')
                home = os.path.expanduser("~").replace('\\', '/')
                if formatted_path.startswith(home):
                    formatted_path = "~" + formatted_path[len(home):]
                    
                # Line 1 of prompt (Colorful layout)
                debug_prefix = "\033[93m[DEBUG]\033[0m " if state['debug_mode'] else ""
                print(f"{debug_prefix}{COLOR_PROMPT_USER}{username}@{device}{COLOR_RESET} {COLOR_PROMPT_OS}CyanixOS{COLOR_RESET} {COLOR_PROMPT_DIR}{formatted_path}{COLOR_RESET}")
                
                # Line 2 of prompt (interactive read)
                prompt_prefix = f"{COLOR_PROMPT_SYMBOL}${COLOR_RESET} "
                
                raw_input = read_line_interactive(prompt_prefix, history).strip()
                
                if not raw_input:
                    continue
                    
                try:
                    args = parse_line(raw_input)
                except ValueError as e:
                    print(e)
                    continue
                    
                if not args:
                    continue
                    
                # Print debug information if debug mode is active
                if state['debug_mode']:
                    print("\033[93m[DEBUG] Tokenized arguments:\033[0m")
                    for idx, arg in enumerate(args):
                        print(f"\033[93m  args[{idx}] = \"{arg}\"\033[0m")
                        
                add_to_history(history, raw_input)
                
                execute_command(args, state)
                
            except KeyboardInterrupt:
                # Print a blank line and reset prompt
                print()
                continue
            except EOFError:
                print()
                break
    finally:
        disable_raw_mode()
            
    sys.exit(0)

if __name__ == "__main__":
    main()