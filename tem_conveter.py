import tkinter as tk
import math
from collections import deque

# ══════════════════════════════════════════════════════════════════
#  THERMO  ·  Designed by Mr Selfish
#  Fully resizable | C→F Navy+Cyan | F→C Maroon+Amber
# ══════════════════════════════════════════════════════════════════

THEMES = {
    "C→F": {
        "bg0":"#0D1B2A","bg1":"#112233","bg2":"#0A2540",
        "accent":"#48CAE4","accent2":"#90E0EF","accent3":"#CAF0F8",
        "pill":"#48CAE4","pill_txt":"#0D1B2A",
        "badge":"#48CAE4","badge_txt":"#0D1B2A",
        "title":"#48CAE4","dim":"#AACCDD","dimmer":"#4A6A88",
        "res_fg":"#48CAE4","grid":"#0F2235",
        "orb1":"#1A3A5C","orb2":"#0A2540","footer":"#060F18",
        "hist_row":"#0F2438","hist_alt":"#0A1C2C",
        "green":"#06D6A0","red":"#EF476F","gold":"#FFD166","brand":"#48CAE4",
    },
    "F→C": {
        "bg0":"#1A0A00","bg1":"#2A1200","bg2":"#1F0D00",
        "accent":"#FF9F1C","accent2":"#FFBF69","accent3":"#FFE5B4",
        "pill":"#FF9F1C","pill_txt":"#1A0A00",
        "badge":"#FF9F1C","badge_txt":"#1A0A00",
        "title":"#FF9F1C","dim":"#DDAA77","dimmer":"#6A3A10",
        "res_fg":"#FF9F1C","grid":"#220E00",
        "orb1":"#3A1A00","orb2":"#2A0E00","footer":"#080300",
        "hist_row":"#261000","hist_alt":"#1A0900",
        "green":"#06D6A0","red":"#EF476F","gold":"#FFD166","brand":"#FF9F1C",
    },
}

def lerp_color(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


class TempConverter:
    def __init__(self, root):
        self.root      = root
        self.root.title("THERMO  ·  Mr Selfish")
        self.root.minsize(500, 700)

        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        dw, dh = min(680, sw), min(960, sh)
        self.root.geometry(f"{dw}x{dh}+{(sw-dw)//2}+{(sh-dh)//2}")
        self.root.resizable(True, True)

        self.mode     = "C→F"
        self._tog_pos = 0.0
        self._theme_t = 0.0
        self._pulse_a = 0.0
        self._is_full = False
        self.history  = deque(maxlen=5)
        self.T        = dict(THEMES["C→F"])

        self.root.configure(bg=self.T["bg0"])

        # ── Build fixed widget layer (never destroyed) ──────
        self._build_widgets()

        # ── Canvas sits BEHIND widgets via lower() ──────────
        self.cv = tk.Canvas(self.root, bg=self.T["bg0"],
                            highlightthickness=0)
        self.cv.place(x=0, y=0, relwidth=1, relheight=1)
        # widgets will be lifted after drawing

        # Keyboard shortcuts
        self.root.bind("<F11>",       lambda e: self._toggle_fullscreen())
        self.root.bind("<Escape>",    lambda e: self._exit_fullscreen())
        self.root.bind("<Control-h>", lambda e: self._half_screen())
        self.root.bind("<Control-f>", lambda e: self._toggle_fullscreen())

        # Resize → redraw canvas only (widgets stay)
        self.root.bind("<Configure>", self._on_resize)

        self.root.update_idletasks()
        self.root.after(60, self._full_redraw)
        self._start_pulse()

    # ══════════════════════════════════════════════════════════
    #  WIDGETS — created ONCE, repositioned on resize
    # ══════════════════════════════════════════════════════════
    def _build_widgets(self):
        T = self.T

        # ── Input frame + entry ──────────────────────────────
        self.inp_frame = tk.Frame(self.root, bg=T["bg1"],
                                   highlightbackground=T["accent"],
                                   highlightthickness=2)
        self.entry = tk.Entry(self.inp_frame,
            font=("Helvetica", 42, "bold"),
            bg=T["bg1"], fg="#FFFFFF",
            insertbackground=T["accent"],
            relief="flat", bd=0, justify="right")
        self.entry.pack(fill="both", expand=True, padx=12, pady=8)
        self.entry.bind("<KeyRelease>", lambda e: self._convert())
        self.entry.bind("<Return>",     lambda e: self._save_record())
        self.entry.bind("<FocusIn>",    lambda e: self._set_inp_focus(True))
        self.entry.bind("<FocusOut>",   lambda e: self._set_inp_focus(False))

        # ── Result frame + label ────────────────────────────
        self.res_frame = tk.Frame(self.root, bg=T["bg2"],
                                   highlightbackground=T["accent"],
                                   highlightthickness=2)
        self.result_var = tk.StringVar(value="—")
        self.res_label = tk.Label(self.res_frame,
            textvariable=self.result_var,
            font=("Helvetica", 52, "bold"),
            bg=T["bg2"], fg=T["res_fg"],
            anchor="e")
        self.res_label.pack(fill="both", expand=True, padx=12, pady=4)

        self.formula_var = tk.StringVar(value="( °C × 9/5 ) + 32  =  °F")
        self.formula_lbl = tk.Label(self.res_frame,
            textvariable=self.formula_var,
            font=("Helvetica", 10, "bold"),
            bg=T["bg2"], fg="#AACCDD", anchor="e")
        self.formula_lbl.pack(fill="x", padx=12, pady=(0,6))

        # Focus entry
        self.root.after(200, self.entry.focus_force)

    def _set_inp_focus(self, focused):
        T = self.T
        col = T["accent"] if focused else T["dimmer"]
        thick = 3 if focused else 1
        self.inp_frame.config(highlightbackground=col,
                               highlightthickness=thick)

    # ══════════════════════════════════════════════════════════
    #  FULL REDRAW — canvas + widget positions
    # ══════════════════════════════════════════════════════════
    def _full_redraw(self):
        W = self.root.winfo_width()
        H = self.root.winfo_height()
        if W < 50 or H < 50:
            return
        self._W, self._H = W, H

        # Resize canvas
        self.cv.config(width=W, height=H)

        # Draw background
        self.cv.delete("all")
        self._paint_bg(W, H)
        self._draw_ui(W, H)

        # Reposition widgets
        self._place_widgets(W, H)

    def _on_resize(self, event=None):
        if hasattr(self, '_rjob'):
            self.root.after_cancel(self._rjob)
        self._rjob = self.root.after(60, self._full_redraw)

    # ── Scale helpers ────────────────────────────────────────
    def sx(self, v): return int(v * self._W / 640)
    def sy(self, v): return int(v * self._H / 960)
    def sf(self, v): return max(8, int(v * min(self._W/640, self._H/960)))

    # ── Background ───────────────────────────────────────────
    def _paint_bg(self, W, H):
        T = self.T
        dark = lerp_color(T["bg0"], "#000000", 0.35)
        for i in range(50):
            self.cv.create_rectangle(0, H*i//50, W, H*(i+1)//50+1,
                fill=lerp_color(T["bg0"], dark, i/50), outline="")
        for x in range(0, W, max(30, W//20)):
            self.cv.create_line(x,0,x,H, fill=T["grid"], width=1)
        for y in range(0, H, max(30, H//30)):
            self.cv.create_line(0,y,W,y, fill=T["grid"], width=1)
        for cx,cy,r,k in [(0,0,int(W*.35),"orb1"),(W,H,int(W*.3),"orb2"),(W,0,int(W*.2),"orb1")]:
            for dr in range(r,0,-max(1,r//12)):
                self.cv.create_oval(cx-dr,cy-dr,cx+dr,cy+dr,
                    fill=lerp_color(T["bg0"],T[k],dr/r), outline="")
        

    # ── Draw all canvas UI text/shapes ───────────────────────
    def _draw_ui(self, W, H):
        T = self.T
        PX = self.sx(44)

        # ── Header ──────────────────────────────────────────
        hy = self.sy(52)
        self.cv.create_text(PX, hy, text="THERMO",
            fill=T["title"], font=("Helvetica", self.sf(38), "bold"), anchor="w")
        self.cv.create_text(PX, hy, text="THERMO",
            fill=T["accent3"], font=("Helvetica", self.sf(38), "bold"),
            anchor="w", stipple="gray50")
        self.cv.create_text(self.sx(252), self.sy(57),
            text="Temperature Converter",
            fill="#FFFFFF", font=("Helvetica", self.sf(11), "bold"), anchor="w")

        # Shortcut hint
        self.cv.create_text(W-PX, self.sy(28),
            text="F11=Full · Ctrl+H=Half · Max/Min from titlebar",
            fill=T["dimmer"], font=("Helvetica", self.sf(7), "bold"), anchor="e")

        # Brand badge
        bx1,by1 = self.sx(392), self.sy(28)
        bx2,by2 = W-PX,         self.sy(74)
        self.cv.create_rectangle(bx1,by1,bx2,by2, fill=T["badge"], outline="")
        self.cv.create_text((bx1+bx2)//2, by1+(by2-by1)//3,
            text="✦  MR SELFISH",
            fill=T["badge_txt"], font=("Helvetica", self.sf(12), "bold"))
        self.cv.create_text((bx1+bx2)//2, by2-(by2-by1)//4,
            text="DESIGNED BY",
            fill=T["badge_txt"], font=("Helvetica", self.sf(7), "bold"))

        # Separator
        self.cv.create_line(PX, self.sy(90), W-PX, self.sy(90),
            fill=T["dimmer"], width=1)

        # Window buttons
        btn_y = self.sy(108)
        bfs = self.sf(9)
        for label, cmd, xoff in [
            ("⛶ Full",    self._toggle_fullscreen, 0),
            ("▣ Half",    self._half_screen,        self.sx(68)),
            ("🗖 Max",    self._maximize,            self.sx(126)),
            ("🗕 Min",    self._minimize,            self.sx(182)),
            ("🗗 Restore",self._restore,             self.sx(248)),
        ]:
            tx = W - PX - xoff
            tid = self.cv.create_text(tx, btn_y, text=label,
                fill=T["accent"] if xoff==0 else T["dim"],
                font=("Helvetica", bfs, "bold"), anchor="e", tags=f"btn{xoff}")
            self.cv.tag_bind(f"btn{xoff}", "<Button-1>",
                             lambda e, c=cmd: c())
            self.cv.tag_bind(f"btn{xoff}", "<Enter>",
                             lambda e, t=tid: self.cv.itemconfig(t, fill=self.T["accent"]))
            self.cv.tag_bind(f"btn{xoff}", "<Leave>",
                             lambda e, t=tid, x=xoff: self.cv.itemconfig(
                                 t, fill=self.T["accent"] if x==0 else self.T["dim"]))

        # Toggle track
        ty1,ty2 = self.sy(124), self.sy(178)
        self.cv.create_text(PX, self.sy(113), text="M O D E",
            fill="#FFFFFF", font=("Helvetica", self.sf(8), "bold"), anchor="w")
        self.cv.create_rectangle(PX, ty1, W-PX, ty2,
            fill=T["bg2"], outline=T["dimmer"], width=1, tags="tog_track")
        self.cv.create_rectangle(PX, ty1, W-PX, ty2,
            fill="", outline="", tags="tog_hit")
        self.cv.tag_bind("tog_hit",   "<Button-1>", self._tog_click)
        self.cv.tag_bind("tog_track", "<Button-1>", self._tog_click)
        self._tog_x1, self._tog_x2 = PX, W-PX
        self._tog_y1, self._tog_y2 = ty1, ty2
        self._draw_pill(self._tog_pos)

        # Input label
        self.cv.create_text(PX, self.sy(206),
            text="E N T E R   °C" if self.mode=="C→F" else "E N T E R   °F",
            fill="#FFFFFF", font=("Helvetica", self.sf(12), "bold"), anchor="w",
            tags="in_lbl")

        # Helper text (below input)
        inp_y  = self.sy(224)
        inp_h  = self.sy(90)
        self.cv.create_text(W-PX, inp_y+inp_h+self.sy(10),
            text="press Enter to save  ·  type a number",
            fill="#AACCDD", font=("Helvetica", self.sf(9), "bold"), anchor="e",
            tags="help_txt")

        # Arrow
        arr_y = inp_y + inp_h + self.sy(44)
        self._arr_y = arr_y
        self.cv.create_text(W//2, arr_y, text="⬇",
            fill=T["accent"], font=("Helvetica", self.sf(24), "bold"),
            tags="arr")

        # Result label
        res_y = arr_y + self.sy(34)
        self.cv.create_text(PX, res_y,
            text="R E S U L T   °F" if self.mode=="C→F" else "R E S U L T   °C",
            fill="#FFFFFF", font=("Helvetica", self.sf(12), "bold"), anchor="w",
            tags="res_lbl")

        # History
        hist_top = res_y + self.sy(136)
        self.cv.create_line(PX, hist_top, W-PX, hist_top,
            fill=T["dimmer"], width=1)
        self.cv.create_text(PX, hist_top+self.sy(18),
            text="📋  LAST 5 CONVERSIONS",
            fill="#FFFFFF", font=("Helvetica", self.sf(10), "bold"), anchor="w")

        # Clear button
        cb_y = hist_top+self.sy(18)
        self.cv.create_rectangle(W-PX-self.sx(58), cb_y-self.sy(10),
            W-PX, cb_y+self.sy(10),
            fill=T["dimmer"], outline="", tags="clr_btn")
        self.cv.create_text(W-PX-self.sx(29), cb_y,
            text="CLEAR", fill=T["bg0"],
            font=("Helvetica", self.sf(8), "bold"), tags="clr_btn")
        self.cv.tag_bind("clr_btn","<Button-1>",lambda e:self._clear_history())

        # 5 history rows
        row_h  = self.sy(44)
        row_gap = self.sy(4)
        self._hist_meta = []
        for i in range(5):
            ry = hist_top + self.sy(36) + i*(row_h+row_gap)
            alt = T["hist_alt"] if i%2==0 else T["hist_row"]
            bg  = self.cv.create_rectangle(PX, ry, W-PX, ry+row_h,
                    fill=alt, outline=T["dimmer"], width=1)
            acc = self.cv.create_rectangle(PX, ry, PX+self.sx(5), ry+row_h,
                    fill=T["dimmer"], outline="")
            num = self.cv.create_text(PX+self.sx(16), ry+row_h//2,
                    text=f"#{i+1}", fill="#FFFFFF",
                    font=("Helvetica", self.sf(9), "bold"), anchor="w")
            mt  = self.cv.create_text(PX+self.sx(46), ry+row_h//3,
                    text="", fill=T["accent"],
                    font=("Helvetica", self.sf(8), "bold"), anchor="w")
            it  = self.cv.create_text(PX+self.sx(46), ry+row_h*2//3,
                    text="—", fill="#FFFFFF",
                    font=("Helvetica", self.sf(10), "bold"), anchor="w")
            at  = self.cv.create_text(W//2, ry+row_h//2,
                    text="", fill=T["dimmer"],
                    font=("Helvetica", self.sf(12), "bold"))
            ot  = self.cv.create_text(W-PX-self.sx(8), ry+row_h//2,
                    text="", fill=T["accent"],
                    font=("Helvetica", self.sf(14), "bold"), anchor="e")
            self._hist_meta.append((bg,acc,num,mt,it,at,ot))

        self._refresh_history()

        # Footer
        foot_y = H - self.sy(108)
        self.cv.create_line(PX, foot_y, W-PX, foot_y, fill=T["dimmer"], width=1)
        self.cv.create_rectangle(0, foot_y, W, H, fill=T["footer"], outline="")
        self.cv.create_text(W//2, foot_y+self.sy(26),
            text="DESIGNED  BY",
            fill="#AACCDD", font=("Helvetica", self.sf(9), "bold"))
        self.cv.create_text(W//2, foot_y+self.sy(60),
            text="MR  SELFISH",
            fill=T["brand"], font=("Helvetica", self.sf(28), "bold"))
        self.cv.create_line(W//2-self.sx(80), foot_y+self.sy(76),
                            W//2+self.sx(80), foot_y+self.sy(76),
                            fill=T["brand"], width=1)
        self.cv.create_text(W//2, foot_y+self.sy(90),
            text="THERMO  ·  Premium Temperature Converter",
            fill="#AACCDD", font=("Helvetica", self.sf(8), "bold"))

        # Pulse dot
        self._pdot = self.cv.create_oval(
            W-self.sx(22), H-self.sy(22), W-self.sx(10), H-self.sy(10),
            fill=T["green"], outline="")

    # ── Place widgets at correct positions ───────────────────
    def _place_widgets(self, W, H):
        PX   = self.sx(44)
        inp_y = self.sy(224)
        inp_h = self.sy(90)
        inp_w = W - PX*2

        # Update entry font size
        fs_inp = max(14, int(40 * min(W/640, H/960)))
        self.entry.config(font=("Helvetica", fs_inp, "bold"))

        # Place input frame
        self.inp_frame.place(x=PX, y=inp_y, width=inp_w, height=inp_h)
        self.inp_frame.config(bg=self.T["bg1"])
        self.entry.config(bg=self.T["bg1"],
                          insertbackground=self.T["accent"],
                          fg="#FFFFFF")

        # Result frame
        arr_y   = inp_y + inp_h + self.sy(44)
        res_y   = arr_y + self.sy(34)
        res_h   = self.sy(120)
        fs_res  = max(18, int(50 * min(W/640, H/960)))
        self.res_label.config(font=("Helvetica", fs_res, "bold"))
        self.res_frame.place(x=PX, y=res_y+self.sy(18),
                              width=inp_w, height=res_h)
        self.res_frame.config(bg=self.T["bg2"])
        self.res_label.config(bg=self.T["bg2"], fg=self.T["res_fg"])
        self.formula_lbl.config(bg=self.T["bg2"], fg="#AACCDD")

        # Lift widgets above canvas
        self.inp_frame.lift()
        self.res_frame.lift()

    # ── Pill ─────────────────────────────────────────────────
    def _draw_pill(self, pos):
        self.cv.delete("pill"); self.cv.delete("pill_txt")
        if not hasattr(self, '_tog_x1'): return
        T   = self.T
        x1,x2 = self._tog_x1, self._tog_x2
        y1,y2 = self._tog_y1, self._tog_y2
        pw  = (x2-x1)//2
        px  = x1 + int(pos * pw)
        for i in range(3,0,-1):
            self.cv.create_rectangle(px-i,y1+i,px+pw+i,y2-i,
                fill="", outline=lerp_color(T["bg2"],T["pill"],0.15*(4-i)),
                width=1, tags="pill")
        self.cv.create_rectangle(px,y1+2,px+pw,y2-2,
            fill=T["pill"], outline="", tags="pill")
        lc = T["pill_txt"] if pos<=0.3 else "#FFFFFF"
        rc = T["pill_txt"] if pos>=0.7 else "#FFFFFF"
        fs = max(9, int(14*min(self._W/640, self._H/960)))
        self.cv.create_text(x1+(x2-x1)//4, (y1+y2)//2,
            text="°C  →  °F", fill=lc,
            font=("Helvetica",fs,"bold"), tags="pill_txt")
        self.cv.create_text(x1+3*(x2-x1)//4, (y1+y2)//2,
            text="°F  →  °C", fill=rc,
            font=("Helvetica",fs,"bold"), tags="pill_txt")

    # ── Toggle ───────────────────────────────────────────────
    def _tog_click(self, event):
        mid = (self._tog_x1+self._tog_x2)//2
        new = "C→F" if event.x < mid else "F→C"
        if new != self.mode:
            self._anim_pill(0.0 if new=="C→F" else 1.0, new, 0)

    def _anim_pill(self, target, new_mode, step=0, steps=18):
        if step <= steps:
            t2   = step/steps
            ease = t2*t2*(3-2*t2)
            self._tog_pos = self._tog_pos + (target-self._tog_pos)*ease
            tt = 0.0 if new_mode=="C→F" else 1.0
            self._theme_t += (tt-self._theme_t)*ease
            for k in THEMES["C→F"]:
                self.T[k] = lerp_color(THEMES["C→F"][k],THEMES["F→C"][k],self._theme_t)
            self._draw_pill(self._tog_pos)
            self._update_theme_colors()
            self.root.after(13, lambda: self._anim_pill(target,new_mode,step+1,steps))
        else:
            self._tog_pos = target
            self._set_mode_final(new_mode)

    def _update_theme_colors(self):
        T = self.T
        self.cv.configure(bg=T["bg0"])
        self.root.configure(bg=T["bg0"])
        self.inp_frame.config(bg=T["bg1"])
        self.entry.config(bg=T["bg1"], insertbackground=T["accent"])
        self.res_frame.config(bg=T["bg2"])
        self.res_label.config(bg=T["bg2"], fg=T["res_fg"])
        self.formula_lbl.config(bg=T["bg2"])
        # Repaint bg + UI
        if hasattr(self, '_W'):
            self.cv.delete("all")
            self._paint_bg(self._W, self._H)
            self._draw_ui(self._W, self._H)
            self.inp_frame.lift()
            self.res_frame.lift()

    # ── History ──────────────────────────────────────────────
    def _save_record(self):
        raw = self.entry.get().strip()
        if not raw: return
        try:
            val = float(raw)
            if self.mode=="C→F":
                res=(val*9/5)+32
                inp_s=f"{val}°C"
                out_s=f"{int(res)}°F" if res==int(res) else f"{res:.1f}°F"
            else:
                res=(val-32)*5/9
                inp_s=f"{val}°F"
                out_s=f"{int(res)}°C" if res==int(res) else f"{res:.1f}°C"
            self.history.appendleft({"mode":self.mode,"inp":inp_s,"out":out_s})
            self._refresh_history()
            self._set_help("✅  saved to history!", self.T["green"])
        except ValueError:
            pass

    def _refresh_history(self):
        if not hasattr(self,'_hist_meta'): return
        T = self.T
        hist = list(self.history)
        for i,(bg,acc,num,mt,it,at,ot) in enumerate(self._hist_meta):
            alt = T["hist_alt"] if i%2==0 else T["hist_row"]
            self.cv.itemconfig(bg,  fill=alt, outline=T["dimmer"])
            self.cv.itemconfig(num, fill="#FFFFFF", text=f"#{i+1}")
            if i < len(hist):
                r = hist[i]
                self.cv.itemconfig(acc, fill=T["accent"])
                self.cv.itemconfig(mt,  text=r["mode"], fill=T["accent"])
                self.cv.itemconfig(it,  text=r["inp"],  fill="#FFFFFF")
                self.cv.itemconfig(at,  text="→",       fill=T["dimmer"])
                self.cv.itemconfig(ot,  text=r["out"],  fill=T["accent"])
            else:
                self.cv.itemconfig(acc, fill=T["dimmer"])
                self.cv.itemconfig(mt,  text="")
                self.cv.itemconfig(it,  text="—")
                self.cv.itemconfig(at,  text="")
                self.cv.itemconfig(ot,  text="")

    def _clear_history(self):
        self.history.clear()
        self._refresh_history()
        self._set_help("history cleared", self.T["dimmer"])

    def _set_help(self, text, color):
        try:
            self.cv.itemconfig("help_txt", text=text, fill=color)
        except Exception:
            pass

    # ── Mode ─────────────────────────────────────────────────
    def _set_mode_final(self, mode):
        self.mode = mode
        T = self.T
        try:
            self.cv.itemconfig("in_lbl",
                text="E N T E R   °C" if mode=="C→F" else "E N T E R   °F")
            self.cv.itemconfig("res_lbl",
                text="R E S U L T   °F" if mode=="C→F" else "R E S U L T   °C")
        except Exception:
            pass
        self.formula_var.set(
            "( °C × 9/5 ) + 32  =  °F" if mode=="C→F"
            else "( °F − 32 ) × 5/9  =  °C")
        self.result_var.set("—")
        self.res_label.config(fg=T["res_fg"])
        self.entry.delete(0, tk.END)
        self.entry.focus()

    # ── Convert ──────────────────────────────────────────────
    def _convert(self):
        raw = self.entry.get().strip()
        T   = self.T
        if not raw:
            self.result_var.set("—")
            self.res_label.config(fg=T["res_fg"])
            self._set_help("press Enter to save  ·  type a number", "#AACCDD")
            return
        try:
            val = float(raw)
            res = (val*9/5)+32 if self.mode=="C→F" else (val-32)*5/9
            unit= "°F"         if self.mode=="C→F" else "°C"
            out = f"{int(res)}{unit}" if res==int(res) else f"{res:.1f}{unit}"
            self.result_var.set(out)
            self.res_label.config(fg=T["accent2"])
            self._set_help("✓  converted  ·  press Enter to save", T["green"])
        except ValueError:
            self.result_var.set("ERR")
            self.res_label.config(fg=T["red"])
            self._set_help("⚠  numbers only", T["red"])

    # ── Pulse ────────────────────────────────────────────────
    def _start_pulse(self): self._pulse()

    def _pulse(self):
        self._pulse_a += 0.06
        a = (math.sin(self._pulse_a)+1)/2
        try:
            if hasattr(self,'_arr_y'):
                items = self.cv.find_withtag("arr")
                if items:
                    coords = self.cv.coords(items[0])
                    if coords:
                        self.cv.coords(items[0], coords[0], self._arr_y+int(a*6))
            if hasattr(self,'_pdot'):
                g=int(0xD6*(0.6+0.4*a)); b=int(0xA0*(0.6+0.4*a))
                self.cv.itemconfig(self._pdot, fill=f"#00{g:02x}{b:02x}")
        except Exception:
            pass
        self.root.after(30, self._pulse)

    # ── Window controls ──────────────────────────────────────
    def _toggle_fullscreen(self):
        self._is_full = not self._is_full
        self.root.attributes("-fullscreen", self._is_full)

    def _exit_fullscreen(self):
        if self._is_full:
            self._is_full = False
            self.root.attributes("-fullscreen", False)

    def _maximize(self):
        self._exit_fullscreen()
        self.root.state("zoomed")

    def _minimize(self):
        self.root.iconify()

    def _restore(self):
        self.root.attributes("-fullscreen", False)
        self._is_full = False
        try: self.root.state("normal")
        except Exception: pass

    def _half_screen(self):
        self._restore()
        sw,sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{sw//2}x{sh}+0+0")


if __name__ == "__main__":
    root = tk.Tk()
    try: root.tk.call("tk", "scaling", 1.0)
    except Exception: pass
    app = TempConverter(root)
    root.mainloop()
