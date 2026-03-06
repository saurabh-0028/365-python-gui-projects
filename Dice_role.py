import tkinter as tk
import random
import threading
import math
import winsound

# ═══════════════════════════════════════════════════════════════════════════════
# SOUND — winsound confirmed working, WAV files pre-generated
# ═══════════════════════════════════════════════════════════════════════════════

# ── Sound: Windows built-in alias — confirmed working ────────────────────────
def play_land():
    """Play Windows built-in sound — no WAV file needed, always works."""
    def _go():
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except Exception:
            pass
    threading.Thread(target=_go, daemon=True).start()

def play_tick(): pass
def play_roll(): pass

# ═══════════════════════════════════════════════════════════════════════════════
# DOTS
# ═══════════════════════════════════════════════════════════════════════════════
DOTS = {
    1: [(0.5, 0.5)],
    2: [(0.28, 0.28), (0.72, 0.72)],
    3: [(0.28, 0.28), (0.5,  0.5),  (0.72, 0.72)],
    4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
    5: [(0.28, 0.28), (0.72, 0.28), (0.5,  0.5),  (0.28, 0.72), (0.72, 0.72)],
    6: [(0.28, 0.22), (0.72, 0.22), (0.28, 0.5),  (0.72, 0.5),
        (0.28, 0.78), (0.72, 0.78)],
}

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BG        = "#1a1a2e"
PANEL     = "#16213e"
CARD      = "#0f3460"
ACCENT    = "#e94560"
GOLD      = "#f5a623"
CREAM     = "#eaeaea"
MUTED     = "#8892a4"
DICE_BG   = "#ffffff"
DICE_DOT  = "#1a1a2e"
SHADOW    = "#0a0a18"
BTN_BG    = "#e94560"
BTN_HOV   = "#ff6b81"
BTN_DIS   = "#555577"
CREDIT_FG = "#00e5ff"

# ═══════════════════════════════════════════════════════════════════════════════
# DICE WIDGET  — Ludo-style shake → settle → land
# ═══════════════════════════════════════════════════════════════════════════════
class DiceFace(tk.Canvas):
    SIZE = 155

    def __init__(self, parent, **kw):
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         bg=PANEL, highlightthickness=0, **kw)
        self._draw_at(1)

    def set_value(self, v):
        self.delete("all")
        self._draw_at(v)

    def animate_roll(self, final_val, done_cb=None):
        schedule = []
        for i in range(14):                              # fast shake
            schedule.append((i * 45, "shake", i))
        for j, d in enumerate([640, 720, 820, 930]):    # slow settle
            schedule.append((d, "settle", j))
        schedule.append((1060, "land", final_val))       # land

        for (delay, phase, arg) in schedule:
            self.after(delay,
                       lambda ph=phase, a=arg, fv=final_val, cb=done_cb:
                       self._frame(ph, a, fv, cb))

    def _frame(self, phase, arg, final_val, done_cb):
        self.delete("all")
        if phase == "shake":
            i  = arg
            ox = int(math.sin(i * 1.9) * 7 * max(0, 1 - i / 14))
            oy = int(math.cos(i * 2.3) * 5 * max(0, 1 - i / 14))
            self._draw_at(random.randint(1, 6), ox=ox, oy=oy, glow=True)
            play_tick()
        elif phase == "settle":
            self._draw_at(random.randint(1, 6), glow=True)
        elif phase == "land":
            self._draw_at(final_val, glow=False)
            play_land()
            if done_cb:
                done_cb()

    def _draw_at(self, value, ox=0, oy=0, glow=False):
        s, r, m = self.SIZE, 22, 5
        if glow:
            self.create_rectangle(ox+2, oy+2, s+ox-4, s+oy-4,
                                  fill="", outline=GOLD, width=3)
        self.create_rectangle(ox+8, oy+8, s+ox-3, s+oy-3,
                               fill=SHADOW, outline="")
        self._rrect(ox+m, oy+m, ox+s-m-3, oy+s-m-3, r,
                    fill=DICE_BG, outline=GOLD, width=3)
        dot_r  = 12
        inner  = s - m * 2 - 3
        for (fx, fy) in DOTS[value]:
            cx = ox + m + 10 + fx * (inner - 20)
            cy = oy + m + 10 + fy * (inner - 20)
            self.create_oval(cx-dot_r+1, cy-dot_r+2,
                             cx+dot_r+1, cy+dot_r+2,
                             fill="#bbbbbb", outline="")
            self.create_oval(cx-dot_r, cy-dot_r,
                             cx+dot_r, cy+dot_r,
                             fill=DICE_DOT, outline="")

    def _rrect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1,  x2-r, y1,  x2,   y1,   x2,   y1+r,
               x2,   y2-r, x2,  y2,  x2-r, y2,   x1+r, y2,
               x1,   y2,   x1,  y2-r, x1,  y1+r, x1,   y1, x1+r, y1]
        self.create_polygon(pts, smooth=True, **kw)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
class DiceRollerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎲  Dice Roller  —  Mr. Selfish")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._num_dice  = tk.IntVar(value=2)
        self._total_var = tk.StringVar(value="—")
        self._history   = []
        self._rolling   = False
        self._build_ui()
        self._center()

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", pady=(28, 4))
        tk.Label(hdr, text="🎲  DICE  ROLLER",
                 bg=BG, fg=CREAM,
                 font=("Helvetica", 34, "bold")).pack()
        tk.Label(hdr, text="Roll the luck  ·  Feel the rush",
                 bg=BG, fg=MUTED,
                 font=("Helvetica", 13)).pack(pady=(4, 0))

        tk.Label(self, text="🔊 Sound: ON",
                 bg=BG, fg="#4caf50",
                 font=("Helvetica", 10)).pack(pady=(4, 0))

        tk.Frame(self, bg=GOLD, height=3).pack(fill="x", padx=40, pady=(12, 18))

        # ── Dice count ──
        sel = tk.Frame(self, bg=PANEL, pady=14)
        sel.pack(fill="x", padx=40)
        tk.Label(sel, text="   HOW MANY DICE?",
                 bg=PANEL, fg=MUTED,
                 font=("Helvetica", 12, "bold")).pack(side="left")
        bf = tk.Frame(sel, bg=PANEL)
        bf.pack(side="right", padx=10)
        for n in range(1, 7):
            tk.Radiobutton(
                bf, text=f"  {n}  ",
                variable=self._num_dice, value=n,
                bg=PANEL, fg=CREAM, selectcolor=ACCENT,
                activebackground=PANEL, activeforeground=GOLD,
                font=("Helvetica", 14, "bold"),
                indicatoron=False, relief="flat",
                padx=14, pady=7, cursor="hand2",
                command=self._rebuild_dice_row,
            ).pack(side="left", padx=3)

        # ── Dice area ──
        outer = tk.Frame(self, bg=PANEL)
        outer.pack(fill="x", padx=40, pady=(2, 0))
        self._dice_frame = tk.Frame(outer, bg=PANEL)
        self._dice_frame.pack(pady=26)
        self._dice_faces = []
        self._rebuild_dice_row()

        # ── Total ──
        tot = tk.Frame(self, bg=CARD, pady=16)
        tot.pack(fill="x", padx=40, pady=(18, 0))
        tk.Label(tot, text="TOTAL SCORE",
                 bg=CARD, fg=MUTED,
                 font=("Helvetica", 12, "bold")).pack()
        tk.Label(tot, textvariable=self._total_var,
                 bg=CARD, fg=GOLD,
                 font=("Helvetica", 56, "bold")).pack()

        # ── Roll button ──
        self._btn = tk.Button(
            self, text="  🎲   R O L L   D I C E  ",
            command=self._roll,
            bg=BTN_BG, fg="white",
            activebackground=BTN_HOV, activeforeground="white",
            font=("Helvetica", 17, "bold"),
            relief="flat", bd=0,
            padx=20, pady=15, cursor="hand2",
        )
        self._btn.pack(pady=22, padx=40, fill="x")
        self._btn.bind("<Enter>", lambda e: self._btn.config(bg=BTN_HOV))
        self._btn.bind("<Leave>", lambda e: self._btn.config(bg=BTN_BG))

        # ── History ──
        tk.Frame(self, bg=MUTED, height=1).pack(fill="x", padx=40)
        tk.Label(self, text="📜  ROLL HISTORY",
                 bg=BG, fg=MUTED,
                 font=("Helvetica", 11, "bold")).pack(pady=(10, 3))
        self._history_var = tk.StringVar(value="No rolls yet...")
        tk.Label(self, textvariable=self._history_var,
                 bg=BG, fg=CREAM,
                 font=("Helvetica", 12),
                 justify="center").pack(pady=(0, 8))

        # ── Credit ──
        tk.Frame(self, bg=GOLD, height=2).pack(fill="x", padx=40, pady=(6, 0))
        tk.Label(self, text="⚡  Designed by  Mr. Selfish  ⚡",
                 bg=BG, fg=CREDIT_FG,
                 font=("Helvetica", 15, "bold italic")).pack(pady=(10, 18))

    def _rebuild_dice_row(self):
        for w in self._dice_frame.winfo_children():
            w.destroy()
        self._dice_faces.clear()
        for _ in range(self._num_dice.get()):
            df = DiceFace(self._dice_frame)
            df.pack(side="left", padx=10)
            self._dice_faces.append(df)

    def _roll(self):
        if self._rolling:
            return
        self._rolling = True
        self._total_var.set("…")
        self._btn.config(state="disabled", bg=BTN_DIS,
                         text="  ⏳   R O L L I N G . . .  ")
        play_roll()   # 🔊 whoosh immediately on click

        results = [random.randint(1, 6) for _ in self._dice_faces]
        pending = [len(self._dice_faces)]

        def on_die_done():
            pending[0] -= 1
            if pending[0] == 0:
                total = sum(results)
                self._total_var.set(str(total))
                self._update_history(results, total)
                self._rolling = False
                self._btn.config(state="normal", bg=BTN_BG,
                                 text="  🎲   R O L L   D I C E  ")

        for i, df in enumerate(self._dice_faces):
            val = results[i]
            self.after(i * 80,
                       lambda d=df, v=val: d.animate_roll(v, done_cb=on_die_done))

    def _update_history(self, results, total):
        self._history.append((results, total))
        if len(self._history) > 5:
            self._history.pop(0)
        lines = []
        for i, (res, tot) in enumerate(reversed(self._history)):
            faces = "  ".join(f"[{v}]" for v in res)
            marker = "▶" if i == 0 else " "
            lines.append(f" {marker}  {faces}   →   Total : {tot}")
        self._history_var.set("\n".join(lines))

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def destroy(self):
        super().destroy()


if __name__ == "__main__":
    app = DiceRollerApp()
    app.mainloop()