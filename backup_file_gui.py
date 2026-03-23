import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import threading
import time
from datetime import datetime


# ──────────────────────────────────────────────
#  THEME
# ──────────────────────────────────────────────
BG        = "#0d0f0e"
PANEL     = "#131614"
BORDER    = "#1f2421"
AMBER     = "#f5a623"
AMBER_DIM = "#7a5210"
GREEN     = "#39d98a"
RED       = "#ff5c5c"
TEXT      = "#d4cfc8"
TEXT_DIM  = "#5a5a55"
MONO      = ("Courier New", 10)
MONO_SM   = ("Courier New", 9)
TITLE_F   = ("Courier New", 14, "bold")


# ──────────────────────────────────────────────
#  APP
# ──────────────────────────────────────────────
class BackupTool:
    def __init__(self, root):
        self.root = root
        self.root.title("BACKUPR // File Backup Tool")
        self.root.geometry("680x620")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.source_path = tk.StringVar(value="")
        self.dest_path   = tk.StringVar(value="")
        self.status_var  = tk.StringVar(value="READY")
        self.progress    = tk.DoubleVar(value=0.0)
        self.is_running  = False

        self._build_ui()

    # ── UI BUILD ──────────────────────────────
    def _build_ui(self):
        # ── Header bar
        header = tk.Frame(self.root, bg=AMBER, height=4)
        header.pack(fill="x")

        title_frame = tk.Frame(self.root, bg=BG, pady=18)
        title_frame.pack(fill="x", padx=28)

        tk.Label(title_frame, text="▣  BACKUPR", font=TITLE_F,
                 bg=BG, fg=AMBER).pack(side="left")
        tk.Label(title_frame, text="v1.0  //  file backup utility",
                 font=MONO_SM, bg=BG, fg=TEXT_DIM).pack(side="left", padx=14)

        ts = datetime.now().strftime("%Y-%m-%d")
        tk.Label(title_frame, text=ts, font=MONO_SM,
                 bg=BG, fg=TEXT_DIM).pack(side="right")

        self._divider()

        # ── Path selectors
        self._path_row("SOURCE", "Select source folder →", self.source_path, self._pick_source)
        self._path_row("BACKUP", "Select backup folder →", self.dest_path,   self._pick_dest)

        self._divider()

        # ── Progress section
        prog_frame = tk.Frame(self.root, bg=BG, padx=28, pady=6)
        prog_frame.pack(fill="x")

        tk.Label(prog_frame, text="PROGRESS", font=MONO_SM,
                 bg=BG, fg=TEXT_DIM).pack(anchor="w")

        bar_bg = tk.Frame(prog_frame, bg=BORDER, height=18, bd=0)
        bar_bg.pack(fill="x", pady=(4, 0))
        bar_bg.pack_propagate(False)

        self.bar_fill = tk.Frame(bar_bg, bg=AMBER, width=0, height=18)
        self.bar_fill.place(x=0, y=0, relheight=1.0)

        self.pct_label = tk.Label(bar_bg, text="0%", font=MONO_SM,
                                  bg=BORDER, fg=TEXT_DIM)
        self.pct_label.place(relx=1.0, rely=0.5, anchor="e", x=-6)

        self._divider()

        # ── Log window
        log_frame = tk.Frame(self.root, bg=BG, padx=28)
        log_frame.pack(fill="both", expand=True)

        tk.Label(log_frame, text="LOG OUTPUT", font=MONO_SM,
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 4))

        log_border = tk.Frame(log_frame, bg=BORDER, padx=1, pady=1)
        log_border.pack(fill="both", expand=True)

        self.log_box = tk.Text(
            log_border, bg=PANEL, fg=TEXT, font=MONO_SM,
            bd=0, relief="flat", wrap="word",
            insertbackground=AMBER, state="disabled",
            selectbackground=AMBER_DIM, height=10
        )
        scroll = tk.Scrollbar(log_border, command=self.log_box.yview,
                              bg=BORDER, troughcolor=PANEL,
                              activebackground=AMBER)
        self.log_box.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_box.pack(side="left", fill="both", expand=True, padx=8, pady=6)

        self._log("System ready. Select folders to begin.", color=TEXT_DIM)

        self._divider()

        # ── Bottom bar: status + button
        bot = tk.Frame(self.root, bg=BG, padx=28, pady=14)
        bot.pack(fill="x")

        status_box = tk.Frame(bot, bg=BORDER, padx=10, pady=6)
        status_box.pack(side="left")
        tk.Label(status_box, text="STATUS:", font=MONO_SM,
                 bg=BORDER, fg=TEXT_DIM).pack(side="left")
        self.status_lbl = tk.Label(status_box, textvariable=self.status_var,
                                   font=("Courier New", 10, "bold"),
                                   bg=BORDER, fg=GREEN)
        self.status_lbl.pack(side="left", padx=(6, 0))

        self.start_btn = tk.Button(
            bot, text="[ START BACKUP ]",
            font=("Courier New", 11, "bold"),
            bg=AMBER, fg="#0d0f0e",
            activebackground="#d48e1a", activeforeground="#0d0f0e",
            bd=0, padx=20, pady=8, cursor="hand2",
            command=self._start_backup
        )
        self.start_btn.pack(side="right")

        # Footer line
        footer = tk.Frame(self.root, bg=AMBER, height=4)
        footer.pack(fill="x", side="bottom")

    def _divider(self):
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=28, pady=8)

    def _path_row(self, label, hint, var, cmd):
        row = tk.Frame(self.root, bg=BG, padx=28, pady=4)
        row.pack(fill="x")

        tk.Label(row, text=label, font=("Courier New", 9, "bold"),
                 bg=BG, fg=AMBER, width=7, anchor="w").pack(side="left")

        btn = tk.Button(row, text="Browse", font=MONO_SM,
                        bg=BORDER, fg=TEXT,
                        activebackground=AMBER_DIM, activeforeground=TEXT,
                        bd=0, padx=10, pady=4, cursor="hand2",
                        command=cmd)
        btn.pack(side="right")

        path_frame = tk.Frame(row, bg=BORDER, padx=8, pady=4)
        path_frame.pack(side="left", fill="x", expand=True, padx=(8, 8))

        tk.Label(path_frame, textvariable=var, font=MONO_SM,
                 bg=BORDER, fg=TEXT, anchor="w",
                 width=50).pack(anchor="w")

        # placeholder hint
        if not var.get():
            var.set(hint)
            var.trace_add("write", lambda *_: None)

    # ── PICKERS ───────────────────────────────
    def _pick_source(self):
        path = filedialog.askdirectory(title="Select Source Folder")
        if path:
            self.source_path.set(path)
            self._log(f"Source set: {path}")

    def _pick_dest(self):
        path = filedialog.askdirectory(title="Select Backup Folder")
        if path:
            self.dest_path.set(path)
            self._log(f"Destination set: {path}")

    # ── BACKUP LOGIC ──────────────────────────
    def _start_backup(self):
        if self.is_running:
            return

        src = self.source_path.get()
        dst = self.dest_path.get()

        # Validate
        if not src or src.endswith("→"):
            self._set_status("ERROR", RED)
            self._log("✖ No source folder selected.", color=RED)
            return
        if not dst or dst.endswith("→"):
            self._set_status("ERROR", RED)
            self._log("✖ No backup folder selected.", color=RED)
            return
        if not os.path.isdir(src):
            self._set_status("ERROR", RED)
            self._log("✖ Source folder does not exist.", color=RED)
            return
        if os.path.abspath(src) == os.path.abspath(dst):
            self._set_status("ERROR", RED)
            self._log("✖ Source and destination cannot be the same.", color=RED)
            return

        thread = threading.Thread(target=self._run_backup, args=(src, dst), daemon=True)
        thread.start()

    def _run_backup(self, src, dst):
        self.is_running = True
        self.start_btn.config(state="disabled", bg=AMBER_DIM)
        self._set_status("RUNNING", AMBER)
        self._update_progress(0)
        self._log("─" * 48, color=TEXT_DIM)
        self._log(f"▶ Backup started at {datetime.now().strftime('%H:%M:%S')}")

        try:
            # Collect all files (recursive)
            all_files = []
            for root_dir, dirs, files in os.walk(src):
                for f in files:
                    all_files.append(os.path.join(root_dir, f))

            total = len(all_files)
            if total == 0:
                self._log("⚠ Source folder is empty. Nothing to back up.", color=AMBER)
                self._set_status("EMPTY", AMBER)
                self._update_progress(0)
                return

            self._log(f"  Found {total} file(s) to copy.")
            os.makedirs(dst, exist_ok=True)

            copied = 0
            errors = 0
            for i, filepath in enumerate(all_files, 1):
                try:
                    rel = os.path.relpath(filepath, src)
                    target = os.path.join(dst, rel)
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    shutil.copy2(filepath, target)
                    copied += 1
                    self._log(f"  ✔ [{i}/{total}]  {rel}")
                except PermissionError:
                    errors += 1
                    self._log(f"  ✖ Permission denied: {os.path.relpath(filepath, src)}", color=RED)
                except Exception as e:
                    errors += 1
                    self._log(f"  ✖ Error: {e}", color=RED)

                pct = (i / total) * 100
                self._update_progress(pct)
                time.sleep(0.03)   # smooth visual feel

            self._log("─" * 48, color=TEXT_DIM)
            if errors == 0:
                self._log(f"✔ Done — {copied} file(s) copied successfully.", color=GREEN)
                self._set_status("COMPLETE", GREEN)
            else:
                self._log(f"⚠ Done — {copied} copied, {errors} error(s).", color=AMBER)
                self._set_status("PARTIAL", AMBER)

        except Exception as e:
            self._log(f"✖ Unexpected error: {e}", color=RED)
            self._set_status("FAILED", RED)
        finally:
            self.is_running = False
            self.start_btn.config(state="normal", bg=AMBER)

    # ── HELPERS ───────────────────────────────
    def _log(self, msg, color=None):
        color = color or TEXT
        def _write():
            self.log_box.config(state="normal")
            tag = f"color_{color.replace('#','')}"
            self.log_box.tag_configure(tag, foreground=color)
            self.log_box.insert("end", msg + "\n", tag)
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.root.after(0, _write)

    def _set_status(self, text, color):
        def _upd():
            self.status_var.set(text)
            self.status_lbl.config(fg=color)
        self.root.after(0, _upd)

    def _update_progress(self, pct):
        def _upd():
            bar_width = 624  # approximate fill area width
            fill_w = int((pct / 100) * bar_width)
            self.bar_fill.place(x=0, y=0, width=fill_w, relheight=1.0)
            self.pct_label.config(text=f"{int(pct)}%")
        self.root.after(0, _upd)


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = BackupTool(root)
    root.mainloop()
