import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ══════════════════════════════════════════════════════
#   PREMIUM EYE-RELIEF THEME  — Deep Forest Dark
#   Background : deep charcoal-green (not pure black)
#   Accent     : emerald / gold
#   Font       : large, readable, soft
# ══════════════════════════════════════════════════════
BG        = "#0e1a14"     # deep forest charcoal — softest on eyes
CARD      = "#142010"     # slightly lighter card
BORDER    = "#1e3a28"     # muted green border
ACCENT    = "#00e096"     # bright emerald — premium feel
ACCENT_DK = "#00a86b"     # darker emerald for hover
GOLD      = "#f5c842"     # gold accent for highlights
TEXT      = "#dff0e8"     # warm soft white — no blue glare
TEXT_DIM  = "#6aaa88"     # muted sage for labels
SUCCESS   = "#00e096"
WARNING   = "#f5c842"
ERROR     = "#ff5370"

# ── LARGE FONTS ──────────────────────────────────────
F_LOGO    = ("Segoe UI", 26, "bold")
F_HEADER  = ("Segoe UI", 13, "bold")
F_LABEL   = ("Segoe UI", 13)
F_ENTRY   = ("Consolas", 13)
F_STATUS  = ("Segoe UI", 12)
F_BTN     = ("Segoe UI", 12, "bold")
F_TREE    = ("Consolas", 12)
F_TREE_HD = ("Segoe UI", 11, "bold")
F_PREVIEW = ("Consolas", 13)
F_COUNT   = ("Segoe UI", 12)


class FileRenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✦ File Renamer — Premium")
        self.geometry("980x760")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.minsize(800, 600)

        self.folder_path = tk.StringVar()
        self.prefix_var  = tk.StringVar(value="file_")
        self.suffix_var  = tk.StringVar(value="")
        self.start_num   = tk.IntVar(value=1)
        self.padding_var = tk.IntVar(value=1)
        self.keep_ext    = tk.BooleanVar(value=True)
        self.files       = []
        self.undo_log    = []
        self.search_var  = tk.StringVar()

        self._apply_styles()
        self._build_ui()
        self._bind_live_preview()

    # ── Styles ────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                         background=CARD,
                         foreground=TEXT,
                         fieldbackground=CARD,
                         rowheight=32,
                         font=F_TREE,
                         borderwidth=0,
                         relief="flat")
        style.configure("Treeview.Heading",
                         background="#0a120d",
                         foreground=TEXT_DIM,
                         font=F_TREE_HD,
                         relief="flat",
                         padding=(8, 6))
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#0e1a14")])

        style.configure("Vertical.TScrollbar",
                         background=BORDER,
                         troughcolor=CARD,
                         arrowcolor=TEXT_DIM,
                         relief="flat",
                         width=8)

    # ── UI Build ──────────────────────────────────────
    def _build_ui(self):
        self._header()
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=28, pady=(10, 8))
        self._folder_row()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._file_panel(body)
        self._options_panel(body)
        self._bottom_bar()

    def _header(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 0))

        # Logo dot
        canvas = tk.Canvas(hdr, width=38, height=38, bg=BG,
                           highlightthickness=0)
        canvas.create_oval(4, 4, 34, 34, fill=ACCENT, outline="")
        canvas.create_text(19, 19, text="✦", fill="#0e1a14",
                           font=("Segoe UI", 14, "bold"))
        canvas.pack(side="left")

        tk.Label(hdr, text="  File Renamer", font=F_LOGO,
                 fg=TEXT, bg=BG).pack(side="left")

        # Gold tag
        tag = tk.Label(hdr, text=" PREMIUM ",
                       font=("Segoe UI", 9, "bold"),
                       fg="#0e1a14", bg=GOLD,
                       padx=6, pady=2)
        tag.pack(side="left", padx=(10, 0), pady=(6, 0))

        tk.Label(hdr, text="  Bulk rename files with full control",
                 font=F_STATUS, fg=TEXT_DIM, bg=BG).pack(
            side="left", pady=(6, 0))

    def _folder_row(self):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=28, pady=(0, 12))

        entry = tk.Entry(row, textvariable=self.folder_path,
                         font=F_ENTRY, bg=CARD, fg=TEXT,
                         insertbackground=ACCENT, relief="flat",
                         highlightbackground=BORDER, highlightthickness=2,
                         highlightcolor=ACCENT)
        entry.pack(side="left", fill="x", expand=True, ipady=10, ipadx=10)

        btn = tk.Button(row, text="  📂  Select Folder  ",
                        font=F_BTN,
                        bg=ACCENT, fg="#0e1a14", relief="flat",
                        activebackground=ACCENT_DK,
                        activeforeground="#0e1a14",
                        cursor="hand2", command=self._select_folder)
        btn.pack(side="left", padx=(10, 0), ipady=10, ipadx=6)

    def _file_panel(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        card.rowconfigure(2, weight=1)
        card.columnconfigure(0, weight=1)

        # Section title
        tk.Label(card, text="📋  FILE LIST",
                 font=F_HEADER, fg=ACCENT, bg=CARD).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 0))

        # Search
        self.search_var.trace_add(
            "write",
            lambda *_: self._populate_tree(self.search_var.get().lower()))

        sf = tk.Frame(card, bg=CARD)
        sf.grid(row=1, column=0, columnspan=2, sticky="ew",
                padx=12, pady=(8, 0))

        tk.Label(sf, text="🔍", bg=CARD, fg=TEXT_DIM,
                 font=("Segoe UI", 13)).pack(side="left", padx=(0, 4))
        tk.Entry(sf, textvariable=self.search_var, font=F_ENTRY,
                 bg="#0a120d", fg=TEXT, relief="flat",
                 insertbackground=ACCENT,
                 highlightbackground=BORDER, highlightthickness=1,
                 highlightcolor=ACCENT).pack(
            side="left", fill="x", expand=True, ipady=7, ipadx=8)

        # Treeview
        cols = ("original", "preview")
        self.tree = ttk.Treeview(card, columns=cols,
                                  show="headings", selectmode="extended")
        self.tree.heading("original", text="  Original Name")
        self.tree.heading("preview",  text="  → New Name (Preview)")
        self.tree.column("original", width=180, minwidth=120)
        self.tree.column("preview",  width=180, minwidth=120)

        vsb = ttk.Scrollbar(card, orient="vertical",
                            command=self.tree.yview,
                            style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=2, column=0, sticky="nsew",
                       padx=(12, 0), pady=(8, 0))
        vsb.grid(row=2, column=1, sticky="ns",
                 pady=(8, 0), padx=(2, 8))

        self.file_count_label = tk.Label(
            card, text="No folder selected",
            font=F_COUNT, fg=TEXT_DIM, bg=CARD)
        self.file_count_label.grid(row=3, column=0, columnspan=2,
                                    sticky="w", padx=14, pady=(6, 10))

    def _options_panel(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=1, sticky="nsew")
        card.columnconfigure(1, weight=1)

        tk.Label(card, text="⚙  RENAME OPTIONS",
                 font=F_HEADER, fg=ACCENT, bg=CARD).grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=14, pady=(12, 4))

        PAD = dict(padx=14, pady=6)

        def lbl(text, row):
            tk.Label(card, text=text, font=F_LABEL,
                     fg=TEXT, bg=CARD, anchor="w").grid(
                row=row, column=0, sticky="w", **PAD)

        def ent(var, row):
            tk.Entry(card, textvariable=var, font=F_ENTRY,
                     bg="#0a120d", fg=TEXT, relief="flat",
                     insertbackground=ACCENT,
                     highlightbackground=BORDER, highlightthickness=1,
                     highlightcolor=ACCENT).grid(
                row=row, column=1, sticky="ew", ipady=7, **PAD)

        def spn(var, row, from_=1, to=999):
            tk.Spinbox(card, from_=from_, to=to, textvariable=var,
                       font=F_ENTRY, bg="#0a120d", fg=TEXT, relief="flat",
                       buttonbackground=BORDER,
                       insertbackground=ACCENT,
                       highlightbackground=BORDER, highlightthickness=1,
                       highlightcolor=ACCENT).grid(
                row=row, column=1, sticky="ew", ipady=7, **PAD)

        lbl("Prefix",        1);  ent(self.prefix_var,  1)
        lbl("Suffix",        2);  ent(self.suffix_var,  2)
        lbl("Start Number",  3);  spn(self.start_num,   3)
        lbl("Zero Padding",  4);  spn(self.padding_var, 4, from_=1, to=6)

        lbl("Keep Extension", 5)
        tk.Checkbutton(card, variable=self.keep_ext,
                       font=F_LABEL, fg=TEXT, bg=CARD,
                       selectcolor="#0a120d",
                       activebackground=CARD,
                       activeforeground=TEXT,
                       command=self._update_preview).grid(
            row=5, column=1, sticky="w", **PAD)

        # Divider
        tk.Frame(card, bg=BORDER, height=1).grid(
            row=6, column=0, columnspan=2,
            sticky="ew", padx=14, pady=10)

        # Preview section
        tk.Label(card, text="👁  LIVE PREVIEW",
                 font=F_HEADER, fg=GOLD, bg=CARD).grid(
            row=7, column=0, columnspan=2,
            sticky="w", padx=14, pady=(0, 4))

        self.example_label = tk.Label(
            card, text="—",
            font=F_PREVIEW, fg=SUCCESS,
            bg="#0a120d",
            wraplength=220, anchor="w", justify="left",
            padx=10, pady=8)
        self.example_label.grid(row=8, column=0, columnspan=2,
                                  sticky="ew", padx=14, pady=(0, 6))

        self.conflict_label = tk.Label(
            card, text="",
            font=F_STATUS, fg=WARNING,
            bg=CARD, wraplength=200, justify="left")
        self.conflict_label.grid(row=9, column=0, columnspan=2,
                                  sticky="w", padx=14, pady=(0, 8))

    def _bottom_bar(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=28, pady=(8, 0))

        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=28, pady=12)

        self.status_var = tk.StringVar(value="Ready — select a folder to begin.")
        tk.Label(bar, textvariable=self.status_var,
                 font=F_STATUS, fg=TEXT_DIM, bg=BG).pack(side="left")

        self.undo_btn = tk.Button(
            bar, text="  ↩  Undo  ",
            font=F_BTN,
            bg=BORDER, fg=TEXT_DIM, relief="flat",
            activebackground="#1e3a28",
            activeforeground=TEXT,
            state="disabled", cursor="hand2",
            command=self._undo_rename)
        self.undo_btn.pack(side="right", padx=(10, 0), ipady=10, ipadx=6)

        self.rename_btn = tk.Button(
            bar, text="  ✦  Rename Files  ",
            font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg="#0e1a14", relief="flat",
            activebackground=ACCENT_DK,
            activeforeground="#0e1a14",
            cursor="hand2",
            command=self._start_rename)
        self.rename_btn.pack(side="right", ipady=10, ipadx=10)

    # ── Core Logic ────────────────────────────────────
    def _bind_live_preview(self):
        for var in (self.prefix_var, self.suffix_var,
                    self.start_num, self.padding_var):
            var.trace_add("write", lambda *_: self._update_preview())

    def _select_folder(self):
        path = filedialog.askdirectory(title="Select a Folder")
        if not path:
            return
        self.folder_path.set(path)
        self._load_files(path)

    def _load_files(self, path):
        try:
            all_items = os.listdir(path)
            self.files = sorted([
                f for f in all_items
                if os.path.isfile(os.path.join(path, f))
            ])
        except PermissionError:
            messagebox.showerror("Permission Error",
                                 "Cannot read folder — permission denied.")
            return

        if not self.files:
            self.file_count_label.config(text="⚠  Folder is empty")
            self.tree.delete(*self.tree.get_children())
            self.example_label.config(text="—")
            return

        self.file_count_label.config(
            text=f"✔  {len(self.files)} file(s) found")
        self._update_preview()

    def _generate_names(self):
        prefix  = self.prefix_var.get()
        suffix  = self.suffix_var.get()
        start   = self.start_num.get()
        padding = self.padding_var.get()
        names   = []
        for i, f in enumerate(self.files):
            ext = os.path.splitext(f)[1] if self.keep_ext.get() else ""
            num = str(start + i).zfill(padding)
            names.append(f"{prefix}{num}{suffix}{ext}")
        return names

    def _populate_tree(self, query=""):
        self.tree.delete(*self.tree.get_children())
        new_names = self._generate_names()
        for orig, new in zip(self.files, new_names):
            if query and query not in orig.lower():
                continue
            self.tree.insert("", "end", values=(orig, new))

    def _update_preview(self):
        if not self.files:
            return
        names = self._generate_names()
        self._populate_tree(self.search_var.get().lower())

        if names:
            self.example_label.config(
                text=f"{self.files[0]}\n→  {names[0]}")

        if len(names) != len(set(names)):
            self.conflict_label.config(
                text="⚠ Duplicate names detected!\nChange prefix / suffix.")
        else:
            self.conflict_label.config(text="")

    def _start_rename(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return
        if not self.files:
            messagebox.showwarning("No Files", "No files to rename.")
            return

        new_names = self._generate_names()

        if len(new_names) != len(set(new_names)):
            messagebox.showerror(
                "Conflict",
                "Duplicate new names detected.\n"
                "Change prefix / suffix / start number.")
            return

        if not messagebox.askyesno(
                "Confirm Rename",
                f"Rename {len(self.files)} file(s)?\n\n"
                "Undo will be available until you close the app."):
            return

        self._do_rename(folder, new_names)

    def _do_rename(self, folder, new_names):
        self.undo_log = []
        errors = []

        for orig, new in zip(self.files, new_names):
            old_path = os.path.join(folder, orig)
            new_path = os.path.join(folder, new)

            if (os.path.exists(new_path) and
                    os.path.abspath(old_path) != os.path.abspath(new_path)):
                errors.append(f"Already exists — skipped: {new}")
                continue
            try:
                os.rename(old_path, new_path)
                self.undo_log.append((new_path, old_path))
            except PermissionError:
                errors.append(f"Permission denied: {orig}")
            except Exception as e:
                errors.append(f"{orig}: {e}")

        self._load_files(folder)
        self.undo_btn.config(state="normal", fg=TEXT,
                             bg="#1e3a28")

        if errors:
            self.status_var.set(f"Done with {len(errors)} error(s).")
            messagebox.showwarning(
                "Partial Success",
                "Some files could not be renamed:\n\n" + "\n".join(errors))
        else:
            self.status_var.set(
                f"✔  {len(self.undo_log)} file(s) renamed successfully.")

    def _undo_rename(self):
        if not self.undo_log:
            messagebox.showinfo("Nothing to Undo", "No rename history.")
            return
        if not messagebox.askyesno("Undo Rename",
                                    f"Revert {len(self.undo_log)} file(s)?"):
            return

        errors = []
        for new_path, old_path in reversed(self.undo_log):
            try:
                os.rename(new_path, old_path)
            except Exception as e:
                errors.append(str(e))

        self.undo_log = []
        self.undo_btn.config(state="disabled", fg=TEXT_DIM, bg=BORDER)
        self._load_files(self.folder_path.get())

        if errors:
            messagebox.showwarning("Undo Errors", "\n".join(errors))
            self.status_var.set("Undo done (with errors).")
        else:
            self.status_var.set("↩  Undo complete — original names restored.")


# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = FileRenamerApp()
    app.mainloop()