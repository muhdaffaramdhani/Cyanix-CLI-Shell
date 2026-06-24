import os
import sys
import subprocess
import datetime
import shutil
from config import COLOR_LOGO, COLOR_RESET, enable_raw_mode, disable_raw_mode, clear_screen

def run_builtin_cd(args: list[str]) -> bool:
    target = args[1] if len(args) > 1 else os.path.expanduser("~")
    try:
        os.chdir(target)
    except FileNotFoundError:
        print(f"cynix: cd: {target}: Direktori atau file tidak ditemukan")
    except NotADirectoryError:
        print(f"cynix: cd: {target}: Bukan sebuah direktori")
    except PermissionError:
        print(f"cynix: cd: {target}: Akses ditolak")
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
    print("  mkdir     - Membuat direktori baru.")
    print("  touch     - Membuat file baru.")
    print("  cat       - Menampilkan isi file.")
    print("  grep      - Mencari teks/pattern dalam file.")
    print("  cp        - Menyalin file atau folder.")
    print("  mv        - Memindahkan atau mengubah nama file/folder.")
    print("  rm        - Menghapus file atau folder.")
    print("  clear/cls - Membersihkan terminal.")
    print("  debug     - Mengaktifkan/menonaktifkan mode debug.")
    print("  exit      - Keluar dari program shell.")
    return True

def run_builtin_debug(state: dict) -> bool:
    state['debug_mode'] = not state['debug_mode']
    if state['debug_mode']:
        print("Debug mode enabled.")
    else:
        print("Debug mode disabled.")
    return True

def run_builtin_dir(args: list[str]) -> bool:
    flags = []
    targets = []
    for arg in args[1:]:
        if arg.startswith('-'):
            flags.append(arg)
        else:
            targets.append(arg)
            
    show_all = False
    for f in flags:
        if f == '-a':
            show_all = True
        else:
            print("dir: error: flag tidak valid.")
            return True
            
    target_dir = targets[0] if targets else "."
    
    try:
        abs_path = os.path.abspath(target_dir)
        if not os.path.isdir(abs_path):
            print(f"cynix: dir: {target_dir}: Bukan sebuah direktori")
            return True
            
        try:
            items = os.listdir(abs_path)
        except Exception as e:
            display_path = abs_path
            if os.name == 'nt':
                display_path = display_path.replace('/', '\\')
            print(f"    Directory: {display_path}")
            print(f"    cynix: dir: tidak dapat membuka: {e}")
            print()
            return True
            
        display_path = abs_path
        if os.name == 'nt':
            display_path = display_path.replace('/', '\\')
        print(f"    Directory: {display_path}")
        print()
        print(f"LastWriteTime             Length Name")
        print(f"-------------             ------ ----")
        
        dirs = []
        files = []
        for name in items:
            if name.startswith('.') and not show_all:
                continue
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
        print()
            
    except Exception as e:
        print(f"cynix: dir: {e}")
        
    return True

def run_builtin_touch(args: list[str]) -> bool:
    if len(args) < 2:
        print("cynix: touch: kekurangan operand. Penggunaan: touch [nama_file]")
        return True
    for target in args[1:]:
        try:
            with open(target, 'a'):
                os.utime(target, None)
        except FileNotFoundError:
            print(f"cynix: touch: tidak dapat membuat file '{target}': Direktori induk tidak ditemukan")
        except PermissionError:
            print(f"cynix: touch: tidak dapat membuat file '{target}': Akses ditolak")
        except Exception as e:
            print(f"cynix: touch: tidak dapat membuat file '{target}': {e}")
    return True

def run_builtin_mkdir(args: list[str]) -> bool:
    if len(args) < 2:
        print("cynix: mkdir: kekurangan operand. Penggunaan: mkdir [nama_folder]")
        return True
    for target in args[1:]:
        try:
            os.makedirs(target, exist_ok=True)
        except FileNotFoundError:
            print(f"cynix: mkdir: tidak dapat membuat direktori '{target}': Direktori induk tidak ditemukan")
        except PermissionError:
            print(f"cynix: mkdir: tidak dapat membuat direktori '{target}': Akses ditolak")
        except Exception as e:
            print(f"cynix: mkdir: tidak dapat membuat direktori '{target}': {e}")
    return True

def run_builtin_cat(args: list[str]) -> bool:
    if len(args) < 2:
        print("cynix: cat: kekurangan operand. Penggunaan: cat [nama_file.txt]")
        return True
    for target in args[1:]:
        try:
            if os.path.isdir(target):
                print(f"cat: error: {target} adalah sebuah direktori.")
                continue
            with open(target, 'r', encoding='utf-8') as f:
                print(f.read(), end='')
        except FileNotFoundError:
            print(f"cat: error: {target} tidak ditemukan.")
        except PermissionError:
            print(f"cat: error: akses ditolak untuk membaca {target}.")
        except Exception as e:
            print(f"cat: error: gagal membaca file: {e}")
    return True

def run_builtin_cp(args: list[str]) -> bool:
    flags = []
    targets = []
    for arg in args[1:]:
        if arg.startswith('-'):
            flags.append(arg)
        else:
            targets.append(arg)
            
    recursive = False
    for f in flags:
        if 'r' in f:
            recursive = True
            
    if not targets:
        print("cynix: cp: kekurangan operand. Penggunaan: cp [file_sumber] [file_tujuan] ATAU cp -r [folder_sumber] [folder_tujuan]")
        return True
    if len(targets) < 2:
        print("cynix: cp: kekurangan tujuan. Penggunaan: cp [file_sumber] [file_tujuan] ATAU cp -r [folder_sumber] [folder_tujuan]")
        return True
        
    sumber = targets[0]
    tujuan = targets[1]
    
    try:
        if os.path.isdir(sumber) and not os.path.islink(sumber):
            if not recursive:
                print(f"cp: error: {sumber} adalah direktori. Gunakan flag '-r' untuk menyalin folder.")
                return True
            shutil.copytree(sumber, tujuan)
        else:
            if os.path.isdir(tujuan):
                tujuan = os.path.join(tujuan, os.path.basename(sumber))
            shutil.copy2(sumber, tujuan)
    except FileNotFoundError:
        print(f"cp: error: {sumber} tidak ditemukan.")
    except PermissionError:
        print(f"cp: error: akses ditolak.")
    except Exception as e:
        print(f"cp: error: {e}")
    return True

def run_builtin_mv(args: list[str]) -> bool:
    flags = []
    targets = []
    for arg in args[1:]:
        if arg.startswith('-'):
            flags.append(arg)
        else:
            targets.append(arg)
            
    if not targets:
        print("cynix: mv: kekurangan operand. Penggunaan: mv [sumber] [tujuan]")
        return True
    if len(targets) < 2:
        print("cynix: mv: kekurangan tujuan. Penggunaan: mv [sumber] [tujuan]")
        return True
        
    sumber = targets[0]
    tujuan = targets[1]
    
    try:
        shutil.move(sumber, tujuan)
    except FileNotFoundError:
        print(f"mv: error: {sumber} tidak ditemukan.")
    except PermissionError:
        print(f"mv: error: akses ditolak.")
    except Exception as e:
        print(f"mv: error: {e}")
    return True

def run_builtin_rm(args: list[str]) -> bool:
    flags = []
    targets = []
    for arg in args[1:]:
        if arg.startswith('-'):
            flags.append(arg)
        else:
            targets.append(arg)
            
    recursive = False
    for f in flags:
        if 'r' in f:
            recursive = True
            
    if not targets:
        print("cynix: rm: kekurangan operand. Penggunaan: rm [nama_file.txt] ATAU rm -r [nama_folder]")
        return True
        
    for target in targets:
        try:
            if not os.path.exists(target):
                if os.path.islink(target):
                    os.remove(target)
                else:
                    print(f"rm: error: {target} tidak ditemukan.")
                continue
                
            if os.path.isdir(target) and not os.path.islink(target):
                if not recursive:
                    print(f"rm: error: {target} adalah direktori. Gunakan flag '-r' untuk menghapus.")
                else:
                    shutil.rmtree(target)
            else:
                os.remove(target)
        except FileNotFoundError:
            print(f"rm: error: {target} tidak ditemukan.")
        except PermissionError:
            print(f"rm: error: akses ditolak.")
        except Exception as e:
            print(f"rm: error: {e}")
    return True

def split_pipeline(args: list[str]) -> list[list[str]]:
    commands = []
    current_cmd = []
    for arg in args:
        if arg == '|':
            if not current_cmd:
                raise ValueError("cynix: error: syntax error near unexpected token '|'")
            commands.append(current_cmd)
            current_cmd = []
        else:
            current_cmd.append(arg)
    if not current_cmd:
        if commands:
            raise ValueError("cynix: error: syntax error near unexpected token '|'")
    else:
        commands.append(current_cmd)
    return commands

def parse_redirection(cmd_args: list[str]) -> tuple:
    clean_args = []
    input_file = None
    output_file = None
    i = 0
    while i < len(cmd_args):
        if cmd_args[i] == '<':
            if i + 1 < len(cmd_args):
                input_file = cmd_args[i+1]
                i += 2
            else:
                raise ValueError("cynix: error: syntax error near unexpected token '<'")
        elif cmd_args[i] == '>':
            if i + 1 < len(cmd_args):
                output_file = cmd_args[i+1]
                i += 2
            else:
                raise ValueError("cynix: error: syntax error near unexpected token '>'")
        else:
            clean_args.append(cmd_args[i])
            i += 1
    return clean_args, input_file, output_file

BUILTINS = {"cd", "pwd", "help", "dir", "mkdir", "touch", "cat", "cp", "mv", "rm", "debug", "cls", "clear", "grep", "exit"}
def is_builtin(cmd: str) -> bool:
    if cmd in BUILTINS:
        return True
    if len(cmd) == 2 and cmd[1] == ':' and cmd[0].isalpha():
        return True
    return False

def run_builtin_grep(args: list[str]) -> bool:
    flags = []
    pos_args = []
    
    # Parse arguments into flags and positional arguments
    for arg in args[1:]:
        if arg.startswith('-') and len(arg) > 1:
            flags.append(arg)
        else:
            pos_args.append(arg)
            
    # Deconstruct flags
    case_insensitive = False
    recursive = False
    line_number = False
    
    for f in flags:
        for char in f[1:]:
            if char == 'i':
                case_insensitive = True
            elif char in ('r', 'R'):
                recursive = True
            elif char == 'n':
                line_number = True
            else:
                print(f"grep: error: opsi tidak valid -- '{char}'")
                return True
                
    if not pos_args:
        print("cynix: grep: kekurangan pattern pencarian. Penggunaan: grep [opsi] \"pattern\" [file...]")
        return True
        
    pattern = pos_args[0]
    files = pos_args[1:]
    
    def match_line(line_content: str, pat: str, case_ins: bool) -> bool:
        if case_ins:
            return pat.lower() in line_content.lower()
        return pat in line_content

    # If no files are specified, and recursive is not enabled, read from stdin
    if not files and not recursive:
        try:
            line_idx = 1
            for line in sys.stdin:
                clean_line = line.rstrip('\r\n')
                if match_line(clean_line, pattern, case_insensitive):
                    if line_number:
                        print(f"{line_idx}:{clean_line}")
                    else:
                        print(clean_line)
                line_idx += 1
        except Exception as e:
            print(f"grep: error membaca stdin: {e}")
        return True

    # Otherwise, resolve files/directories to search
    search_paths = files if files else ["."]
    files_to_search = []
    
    if recursive:
        for path in search_paths:
            if os.path.isdir(path):
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        files_to_search.append(full_path)
            elif os.path.isfile(path):
                files_to_search.append(path)
            else:
                print(f"grep: error: {path} tidak ditemukan.")
    else:
        for path in search_paths:
            if os.path.isdir(path):
                print(f"grep: error: {path} adalah direktori.")
            elif os.path.exists(path):
                files_to_search.append(path)
            else:
                print(f"grep: error: {path} tidak ditemukan.")

    print_filename = recursive or (len(files) > 1)

    for filepath in files_to_search:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_idx, line in enumerate(f, 1):
                    clean_line = line.rstrip('\r\n')
                    if match_line(clean_line, pattern, case_insensitive):
                        prefix = ""
                        if print_filename:
                            prefix += filepath.replace('\\', '/') + ":"
                        if line_number:
                            prefix += f"{line_idx}:"
                        print(f"{prefix}{clean_line}")
        except PermissionError:
            sys.stderr.write(f"grep: {filepath}: Akses ditolak\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"grep: {filepath}: {e}\n")
            sys.stderr.flush()

    return True

def execute_single_command(args: list[str], state: dict) -> bool:
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
        
    elif cmd == "mkdir":
        return run_builtin_mkdir(args)
        
    elif cmd == "touch":
        return run_builtin_touch(args)
        
    elif cmd == "cat":
        return run_builtin_cat(args)
        
    elif cmd == "cp":
        return run_builtin_cp(args)
        
    elif cmd == "mv":
        return run_builtin_mv(args)
        
    elif cmd == "rm":
        return run_builtin_rm(args)
        
    elif cmd == "grep":
        return run_builtin_grep(args)
        
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
            if hasattr(os, 'fork'):
                pid = os.fork()
                if pid == 0:
                    import signal
                    signal.signal(signal.SIGINT, signal.SIG_DFL)
                    try:
                        os.execvp(args[0], args)
                    except FileNotFoundError:
                        sys.stderr.write(f"cynix: perintah tidak ditemukan: {args[0]}\n")
                        sys.stderr.flush()
                        os._exit(127)
                    except Exception as e:
                        sys.stderr.write(f"cynix: eksekusi gagal: {e}\n")
                        sys.stderr.flush()
                        os._exit(1)
                else:
                    import signal
                    old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
                    try:
                        _, status = os.waitpid(pid, 0)
                    finally:
                        signal.signal(signal.SIGINT, old_handler)
            else:
                try:
                    subprocess.run(args, shell=False)
                except FileNotFoundError:
                    try:
                        res = subprocess.run(args, shell=True, capture_output=True, text=True)
                        if res.returncode != 0 and ("is not recognized" in res.stderr or "tidak dikenali" in res.stderr or "FileNotFoundError" in res.stderr):
                            print(f"'{args[0]}' tidak dikenali sebagai perintah internal atau eksternal, program yang dapat dijalankan, atau file batch.")
                        else:
                            if res.stdout:
                                print(res.stdout, end="")
                            if res.stderr:
                                print(res.stderr, end="", file=sys.stderr)
                    except Exception:
                        print(f"'{args[0]}' tidak dikenali sebagai perintah internal atau eksternal, program yang dapat dijalankan, atau file batch.")
        except KeyboardInterrupt:
            print()
        except Exception as e:
            print(f"cynix: kesalahan eksekusi perintah: {e}")
        finally:
            enable_raw_mode()
        return True

def execute_command(args: list[str], state: dict) -> bool:
    try:
        commands = split_pipeline(args)
    except ValueError as e:
        print(e)
        return True

    if len(commands) == 0:
        return True

    # Check if POSIX fork-exec piping is available
    if hasattr(os, 'fork'):
        if len(commands) == 1:
            # Single command
            cmd_tokens = commands[0]
            try:
                clean_cmd, cmd_in_file, cmd_out_file = parse_redirection(cmd_tokens)
            except ValueError as e:
                print(e)
                return True
                
            if not clean_cmd:
                return True
                
            cmd_name = clean_cmd[0]
            if is_builtin(cmd_name):
                # Run built-in in the parent process
                saved_stdin_fd = None
                saved_stdout_fd = None
                fd_in = None
                fd_out = None
                
                try:
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    if cmd_in_file:
                        try:
                            fd_in = os.open(cmd_in_file, os.O_RDONLY)
                            saved_stdin_fd = os.dup(0)
                            os.dup2(fd_in, 0)
                            os.close(fd_in)
                            fd_in = None
                        except FileNotFoundError:
                            print(f"cynix: error: {cmd_in_file}: No such file or directory")
                            return True
                        except Exception as e:
                            print(f"cynix: error: {cmd_in_file}: {e}")
                            return True
                            
                    if cmd_out_file:
                        try:
                            fd_out = os.open(cmd_out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o666)
                            saved_stdout_fd = os.dup(1)
                            os.dup2(fd_out, 1)
                            os.close(fd_out)
                            fd_out = None
                        except Exception as e:
                            print(f"cynix: error: {cmd_out_file}: {e}")
                            if saved_stdin_fd is not None:
                                os.dup2(saved_stdin_fd, 0)
                                os.close(saved_stdin_fd)
                            return True
                            
                    execute_single_command(clean_cmd, state)
                    sys.stdout.flush()
                    sys.stderr.flush()
                finally:
                    if saved_stdin_fd is not None:
                        os.dup2(saved_stdin_fd, 0)
                        os.close(saved_stdin_fd)
                    if saved_stdout_fd is not None:
                        os.dup2(saved_stdout_fd, 1)
                        os.close(saved_stdout_fd)
                return True
            else:
                # Fork and execute single external command
                disable_raw_mode()
                try:
                    pid = os.fork()
                    if pid == 0:
                        import signal
                        signal.signal(signal.SIGINT, signal.SIG_DFL)
                        
                        if cmd_in_file:
                            try:
                                fd_in = os.open(cmd_in_file, os.O_RDONLY)
                                os.dup2(fd_in, 0)
                                os.close(fd_in)
                            except FileNotFoundError:
                                sys.stderr.write(f"cynix: error: {cmd_in_file}: No such file or directory\n")
                                sys.stderr.flush()
                                os._exit(1)
                            except Exception as e:
                                sys.stderr.write(f"cynix: error: {cmd_in_file}: {e}\n")
                                sys.stderr.flush()
                                os._exit(1)
                                
                        if cmd_out_file:
                            try:
                                fd_out = os.open(cmd_out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o666)
                                os.dup2(fd_out, 1)
                                os.close(fd_out)
                            except Exception as e:
                                sys.stderr.write(f"cynix: error: {cmd_out_file}: {e}\n")
                                sys.stderr.flush()
                                os._exit(1)
                                
                        try:
                            os.execvp(cmd_name, clean_cmd)
                        except FileNotFoundError:
                            sys.stderr.write(f"cynix: perintah tidak ditemukan: {cmd_name}\n")
                            sys.stderr.flush()
                            os._exit(127)
                        except Exception as e:
                            sys.stderr.write(f"cynix: eksekusi gagal: {e}\n")
                            sys.stderr.flush()
                            os._exit(1)
                    else:
                        import signal
                        old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
                        try:
                            _, status = os.waitpid(pid, 0)
                        finally:
                            signal.signal(signal.SIGINT, old_handler)
                except KeyboardInterrupt:
                    print()
                except Exception as e:
                    print(f"cynix: kesalahan eksekusi perintah: {e}")
                finally:
                    enable_raw_mode()
                return True
        else:
            # Multi-command pipeline on POSIX
            disable_raw_mode()
            pids = []
            prev_read = None
            
            try:
                for idx, cmd_tokens in enumerate(commands):
                    is_last = (idx == len(commands) - 1)
                    r, w = None, None
                    if not is_last:
                        r, w = os.pipe()
                        
                    pid = os.fork()
                    if pid == 0:
                        import signal
                        signal.signal(signal.SIGINT, signal.SIG_DFL)
                        
                        if idx > 0:
                            os.dup2(prev_read, 0)
                            os.close(prev_read)
                            
                        if not is_last:
                            os.dup2(w, 1)
                            os.close(w)
                            os.close(r)
                            
                        try:
                            clean_cmd, cmd_in_file, cmd_out_file = parse_redirection(cmd_tokens)
                        except ValueError as e:
                            sys.stderr.write(f"{e}\n")
                            sys.stderr.flush()
                            os._exit(1)
                            
                        if cmd_in_file:
                            try:
                                fd_in = os.open(cmd_in_file, os.O_RDONLY)
                                os.dup2(fd_in, 0)
                                os.close(fd_in)
                            except FileNotFoundError:
                                sys.stderr.write(f"cynix: error: {cmd_in_file}: No such file or directory\n")
                                sys.stderr.flush()
                                os._exit(1)
                            except Exception as e:
                                sys.stderr.write(f"cynix: error: {cmd_in_file}: {e}\n")
                                sys.stderr.flush()
                                os._exit(1)
                                
                        if cmd_out_file:
                            try:
                                fd_out = os.open(cmd_out_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o666)
                                os.dup2(fd_out, 1)
                                os.close(fd_out)
                            except Exception as e:
                                sys.stderr.write(f"cynix: error: {cmd_out_file}: {e}\n")
                                sys.stderr.flush()
                                os._exit(1)
                                
                        cmd_name = clean_cmd[0]
                        if is_builtin(cmd_name):
                            try:
                                execute_single_command(clean_cmd, state)
                                sys.stdout.flush()
                                sys.stderr.flush()
                                os._exit(0)
                            except Exception as e:
                                sys.stderr.write(f"cynix: {cmd_name}: error: {e}\n")
                                sys.stderr.flush()
                                os._exit(1)
                        else:
                            try:
                                os.execvp(cmd_name, clean_cmd)
                            except FileNotFoundError:
                                sys.stderr.write(f"cynix: perintah tidak ditemukan: {cmd_name}\n")
                                sys.stderr.flush()
                                os._exit(127)
                            except Exception as e:
                                sys.stderr.write(f"cynix: eksekusi gagal: {e}\n")
                                sys.stderr.flush()
                                os._exit(1)
                    else:
                        pids.append(pid)
                        if idx > 0:
                            os.close(prev_read)
                        if not is_last:
                            os.close(w)
                            prev_read = r
                            
                import signal
                old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
                try:
                    for p in pids:
                        os.waitpid(p, 0)
                finally:
                    signal.signal(signal.SIGINT, old_handler)
            except KeyboardInterrupt:
                print()
            except Exception as e:
                print(f"cynix: kesalahan eksekusi pipeline: {e}")
            finally:
                enable_raw_mode()
            return True
            
    else:
        # Windows Fallback Implementation (no os.fork)
        input_data = None
        
        for idx, cmd_tokens in enumerate(commands):
            try:
                clean_cmd, cmd_in_file, cmd_out_file = parse_redirection(cmd_tokens)
            except ValueError as e:
                print(e)
                return True
                
            if not clean_cmd:
                return True
                
            if cmd_in_file:
                try:
                    with open(cmd_in_file, 'r', encoding='utf-8') as f:
                        cmd_stdin_data = f.read()
                except FileNotFoundError:
                    print(f"cynix: error: {cmd_in_file}: No such file or directory")
                    return True
                except Exception as e:
                    print(f"cynix: error: {cmd_in_file}: {e}")
                    return True
            elif input_data is not None:
                cmd_stdin_data = input_data
            else:
                cmd_stdin_data = None
                
            is_last = (idx == len(commands) - 1)
            cmd_name = clean_cmd[0]
            
            if is_builtin(cmd_name):
                import io
                saved_stdin = sys.stdin
                saved_stdout = sys.stdout
                
                if cmd_stdin_data is not None:
                    sys.stdin = io.StringIO(cmd_stdin_data)
                else:
                    if idx > 0:
                        sys.stdin = io.StringIO("")
                        
                captured_stdout = io.StringIO()
                sys.stdout = captured_stdout
                
                try:
                    execute_single_command(clean_cmd, state)
                finally:
                    sys.stdin = saved_stdin
                    sys.stdout = saved_stdout
                    
                cmd_stdout_data = captured_stdout.getvalue()
            else:
                try:
                    disable_raw_mode()
                    
                    stdin_val = None
                    if cmd_stdin_data is not None:
                        stdin_val = subprocess.PIPE
                        
                    stdout_val = subprocess.PIPE
                    if is_last and not cmd_out_file:
                        stdout_val = None
                        
                    p = subprocess.Popen(clean_cmd, stdin=stdin_val, stdout=stdout_val, stderr=subprocess.PIPE, text=True, shell=False)
                    
                    if stdin_val is not None:
                        out_data, err_data = p.communicate(input=cmd_stdin_data)
                    else:
                        out_data, err_data = p.communicate()
                        
                    if err_data:
                        sys.stderr.write(err_data)
                        sys.stderr.flush()
                        
                    cmd_stdout_data = out_data if stdout_val is not None else ""
                except FileNotFoundError:
                    try:
                        stdin_val = subprocess.PIPE if cmd_stdin_data is not None else None
                        stdout_val = subprocess.PIPE if (not is_last or cmd_out_file) else None
                        p = subprocess.Popen(clean_cmd, stdin=stdin_val, stdout=stdout_val, stderr=subprocess.PIPE, text=True, shell=True)
                        if stdin_val is not None:
                            out_data, err_data = p.communicate(input=cmd_stdin_data)
                        else:
                            out_data, err_data = p.communicate()
                        if err_data:
                            sys.stderr.write(err_data)
                            sys.stderr.flush()
                        cmd_stdout_data = out_data if stdout_val is not None else ""
                    except Exception as e:
                        print(f"'{cmd_name}' tidak dikenali sebagai perintah internal atau eksternal, program yang dapat dijalankan, atau file batch.")
                        cmd_stdout_data = ""
                except Exception as e:
                    print(f"cynix: kesalahan eksekusi perintah: {e}")
                    cmd_stdout_data = ""
                finally:
                    enable_raw_mode()
                    
            if cmd_out_file:
                try:
                    with open(cmd_out_file, 'w', encoding='utf-8') as f:
                        f.write(cmd_stdout_data)
                except Exception as e:
                    print(f"cynix: error: {cmd_out_file}: {e}")
                    return True
                input_data = ""
            else:
                input_data = cmd_stdout_data
                
            if is_last and cmd_stdout_data and not cmd_out_file:
                if is_builtin(cmd_name):
                    sys.stdout.write(cmd_stdout_data)
                    sys.stdout.flush()
                    
        return True
