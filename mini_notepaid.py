import tkinter as tk
from tkinter import filedialog, messagebox, font
import os

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#1E1E2E"   # deep navy
EDITOR_BG   = "#262637"   # slightly lighter
TOOLBAR_BG  = "#16162A"   # darkest strip
FG          = "#E8E3D5"   # warm cream text
ACCENT      = "#F5A623"   # amber
ACCENT2     = "#7EC8A4"   # sage green
CURSOR_CLR  = "#F5A623"
SELECT_BG   = "#3A3A5C"
LINE_BG     = "#1E1E2E"
LINE_FG     = "#555580"
BORDER      = "#35354F"
BTN_HOVER   = "#2E2E4A"
STATUS_BG   = "#13132A"

FONT_FAMILY = "Courier New"
FONT_SIZE   = 16
LINE_HEIGHT = 24

# ── App ───────────────────────────────────────────────────────────────────────
class NotepadApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("✦ Notepad")
        self.root.configure(bg=BG)
        self.root.geometry("900x680")
        self.root.minsize(600, 400)

        self.current_file = None
        self.modified = False

        self._build_ui()
        self._bind_keys()
        self._update_status()

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Title bar row ─────────────────────────────────────────────────────
        title_bar = tk.Frame(self.root, bg=TOOLBAR_BG, height=50)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        title_lbl = tk.Label(
            title_bar, text="✦  NOTEPAD",
            bg=TOOLBAR_BG, fg=ACCENT,
            font=(FONT_FAMILY, 20, "bold"),
            padx=18
        )
        title_lbl.pack(side=tk.LEFT, pady=12)

        # Designer credit — right side of title bar
        credit_lbl = tk.Label(
            title_bar, text="⚡ Design by Mr Selfish.",
            bg=TOOLBAR_BG, fg=ACCENT2,
            font=(FONT_FAMILY, 15, "italic"),
            padx=18
        )
        credit_lbl.pack(side=tk.RIGHT, pady=12)

        self.file_lbl = tk.Label(
            title_bar, text="untitled",
            bg=TOOLBAR_BG, fg=FG,
            font=(FONT_FAMILY, 11),
        )
        self.file_lbl.pack(side=tk.LEFT, pady=12)

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = tk.Frame(self.root, bg=TOOLBAR_BG, pady=6)
        toolbar.pack(fill=tk.X)

        sep = tk.Frame(self.root, bg=BORDER, height=1)
        sep.pack(fill=tk.X)

        buttons = [
            ("⊕  New",   self.new_file,   ACCENT2),
            ("⌂  Open",  self.open_file,  FG),
            ("✦  Save",  self.save_file,  ACCENT),
            ("⎘  Save As", self.save_as,  FG),
        ]

        for label, cmd, color in buttons:
            b = tk.Button(
                toolbar, text=label,
                bg=TOOLBAR_BG, fg=color,
                font=(FONT_FAMILY, 12, "bold"),
                activebackground=BTN_HOVER, activeforeground=ACCENT,
                relief=tk.FLAT, bd=0, padx=14, pady=4, cursor="hand2",
                command=cmd
            )
            b.pack(side=tk.LEFT, padx=2)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=BTN_HOVER))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=TOOLBAR_BG))

        # Font-size control on the right
        tk.Label(
            toolbar, text="Size:", bg=TOOLBAR_BG, fg=LINE_FG,
            font=(FONT_FAMILY, 10)
        ).pack(side=tk.RIGHT, padx=(0, 2))

        self.size_var = tk.IntVar(value=FONT_SIZE)
        size_spin = tk.Spinbox(
            toolbar, from_=10, to=36, textvariable=self.size_var,
            width=3, bg=EDITOR_BG, fg=FG, insertbackground=CURSOR_CLR,
            font=(FONT_FAMILY, 11), relief=tk.FLAT, bd=0,
            buttonbackground=TOOLBAR_BG,
            command=self._change_font
        )
        size_spin.pack(side=tk.RIGHT, padx=(0, 10))
        size_spin.bind("<Return>", lambda e: self._change_font())

        # Word-wrap toggle
        self.wrap_var = tk.BooleanVar(value=True)
        wrap_btn = tk.Checkbutton(
            toolbar, text="Wrap", variable=self.wrap_var,
            bg=TOOLBAR_BG, fg=LINE_FG,
            selectcolor=BG, activebackground=TOOLBAR_BG,
            font=(FONT_FAMILY, 10),
            command=self._toggle_wrap
        )
        wrap_btn.pack(side=tk.RIGHT, padx=6)

        # ── Editor area ───────────────────────────────────────────────────────
        editor_frame = tk.Frame(self.root, bg=BG)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_canvas = tk.Canvas(
            editor_frame, width=52, bg=LINE_BG,
            highlightthickness=0, bd=0
        )
        self.line_canvas.pack(side=tk.LEFT, fill=tk.Y)

        # Vertical scrollbar
        vscroll = tk.Scrollbar(editor_frame, orient=tk.VERTICAL, bg=BG, troughcolor=BG)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        hscroll = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, bg=BG, troughcolor=BG)
        hscroll.pack(fill=tk.X)

        # Main text widget
        self.text = tk.Text(
            editor_frame,
            bg=EDITOR_BG, fg=FG,
            insertbackground=CURSOR_CLR,
            selectbackground=SELECT_BG, selectforeground=FG,
            font=(FONT_FAMILY, FONT_SIZE),
            relief=tk.FLAT, bd=0,
            padx=16, pady=12,
            spacing1=4, spacing3=4,
            undo=True, autoseparators=True, maxundo=-1,
            wrap=tk.WORD,
            yscrollcommand=self._on_text_scroll,
            xscrollcommand=hscroll.set,
            highlightthickness=0,
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vscroll.config(command=self._scroll_both)
        hscroll.config(command=self.text.xview)

        # ── Status bar ────────────────────────────────────────────────────────
        sep2 = tk.Frame(self.root, bg=BORDER, height=1)
        sep2.pack(fill=tk.X)

        status_bar = tk.Frame(self.root, bg=STATUS_BG, height=26)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_lbl = tk.Label(
            status_bar, text="",
            bg=STATUS_BG, fg=LINE_FG,
            font=(FONT_FAMILY, 10),
            padx=14
        )
        self.status_lbl.pack(side=tk.LEFT)

        self.mod_lbl = tk.Label(
            status_bar, text="",
            bg=STATUS_BG, fg=ACCENT,
            font=(FONT_FAMILY, 10, "bold"),
            padx=14
        )
        self.mod_lbl.pack(side=tk.RIGHT)

        bottom_credit = tk.Label(
            status_bar, text="⚡ Mr Selfish · BBI",
            bg=STATUS_BG, fg=ACCENT2,
            font=(FONT_FAMILY, 9, "italic"),
            padx=12
        )
        bottom_credit.pack(side=tk.RIGHT)

    # ── Event helpers ─────────────────────────────────────────────────────────
    def _on_text_scroll(self, *args):
        self.line_canvas.yview_moveto(args[0])
        # rebuild line numbers on scroll
        self._update_line_numbers()

    def _scroll_both(self, *args):
        self.text.yview(*args)
        self._update_line_numbers()

    def _bind_keys(self):
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", lambda e: self._update_status())
        self.text.bind("<ButtonRelease>", lambda e: self._update_status())
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as())
        self.root.bind("<Control-z>", lambda e: self.text.edit_undo())
        self.root.bind("<Control-y>", lambda e: self.text.edit_redo())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.text.bind("<Configure>", lambda e: self._update_line_numbers())
        self.root.after(200, self._update_line_numbers)

    def _on_modified(self, event=None):
        if self.text.edit_modified():
            self.modified = True
            self.mod_lbl.config(text="● unsaved")
            self.text.edit_modified(False)
        self._update_line_numbers()
        self._update_status()

    def _update_status(self):
        try:
            idx = self.text.index(tk.INSERT)
            line, col = idx.split(".")
            chars = len(self.text.get("1.0", tk.END)) - 1
            words = len(self.text.get("1.0", tk.END).split())
            self.status_lbl.config(
                text=f"  Ln {line}  Col {int(col)+1}  │  {words} words  {chars} chars"
            )
        except Exception:
            pass

    def _update_line_numbers(self):
        self.line_canvas.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.line_canvas.create_text(
                44, y + 12,
                anchor="e",
                text=linenum,
                fill=LINE_FG if linenum != self.text.index(tk.INSERT).split(".")[0] else ACCENT,
                font=(FONT_FAMILY, FONT_SIZE - 3)
            )
            next_i = self.text.index(f"{i}+1line")
            if next_i == i:
                break
            i = next_i

    def _change_font(self):
        try:
            size = int(self.size_var.get())
            size = max(10, min(size, 36))
            self.text.config(font=(FONT_FAMILY, size))
            self._update_line_numbers()
        except Exception:
            pass

    def _toggle_wrap(self):
        self.text.config(wrap=tk.WORD if self.wrap_var.get() else tk.NONE)

    # ── File operations ───────────────────────────────────────────────────────
    def _ask_save_if_modified(self):
        if self.modified:
            answer = messagebox.askyesnocancel(
                "Unsaved changes",
                "Save changes before continuing?"
            )
            if answer is None:
                return False   # cancel
            if answer:
                self.save_file()
        return True

    def new_file(self):
        if not self._ask_save_if_modified():
            return
        self.text.delete("1.0", tk.END)
        self.current_file = None
        self.modified = False
        self.mod_lbl.config(text="")
        self.file_lbl.config(text="untitled")
        self.root.title("✦ Notepad")
        self._update_line_numbers()

    def open_file(self):
        if not self._ask_save_if_modified():
            return
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
            self.current_file = path
            self.modified = False
            self.mod_lbl.config(text="")
            name = os.path.basename(path)
            self.file_lbl.config(text=name)
            self.root.title(f"✦ Notepad — {name}")
            self._update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        if self.current_file:
            self._write(self.current_file)
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self._write(path)
            self.current_file = path
            name = os.path.basename(path)
            self.file_lbl.config(text=name)
            self.root.title(f"✦ Notepad — {name}")

    def _write(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))
            self.modified = False
            self.mod_lbl.config(text="")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def _on_close(self):
        if self._ask_save_if_modified():
            self.root.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.tk_setPalette(background=BG, foreground=FG)
    app = NotepadApp(root)
    root.mainloop()