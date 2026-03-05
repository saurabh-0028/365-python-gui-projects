import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

# ── Soft Light Palette ────────────────────────────────────────────────────────
BG         = "#F5F7FA"
PANEL      = "#FFFFFF"
SIDEBAR    = "#EEF2F7"
ACCENT     = "#4F6EF7"
ACCENT2    = "#27AE8F"
DANGER     = "#E05C5C"
TEXT       = "#1A1A2E"
MUTED      = "#8892A4"
CARD_BG    = "#FFFFFF"
BORDER     = "#DDE3ED"
WORD_COLOR = "#4F6EF7"

FONT_TITLE  = ("Segoe UI", 15, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_MUTED  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 11, "bold")
FONT_MONO   = ("Consolas", 13)
FONT_BIG    = ("Segoe UI", 52, "bold")
FONT_STAT_V = ("Segoe UI", 20, "bold")
FONT_STAT_L = ("Segoe UI", 10)
FONT_FILE   = ("Segoe UI", 10)


def count_stats(text: str) -> dict:
    words     = len(text.split()) if text.strip() else 0
    chars_ws  = len(text)
    chars_no  = len(re.sub(r'\s', '', text))
    lines     = text.count("\n") + (1 if text else 0)
    sentences = len(re.findall(r'[^.!?]+[.!?]', text))
    paras     = len([p for p in text.split("\n\n") if p.strip()])
    avg_word  = (chars_no / words) if words else 0
    return dict(
        words=words, chars_ws=chars_ws, chars_no=chars_no,
        lines=lines, sentences=sentences, paras=paras, avg_word=avg_word,
    )


class WordCounterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Word Counter")
        root.configure(bg=BG)
        root.geometry("1000x700")
        root.minsize(800, 580)

        self.filepath = None
        self.stat_vars: dict[str, tk.StringVar] = {}
        self._build_ui()
        self._refresh_stats("")

    def _btn(self, parent, text, cmd, bg, fg="#FFFFFF", width=12):
        return tk.Button(
            parent, text=text, command=cmd,
            font=FONT_BTN, bg=bg, fg=fg,
            activebackground=TEXT, activeforeground="#FFFFFF",
            bd=0, padx=18, pady=9,
            cursor="hand2", relief="flat", width=width,
        )

    def _card(self, parent, label, key, icon=""):
        frame = tk.Frame(parent, bg=CARD_BG, bd=0,
                         highlightthickness=1, highlightbackground=BORDER)
        frame.pack(fill="x", pady=5, ipady=8, ipadx=10)

        top_row = tk.Frame(frame, bg=CARD_BG)
        top_row.pack(fill="x", padx=12, pady=(6, 0))
        tk.Label(top_row, text=icon + "  " + label, font=FONT_STAT_L,
                 bg=CARD_BG, fg=MUTED, anchor="w").pack(side="left")

        v = tk.StringVar(value="0")
        self.stat_vars[key] = v
        tk.Label(frame, textvariable=v, font=FONT_STAT_V,
                 bg=CARD_BG, fg=TEXT, anchor="e").pack(fill="x", padx=12, pady=(2, 6))

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=PANEL,
                          highlightthickness=1, highlightbackground=BORDER)
        header.pack(fill="x")

        inner_h = tk.Frame(header, bg=PANEL, padx=24, pady=14)
        inner_h.pack(fill="x")

        tk.Label(inner_h, text="📄  Word Counter",
                 font=FONT_TITLE, bg=PANEL, fg=TEXT).pack(side="left")

        btn_row = tk.Frame(inner_h, bg=PANEL)
        btn_row.pack(side="right")
        self._btn(btn_row, "📂  Open File",   self._open_file,  ACCENT,  width=13).pack(side="left", padx=5)
        self._btn(btn_row, "📋  Copy Stats",  self._copy_stats, ACCENT2, width=13).pack(side="left", padx=5)
        self._btn(btn_row, "🗑  Clear",       self._clear,      DANGER,  width=10).pack(side="left", padx=5)

        # Body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        # Left – editor
        left = tk.Frame(body, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        ed_header = tk.Frame(left, bg=SIDEBAR, padx=14, pady=10)
        ed_header.pack(fill="x")
        tk.Label(ed_header, text="✏️  Input Text", font=FONT_LABEL,
                 bg=SIDEBAR, fg=TEXT).pack(side="left")
        self.file_lbl = tk.Label(ed_header, text="", font=FONT_FILE,
                                 bg=SIDEBAR, fg=ACCENT2)
        self.file_lbl.pack(side="right")

        text_frame = tk.Frame(left, bg=PANEL)
        text_frame.pack(fill="both", expand=True)

        self.text_area = tk.Text(
            text_frame,
            bg=PANEL, fg=TEXT,
            insertbackground=ACCENT,
            font=FONT_MONO,
            bd=0, padx=16, pady=14,
            wrap="word", undo=True,
            selectbackground=ACCENT,
            selectforeground="#FFFFFF",
            relief="flat",
            highlightthickness=0,
            spacing1=3, spacing3=3,
        )
        self.text_area.pack(side="left", fill="both", expand=True)
        self.text_area.bind("<KeyRelease>", self._on_key)

        sb = tk.Scrollbar(text_frame, command=self.text_area.yview,
                          bg=SIDEBAR, troughcolor=BG,
                          activebackground=ACCENT,
                          width=10, relief="flat", bd=0)
        sb.pack(side="right", fill="y")
        self.text_area["yscrollcommand"] = sb.set

        # Right – stats
        right = tk.Frame(body, bg=BG, width=290)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # Hero word count
        hero = tk.Frame(right, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        hero.pack(fill="x", pady=(0, 6))
        tk.Label(hero, text="TOTAL WORDS", font=("Segoe UI", 11),
                 bg=PANEL, fg=MUTED).pack(pady=(14, 0))
        self.word_big = tk.Label(hero, text="0", font=FONT_BIG,
                                 bg=PANEL, fg=WORD_COLOR)
        self.word_big.pack(pady=(0, 14))

        # Stat cards
        cards = [
            ("Characters (with spaces)", "chars_ws",  "🔤"),
            ("Characters (no spaces)",   "chars_no",  "🔡"),
            ("Lines",                    "lines",     "📏"),
            ("Sentences",                "sentences", "💬"),
            ("Paragraphs",               "paras",     "📝"),
            ("Avg word length",          "avg_word",  "📐"),
        ]
        for label, key, icon in cards:
            self._card(right, label, key, icon)

        # Status bar
        statusbar = tk.Frame(self.root, bg=SIDEBAR,
                             highlightthickness=1, highlightbackground=BORDER,
                             padx=20, pady=8)
        statusbar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Paste text above or open a .txt file.")
        tk.Label(statusbar, textvariable=self.status_var,
                 font=FONT_MUTED, bg=SIDEBAR, fg=MUTED, anchor="w").pack(side="left")

    def _on_key(self, _=None):
        self._refresh_stats(self.text_area.get("1.0", "end-1c"))

    def _refresh_stats(self, text: str):
        s = count_stats(text)
        self.word_big.config(text=str(s["words"]))
        self.stat_vars["chars_ws"].set(str(s["chars_ws"]))
        self.stat_vars["chars_no"].set(str(s["chars_no"]))
        self.stat_vars["lines"].set(str(s["lines"]))
        self.stat_vars["sentences"].set(str(s["sentences"]))
        self.stat_vars["paras"].set(str(s["paras"]))
        self.stat_vars["avg_word"].set(f'{s["avg_word"]:.1f}')

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            return
        self.filepath = path
        self.file_lbl.config(text=f"  {os.path.basename(path)}")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)
        self._refresh_stats(content)
        self.status_var.set(f"✅  Loaded: {path}")

    def _clear(self):
        self.text_area.delete("1.0", "end")
        self.filepath = None
        self.file_lbl.config(text="")
        self._refresh_stats("")
        self.status_var.set("🗑  Cleared.")

    def _copy_stats(self):
        text = self.text_area.get("1.0", "end-1c")
        s = count_stats(text)
        summary = (
            f"Words                    : {s['words']}\n"
            f"Characters (with spaces) : {s['chars_ws']}\n"
            f"Characters (no spaces)   : {s['chars_no']}\n"
            f"Lines                    : {s['lines']}\n"
            f"Sentences                : {s['sentences']}\n"
            f"Paragraphs               : {s['paras']}\n"
            f"Avg word length          : {s['avg_word']:.1f}\n"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(summary)
        self.status_var.set("📋  Stats copied to clipboard!")


if __name__ == "__main__":
    root = tk.Tk()
    app = WordCounterApp(root)
    root.mainloop()