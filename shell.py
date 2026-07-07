import os
import sys
import getpass
import socket
import ctypes
import time
import unicodedata
import atexit
from utils.parser import parse_line
from utils.builtins import execute_command

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

atexit.register(disable_raw_mode)

HISTORY_FILE = os.path.expanduser("~/.cyanix_history")

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False

if not WINDOWS:
    import tty
    import termios
    import select

KEY_UP = (b'\xe0H', b'\x00H', b'\x1b[A')
KEY_DOWN = (b'\xe0P', b'\x00P', b'\x1b[B')
KEY_RIGHT = (b'\xe0M', b'\x00M', b'\x1b[C')
KEY_LEFT = (b'\xe0K', b'\x00K', b'\x1b[D')
KEY_DELETE = (b'\xe0S', b'\x00S', b'\x1b[3~')

def get_char_width(char: str) -> int:
    if not char:
        return 0
    if ord(char) < 32 or (127 <= ord(char) < 160):
        return 0
    w = unicodedata.east_asian_width(char)
    if w in ('W', 'F'):
        return 2
    return 1

def get_str_width(s: str) -> int:
    return sum(get_char_width(c) for c in s)

def check_arg_limit(buf_list: list[str], insert_char: str, pos: int) -> bool:
    import shlex
    temp_buf = list(buf_list)
    temp_buf.insert(pos, insert_char)
    temp_str = "".join(temp_buf)
    try:
        tokens = shlex.split(temp_str)
        return len(tokens) <= 64
    except ValueError:
        tokens = temp_str.split()
        return len(tokens) <= 64

def calculate_visible_slice(buffer: list[str], pos: int, visible_width: int) -> tuple[int, list[str], int]:
    start_idx = pos
    w = 0
    while start_idx > 0:
        char_w = get_char_width(buffer[start_idx - 1])
        if w + char_w > visible_width:
            break
        w += char_w
        start_idx -= 1
        
    visible_chars = []
    curr_width = 0
    cursor_offset_width = 0
    
    for i in range(start_idx, len(buffer)):
        c = buffer[i]
        char_w = get_char_width(c)
        if curr_width + char_w > visible_width:
            if curr_width == 0:
                curr_width += char_w
                if i < pos:
                    cursor_offset_width += char_w
                visible_chars.append(c)
            break
        if i < pos:
            cursor_offset_width += char_w
        visible_chars.append(c)
        curr_width += char_w
        
    return start_idx, visible_chars, cursor_offset_width

def get_clipboard_text() -> str:
    if sys.platform == 'win32':
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if ctypes.windll.user32.OpenClipboard(hwnd):
                try:
                    h_clip_mem = ctypes.windll.user32.GetClipboardData(13)
                    if h_clip_mem:
                        ctypes.windll.kernel32.GlobalLock.restype = ctypes.c_void_p
                        ctypes.windll.kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
                        p_mem = ctypes.windll.kernel32.GlobalLock(h_clip_mem)
                        if p_mem:
                            text = ctypes.wstring_at(p_mem)
                            ctypes.windll.kernel32.GlobalUnlock(h_clip_mem)
                            return text
                finally:
                    ctypes.windll.user32.CloseClipboard()
        except Exception:
            pass
            
        try:
            import subprocess
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                text=True,
                errors='ignore',
                shell=True
            )
            if out:
                return out.strip('\r\n')
        except Exception:
            pass
            
    elif sys.platform == 'darwin':
        try:
            import subprocess
            return subprocess.check_output(['pbpaste'], text=True, errors='ignore')
        except Exception:
            pass
    else:
        try:
            import subprocess
            for cmd in [['xclip', '-selection', 'clipboard', '-o'], ['xsel', '-b', '-o'], ['wl-paste']]:
                try:
                    return subprocess.check_output(cmd, text=True, errors='ignore')
                except Exception:
                    continue
        except Exception:
            pass
    return ""

def bytes_available_windows() -> int:
    try:
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
            r, w, x = select.select([0], [], [], 0.001)
            if r:
                return True
        if (time.time() - start_time) * 1000 > 10:
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
    
    in_quote = None
    last_space_idx = -1
    quote_start_idx = -1
    for i, c in enumerate(buffer_str):
        if c == ' ' and in_quote is None:
            last_space_idx = i
        elif c in ('"', "'"):
            if in_quote == c:
                in_quote = None
            elif in_quote is None:
                in_quote = c
                quote_start_idx = i
                
    if in_quote is not None:
        last_word = buffer_str[quote_start_idx:]
    else:
        last_word = buffer_str[last_space_idx+1:]
        
    is_cd = buffer_str.strip().startswith("cd")
    clean_last_word = last_word.strip('"\'')
    
    search_dir = "."
    filter_prefix = clean_last_word
    
    if '/' in clean_last_word or '\\' in clean_last_word:
        normalized = clean_last_word.replace('\\', '/')
        dir_idx = normalized.rfind('/')
        dir_part = clean_last_word[:dir_idx]
        filter_prefix = clean_last_word[dir_idx+1:]
        search_dir = dir_part if dir_part else "."
        
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

def get_all_matches(buffer_str: str) -> tuple[str, list[str]]:
    in_quote = None
    last_space_idx = -1
    quote_start_idx = -1
    for i, c in enumerate(buffer_str):
        if c == ' ' and in_quote is None:
            last_space_idx = i
        elif c in ('"', "'"):
            if in_quote == c:
                in_quote = None
            elif in_quote is None:
                in_quote = c
                quote_start_idx = i
                
    if in_quote is not None:
        prefix = buffer_str[:quote_start_idx]
        last_word = buffer_str[quote_start_idx:]
    else:
        prefix = buffer_str[:last_space_idx+1]
        last_word = buffer_str[last_space_idx+1:]
        
    is_cd = buffer_str.strip().startswith("cd")
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
        
    matches = []
    try:
        if os.path.isdir(search_dir):
            items = os.listdir(search_dir)
            for name in items:
                if name.startswith('.') and not filter_prefix.startswith('.'):
                    continue
                full_path = os.path.join(search_dir, name)
                if is_cd and not os.path.isdir(full_path):
                    continue
                if name.lower().startswith(filter_prefix.lower()):
                    completed = dir_prefix + name
                    if os.path.isdir(full_path):
                        completed += "/"
                    if " " in completed:
                        completed = f'"{completed}"'
                    matches.append(completed)
            matches.sort(key=str.lower)
    except Exception:
        pass
    return prefix, matches


def get_char() -> bytes:
    if WINDOWS and not IS_GIT_BASH:
        try:
            ch = msvcrt.getwch()
        except KeyboardInterrupt:
            return b'\x03'
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            return (ch + ch2).encode('latin-1')
        if ch == '\x03':
            return b'\x03'
        return ch.encode('utf-8')
    else:
        try:
            ch = os.read(0, 1)
        except Exception:
            return b""
        if ch == b'\x1b':
            if is_char_available():
                try:
                    ch2 = os.read(0, 1)
                except Exception:
                    ch2 = b""
                if ch2 == b'[':
                    if is_char_available():
                        try:
                            ch3 = os.read(0, 1)
                        except Exception:
                            ch3 = b""
                        if ch3 in (b'3', b'1'):
                            if is_char_available():
                                try:
                                    ch4 = os.read(0, 1)
                                except Exception:
                                    ch4 = b""
                                return ch + ch2 + ch3 + ch4
                        return ch + ch2 + ch3
                return ch + ch2
        return ch

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
    current_matches = []
    match_index = -1
    original_prefix = ""
    
    enable_raw_mode()
    try:
        sys.stdout.write(prompt_prefix)
        sys.stdout.flush()
        
        while True:
            buffer_str = "".join(buffer)
            suggestion = get_suggestion(buffer_str) if pos == len(buffer) else ""
            
            try:
                cols = os.get_terminal_size().columns
            except Exception:
                try:
                    cols = shutil.get_terminal_size().columns
                except Exception:
                    cols = 80
                    
            prompt_len = 2
            visible_width = max(10, cols - prompt_len - 4)
            
            start_idx, visible_chars, cursor_offset_width = calculate_visible_slice(buffer, pos, visible_width)
            buffer_visible_str = "".join(visible_chars)
            
            suggestion_visible = ""
            if suggestion:
                rem = visible_width - get_str_width(visible_chars)
                if rem > 0:
                    suggestion_visible_chars = []
                    sugg_w = 0
                    for c in suggestion:
                        char_w = get_char_width(c)
                        if sugg_w + char_w > rem:
                            break
                        suggestion_visible_chars.append(c)
                        sugg_w += char_w
                    suggestion_visible = "".join(suggestion_visible_chars)
                    
            suggestion_rendered = ""
            if suggestion_visible:
                suggestion_rendered = f"\033[90m{suggestion_visible}\033[0m"
                
            sys.stdout.write("\r" + prompt_prefix + buffer_visible_str + suggestion_rendered + "\033[K")
            
            visual_printed_width = get_str_width(visible_chars) + get_str_width(suggestion_visible)
            move_left = visual_printed_width - cursor_offset_width
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
                
            if ch == b'\x03':
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise KeyboardInterrupt
                
            elif ch == b'\x04':
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise EOFError
                
            elif ch == b'\x16':
                current_matches = []
                match_index = -1
                original_prefix = ""
                clip_text = get_clipboard_text()
                if clip_text:
                    clean_text = ""
                    for c in clip_text:
                        if ord(c) >= 32:
                            clean_text += c
                        elif c in ('\r', '\n', '\t'):
                            clean_text += ' '
                    for c in clean_text:
                        if len(buffer) < 1024 and check_arg_limit(buffer, c, pos):
                            buffer.insert(pos, c)
                            pos += 1
                        else:
                            break
                
            elif ch in (b'\r', b'\n'):
                disable_raw_mode()
                sys.stdout.write("\r" + prompt_prefix + buffer_str + "\033[K\n")
                sys.stdout.flush()
                return buffer_str
                
            elif ch in (b'\x08', b'\x7f'):
                current_matches = []
                match_index = -1
                original_prefix = ""
                if pos > 0:
                    buffer.pop(pos - 1)
                    pos -= 1
                    
            elif ch in KEY_DELETE:
                current_matches = []
                match_index = -1
                original_prefix = ""
                if pos < len(buffer):
                    buffer.pop(pos)
                    
            elif ch in (b'\t',):
                if current_matches:
                    match_index = (match_index + 1) % len(current_matches)
                else:
                    prefix_part, matches = get_all_matches(buffer_str)
                    if matches:
                        current_matches = matches
                        original_prefix = prefix_part
                        match_index = 0
                
                if current_matches:
                    completed_str = original_prefix + current_matches[match_index]
                    import shlex
                    try:
                        tokens = shlex.split(completed_str)
                        arg_ok = len(tokens) <= 64
                    except ValueError:
                        arg_ok = len(completed_str.split()) <= 64
                    if len(completed_str) <= 1024 and arg_ok:
                        buffer = list(completed_str)
                        pos = len(buffer)
                    
            elif ch in KEY_LEFT:
                current_matches = []
                match_index = -1
                original_prefix = ""
                if pos > 0:
                    pos -= 1
                    
            elif ch in KEY_RIGHT:
                current_matches = []
                match_index = -1
                original_prefix = ""
                if suggestion:
                    in_quote = None
                    last_space_idx = -1
                    quote_start_idx = -1
                    for i, c in enumerate(buffer_str):
                        if c == ' ' and in_quote is None:
                            last_space_idx = i
                        elif c in ('"', "'"):
                            if in_quote == c:
                                in_quote = None
                            elif in_quote is None:
                                in_quote = c
                                quote_start_idx = i
                                
                    if in_quote is not None:
                        prefix = buffer_str[:quote_start_idx]
                        last_word = buffer_str[quote_start_idx:]
                    else:
                        prefix = buffer_str[:last_space_idx+1]
                        last_word = buffer_str[last_space_idx+1:]
                    
                    full_word = last_word + suggestion
                    clean_word = full_word.strip('"\'')
                    if " " in clean_word:
                        completed_word = f'"{clean_word}"'
                    else:
                        completed_word = clean_word
                        
                    completed_str = prefix + completed_word
                    import shlex
                    try:
                        tokens = shlex.split(completed_str)
                        arg_ok = len(tokens) <= 64
                    except ValueError:
                        arg_ok = len(completed_str.split()) <= 64
                    if len(completed_str) <= 1024 and arg_ok:
                        buffer = list(completed_str)
                        pos = len(buffer)
                elif pos < len(buffer):
                    pos += 1
                    
            elif ch in KEY_UP:
                current_matches = []
                match_index = -1
                original_prefix = ""
                if history:
                    if history_index == len(history):
                        saved_buffer = buffer_str
                    if history_index > 0:
                        history_index -= 1
                        buffer = list(history[history_index])
                        pos = len(buffer)
                        
            elif ch in KEY_DOWN:
                current_matches = []
                match_index = -1
                original_prefix = ""
                if history_index < len(history):
                    history_index += 1
                    if history_index == len(history):
                        buffer = list(saved_buffer)
                    else:
                        buffer = list(history[history_index])
                    pos = len(buffer)
                    
            elif len(ch) >= 1:
                try:
                    decoded = ch.decode('utf-8')
                    if len(decoded) == 1:
                        c = decoded
                        if ord(c) >= 32 and ord(c) != 127:
                            current_matches = []
                            match_index = -1
                            original_prefix = ""
                            if len(buffer) < 1024 and check_arg_limit(buffer, c, pos):
                                buffer.insert(pos, c)
                                pos += 1
                except UnicodeDecodeError:
                    pass
    finally:
        disable_raw_mode()

def main():
    setup_terminal()
    clear_screen()
    print_splash_banner()
    print("  Ketik 'help' untuk daftar perintah, 'exit' untuk keluar.\n")
    
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
    
    try:
        while state['running']:
            try:
                if not first_prompt:
                    print()
                first_prompt = False
                
                raw_path = os.getcwd()
                formatted_path = raw_path.replace('\\', '/')
                home = os.path.expanduser("~").replace('\\', '/')
                if formatted_path.startswith(home):
                    formatted_path = "~" + formatted_path[len(home):]
                    
                debug_prefix = "\033[93m[DEBUG]\033[0m " if state['debug_mode'] else ""
                print(f"{debug_prefix}{COLOR_PROMPT_USER}{username}@{device}{COLOR_RESET} {COLOR_PROMPT_OS}CyanixOS{COLOR_RESET} {COLOR_PROMPT_DIR}{formatted_path}{COLOR_RESET}")
                
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
                    
                if state['debug_mode']:
                    print("\033[93m[DEBUG] Tokenized arguments:\033[0m")
                    for idx, arg in enumerate(args):
                        print(f"\033[93m  args[{idx}] = \"{arg}\"\033[0m")
                        
                add_to_history(history, raw_input)
                
                execute_command(args, state)
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                print()
                break
    finally:
        disable_raw_mode()
            
    sys.exit(0)

if __name__ == "__main__":
    main()