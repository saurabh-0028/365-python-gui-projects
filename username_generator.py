import tkinter as tk
from tkinter import ttk
import random
import string
import time
import threading

# ─── DATA POOLS ─────────────────────────────────────────────────────────────

ADJECTIVES = [
    "silent", "cosmic", "neon", "shadow", "frozen", "blazing", "dark",
    "swift", "bold", "mystic", "electric", "void", "lunar", "solar",
    "atomic", "crimson", "obsidian", "phantom", "toxic", "savage",
    "stellar", "hyper", "rogue", "alpha", "stealth", "rebel", "nova",
    "fierce", "ultra", "glitch", "cyber", "ghost", "iron", "acid",
    "storm", "ember", "frost", "wild", "steel", "chrome"
]

NOUNS = [
    "wolf", "viper", "hawk", "cipher", "nexus", "byte", "pixel",
    "grid", "blade", "comet", "drifter", "spark", "phantom", "signal",
    "apex", "pulse", "titan", "core", "flux", "zero", "raven",
    "knight", "ghost", "storm", "forge", "matrix", "vector", "link",
    "shell", "echo", "night", "drift", "surge", "glitch", "void",
    "node", "orbit", "rift", "turbo", "reaper"
]

PREFIXES = ["xX", "_", "its", "im", "real", "the", "iam", "mr", "just",
            "official", "og", "not", "dark", "neo", "pro", "sub", "dev"]
SUFFIXES = ["Xx", "_", "99", "00", "404", "777", "x", "pro", "gg",
            "real", "og", "dev", "xyz", "hq", "io"]

# ─── GENERATOR LOGIC ────────────────────────────────────────────────────────

def generate_usernames(style, count=10, use_numbers=True, use_symbols=True, length_limit=16):
    results = []
    for _ in range(count):
        adj = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        num = str(random.randint(1, 999)) if use_numbers else ""
        sym = random.choice(["_", ".", "-", ""]) if use_symbols else ""

        if style == "Classic":
            base = f"{adj}{sym}{noun}{num}"
        elif style == "Gamer Tag":
            prefix = random.choice(PREFIXES) if random.random() > 0.4 else ""
            suffix = random.choice(SUFFIXES) if random.random() > 0.4 else ""
            base = f"{prefix}{adj}{noun}{suffix}"
        elif style == "Professional":
            base = f"{adj}{noun}" + (f"{num[:2]}" if use_numbers else "")
        elif style == "Minimalist":
            base = f"{adj[:4]}{noun[:4]}{num[:2] if use_numbers else ''}"
        elif style == "Edgy / Dark":
            prefix = random.choice(["xX", "_", "dark", "void", "neo"])
            suffix = random.choice(["Xx", "_", "404", "666", "x"])
            base = f"{prefix}_{adj}{noun}_{suffix}"
        elif style == "Random Chaos":
            chars = string.ascii_letters + (string.digits if use_numbers else "")
            base = ''.join(random.choices(chars, k=random.randint(6, 12)))
        else:
            base = f"{adj}{noun}"

        results.append(base[:length_limit])
    return results


# ─── ROUNDED BUTTON ──────────────────────────────────────────────────────────

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, fg_color, hover_color,
                 width=160, height=44, radius=22, font=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.radius = radius
        self.w = width
        self.h = height
        self.font = font or ("Segoe UI", 11, "bold")
        self.text = text
        self._draw(bg_color)
        self.bind("<Enter>", lambda e: self._draw(hover_color))
        self.bind("<Leave>", lambda e: self._draw(bg_color))
        self.bind("<Button-1>", lambda e: command())

    def _draw(self, color):
        self.delete("all")
        r, w, h = self.radius, self.w, self.h
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h-r, fill=color, outline=color)
        self.create_text(w//2, h//2, text=self.text, fill=self.fg_color, font=self.font)


# ─── MAIN APP ────────────────────────────────────────────────────────────────

class UsernameGeneratorApp:
    BG       = "#1a1b2e"
    SURFACE  = "#22233a"
    SURFACE2 = "#2a2b45"
    ACCENT   = "#7c83fd"
    ACCENT2  = "#fd7c7c"
    GREEN    = "#7cfdb0"
    FG       = "#e8e9ff"
    MUTED    = "#6b6d8a"
    BORDER   = "#32345a"

    def __init__(self, root):
        self.root = root
        self.root.title("Username Forge  ·  by Mr. Selfish")
        self.root.geometry("820x800")
        self.root.resizable(True, True)
        self.root.configure(bg=self.BG)
        self.root.minsize(700, 650)
        self.usernames = []

        self.f_title  = ("Segoe UI", 28, "bold")
        self.f_sub    = ("Segoe UI", 12)
        self.f_label  = ("Segoe UI", 13, "bold")
        self.f_body   = ("Segoe UI", 12)
        self.f_list   = ("Consolas", 15)
        self.f_btn    = ("Segoe UI", 12, "bold")
        self.f_status = ("Segoe UI", 11)
        self.f_tag    = ("Segoe UI", 10)

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("C.TCombobox",
                    fieldbackground=self.SURFACE2,
                    background=self.SURFACE2,
                    foreground=self.FG,
                    arrowcolor=self.ACCENT,
                    bordercolor=self.BORDER,
                    lightcolor=self.SURFACE2,
                    darkcolor=self.SURFACE2,
                    selectbackground=self.SURFACE2,
                    selectforeground=self.FG,
                    padding=8)
        s.map("C.TCombobox", fieldbackground=[("readonly", self.SURFACE2)],
              foreground=[("readonly", self.FG)])

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=self.BG)
        hdr.pack(fill="x", padx=40, pady=(30, 0))

        tk.Label(hdr, text="Username Forge", font=self.f_title,
                 fg=self.FG, bg=self.BG).pack(side="left")
        tk.Label(hdr, text="by Mr. Selfish", font=self.f_tag,
                 fg=self.ACCENT2, bg=self.BG).pack(side="right", pady=(16, 0))

        tk.Label(self.root, text="Generate cool usernames in one click",
                 font=self.f_sub, fg=self.MUTED, bg=self.BG).pack(anchor="w", padx=40, pady=(4, 0))

        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x", padx=40, pady=(18, 22))

        # ── Config Card ─────────────────────────────────────────────────────
        card = tk.Frame(self.root, bg=self.SURFACE,
                        highlightthickness=1, highlightbackground=self.BORDER)
        card.pack(fill="x", padx=40)

        inner = tk.Frame(card, bg=self.SURFACE)
        inner.pack(fill="x", padx=28, pady=22)

        # Row 1: Style / Count / Length
        row1 = tk.Frame(inner, bg=self.SURFACE)
        row1.pack(fill="x", pady=(0, 20))

        self._col(row1, "Style")
        self.style_var = tk.StringVar(value="Classic")
        styles = ["Classic", "Gamer Tag", "Professional", "Minimalist", "Edgy / Dark", "Random Chaos"]
        cb = ttk.Combobox(row1, textvariable=self.style_var, values=styles,
                          state="readonly", width=15, style="C.TCombobox",
                          font=("Segoe UI", 12))
        cb.pack(side="left", padx=(0, 32))

        self._col(row1, "Count")
        self.count_var = tk.IntVar(value=10)
        self._spin(row1, self.count_var, 1, 50)

        self._col(row1, "Max Length")
        self.len_var = tk.IntVar(value=16)
        self._spin(row1, self.len_var, 6, 30)

        # Row 2: Toggles
        row2 = tk.Frame(inner, bg=self.SURFACE)
        row2.pack(fill="x")

        tk.Label(row2, text="Include:", font=self.f_label,
                 fg=self.MUTED, bg=self.SURFACE).pack(side="left", padx=(0, 16))

        self.use_nums = tk.BooleanVar(value=True)
        self.use_syms = tk.BooleanVar(value=True)
        self._pill(row2, "  Numbers  ", self.use_nums)
        self._pill(row2, "  Symbols ( _ . - )  ", self.use_syms)

        # ── Generate Button ──────────────────────────────────────────────────
        btn_wrap = tk.Frame(self.root, bg=self.BG)
        btn_wrap.pack(pady=(20, 18))

        self.gen_btn = RoundedButton(
            btn_wrap, text="⚡  Generate Usernames",
            command=self._on_generate,
            bg_color=self.ACCENT, fg_color=self.BG,
            hover_color="#9ba3ff",
            width=240, height=52, radius=26,
            font=("Segoe UI", 14, "bold")
        )
        self.gen_btn.pack()

        # ── Results Header ────────────────────────────────────────────────────
        rh = tk.Frame(self.root, bg=self.BG)
        rh.pack(fill="x", padx=40, pady=(0, 8))
        tk.Label(rh, text="Results", font=self.f_label,
                 fg=self.MUTED, bg=self.BG).pack(side="left")
        self.count_badge = tk.Label(rh, text="", font=("Segoe UI", 11),
                                    fg=self.ACCENT, bg=self.BG)
        self.count_badge.pack(side="left", padx=(10, 0))

        # ── Listbox ───────────────────────────────────────────────────────────
        lc = tk.Frame(self.root, bg=self.SURFACE,
                      highlightthickness=1, highlightbackground=self.BORDER)
        lc.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        sb = tk.Scrollbar(lc, bg=self.SURFACE2, troughcolor=self.SURFACE,
                          activebackground=self.ACCENT, relief="flat", width=8, bd=0)
        sb.pack(side="right", fill="y", padx=(0, 6), pady=10)

        self.listbox = tk.Listbox(
            lc, font=self.f_list,
            bg=self.SURFACE, fg=self.FG,
            selectbackground=self.ACCENT, selectforeground=self.BG,
            activestyle="none", relief="flat", bd=0,
            yscrollcommand=sb.set, highlightthickness=0,
            cursor="hand2", selectmode="single"
        )
        self.listbox.pack(fill="both", expand=True, padx=16, pady=14)
        sb.config(command=self.listbox.yview)
        self.listbox.bind("<Double-Button-1>", self._copy_selected)

        # ── Bottom Bar ─────────────────────────────────────────────────────────
        bot = tk.Frame(self.root, bg=self.BG)
        bot.pack(fill="x", padx=40, pady=(0, 22))

        self.status_var = tk.StringVar(value="Ready  ·  Double-click any username to copy")
        self.status_lbl = tk.Label(bot, textvariable=self.status_var,
                                   font=self.f_status, fg=self.MUTED, bg=self.BG)
        self.status_lbl.pack(side="left")

        RoundedButton(bot, "Copy All", self._copy_all,
                      bg_color=self.SURFACE2, fg_color=self.FG,
                      hover_color=self.BORDER, width=110, height=36,
                      radius=18, font=("Segoe UI", 10, "bold")).pack(side="right", padx=(8, 0))

        RoundedButton(bot, "Clear", self._clear,
                      bg_color=self.SURFACE2, fg_color=self.FG,
                      hover_color=self.BORDER, width=90, height=36,
                      radius=18, font=("Segoe UI", 10, "bold")).pack(side="right")

    # ── Widget Helpers ────────────────────────────────────────────────────────

    def _col(self, parent, label):
        tk.Label(parent, text=label, font=self.f_label,
                 fg=self.ACCENT, bg=self.SURFACE).pack(side="left", padx=(0, 6))

    def _spin(self, parent, var, lo, hi):
        s = tk.Spinbox(parent, from_=lo, to=hi, textvariable=var,
                       width=5, font=("Segoe UI", 13),
                       bg=self.SURFACE2, fg=self.FG,
                       insertbackground=self.ACCENT,
                       buttonbackground=self.BORDER,
                       relief="flat",
                       highlightthickness=1, highlightcolor=self.ACCENT,
                       highlightbackground=self.BORDER)
        s.pack(side="left", padx=(0, 32))
        return s

    def _pill(self, parent, text, var):
        def colors():
            return (self.ACCENT, self.BG) if var.get() else (self.SURFACE2, self.MUTED)

        lbl = tk.Label(parent, text=text, font=("Segoe UI", 11),
                       cursor="hand2", padx=6, pady=6, relief="flat")

        def refresh():
            bg, fg = colors()
            lbl.config(bg=bg, fg=fg)

        def toggle(e=None):
            var.set(not var.get())
            refresh()

        refresh()
        lbl.pack(side="left", padx=(0, 10))
        lbl.bind("<Button-1>", toggle)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _on_generate(self):
        self.listbox.delete(0, tk.END)
        self.usernames = []
        self.count_badge.config(text="")
        self._status("Generating...", self.ACCENT)
        self.gen_btn.config(state="disabled")

        def run():
            names = generate_usernames(
                style=self.style_var.get(),
                count=self.count_var.get(),
                use_numbers=self.use_nums.get(),
                use_symbols=self.use_syms.get(),
                length_limit=self.len_var.get()
            )
            for i, name in enumerate(names):
                time.sleep(0.04)
                self.root.after(0, self._add_item, i, name)
            self.root.after(0, self._done, len(names))

        threading.Thread(target=run, daemon=True).start()

    def _add_item(self, i, name):
        self.listbox.insert(tk.END, f"   {str(i+1).rjust(2,'0')}    {name}")
        self.usernames.append(name)
        self.listbox.see(tk.END)

    def _done(self, n):
        self._status(f"{n} usernames ready  ·  Double-click any to copy", self.MUTED)
        self.count_badge.config(text=f"({n})")
        self.gen_btn.config(state="normal")

    def _copy_selected(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        raw = self.listbox.get(sel[0]).strip()
        parts = raw.split(None, 1)
        name = parts[1].strip() if len(parts) > 1 else raw
        try:
            import pyperclip
            pyperclip.copy(name)
            self._status(f"✓  Copied:  {name}", self.GREEN)
            self.root.after(2500, lambda: self._status(
                f"{len(self.usernames)} usernames ready  ·  Double-click any to copy", self.MUTED))
        except Exception:
            self._status(f"Selected: {name}  (pip install pyperclip to enable copy)", self.MUTED)

    def _copy_all(self):
        if not self.usernames:
            return
        try:
            import pyperclip
            pyperclip.copy("\n".join(self.usernames))
            self._status(f"✓  All {len(self.usernames)} usernames copied to clipboard!", self.GREEN)
            self.root.after(2500, lambda: self._status(
                f"{len(self.usernames)} usernames ready  ·  Double-click any to copy", self.MUTED))
        except Exception:
            self._status("Install pyperclip for clipboard support", self.MUTED)

    def _clear(self):
        self.listbox.delete(0, tk.END)
        self.usernames = []
        self.count_badge.config(text="")
        self._status("Cleared  ·  Ready", self.MUTED)

    def _status(self, msg, color):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color)


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "pip", "install", "pyperclip", "--quiet"],
                       check=False)

    root = tk.Tk()
    app = UsernameGeneratorApp(root)
    root.mainloop()