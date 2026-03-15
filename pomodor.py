## Pomodoro Timer — Designed by Mr. Selfish
# Run: python pomodoro_timer.py

import tkinter as tk
from tkinter import font as tkfont
import math, time, threading, platform

# ─────────────────────────────────────────────────────────────────────────────
#  THEMES  (each mode gets its own full colour identity)
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "Focus": {
        "duration": 25 * 60,
        "label":    "FOCUS",
        "accent":   "#E8504A",
        "glow":     "#FF6B6B",
        "bg_top":   "#1C0A08",
        "bg_bot":   "#0A0A0A",
        "track":    "#2C1210",
        "inner":    "#160808",
    },
    "Short Break": {
        "duration":  5 * 60,
        "label":    "SHORT BREAK",
        "accent":   "#2BB5AE",
        "glow":     "#4ECDC4",
        "bg_top":   "#061817",
        "bg_bot":   "#0A0A0A",
        "track":    "#0C2624",
        "inner":    "#071413",
    },
    "Long Break": {
        "duration": 15 * 60,
        "label":    "LONG BREAK",
        "accent":   "#8B72E0",
        "glow":     "#A78BFA",
        "bg_top":   "#100B1E",
        "bg_bot":   "#0A0A0A",
        "track":    "#1A1030",
        "inner":    "#0D0918",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  FIXED COLOURS
# ─────────────────────────────────────────────────────────────────────────────
C_CHROME   = "#1A1A1A"   # titlebar background
C_CHROME_H = "#242424"   # hover
C_TEXT     = "#EDEDED"
C_DIM      = "#3A3A3A"
C_MID      = "#666666"
C_BTN      = "#1E1E1E"
C_BTN_H    = "#2C2C2C"
C_BORDER   = "#2A2A2A"

FPS    = 60
LERP_S = 0.06   # colour lerp speed

# ─────────────────────────────────────────────────────────────────────────────
#  COLOUR HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def h2rgb(h):
    h = h.lstrip("#")[:6]
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_c(a, b, t):
    t = max(0.0, min(1.0, t))
    t = t * t * (3 - 2 * t)
    r1,g1,b1 = h2rgb(a); r2,g2,b2 = h2rgb(b)
    return "#{:02X}{:02X}{:02X}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

def dim(col, factor=0.45):
    r,g,b = h2rgb(col)
    return "#{:02X}{:02X}{:02X}".format(int(r*factor),int(g*factor),int(b*factor))

# ─────────────────────────────────────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────────────────────────────────────
class Pomodoro(tk.Tk):
    # ── init ──────────────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()
        self.title("")
        self.overrideredirect(True)          # borderless — custom chrome
        self.resizable(True, True)

        # Base geometry
        self.BASE_W, self.BASE_H = 480, 660
        self._win_w = self.BASE_W
        self._win_h = self.BASE_H
        self._is_maximized = False
        self._normal_geo   = f"{self.BASE_W}x{self.BASE_H}+200+80"
        self.geometry(self._normal_geo)

        # Drag state
        self._drag_x = self._drag_y = 0

        # Timer
        self.mode_key  = "Focus"
        self.th        = THEMES["Focus"]
        self.time_left = self.th["duration"]
        self.running   = False
        self.sessions  = 0

        # Animated colour state
        def _cs(k): return dict(cur=k, frm=k, to=k, t=1.0)
        self._A  = _cs(self.th["accent"])
        self._G  = _cs(self.th["glow"])
        self._BT = _cs(self.th["bg_top"])
        self._BB = _cs(self.th["bg_bot"])
        self._TK = _cs(self.th["track"])
        self._IN = _cs(self.th["inner"])

        # Ring
        self._ring        = 360.0
        self._ring_target = 360.0

        # Pulse
        self._pulse_ph  = 0.0
        self._pulse_amp = 0.0

        self._build()
        self._loop()

    # ── responsive scale ──────────────────────────────────────────────────────
    @property
    def _sx(self): return self._win_w / self.BASE_W
    @property
    def _sy(self): return self._win_h / self.BASE_H

    def _s(self, v):
        """Scale a value by the smaller axis to keep ring circular."""
        return int(v * min(self._sx, self._sy))

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        self.configure(bg="#0A0A0A")

        # ── Custom title bar ──────────────────────────────────────────────────
        self.titlebar = tk.Frame(self, bg=C_CHROME, height=38, cursor="fleur")
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)

        # App name in titlebar
        tk.Label(self.titlebar, text="  🍅  Pomodoro  ·  Mr. Selfish",
                 bg=C_CHROME, fg=C_MID,
                 font=("Segoe UI", 9)).pack(side="left", padx=8)

        # Window controls (right side)
        ctrl = tk.Frame(self.titlebar, bg=C_CHROME)
        ctrl.pack(side="right", padx=4)

        self._btn_min = self._wc_btn(ctrl, "—", self._minimize, "#3A3A3A", "#F0C030")
        self._btn_min.pack(side="left", padx=2)
        self._btn_max = self._wc_btn(ctrl, "□", self._toggle_maximize, "#3A3A3A", "#34C749")
        self._btn_max.pack(side="left", padx=2)
        self._btn_cls = self._wc_btn(ctrl, "✕", self.destroy,           "#3A3A3A", "#FF5F56")
        self._btn_cls.pack(side="left", padx=2)

        # Drag titlebar
        self.titlebar.bind("<ButtonPress-1>",   self._drag_start)
        self.titlebar.bind("<B1-Motion>",        self._drag_move)

        # ── Resize grip (bottom-right) ────────────────────────────────────────
        self.grip = tk.Label(self, text="⊡", bg="#0A0A0A", fg=C_DIM,
                              font=("Arial", 10), cursor="size_nw_se")
        self.grip.place(relx=1.0, rely=1.0, anchor="se", x=-2, y=-2)
        self.grip.bind("<ButtonPress-1>",  self._resize_start)
        self.grip.bind("<B1-Motion>",      self._resize_move)

        # ── Main canvas ───────────────────────────────────────────────────────
        self.cv = tk.Canvas(self, bg="#0A0A0A", highlightthickness=0)
        self.cv.pack(fill="both", expand=True)

        # ── Overlay widgets (placed on canvas via window_create) ──────────────
        # Mode pills container
        self._pill_frame = tk.Frame(self.cv, bg="#0A0A0A")
        self._pills = {}
        for mode, th in THEMES.items():
            b = tk.Label(self._pill_frame, text=th["label"],
                         bg=C_BTN, fg=C_MID,
                         font=("Segoe UI", 8, "bold"),
                         padx=12, pady=5, cursor="hand2")
            b.pack(side="left", padx=4)
            b.bind("<Button-1>", lambda e, m=mode: self._set_mode(m))
            b.bind("<Enter>",    lambda e, w=b: w.config(bg=C_BTN_H))
            b.bind("<Leave>",    lambda e, w=b: self._pill_leave(w))
            self._pills[mode] = b
        self._pill_win = self.cv.create_window(0, 0, window=self._pill_frame, anchor="n")
        self._refresh_pills()

        # Start / Pause button
        self._btn_start_w = tk.Label(self.cv,
                                     text="▶   START",
                                     bg=C_BTN, fg=C_TEXT,
                                     font=("Segoe UI", 13, "bold"),
                                     padx=32, pady=12, cursor="hand2")
        self._btn_start_w.bind("<Button-1>", lambda e: self._toggle())
        self._btn_start_w.bind("<Enter>",    lambda e: self._btn_start_w.config(bg=C_BTN_H))
        self._btn_start_w.bind("<Leave>",    lambda e: self._btn_start_w.config(bg=C_BTN))
        self._bsw = self.cv.create_window(0, 0, window=self._btn_start_w, anchor="center")

        # Reset button
        self._btn_reset_w = tk.Label(self.cv, text="↺",
                                      bg=C_BTN, fg=C_MID,
                                      font=("Segoe UI", 15, "bold"),
                                      padx=14, pady=12, cursor="hand2")
        self._btn_reset_w.bind("<Button-1>", lambda e: self._reset())
        self._btn_reset_w.bind("<Enter>",    lambda e: self._btn_reset_w.config(bg=C_BTN_H))
        self._btn_reset_w.bind("<Leave>",    lambda e: self._btn_reset_w.config(bg=C_BTN))
        self._brw = self.cv.create_window(0, 0, window=self._btn_reset_w, anchor="center")

        # Session dots
        self._dot_frame = tk.Frame(self.cv, bg="#0A0A0A")
        self._dot_cvs = []
        for _ in range(4):
            dc = tk.Canvas(self._dot_frame, width=10, height=10,
                           bg="#0A0A0A", highlightthickness=0)
            dc.pack(side="left", padx=5)
            dc.create_oval(1,1,9,9, fill=C_DIM, outline="", tags="d")
            self._dot_cvs.append(dc)
        self._dfw = self.cv.create_window(0, 0, window=self._dot_frame, anchor="center")

        # Credit label
        self._cred = tk.Label(self.cv, text="Designed by Mr. Selfish",
                               bg="#0A0A0A", fg=C_DIM,
                               font=("Segoe UI", 7, "italic"))
        self._credw = self.cv.create_window(0, 0, window=self._cred, anchor="s")

        self.cv.bind("<Configure>", self._on_resize)

    def _wc_btn(self, parent, sym, cmd, bg_n, bg_h):
        b = tk.Label(parent, text=sym, bg=bg_n, fg=C_MID,
                     font=("Arial", 9, "bold"),
                     width=3, height=1, cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=bg_h, fg="#FFFFFF"))
        b.bind("<Leave>",    lambda e: b.config(bg=bg_n, fg=C_MID))
        return b

    # ── Resize / Drag / Maximize ───────────────────────────────────────────────
    def _drag_start(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _drag_move(self, e):
        if self._is_maximized: return
        x = e.x_root - self._drag_x
        y = e.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _resize_start(self, e):
        self._rx = e.x_root
        self._ry = e.y_root
        self._rw = self.winfo_width()
        self._rh = self.winfo_height()

    def _resize_move(self, e):
        dw = e.x_root - self._rx
        dh = e.y_root - self._ry
        nw = max(340, self._rw + dw)
        nh = max(480, self._rh + dh)
        self._win_w = nw
        self._win_h = nh
        self.geometry(f"{nw}x{nh}")

    def _minimize(self):
        self.overrideredirect(False)
        self.iconify()
        def _restore(e):
            self.overrideredirect(True)
            self.deiconify()
        self.bind("<Map>", _restore)

    def _toggle_maximize(self):
        if self._is_maximized:
            self._is_maximized = False
            self.geometry(self._normal_geo)
            g = self._normal_geo.split("+")[0]
            self._win_w, self._win_h = map(int, g.split("x"))
            self._btn_max.config(text="□")
        else:
            # save current
            self._normal_geo = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self._win_w = sw
            self._win_h = sh
            self.geometry(f"{sw}x{sh}+0+0")
            self._is_maximized = True
            self._btn_max.config(text="❐")

    def _on_resize(self, e):
        self._win_w = e.width
        self._win_h = e.height
        self._place_widgets()

    # ── Widget placement (responsive) ─────────────────────────────────────────
    def _place_widgets(self):
        cw = self._win_w
        ch = self._win_h - 38   # subtract titlebar
        cy_ring = int(ch * 0.46)

        # pills
        self.cv.coords(self._pill_win, cw//2, int(ch * 0.06))
        # start button
        self.cv.coords(self._bsw, cw//2 - self._s(50), int(ch * 0.84))
        # reset button
        self.cv.coords(self._brw, cw//2 + self._s(90), int(ch * 0.84))
        # dots
        self.cv.coords(self._dfw, cw//2, int(ch * 0.93))
        # credit
        self.cv.coords(self._credw, cw//2, ch - 4)

    # ── Render loop ───────────────────────────────────────────────────────────
    def _loop(self):
        self._step()
        self._draw()
        self.after(1000 // FPS, self._loop)

    def _step(self):
        def adv(s): s["t"] = min(1.0, s["t"] + LERP_S); s["cur"] = lerp_c(s["frm"], s["to"], s["t"])
        for s in (self._A, self._G, self._BT, self._BB, self._TK, self._IN):
            adv(s)

        diff = self._ring_target - self._ring
        self._ring += diff * 0.08
        if abs(diff) < 0.04: self._ring = self._ring_target

        target_amp = 1.0 if self.running else 0.0
        self._pulse_amp += (target_amp - self._pulse_amp) * 0.055
        self._pulse_ph  += 0.05 if self.running else -0.03
        self._pulse_ph   = max(0.0, self._pulse_ph)

    def _draw(self):
        cv = self.cv
        cv.delete("ring", "bg", "overlay")

        cw = self._win_w
        ch = self._win_h - 38
        cx = cw // 2
        cy = int(ch * 0.46)
        scale = min(self._sx, self._sy)
        R_OUT = int(148 * scale)
        R_IN  = int(108 * scale)
        thick = R_OUT - R_IN

        acc  = self._A["cur"]
        glow = self._G["cur"]
        bt   = self._BT["cur"]
        bb   = self._BB["cur"]
        trk  = self._TK["cur"]
        inn  = self._IN["cur"]

        # ── Gradient background ──
        steps = 50
        for i in range(steps):
            t  = i / steps
            bg = lerp_c(bt, bb, t)
            y0 = int(i * ch / steps)
            y1 = int((i+1) * ch / steps)
            cv.create_rectangle(0, y0, cw, y1, fill=bg, outline="", tags="bg")

        # ── Soft glow halo ──
        if self._pulse_amp > 0.02:
            p = (math.sin(self._pulse_ph) * 0.5 + 0.5)
            for i in range(10, 0, -1):
                r    = R_OUT + 4 + i * int(4*scale)
                alph = int(22 * self._pulse_amp * (1 - i/11) * p)
                if alph < 1: continue
                g_col = dim(glow, 0.6 + 0.4*p)
                cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                               outline=g_col, width=1, tags="ring")

        # ── Track ring ──
        cv.create_arc(cx-R_OUT, cy-R_OUT, cx+R_OUT, cy+R_OUT,
                      start=0, extent=359.9,
                      outline=trk, width=thick, style=tk.ARC, tags="ring")

        # ── Progress arc ──
        ang = max(0.2, self._ring)
        cv.create_arc(cx-R_OUT, cy-R_OUT, cx+R_OUT, cy+R_OUT,
                      start=90, extent=-ang,
                      outline=acc, width=thick, style=tk.ARC, tags="ring")

        # ── Tip dot (glowing) ──
        rad = math.radians(90 - ang)
        mr  = (R_OUT + R_IN) / 2
        tx  = cx + mr * math.cos(rad)
        ty  = cy - mr * math.sin(rad)
        ds  = thick / 2 + int(3*scale)
        # outer glow
        for gi in range(3, 0, -1):
            gs = ds + gi*int(2*scale)
            ga = int(40 * self._pulse_amp * gi/3)
            cv.create_oval(tx-gs, ty-gs, tx+gs, ty+gs,
                           fill="", outline=dim(glow, 0.5), width=1, tags="ring")
        cv.create_oval(tx-ds, ty-ds, tx+ds, ty+ds,
                       fill=acc, outline="", tags="ring")

        # 12-o'clock cap
        rad0 = math.radians(90)
        sx   = cx + mr * math.cos(rad0)
        sy   = cy - mr * math.sin(rad0)
        sc   = thick / 2
        cv.create_oval(sx-sc, sy-sc, sx+sc, sy+sc,
                       fill=lerp_c(trk, acc, 0.35), outline="", tags="ring")

        # ── Inner disc ──
        cv.create_oval(cx-R_IN+1, cy-R_IN+1, cx+R_IN-1, cy+R_IN-1,
                       fill=inn, outline="", tags="ring")

        # ── Time display ──
        tsize = max(22, int(48 * scale))
        cv.create_text(cx, cy - int(14*scale),
                       text=f"{self.time_left//60:02d}:{self.time_left%60:02d}",
                       fill=C_TEXT,
                       font=("Segoe UI", tsize, "bold"),
                       anchor="center", tags="overlay")

        # ── Mode label under time ──
        lsize = max(8, int(10 * scale))
        cv.create_text(cx, cy + int(32*scale),
                       text=self.th["label"],
                       fill=acc,
                       font=("Segoe UI", lsize, "bold"),
                       anchor="center", tags="overlay")

        # ── Watermark ──
        cv.create_text(cx, cy - int(44*scale),
                       text="mr. selfish",
                       fill=dim(acc, 0.25),
                       font=("Segoe UI", max(7, int(8*scale)), "italic"),
                       anchor="center", tags="overlay")

        # ── Status indicator ──
        si_y = cy + int(60*scale)
        if self.running:
            sr = int(3.5*scale) + math.sin(self._pulse_ph)*int(1.5*scale)*self._pulse_amp
            cv.create_oval(cx-sr, si_y-sr, cx+sr, si_y+sr,
                           fill=acc, outline="", tags="overlay")
        else:
            cv.create_text(cx, si_y, text="· · ·",
                           fill=C_DIM, font=("Segoe UI", max(7, int(9*scale))),
                           anchor="center", tags="overlay")

        # Bring overlay widgets forward
        self.cv.lift(self._pill_win)
        self.cv.lift(self._bsw)
        self.cv.lift(self._brw)
        self.cv.lift(self._dfw)
        self.cv.lift(self._credw)
        self.grip.lift()

    # ── Timer logic ───────────────────────────────────────────────────────────
    def _set_mode(self, mode):
        self.running  = False
        self.mode_key = mode
        self.th       = THEMES[mode]
        self.time_left= self.th["duration"]
        self._ring = self._ring_target = 360.0

        def tr(s, to): s["frm"]=s["cur"]; s["to"]=to; s["t"]=0.0
        tr(self._A,  self.th["accent"])
        tr(self._G,  self.th["glow"])
        tr(self._BT, self.th["bg_top"])
        tr(self._BB, self.th["bg_bot"])
        tr(self._TK, self.th["track"])
        tr(self._IN, self.th["inner"])

        self._refresh_pills()
        self._refresh_btn()

    def _toggle(self):
        if self.running:
            self.running = False
        else:
            self.running = True
            threading.Thread(target=self._countdown, daemon=True).start()
        self._refresh_btn()

    def _reset(self):
        self.running   = False
        self.time_left = self.th["duration"]
        self._ring_target = 360.0
        self._refresh_btn()

    def _countdown(self):
        total = self.th["duration"]
        while self.running and self.time_left > 0:
            time.sleep(1)
            if not self.running: break
            self.time_left    -= 1
            self._ring_target  = (self.time_left / total) * 360.0
        if self.time_left == 0 and self.running:
            self.running = False
            self.sessions += 1
            self.after(0, self._done)

    def _done(self):
        self._refresh_btn()
        self._refresh_dots()
        self._flash(8)

    def _flash(self, n):
        if n <= 0: return
        to = "#FFFFFF" if n%2==0 else self.th["accent"]
        self._A["frm"]=self._A["cur"]; self._A["to"]=to; self._A["t"]=0
        self.after(90, lambda: self._flash(n-1))

    def _next_mode(self):
        keys = list(THEMES.keys())
        self._set_mode(keys[(keys.index(self.mode_key)+1)%len(keys)])

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _refresh_pills(self):
        for mode, btn in self._pills.items():
            if mode == self.mode_key:
                btn.config(bg=self.th["accent"], fg="#0A0A0A")
            else:
                btn.config(bg=C_BTN, fg=C_MID)

    def _pill_leave(self, w):
        mode = next(m for m,b in self._pills.items() if b is w)
        if mode != self.mode_key:
            w.config(bg=C_BTN)

    def _refresh_btn(self):
        self._btn_start_w.config(
            text="⏸   PAUSE" if self.running else "▶   START")

    def _refresh_dots(self):
        for i, dc in enumerate(self._dot_cvs):
            col = self.th["accent"] if i < self.sessions % 4 else C_DIM
            dc.itemconfig("d", fill=col)


if __name__ == "__main__":
    app = Pomodoro()
    app.mainloop()
