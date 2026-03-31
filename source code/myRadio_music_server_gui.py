import argparse
import os
import sys
import time
import random
import pathlib
import http.server
import socketserver
import threading
import socket
import subprocess
from urllib.parse import quote
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

try:
    import winreg
except Exception:
    winreg = None


# ------------------------------------------------------------------
# ORIGINAL WORKING CLI SERVER CODE
# kept functionally the same, only wrapped into cli_server_main()
# ------------------------------------------------------------------

def list_mp3_files(root: pathlib.Path):
    files = []
    for p in root.rglob("*.mp3"):
        if p.is_file():
            files.append(p)
    files.sort(key=lambda x: str(x).lower())
    return files


def make_url(ip, port, relpath):
    rel = str(relpath).replace('\\', '/').lstrip('/')
    rel_enc = quote(rel, safe="/().-_~")
    return f"http://{ip}:{port}/{rel_enc}"


def write_playlists(root: pathlib.Path, ip: str, port: int):
    mp3s = list_mp3_files(root)
    urls = [make_url(ip, port, p.relative_to(root)) for p in mp3s]

    (root / "playlist.m3u").write_text("#EXTM3U\n" + "\n".join(urls) + "\n", encoding="utf-8-sig")

    shuf = urls[:]
    random.shuffle(shuf)
    (root / "playlist_shuffle.m3u").write_text("#EXTM3U\n" + "\n".join(shuf) + "\n", encoding="utf-8-sig")

    outdir = root / "album_playlists"
    outdir.mkdir(exist_ok=True)
    groups = defaultdict(list)
    for u, p in zip(urls, mp3s):
        rel = p.relative_to(root).parts
        album = rel[0] if len(rel) >= 2 else "_root"
        groups[album].append(u)

    for old in outdir.glob("*.m3u"):
        old.unlink(missing_ok=True)

    for album, tracks in sorted(groups.items(), key=lambda kv: kv[0].lower()):
        safe = "".join(ch if ch.isalnum() or ch in "_- " else "_" for ch in album).strip().replace(" ", "_")
        (outdir / f"{safe}.m3u").write_text("#EXTM3U\n" + "\n".join(tracks) + "\n", encoding="utf-8-sig")

    return len(mp3s), len(groups)


def start_http(root: pathlib.Path, port: int):
    os.chdir(root)
    handler = http.server.SimpleHTTPRequestHandler

    class ThreadingTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    httpd = ThreadingTCPServer(("", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def cli_server_main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("music_dir", help="Music folder to serve (will also store playlists here)")
    ap.add_argument("--ip", default="192.168.31.101", help="IP address your ESP32 will use to reach the PC")
    ap.add_argument("--port", type=int, default=8000, help="HTTP port")
    ap.add_argument("--interval", type=int, default=10, help="Rescan interval seconds (auto-refresh)")
    ap.add_argument("--lang", default="en", choices=["hu", "en"], help="Log language")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.music_dir).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Folder not found: {root}")

    if args.lang == "hu":
        msg_http = f"HTTP szerver: http://{args.ip}:{args.port}/"
        msg_playlist = "A lejátszási listák ugyanebbe a mappába kerülnek."
        msg_stop = "Leállítás: Ctrl+C"
    else:
        msg_http = f"HTTP server: http://{args.ip}:{args.port}/"
        msg_playlist = "Playlists will be generated into the same folder."
        msg_stop = "Press Ctrl+C to stop."

    httpd = start_http(root, args.port)
    print(msg_http, flush=True)
    print(msg_playlist, flush=True)
    print(msg_stop, flush=True)

    last_sig = None
    try:
        while True:
            mp3s = list_mp3_files(root)
            newest = max((p.stat().st_mtime for p in mp3s), default=0)
            sig = (len(mp3s), newest)
            if sig != last_sig:
                n_tracks, n_albums = write_playlists(root, args.ip, args.port)
                if args.lang == "hu":
                    print(f"[frissítve] számok={n_tracks} albumok={n_albums}", flush=True)
                else:
                    print(f"[updated] tracks={n_tracks} albums={n_albums}", flush=True)
                last_sig = sig
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()


# ------------------------------------------------------------------
# GUI
# ------------------------------------------------------------------

TEXT = {
    "hu": {
        "title": "myRadio Music Server",
        "language": "Nyelv",
        "folder": "Zene mappa",
        "browse": "Tallózás",
        "detect_ip": "IP felismerése",
        "ip": "IP cím",
        "port": "Port",
        "interval": "Frissítési időköz (mp)",
        "interval_hint": "0 = csak induláskor frissít",
        "start": "Indítás",
        "stop": "Leállítás",
        "server_url": "Szerver URL",
        "playlist_url": "Playlist URL",
        "shuffle_url": "Shuffle URL",
        "copy": "Másolás",
        "log": "Napló",
        "ready": "Kész.",
        "server_started": "Szerver elindult.",
        "server_stopped": "Szerver leállt.",
        "folder_missing": "A kiválasztott mappa nem található.",
        "folder_required": "Válassz ki egy zene mappát.",
        "invalid_port": "A portnak 1 és 65535 közé kell esnie.",
        "invalid_interval": "A frissítési időköz nem lehet negatív.",
        "already_running": "A szerver már fut.",
        "not_running": "A szerver nem fut.",
        "copied": "Vágólapra másolva.",
        "error": "Hiba",
        "status_running": "Állapot: fut",
        "status_stopped": "Állapot: leállítva",
        "build_info": "Az URL-eket a rádióban használd.",
        "footer_text": "myRadio Music Server by gidano",
    },
    "en": {
        "title": "myRadio Music Server",
        "language": "Language",
        "folder": "Music folder",
        "browse": "Browse",
        "detect_ip": "Detect IP",
        "ip": "IP address",
        "port": "Port",
        "interval": "Rescan interval (sec)",
        "interval_hint": "0 = refresh only at startup",
        "start": "Start",
        "stop": "Stop",
        "server_url": "Server URL",
        "playlist_url": "Playlist URL",
        "shuffle_url": "Shuffle URL",
        "copy": "Copy",
        "log": "Log",
        "ready": "Ready.",
        "server_started": "Server started.",
        "server_stopped": "Server stopped.",
        "folder_missing": "The selected folder was not found.",
        "folder_required": "Please choose a music folder.",
        "invalid_port": "Port must be between 1 and 65535.",
        "invalid_interval": "Rescan interval cannot be negative.",
        "already_running": "Server is already running.",
        "not_running": "Server is not running.",
        "copied": "Copied to clipboard.",
        "error": "Error",
        "status_running": "Status: running",
        "status_stopped": "Status: stopped",
        "build_info": "Use the URLs in your radio.",
        "footer_text": "myRadio Music Server by gidano",
    },
}


def resource_path(relative_path: str) -> pathlib.Path:
    if hasattr(sys, "_MEIPASS"):
        return pathlib.Path(sys._MEIPASS) / relative_path
    return pathlib.Path(__file__).resolve().parent / relative_path


def get_windows_is_dark() -> bool:
    if winreg is None:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class MusicServerApp:
    def __init__(self, root):
        self.root = root
        self.lang = "hu"
        self.server_process = None
        self.reader_thread = None
        self.footer_icon = None
        self.is_dark = get_windows_is_dark()
        self._skip_traceback = False

        self.folder_var = tk.StringVar()
        self.ip_var = tk.StringVar(value=get_local_ip())
        self.port_var = tk.StringVar(value="8000")
        self.interval_var = tk.StringVar(value="10")
        self.server_url_var = tk.StringVar()
        self.playlist_url_var = tk.StringVar()
        self.shuffle_url_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.root.title(TEXT[self.lang]["title"])
        self.root.geometry("780x660")
        self.root.minsize(780, 660)
        self.set_window_icon()
        self.apply_theme()

        self.build_ui()
        self.refresh_texts()
        self.update_urls()
        self.log(self.tr("ready"))
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def tr(self, key):
        return TEXT[self.lang][key]

    def set_window_icon(self):
        try:
            ico_path = resource_path("music_server.ico")
            if ico_path.exists():
                self.root.iconbitmap(default=str(ico_path))
        except Exception:
            pass

    def apply_theme(self):
        bg = "#202020" if self.is_dark else "#f0f0f0"
        fg = "#f2f2f2" if self.is_dark else "#111111"
        entry_bg = "#2b2b2b" if self.is_dark else "#ffffff"
        entry_fg = "#f2f2f2" if self.is_dark else "#111111"

        self.root.configure(bg=bg)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        style.configure("TButton", padding=6)
        style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg)
        style.configure("App.TCombobox", fieldbackground=entry_bg, foreground=entry_fg, arrowsize=18, padding=3)
        style.map(
            "App.TCombobox",
            fieldbackground=[("readonly", entry_bg)],
            foreground=[("readonly", entry_fg)],
            selectbackground=[("readonly", entry_bg)],
            selectforeground=[("readonly", entry_fg)],
            background=[("readonly", bg)],
        )

    def build_ui(self):
        pad = {"padx": 10, "pady": 6}

        self.footer_frame = tk.Frame(
            self.root,
            height=42,
            bg=("#1a1a1a" if self.is_dark else "#e9e9e9"),
            bd=1,
            relief="sunken"
        )
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.footer_frame.pack_propagate(False)

        self.footer_right = tk.Frame(
            self.footer_frame,
            bg=("#1a1a1a" if self.is_dark else "#e9e9e9")
        )
        self.footer_right.pack(side="right", padx=10, pady=8)

        try:
            png_path = resource_path("music_server.png")
            if png_path.exists():
                self.footer_icon = tk.PhotoImage(file=str(png_path))
        except Exception:
            self.footer_icon = None

        footer_fg = "#f2f2f2" if self.is_dark else "#111111"
        footer_bg = "#1a1a1a" if self.is_dark else "#e9e9e9"

        self.footer_icon_label = tk.Label(self.footer_right, bg=footer_bg, fg=footer_fg)
        self.footer_icon_label.pack(side="left", padx=(0, 6))

        self.footer_text_label = tk.Label(self.footer_right, bg=footer_bg, fg=footer_fg)
        self.footer_text_label.pack(side="left")

        content = ttk.Frame(self.root)
        content.pack(side="top", fill="both", expand=True)

        top = ttk.Frame(content)
        top.pack(fill="x", **pad)

        self.language_label = ttk.Label(top)
        self.language_label.pack(side="left")

        self.language_combo = ttk.Combobox(
            top,
            values=["Magyar", "English"],
            state="readonly",
            width=12,
            style="App.TCombobox"
        )
        self.language_combo.pack(side="left", padx=(8, 0))
        self.language_combo.set("Magyar")
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        self.status_label = ttk.Label(top, textvariable=self.status_var)
        self.status_label.pack(side="right")

        form = ttk.Frame(content)
        form.pack(fill="x", **pad)
        form.columnconfigure(1, weight=1)

        self.folder_label = ttk.Label(form)
        self.folder_label.grid(row=0, column=0, sticky="w")

        self.folder_entry = ttk.Entry(form, textvariable=self.folder_var)
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))

        self.browse_button = ttk.Button(form, command=self.browse_folder)
        self.browse_button.grid(row=0, column=2)

        self.ip_label = ttk.Label(form)
        self.ip_label.grid(row=1, column=0, sticky="w")

        ip_row = ttk.Frame(form)
        ip_row.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0))
        ip_row.columnconfigure(0, weight=1)

        self.ip_entry = ttk.Entry(ip_row, textvariable=self.ip_var)
        self.ip_entry.grid(row=0, column=0, sticky="ew")

        self.detect_ip_button = ttk.Button(ip_row, command=self.detect_ip)
        self.detect_ip_button.grid(row=0, column=1, padx=(8, 0))

        self.port_label = ttk.Label(form)
        self.port_label.grid(row=2, column=0, sticky="w")

        self.port_entry = ttk.Entry(form, textvariable=self.port_var, width=12)
        self.port_entry.grid(row=2, column=1, sticky="w", padx=(8, 0))

        self.interval_label = ttk.Label(form)
        self.interval_label.grid(row=3, column=0, sticky="w")

        interval_wrap = ttk.Frame(form)
        interval_wrap.grid(row=3, column=1, columnspan=2, sticky="w", padx=(8, 0))

        self.interval_entry = ttk.Entry(interval_wrap, textvariable=self.interval_var, width=12)
        self.interval_entry.pack(side="left")

        self.interval_hint_label = ttk.Label(interval_wrap)
        self.interval_hint_label.pack(side="left", padx=(10, 0))

        buttons = ttk.Frame(content)
        buttons.pack(fill="x", **pad)

        self.start_button = ttk.Button(buttons, command=self.start_server)
        self.start_button.pack(side="left")

        self.stop_button = ttk.Button(buttons, command=self.stop_server)
        self.stop_button.pack(side="left", padx=(8, 0))

        urls = ttk.LabelFrame(content)
        urls.pack(fill="x", **pad)
        urls.columnconfigure(1, weight=1)

        self.server_url_label = ttk.Label(urls)
        self.server_url_label.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.server_url_entry = ttk.Entry(urls, textvariable=self.server_url_var)
        self.server_url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=8)

        self.server_url_copy = ttk.Button(urls, command=lambda: self.copy_value(self.server_url_var.get()))
        self.server_url_copy.grid(row=0, column=2, padx=(0, 8), pady=8)

        self.playlist_url_label = ttk.Label(urls)
        self.playlist_url_label.grid(row=1, column=0, sticky="w", padx=8, pady=8)

        self.playlist_url_entry = ttk.Entry(urls, textvariable=self.playlist_url_var)
        self.playlist_url_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=8)

        self.playlist_url_copy = ttk.Button(urls, command=lambda: self.copy_value(self.playlist_url_var.get()))
        self.playlist_url_copy.grid(row=1, column=2, padx=(0, 8), pady=8)

        self.shuffle_url_label = ttk.Label(urls)
        self.shuffle_url_label.grid(row=2, column=0, sticky="w", padx=8, pady=8)

        self.shuffle_url_entry = ttk.Entry(urls, textvariable=self.shuffle_url_var)
        self.shuffle_url_entry.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=8)

        self.shuffle_url_copy = ttk.Button(urls, command=lambda: self.copy_value(self.shuffle_url_var.get()))
        self.shuffle_url_copy.grid(row=2, column=2, padx=(0, 8), pady=8)

        self.build_info_label = ttk.Label(content)
        self.build_info_label.pack(anchor="w", **pad)

        self.log_frame = ttk.LabelFrame(content)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=(6, 6))

        log_bg = "#181818" if self.is_dark else "#ffffff"
        log_fg = "#f2f2f2" if self.is_dark else "#111111"
        self.log_box = tk.Text(
            self.log_frame,
            height=12,
            wrap="word",
            bg=log_bg,
            fg=log_fg,
            insertbackground=log_fg,
            relief="flat",
            borderwidth=0
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)
        self.log_box.configure(state="disabled")

        for var in (self.ip_var, self.port_var):
            var.trace_add("write", lambda *args: self.update_urls())

    def refresh_texts(self):
        self.root.title(self.tr("title"))
        self.language_label.config(text=self.tr("language") + ":")
        self.folder_label.config(text=self.tr("folder"))
        self.browse_button.config(text=self.tr("browse"))
        self.detect_ip_button.config(text=self.tr("detect_ip"))
        self.ip_label.config(text=self.tr("ip"))
        self.port_label.config(text=self.tr("port"))
        self.interval_label.config(text=self.tr("interval"))
        self.interval_hint_label.config(text=self.tr("interval_hint"))
        self.start_button.config(text=self.tr("start"))
        self.stop_button.config(text=self.tr("stop"))
        self.server_url_label.config(text=self.tr("server_url"))
        self.playlist_url_label.config(text=self.tr("playlist_url"))
        self.shuffle_url_label.config(text=self.tr("shuffle_url"))
        self.server_url_copy.config(text=self.tr("copy"))
        self.playlist_url_copy.config(text=self.tr("copy"))
        self.shuffle_url_copy.config(text=self.tr("copy"))
        self.log_frame.config(text=self.tr("log"))
        self.build_info_label.config(text=self.tr("build_info"))
        running = self.server_process is not None and self.server_process.poll() is None
        self.status_var.set(self.tr("status_running") if running else self.tr("status_stopped"))
        self.footer_text_label.config(text=self.tr("footer_text"))

        if self.footer_icon is not None:
            self.footer_icon_label.config(image=self.footer_icon, text="")
        else:
            self.footer_icon_label.config(text="♪")

    def on_language_change(self, event=None):
        self.lang = "hu" if self.language_combo.get() == "Magyar" else "en"
        self.refresh_texts()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def detect_ip(self):
        self.ip_var.set(get_local_ip())

    def update_urls(self):
        ip = self.ip_var.get().strip() or "127.0.0.1"
        port = self.port_var.get().strip() or "8000"
        self.server_url_var.set(f"http://{ip}:{port}/")
        self.playlist_url_var.set(f"http://{ip}:{port}/playlist.m3u")
        self.shuffle_url_var.set(f"http://{ip}:{port}/playlist_shuffle.m3u")

    def copy_value(self, value):
        if not value:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.log(self.tr("copied"))

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def safe_log(self, message):
        self.root.after(0, lambda: self.log(message))

    def validate_inputs(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showerror(self.tr("error"), self.tr("folder_required"))
            return None

        root_path = pathlib.Path(folder).expanduser().resolve()
        if not root_path.exists():
            messagebox.showerror(self.tr("error"), self.tr("folder_missing"))
            return None

        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showerror(self.tr("error"), self.tr("invalid_port"))
            return None

        if not (1 <= port <= 65535):
            messagebox.showerror(self.tr("error"), self.tr("invalid_port"))
            return None

        try:
            interval = int(self.interval_var.get().strip())
        except ValueError:
            messagebox.showerror(self.tr("error"), self.tr("invalid_interval"))
            return None

        if interval < 0:
            messagebox.showerror(self.tr("error"), self.tr("invalid_interval"))
            return None

        ip = self.ip_var.get().strip() or get_local_ip()
        return root_path, ip, port, interval

    def build_server_command(self, root_path, ip, port, interval):
        if getattr(sys, "frozen", False):
            return [
                sys.executable,
                "--cli-server",
                str(root_path),
                "--ip", ip,
                "--port", str(port),
                "--interval", str(interval),
                "--lang", self.lang,
            ]
        return [
            sys.executable,
            os.path.abspath(__file__),
            "--cli-server",
            str(root_path),
            "--ip", ip,
            "--port", str(port),
            "--interval", str(interval),
            "--lang", self.lang,
        ]

    def process_log_line(self, line: str):
        stripped = line.rstrip()

        if stripped.startswith("Traceback (most recent call last):"):
            self._skip_traceback = True
            return None

        if self._skip_traceback:
            if "ConnectionResetError" in stripped or "WinError 10054" in stripped:
                self._skip_traceback = False
                return None
            if stripped.startswith("  File "):
                return None
            self._skip_traceback = False

        if "ConnectionResetError" in stripped or "WinError 10054" in stripped:
            return None

        return stripped

    def read_server_output(self):
        try:
            while self.server_process and self.server_process.stdout:
                line = self.server_process.stdout.readline()
                if not line:
                    break
                processed = self.process_log_line(line)
                if processed:
                    self.safe_log(processed)
        except Exception as e:
            self.safe_log(f"{self.tr('error')}: {e}")
        finally:
            self.root.after(0, self.on_server_exit)

    def on_server_exit(self):
        if self.server_process is not None:
            rc = self.server_process.poll()
            if rc is not None:
                self.server_process = None
                self.status_var.set(self.tr("status_stopped"))

    def start_server(self):
        if self.server_process is not None and self.server_process.poll() is None:
            self.log(self.tr("already_running"))
            return

        validated = self.validate_inputs()
        if validated is None:
            return

        root_path, ip, port, interval = validated
        self.update_urls()
        cmd = self.build_server_command(root_path, ip, port, interval)

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="mbcs",
                errors="replace",
                creationflags=creationflags
            )
        except Exception as e:
            self.server_process = None
            messagebox.showerror(self.tr("error"), str(e))
            return

        self._skip_traceback = False
        self.reader_thread = threading.Thread(target=self.read_server_output, daemon=True)
        self.reader_thread.start()

        self.status_var.set(self.tr("status_running"))
        self.log(self.tr("server_started"))
        self.log(self.server_url_var.get())
        self.log(self.playlist_url_var.get())
        self.log(self.shuffle_url_var.get())

    def stop_server(self):
        if self.server_process is None or self.server_process.poll() is not None:
            self.log(self.tr("not_running"))
            return

        try:
            self.server_process.terminate()
        except Exception:
            pass

        self.server_process = None
        self.status_var.set(self.tr("status_stopped"))
        self.log(self.tr("server_stopped"))

    def on_close(self):
        if self.server_process is not None and self.server_process.poll() is None:
            try:
                self.server_process.terminate()
            except Exception:
                pass
        self.root.destroy()


def gui_main():
    root = tk.Tk()
    MusicServerApp(root)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli-server":
        cli_server_main(sys.argv[2:])
    else:
        gui_main()
