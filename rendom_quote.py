"""
╔══════════════════════════════════════════════════╗
║   KAROO  —  Random Quote Generator               ║
║   Premium GUI Edition  |  by  Mr Selfish         ║
╚══════════════════════════════════════════════════╝
  Run:  python karoo_quote_app.py
  Requires: Python 3.x  (tkinter built-in, no pip needed)
"""

import tkinter as tk
from tkinter import ttk
import random
import math

# ══════════════════════════════════════════════════
#  QUOTE DATABASE
# ══════════════════════════════════════════════════
QUOTES = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "cat": "Motivation"},
    {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein", "cat": "Wisdom"},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius", "cat": "Perseverance"},
    {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon", "cat": "Life"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt", "cat": "Inspiration"},
    {"text": "Spread love everywhere you go. Let no one ever come to you without leaving happier.", "author": "Mother Teresa", "cat": "Love"},
    {"text": "When you reach the end of your rope, tie a knot in it and hang on.", "author": "Franklin D. Roosevelt", "cat": "Perseverance"},
    {"text": "Always remember that you are absolutely unique. Just like everyone else.", "author": "Margaret Mead", "cat": "Humor"},
    {"text": "Do not go where the path may lead, go instead where there is no path and leave a trail.", "author": "Ralph Waldo Emerson", "cat": "Leadership"},
    {"text": "You will face many defeats in life, but never let yourself be defeated.", "author": "Maya Angelou", "cat": "Strength"},
    {"text": "The greatest glory in living lies not in never falling, but in rising every time we fall.", "author": "Nelson Mandela", "cat": "Resilience"},
    {"text": "In the end, it's not the years in your life that count. It's the life in your years.", "author": "Abraham Lincoln", "cat": "Life"},
    {"text": "Never let the fear of striking out keep you from playing the game.", "author": "Babe Ruth", "cat": "Courage"},
    {"text": "Life is either a daring adventure or nothing at all.", "author": "Helen Keller", "cat": "Adventure"},
    {"text": "Many of life's failures are people who did not realize how close they were to success.", "author": "Thomas A. Edison", "cat": "Perseverance"},
    {"text": "You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.", "author": "Dr. Seuss", "cat": "Inspiration"},
    {"text": "If you look at what you have in life, you'll always have more.", "author": "Oprah Winfrey", "cat": "Gratitude"},
    {"text": "If you want to live a happy life, tie it to a goal, not to people or things.", "author": "Albert Einstein", "cat": "Happiness"},
    {"text": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs", "cat": "Life"},
    {"text": "Not how long, but how well you have lived is the main thing.", "author": "Seneca", "cat": "Philosophy"},
    {"text": "All our dreams can come true, if we have the courage to pursue them.", "author": "Walt Disney", "cat": "Dreams"},
    {"text": "It's not whether you get knocked down, it's whether you get up.", "author": "Vince Lombardi", "cat": "Resilience"},
    {"text": "Knowing is not enough; we must apply. Wishing is not enough; we must do.", "author": "Goethe", "cat": "Action"},
    {"text": "We generate fears while we sit. We overcome them by action.", "author": "Dr. Henry Link", "cat": "Courage"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt", "cat": "Motivation"},
    {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill", "cat": "Courage"},
    {"text": "Happiness is not something ready made. It comes from your own actions.", "author": "Dalai Lama", "cat": "Happiness"},
    {"text": "The mind is everything. What you think you become.", "author": "Buddha", "cat": "Wisdom"},
    {"text": "An unexamined life is not worth living.", "author": "Socrates", "cat": "Philosophy"},
    {"text": "Creativity is intelligence having fun.", "author": "Albert Einstein", "cat": "Wisdom"},
]

# ══════════════════════════════════════════════════
#  THEME COLORS
# ══════════════════════════════════════════════════
BG        = "#08080e"
BG_CARD   = "#0f0f18"
BG_CARD2  = "#14141e"
BG_PILL   = "#1a1a26"
GOLD      = "#c9a84c"
GOLD2     = "#f0d080"
GOLD_GLOW = "#7a6428"
GOLD_DARK = "#3a2e10"
WHITE     = "#ede5d4"
SOFT      = "#b0a898"
DIM       = "#555060"
BORDER    = "#2a2535"

CAT_COLORS = {
    "Motivation":   "#f5c842",
    "Wisdom":       "#42d4f5",
    "Perseverance": "#42f584",
    "Life":         "#e842f5",
    "Inspiration":  "#f5e642",
    "Love":         "#f56042",
    "Humor":        "#84f542",
    "Leadership":   "#4284f5",
    "Strength":     "#f58442",
    "Resilience":   "#42f5b8",
    "Courage":      "#f54242",
    "Adventure":    "#42f5f5",
    "Gratitude":    "#c042f5",
    "Happiness":    "#f5f542",
    "Success":      "#f5c842",
    "Philosophy":   "#7ab8f5",
    "Dreams":       "#b842f5",
    "Action":       "#42f5a0",
}


# ══════════════════════════════════════════════════
#  ANIMATED STAR BACKGROUND
# ══════════════════════════════════════════════════
class StarBG(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, bd=0, highlightthickness=0, **kw)
        self._tick  = 0
        self._stars = [
            {
                "x":     random.uniform(0, 1),
                "y":     random.uniform(0, 1),
                "r":     random.uniform(0.6, 2.5),
                "speed": random.uniform(0.0002, 0.0009),
                "phase": random.uniform(0, math.pi * 2),
            }
            for _ in range(70)
        ]
        self._run()

    def _run(self):
        self._tick += 1
        w = self.winfo_width()
        h = self.winfo_height()
        if w > 1 and h > 1:
            self.delete("s")
            for s in self._stars:
                a  = 0.15 + 0.7 * abs(math.sin(
                         self._tick * s["speed"] * 55 + s["phase"]))
                br = int(a * 200)
                c  = f"#{br:02x}{int(br*0.85):02x}{int(br*0.45):02x}"
                cx, cy, r = s["x"]*w, s["y"]*h, s["r"]
                self.create_oval(cx-r, cy-r, cx+r, cy+r,
                                 fill=c, outline="", tags="s")
        self.after(38, self._run)


# ══════════════════════════════════════════════════
#  CUSTOM BUTTON WIDGET
# ══════════════════════════════════════════════════
class FancyBtn(tk.Frame):
    """Bordered label-button with hover glow."""
    def __init__(self, master, text, cmd, primary=False, **kw):
        ibg = GOLD_DARK if primary else BG_PILL
        ifg = GOLD2     if primary else SOFT
        brd = GOLD      if primary else BORDER
        hbg = "#50401a" if primary else "#22223a"
        hfg = GOLD2     if primary else GOLD

        super().__init__(master, bg=brd, padx=1, pady=1, **kw)
        self._lbl = tk.Label(
            self, text=text,
            font=("Georgia", 12, "bold"),
            bg=ibg, fg=ifg,
            padx=26, pady=14,
            cursor="hand2"
        )
        self._lbl.pack(fill="both", expand=True)
        self._lbl.bind("<Button-1>", lambda e: cmd())
        self._lbl.bind("<Enter>",    lambda e: self._lbl.configure(bg=hbg, fg=hfg))
        self._lbl.bind("<Leave>",    lambda e: self._lbl.configure(bg=ibg, fg=ifg))
        self._ibg = ibg
        self._ifg = ifg

    def relabel(self, text, fg=None, bg=None):
        self._lbl.configure(
            text=text,
            fg=fg or self._ifg,
            bg=bg or self._ibg
        )


# ══════════════════════════════════════════════════
#  MAIN APP CLASS
# ══════════════════════════════════════════════════
class KarooApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QUOTES  ✦  Quote Generator  ✦  by Mr Selfish")
        self.geometry("1000x780")
        self.minsize(820, 660)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.filtered      = QUOTES[:]
        self.current_index = 0
        self.history       = []
        self.auto_running  = False

        self._build()
        self._show(random.randint(0, len(self.filtered) - 1))

    # ────────────────────────────────────────────────
    def _build(self):
        # Animated star canvas behind everything
        self.bg_cv = StarBG(self)
        self.bg_cv.place(x=0, y=0, relwidth=1, relheight=1)

        # Overlay container
        root = tk.Frame(self, bg=BG)
        root.place(x=0, y=0, relwidth=1, relheight=1)

        # ── HEADER ────────────────────────────────
        hdr = tk.Frame(root, bg=BG, pady=20)
        hdr.pack(fill="x", padx=40)

        lf = tk.Frame(hdr, bg=BG)
        lf.pack(side="left")
        tk.Label(lf, text="Quotes Generator",
                 font=("Georgia", 32, "bold"),
                 fg=GOLD, bg=BG).pack(side="left", anchor="s")
        tk.Label(lf, text="  ™",
                 font=("Georgia", 13),
                 fg=DIM, bg=BG).pack(side="left", anchor="s", pady=(0, 10))

        rf = tk.Frame(hdr, bg=BG)
        rf.pack(side="right")
        tk.Label(rf, text="D E S I G N E D   B Y",
                 font=("Helvetica", 7), fg=DIM, bg=BG).pack(anchor="e")
        tk.Label(rf, text="✦  Mr Selfish  ✦",
                 font=("Georgia", 17, "italic bold"),
                 fg=GOLD2, bg=BG).pack(anchor="e")

        # Gold divider
        tk.Frame(root, bg=GOLD_GLOW, height=1).pack(fill="x", padx=40, pady=(0, 20))

        # ── CATEGORY PILLS ────────────────────────
        self._build_cats(root)

        # ── QUOTE CARD ────────────────────────────
        self._build_card(root)

        # ── PROGRESS BAR ──────────────────────────
        pf = tk.Frame(root, bg=BG)
        pf.pack(fill="x", padx=40, pady=(12, 2))
        self.prog_var = tk.DoubleVar(value=0)
        sty = ttk.Style()
        sty.theme_use("default")
        sty.configure("G.Horizontal.TProgressbar",
                      troughcolor="#181825",
                      background=GOLD,
                      thickness=5,
                      borderwidth=0)
        ttk.Progressbar(pf, variable=self.prog_var,
                        maximum=100,
                        style="G.Horizontal.TProgressbar").pack(fill="x")

        # ── COUNTER ──
        self.ctr_var = tk.StringVar(value="Quote 1 of 30")
        tk.Label(root, textvariable=self.ctr_var,
                 font=("Helvetica", 9), fg=DIM, bg=BG).pack(pady=(4, 0))

        # ── BUTTONS ───────────────────────────────
        self._build_btns(root)

        # ── FOOTER ────────────────────────────────
        tk.Frame(root, bg=GOLD_GLOW, height=1).pack(fill="x", padx=40, pady=(14, 0))
        tk.Label(root,
                 text="✦   M R   S E L F I S H   ✦   K A R O O   Q U O T E   G E N E R A T O R   ✦   2 0 2 5   ✦",
                 font=("Helvetica", 8), fg=GOLD_GLOW, bg=BG).pack(pady=9)

    # ── Category bar ────────────────────────────────
    def _build_cats(self, parent):
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="x", padx=40, pady=(0, 18))

        cv = tk.Canvas(wrap, bg=BG, height=40, bd=0, highlightthickness=0)
        cv.pack(fill="x", expand=True)

        inn = tk.Frame(cv, bg=BG)
        cv.create_window((0, 0), window=inn, anchor="nw")
        inn.bind("<Configure>", lambda e: cv.configure(
            scrollregion=cv.bbox("all")))

        def _mw(e):
            cv.xview_scroll(int(-1*(e.delta/120)), "units")
        cv.bind("<MouseWheel>", _mw)
        inn.bind("<MouseWheel>", _mw)

        self.pills = {}
        cats = ["All"] + sorted(set(q["cat"] for q in QUOTES))
        for cat in cats:
            lbl = tk.Label(inn, text=cat,
                           font=("Helvetica", 10, "bold"),
                           bg=BG_PILL, fg=DIM,
                           padx=18, pady=7,
                           cursor="hand2")
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda e, c=cat, b=lbl: self._filt(c, b))
            lbl.bind("<Enter>",    lambda e, b=lbl: self._ph(b, True))
            lbl.bind("<Leave>",    lambda e, b=lbl: self._ph(b, False))
            lbl.bind("<MouseWheel>", _mw)
            self.pills[cat] = lbl
        self._active_pill("All")

    def _ph(self, b, on):
        if b.cget("fg") != GOLD:
            b.configure(fg=GOLD if on else DIM,
                        bg="#20203a" if on else BG_PILL)

    def _active_pill(self, cat):
        for c, b in self.pills.items():
            if c == cat:
                b.configure(bg=GOLD_DARK, fg=GOLD2,
                            highlightbackground=GOLD,
                            highlightthickness=1)
            else:
                b.configure(bg=BG_PILL, fg=DIM, highlightthickness=0)

    # ── Quote card ──────────────────────────────────
    def _build_card(self, parent):
        outer = tk.Frame(parent, bg=BG, padx=40)
        outer.pack(fill="both", expand=True)

        self.card = tk.Frame(outer, bg=BG_CARD,
                             highlightbackground=BORDER,
                             highlightthickness=1)
        self.card.pack(fill="both", expand=True)

        inner = tk.Frame(self.card, bg=BG_CARD, padx=56, pady=42)
        inner.pack(fill="both", expand=True)

        # Decorative giant quote mark
        tk.Label(inner, text="\u201c",
                 font=("Georgia", 130, "italic"),
                 fg="#1a1a28", bg=BG_CARD).place(x=-12, y=-36)

        # Category badge
        self.cat_var = tk.StringVar()
        self.cat_lbl = tk.Label(inner, textvariable=self.cat_var,
                                font=("Helvetica", 11, "bold"),
                                bg=BG_CARD2, fg=GOLD,
                                padx=20, pady=7)
        self.cat_lbl.pack(anchor="w", pady=(0, 24))

        # Quote text  — BIG & italic
        self.q_var = tk.StringVar()
        self.q_lbl = tk.Label(inner, textvariable=self.q_var,
                              font=("Georgia", 21, "italic"),
                              fg=WHITE, bg=BG_CARD,
                              wraplength=840,
                              justify="left",
                              anchor="w")
        self.q_lbl.pack(fill="x", pady=(0, 34))

        # Author
        arow = tk.Frame(inner, bg=BG_CARD)
        arow.pack(fill="x")
        tk.Frame(arow, bg=GOLD, width=40, height=2).pack(
            side="left", pady=9, padx=(0, 16))
        self.auth_var = tk.StringVar()
        tk.Label(arow, textvariable=self.auth_var,
                 font=("Georgia", 14, "bold"),
                 fg=GOLD2, bg=BG_CARD).pack(side="left")

    # ── Buttons ─────────────────────────────────────
    def _build_btns(self, parent):
        row = tk.Frame(parent, bg=BG)
        row.pack(pady=18)

        self.b_prev = FancyBtn(row, "← Prev",       self._prev)
        self.b_new  = FancyBtn(row, "✦  New Quote",  self._new,  primary=True)
        self.b_copy = FancyBtn(row, "Copy Quote",    self._copy)
        self.b_auto = FancyBtn(row, "▶  Auto Play",  self._auto)

        for b in [self.b_prev, self.b_new, self.b_copy, self.b_auto]:
            b.pack(side="left", padx=9)

    # ── Quote logic ─────────────────────────────────
    def _filt(self, cat, btn):
        self._active_pill(cat)
        self.filtered = QUOTES[:] if cat == "All" else [
            q for q in QUOTES if q["cat"] == cat]
        self.history = []
        self._show(random.randint(0, len(self.filtered) - 1))

    def _show(self, idx, push=True):
        if not self.filtered:
            return
        idx = max(0, min(idx, len(self.filtered) - 1))
        self.current_index = idx
        if push:
            self.history.append(idx)

        q   = self.filtered[idx]
        col = CAT_COLORS.get(q["cat"], GOLD)

        self.cat_var.set(f"  {q['cat']}  ")
        self.cat_lbl.configure(fg=col)
        self.auth_var.set(q["author"])

        n = len(self.filtered)
        self.ctr_var.set(f"Quote {idx+1} of {n}")
        self.prog_var.set(((idx+1) / n) * 100)

        self._fade(f'\u201c{q["text"]}\u201d')

    def _fade(self, text, step=0, total=18):
        """Fade quote text colour from dark to bright."""
        t = step / total
        r = int(0xed * t)
        g = int(0xe5 * t)
        b = int(0xd4 * t)
        self.q_var.set(text)
        self.q_lbl.configure(fg=f"#{r:02x}{g:02x}{b:02x}")
        if step < total:
            self.after(18, lambda: self._fade(text, step+1, total))
        else:
            self.q_lbl.configure(fg=WHITE)

    def _new(self):
        if len(self.filtered) <= 1:
            return
        idx = self.current_index
        while idx == self.current_index:
            idx = random.randint(0, len(self.filtered)-1)
        self._show(idx)

    def _prev(self):
        if len(self.history) > 1:
            self.history.pop()
            self._show(self.history[-1], push=False)

    def _copy(self):
        q = self.filtered[self.current_index]
        self.clipboard_clear()
        self.clipboard_append(f'"{q["text"]}" — {q["author"]}')
        self._toast("✓  Copied to clipboard!")

    def _auto(self):
        if self.auto_running:
            self.auto_running = False
            self.b_auto.relabel("▶  Auto Play", fg=SOFT, bg=BG_PILL)
        else:
            self.auto_running = True
            self.b_auto.relabel("⏹  Stop", fg=GOLD2, bg=GOLD_DARK)
            self._autoloop()

    def _autoloop(self):
        if not self.auto_running:
            return
        self._new()
        self.after(4200, self._autoloop)

    def _toast(self, msg):
        t = tk.Toplevel(self)
        t.overrideredirect(True)
        t.attributes("-topmost", True)
        t.configure(bg=BG_CARD2)
        tk.Frame(t, bg=GOLD, height=2).pack(fill="x")
        tk.Label(t, text=msg,
                 font=("Georgia", 10, "bold"),
                 fg=GOLD2, bg=BG_CARD2,
                 padx=32, pady=13).pack()
        tk.Frame(t, bg=GOLD, height=2).pack(fill="x")
        self.update_idletasks()
        x = self.winfo_x() + self.winfo_width()//2 - 155
        y = self.winfo_y() + self.winfo_height() - 95
        t.geometry(f"310x46+{x}+{y}")

        def fade(a=1.0):
            if a <= 0:
                t.destroy(); return
            try:
                t.attributes("-alpha", a)
                t.after(38, lambda: fade(round(a-0.06, 2)))
            except Exception:
                pass
        self.after(2000, lambda: fade(1.0))


# ══════════════════════════════════════════════════
if __name__ == "__main__":
    app = KarooApp()
    app.mainloop()