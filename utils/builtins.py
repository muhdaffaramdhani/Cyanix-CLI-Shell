import os
import sys
import subprocess
import datetime
from config import COLOR_LOGO, COLOR_RESET, enable_raw_mode, disable_raw_mode, clear_screen

def run_builtin_cd(args: list[str]) -> bool:
    target = args[1] if len(args) > 1 else os.path.expanduser("~")
    try:
        os.chdir(target)
    except FileNotFoundError:
        print(f"cynix: cd: {target}: No such file or directory")
    except NotADirectoryError:
        print(f"cynix: cd: {target}: Not a directory")
    except PermissionError:
        print(f"cynix: cd: {target}: Permission denied")
    except Exception as e:
        print(f"cynix: cd: {target}: {e}")
    return True

def run_builtin_pwd() -> bool:
    print(os.getcwd())
    return True

def run_builtin_help() -> bool:
    print()
    print(f"{COLOR_LOGO}Cynix-CLI-Shell (CyanSh) - Panduan Perintah:{COLOR_RESET}")
    print("  help      - Menampilkan menu bantuan.")
    print("  cd        - Mengubah direktori saat ini.")
    print("  pwd       - Menampilkan direktori saat ini.")
    print("  dir       - Menampilkan isi direktori saat ini.")
    print("  debug     - Mengaktifkan atau menonaktifkan mode debug.")
    print("  exit      - Keluar dari program shell.")
    print()
    return True

def run_builtin_debug(state: dict) -> bool:
    state['debug_mode'] = not state['debug_mode']
    if state['debug_mode']:
        print("Debug mode enabled.")
    else:
        print("Debug mode disabled.")
    return True

def run_builtin_dir(args: list[str]) -> bool:
    target_dir = args[1] if len(args) > 1 else "."
    try:
        abs_path = os.path.abspath(target_dir)
        if not os.path.isdir(abs_path):
            print(f"cynix: dir: {target_dir}: Not a directory")
            return True
            
        # Display directory with backslashes
        print(f"    Directory: {abs_path.replace('/', '\\')}")
        print()
        print(f"LastWriteTime             Length Name")
        print(f"-------------             ------ ----")
        
        items = os.listdir(abs_path)
        
        # Sort directories first, then files alphabetically (case-insensitive a-z)
        dirs = []
        files = []
        for name in items:
            full_path = os.path.join(abs_path, name)
            if os.path.isdir(full_path):
                dirs.append(name)
            else:
                files.append(name)
                
        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        
        def print_item(name, is_dir):
            full_path = os.path.join(abs_path, name)
            try:
                mtime = os.path.getmtime(full_path)
                dt = datetime.datetime.fromtimestamp(mtime)
                # Format: M/D/YYYY   H:MM PM/AM
                ampm = dt.strftime("%p")
                hour = dt.hour % 12
                if hour == 0:
                    hour = 12
                time_str = f"{dt.month}/{dt.day}/{dt.year}   {hour}:{dt.minute:02d} {ampm}"
                
                if is_dir:
                    len_str = ""
                else:
                    try:
                        size = os.path.getsize(full_path)
                        len_str = str(size)
                    except Exception:
                        len_str = "0"
                        
                print(f"{time_str:<22}{len_str:>10} {name}")
            except Exception:
                print(f"{'':<22}{'':>10} {name}")
                
        for d in dirs:
            print_item(d, is_dir=True)
        for f in files:
            print_item(f, is_dir=False)
            
    except Exception as e:
        print(f"cynix: dir: {e}")
        
    return True

def execute_command(args: list[str], state: dict) -> bool:
    cmd = args[0]
    
    if cmd == "exit":
        state['running'] = False
        return True
        
    elif cmd == "help":
        return run_builtin_help()
        
    elif cmd == "pwd":
        return run_builtin_pwd()
        
    elif cmd == "cd":
        return run_builtin_cd(args)
        
    elif cmd == "dir":
        return run_builtin_dir(args)
        
    elif cmd == "debug":
        return run_builtin_debug(state)
        
    elif cmd in ("cls", "clear"):
        clear_screen()
        return True
        
    # Drive change shortcut (e.g. c:, d:, e:)
    elif len(cmd) == 2 and cmd[1] == ':' and cmd[0].isalpha():
        drive = cmd.upper() + "/"
        try:
            os.chdir(drive)
        except Exception as e:
            print(f"cynix: cd: {drive}: {e}")
        return True
        
    else:
        # Suspend raw mode while external command runs so it has sane terminal I/O
        disable_raw_mode()
        try:
            try:
                subprocess.run(args, shell=False)
            except FileNotFoundError:
                subprocess.run(args, shell=True)
        except KeyboardInterrupt:
            print()
        except Exception as e:
            print(f"cynix: command execution error: {e}")
        finally:
            # Resume raw mode
            enable_raw_mode()
        return True
