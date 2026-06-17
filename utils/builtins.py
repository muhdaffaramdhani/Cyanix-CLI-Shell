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
