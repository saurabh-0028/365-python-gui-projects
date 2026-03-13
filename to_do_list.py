"""
╔══════════════════════════════════════════════╗
║   MR. SELFISH — TO-DO LIST v2.0             ║
║   Due dates · Priority · Dark Mode · Save   ║
╚══════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, date

# ─── SAVE FILE ────────────────────────────────────────────────────────────────
SAVE_FILE = os.path.join(os.path.expanduser("~"), "mr_selfish_tasks.json")

# ─── THEMES ───────────────────────────────────────────────────────────────────
THEMES = {
    "light": {
        "BG":         "#F5F0E8",
        "SURFACE":    "#EDE8DC",
        "SIDEBAR":    "#E6E0D2",
        "CARD":       "#FDFAF4",
        "CARD_HOVER": "#F0EBE0",
        "ACCENT":     "#5C8A3C",
        "ACCENT2":    "#C0522A",
        "TEXT":       "#2E2A22",
        "TEXT_DIM":   "#8A8070",
        "TEXT_DONE":  "#B0A898",
        "BORDER":     "#D6CFC2",
        "BORDER2":    "#C8C0B0",
        "SCROLLBAR":  "#D0C8BA",
        "SEL_BG":     "#DFF0D4",
        "P_HIGH":     ("#FAE5D3", "#C05020", "#8A2A08"),
        "P_MED":      ("#FEF3D0", "#9A7010", "#6A4A08"),
        "P_LOW":      ("#DFF0D4", "#3A6B20", "#1A4B08"),
        "TAG_WORK":   ("#DFF0D4", "#3A6B20"),
        "TAG_PERS":   ("#F5E0D8", "#9E3D1E"),
        "TAG_URG":    ("#FAE5D3", "#C05020"),
        "TAG_HLTH":   ("#D4EAF5", "#2A6E8A"),
        "TAG_FIN":    ("#F5EDD0", "#7A6010"),
        "INS_BG":     "#FDFAF4",
        "TOAST_FG":   "#FDFAF4",
        "RING_TRK":   "#D6CFC2",
        "BAR1":       (92,  138, 60),
        "BAR2":       (192, 82,  42),
        "ICON_DEL":   "#C0522A",
        "ICON_EDIT":  "#8A8070",
    },
    "dark": {
        "BG":         "#0D0D0F",
        "SURFACE":    "#16161A",
        "SIDEBAR":    "#111115",
        "CARD":       "#1E1E24",
        "CARD_HOVER": "#26262E",
        "ACCENT":     "#7EC850",
        "ACCENT2":    "#E8643C",
        "TEXT":       "#F0F0F2",
        "TEXT_DIM":   "#6B6B7A",
        "TEXT_DONE":  "#45455A",
        "BORDER":     "#2A2A35",
        "BORDER2":    "#3A3A48",
        "SCROLLBAR":  "#2A2A35",
        "SEL_BG":     "#1A3010",
        "P_HIGH":     ("#3A1008", "#F08060", "#FFAA88"),
        "P_MED":      ("#2E2008", "#D4A030", "#FFD080"),
        "P_LOW":      ("#0A2010", "#60C050", "#A0E888"),
        "TAG_WORK":   ("#1A2C0A", "#A8E065"),
        "TAG_PERS":   ("#2A0D1A", "#F07BB0"),
        "TAG_URG":    ("#2A0A0A", "#FF6B6B"),
        "TAG_HLTH":   ("#0A1E2A", "#6BC5F0"),
        "TAG_FIN":    ("#1E1A0A", "#F0C96B"),
        "INS_BG":     "#1E1E24",
        "TOAST_FG":   "#0D0D0F",
        "RING_TRK":   "#2A2A35",
        "BAR1":       (126, 200, 80),
        "BAR2":       (232, 100, 60),
        "ICON_DEL":   "#E8643C",
        "ICON_EDIT":  "#6B6B7A",
    }
}

T = THEMES["light"]   # active theme dict — updated on toggle

PRIORITY_LABELS = {"high": "● HIGH", "med": "◐ MED", "low": "○ LOW", "": ""}
TAGS = ["", "work", "personal", "urgent", "health", "finance"]

FONT_TITLE  = ("Georgia",    24, "bold")
FONT_BRAND  = ("Georgia",    11, "italic")
FONT_ITEM   = ("Segoe UI",   15)
FONT_ITEM_B = ("Segoe UI",   15, "bold")
FONT_TAG    = ("Courier New",11, "bold")
FONT_BTN    = ("Segoe UI",   13, "bold")
FONT_SMALL  = ("Segoe UI",   12)
FONT_COUNT  = ("Georgia",    34, "bold")
FONT_HINT   = ("Segoe UI",   11)
FONT_DATE   = ("Courier New",10)
FONT_PRIO   = ("Courier New",10, "bold")


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def hex_lerp(c1_rgb, c2_rgb, t):
    r = int(c1_rgb[0] + (c2_rgb[0] - c1_rgb[0]) * t)
    g = int(c1_rgb[1] + (c2_rgb[1] - c1_rgb[1]) * t)
    b = int(c1_rgb[2] + (c2_rgb[2] - c1_rgb[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def days_until(due_str):
    """Return int days until due, or None."""
    if not due_str:
        return None
    try:
        due = datetime.strptime(due_str, "%Y-%m-%d").date()
        return (due - date.today()).days
    except Exception:
        return None

def due_label(due_str):
    d = days_until(due_str)
    if d is None:
        return "", T["TEXT_DIM"]
    if d < 0:
        return f"⚠ {abs(d)}d overdue", T["P_HIGH"][1]
    if d == 0:
        return "⚡ Today", T["P_HIGH"][1]
    if d == 1:
        return "↑ Tomorrow", T["P_MED"][1]
    if d <= 7:
        return f"↑ {d}d left", T["P_MED"][1]
    return f"◷ {due_str}", T["TEXT_DIM"]


class AnimatedValue:
    def __init__(self, start=0.0):
        self.current = float(start)
        self.target  = float(start)
        self._speed  = 0.15

    def set_target(self, v, speed=0.15):
        self.target = float(v)
        self._speed = speed

    def step(self):
        diff = self.target - self.current
        if abs(diff) < 0.5:
            self.current = self.target
        else:
            self.current += diff * self._speed
        return self.current

    @property
    def settled(self):
        return abs(self.target - self.current) < 0.5


# ─── TOAST ────────────────────────────────────────────────────────────────────
class Toast:
    def __init__(self, root):
        self.root = root
        self._win = None

    def show(self, msg, color=None, duration=2400):
        color = color or T["ACCENT"]
        if self._win:
            try: self._win.destroy()
            except: pass
        w = tk.Toplevel(self.root)
        w.overrideredirect(True)
        w.attributes("-topmost", True)
        w.configure(bg=color)
        tk.Label(w, text=msg, bg=color, fg=T["TOAST_FG"],
                 font=FONT_BTN, padx=22, pady=11).pack()
        self._win = w
        self.root.update_idletasks()
        rx, ry = self.root.winfo_x(), self.root.winfo_y()
        rw = self.root.winfo_width()
        w.update_idletasks()
        ww = w.winfo_reqwidth()
        w.geometry(f"+{rx + rw - ww - 24}+{ry + 28}")
        self._fade(w, 0, 10, 18, lambda: w.after(duration, lambda: self._fade(w, 10, 0, 18)))

    def _fade(self, w, frm, to, steps, done=None):
        def step(i=0):
            if not w.winfo_exists(): return
            t = ease_out_cubic(i / steps)
            alpha = frm/10 + (to - frm)/10 * t
            try: w.attributes("-alpha", max(0.0, min(1.0, alpha)))
            except: return
            if i < steps:
                w.after(20, lambda: step(i + 1))
            elif done:
                done()
            elif to == 0:
                try: w.destroy()
                except: pass
        step()


# ─── PROGRESS RING ────────────────────────────────────────────────────────────
class ProgressRing(tk.Canvas):
    def __init__(self, parent, size=96, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=T["BG"], highlightthickness=0, **kw)
        self.size = size
        self._pct = AnimatedValue(0)
        self._draw(0)
        self._loop()

    def _loop(self):
        if not self._pct.settled:
            self._pct.step()
            self._draw(self._pct.current)
        self.after(16, self._loop)

    def set_percent(self, pct):
        self._pct.set_target(pct, speed=0.07)

    def recolor(self):
        self.configure(bg=T["BG"])
        self._draw(self._pct.current)

    def _draw(self, pct):
        self.delete("all")
        s, p = self.size, max(0, min(100, pct))
        m = 10
        self.create_arc(m, m, s-m, s-m, start=90, extent=360,
                        outline=T["RING_TRK"], width=8, style="arc")
        if p > 0:
            self.create_arc(m, m, s-m, s-m, start=90, extent=-(3.6*p),
                            outline=T["ACCENT"], width=8, style="arc")
        self.create_text(s//2, s//2, text=f"{int(p)}%",
                         fill=T["TEXT"], font=("Georgia", 14, "bold"))


# ─── ADD / EDIT DIALOG ────────────────────────────────────────────────────────
class TaskDialog(tk.Toplevel):
    """Shared dialog for adding and editing tasks."""

    def __init__(self, root, title="Add Task", task=None, on_save=None):
        super().__init__(root)
        self.result  = None
        self.on_save = on_save
        self.task    = task or {}

        self.title(title)
        self.geometry("500x420")
        self.configure(bg=T["SURFACE"])
        self.resizable(False, False)
        self.transient(root)
        self.grab_set()

        self._build()

    def _field(self, parent, label):
        tk.Label(parent, text=label, bg=T["SURFACE"], fg=T["TEXT_DIM"],
                 font=FONT_HINT).pack(anchor="w", padx=24, pady=(14, 3))

    def _entry_frame(self, parent):
        f = tk.Frame(parent, bg=T["CARD"],
                     highlightbackground=T["BORDER"], highlightthickness=1)
        f.pack(fill="x", padx=24)
        return f

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=T["ACCENT"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), bg=T["ACCENT"], fg=T["TOAST_FG"],
                 font=FONT_BTN, padx=20, pady=10, anchor="w").pack(anchor="w")

        # Task text
        self._field(self, "Task description *")
        ef = self._entry_frame(self)
        self.e_text = tk.Entry(ef, bg=T["CARD"], fg=T["TEXT"],
                               insertbackground=T["ACCENT"],
                               font=FONT_ITEM, bd=0, highlightthickness=0)
        self.e_text.pack(fill="x", padx=12, pady=10)
        self.e_text.insert(0, self.task.get("text", ""))

        # Row: Priority + Tag
        row = tk.Frame(self, bg=T["SURFACE"])
        row.pack(fill="x", padx=24, pady=(14, 0))

        # Priority
        pl = tk.Frame(row, bg=T["SURFACE"])
        pl.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(pl, text="Priority", bg=T["SURFACE"], fg=T["TEXT_DIM"],
                 font=FONT_HINT).pack(anchor="w", pady=(0, 3))
        pf = tk.Frame(pl, bg=T["CARD"],
                      highlightbackground=T["BORDER"], highlightthickness=1)
        pf.pack(fill="x")
        self._prio_var = tk.StringVar(value=self.task.get("priority", "med"))
        prio_cb = ttk.Combobox(pf, textvariable=self._prio_var,
                               values=["high", "med", "low"], state="readonly",
                               font=FONT_SMALL, width=8)
        prio_cb.pack(fill="x", padx=8, pady=7)

        # Tag
        tl = tk.Frame(row, bg=T["SURFACE"])
        tl.pack(side="left", expand=True, fill="x")
        tk.Label(tl, text="Tag", bg=T["SURFACE"], fg=T["TEXT_DIM"],
                 font=FONT_HINT).pack(anchor="w", pady=(0, 3))
        tf = tk.Frame(tl, bg=T["CARD"],
                      highlightbackground=T["BORDER"], highlightthickness=1)
        tf.pack(fill="x")
        self._tag_var = tk.StringVar(value=self.task.get("tag", ""))
        tag_cb = ttk.Combobox(tf, textvariable=self._tag_var,
                              values=TAGS, state="readonly",
                              font=FONT_SMALL, width=10)
        tag_cb.pack(fill="x", padx=8, pady=7)

        self._apply_combobox_style()

        # Due date
        self._field(self, "Due date (YYYY-MM-DD, optional)")
        df = self._entry_frame(self)
        self.e_due = tk.Entry(df, bg=T["CARD"], fg=T["TEXT"],
                              insertbackground=T["ACCENT"],
                              font=FONT_SMALL, bd=0, highlightthickness=0)
        self.e_due.pack(fill="x", padx=12, pady=9)
        self.e_due.insert(0, self.task.get("due", ""))

        # Note
        self._field(self, "Note (optional)")
        nf = self._entry_frame(self)
        self.e_note = tk.Entry(nf, bg=T["CARD"], fg=T["TEXT"],
                               insertbackground=T["ACCENT"],
                               font=FONT_SMALL, bd=0, highlightthickness=0)
        self.e_note.pack(fill="x", padx=12, pady=9)
        self.e_note.insert(0, self.task.get("note", ""))

        # Buttons
        btn_row = tk.Frame(self, bg=T["SURFACE"])
        btn_row.pack(fill="x", padx=24, pady=20)

        cancel = tk.Label(btn_row, text="Cancel", bg=T["SURFACE"],
                          fg=T["TEXT_DIM"], font=FONT_BTN,
                          padx=18, pady=9, cursor="hand2")
        cancel.pack(side="right", padx=(8, 0))
        cancel.bind("<Button-1>", lambda e: self.destroy())

        save = tk.Label(btn_row, text="  SAVE  ", bg=T["ACCENT"],
                        fg=T["TOAST_FG"], font=FONT_BTN,
                        padx=18, pady=9, cursor="hand2")
        save.pack(side="right")
        save.bind("<Button-1>", lambda e: self._save())

        self.e_text.bind("<Return>", lambda e: self._save())
        self.e_text.focus_set()

    def _apply_combobox_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TCombobox",
                    fieldbackground=T["CARD"], background=T["CARD"],
                    foreground=T["TEXT"], bordercolor=T["BORDER"],
                    arrowcolor=T["ACCENT"], selectbackground=T["SEL_BG"],
                    selectforeground=T["TEXT"])
        s.map("TCombobox", fieldbackground=[("readonly", T["CARD"])],
              foreground=[("readonly", T["TEXT"])])

    def _save(self):
        text = self.e_text.get().strip()
        if not text:
            self.e_text.configure(highlightbackground=T["ACCENT2"],
                                  highlightthickness=2)
            return
        self.result = {
            "text":     text,
            "priority": self._prio_var.get(),
            "tag":      self._tag_var.get(),
            "due":      self.e_due.get().strip(),
            "note":     self.e_note.get().strip(),
        }
        if self.on_save:
            self.on_save(self.result)
        self.destroy()


# ─── TASK ROW ─────────────────────────────────────────────────────────────────
class TaskRow(tk.Frame):
    def __init__(self, parent, task, on_toggle, on_delete, on_edit, **kw):
        super().__init__(parent, bg=T["CARD"], **kw)
        self.task      = task
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self.on_edit   = on_edit
        self._build()
        self._slide_in()

    def _build(self):
        done = self.task.get("done", False)
        prio = self.task.get("priority", "med")
        tag  = self.task.get("tag",  "")
        due  = self.task.get("due",  "")
        note = self.task.get("note", "")

        # priority left stripe
        stripe_colors = {
            "high": T["P_HIGH"][1],
            "med":  T["P_MED"][1],
            "low":  T["P_LOW"][1],
            "":     T["BORDER"],
        }
        stripe = tk.Frame(self, bg=stripe_colors.get(prio, T["BORDER"]), width=4)
        stripe.pack(side="left", fill="y")

        inner = tk.Frame(self, bg=T["CARD"])
        inner.pack(fill="x", padx=12, pady=10, expand=True)
        self._inner = inner
        self._stripe = stripe

        # checkbox
        cb_size = 22
        self._cb = tk.Canvas(inner, width=cb_size, height=cb_size,
                             bg=T["CARD"], highlightthickness=0, cursor="hand2")
        self._cb.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="nw", pady=2)
        self._draw_cb(done)
        self._cb.bind("<Button-1>", lambda e: self.on_toggle(self.task["id"]))

        # text
        txt_col = T["TEXT_DONE"] if done else T["TEXT"]
        self._lbl = tk.Label(inner, text=self.task["text"],
                             bg=T["CARD"], fg=txt_col,
                             font=FONT_ITEM_B if not done else FONT_ITEM,
                             anchor="w", justify="left", wraplength=380)
        self._lbl.grid(row=0, column=1, sticky="ew")
        inner.columnconfigure(1, weight=1)

        # meta row: tag + due + note
        meta = tk.Frame(inner, bg=T["CARD"])
        meta.grid(row=1, column=1, sticky="w", pady=(3, 0))
        self._meta = meta

        # priority badge
        if prio:
            pbg, pfg, _ = T[f"P_{prio.upper()}"]
            tk.Label(meta, text=PRIORITY_LABELS[prio],
                     bg=pbg, fg=pfg, font=FONT_PRIO,
                     padx=5, pady=1).pack(side="left", padx=(0, 6))

        # tag badge
        tag_key = f"TAG_{tag[:4].upper()}" if tag else None
        if tag_key and tag_key in T:
            tbg, tfg = T[tag_key]
            tk.Label(meta, text=f" {tag.upper()} ",
                     bg=tbg, fg=tfg, font=FONT_TAG,
                     padx=4, pady=1).pack(side="left", padx=(0, 6))

        # due label
        dlabel, dcolor = due_label(due)
        if dlabel:
            tk.Label(meta, text=dlabel, bg=T["CARD"], fg=dcolor,
                     font=FONT_DATE).pack(side="left", padx=(0, 6))

        # note
        if note:
            tk.Label(meta, text=note, bg=T["CARD"], fg=T["TEXT_DIM"],
                     font=FONT_SMALL).pack(side="left")

        # action buttons (shown on hover)
        self._btn_frame = tk.Frame(inner, bg=T["CARD"])
        self._btn_frame.grid(row=0, column=2, sticky="ne", padx=(8, 0))
        self._edit_btn = tk.Label(self._btn_frame, text="✎",
                                  bg=T["CARD"], fg=T["ICON_EDIT"],
                                  font=("Segoe UI", 15), cursor="hand2")
        self._edit_btn.pack(side="left", padx=3)
        self._edit_btn.bind("<Button-1>", lambda e: self.on_edit(self.task["id"]))

        self._del_btn = tk.Label(self._btn_frame, text="✕",
                                 bg=T["CARD"], fg=T["ICON_DEL"],
                                 font=("Segoe UI", 14, "bold"), cursor="hand2")
        self._del_btn.pack(side="left", padx=3)
        self._del_btn.bind("<Button-1>", lambda e: self.on_delete(self.task["id"]))

        self._btn_frame.grid_remove()

        # hover bindings
        self._all_widgets = [self, inner, self._lbl, meta, self._cb,
                             stripe, self._edit_btn, self._del_btn, self._btn_frame]
        self._all_widgets += list(meta.winfo_children())
        for w in self._all_widgets:
            try:
                w.bind("<Enter>", self._on_enter)
                w.bind("<Leave>", self._on_leave)
            except Exception:
                pass

    def _draw_cb(self, done):
        self._cb.delete("all")
        sz = 22
        if done:
            self._cb.create_oval(1, 1, sz-1, sz-1,
                                 fill=T["ACCENT"], outline=T["ACCENT"])
            self._cb.create_text(sz//2, sz//2, text="✓",
                                 fill=T["TOAST_FG"],
                                 font=("Segoe UI", 11, "bold"))
        else:
            self._cb.create_oval(1, 1, sz-1, sz-1,
                                 fill="", outline=T["TEXT_DIM"], width=2)

    def _on_enter(self, e=None):
        self._set_bg(T["CARD_HOVER"])
        self._btn_frame.grid()

    def _on_leave(self, e=None):
        self._set_bg(T["CARD"])
        self._btn_frame.grid_remove()

    def _set_bg(self, color):
        self.configure(bg=color)
        for w in self._all_widgets:
            try:
                w.configure(bg=color)
            except Exception:
                pass
        try:
            self._cb.configure(bg=color)
        except Exception:
            pass

    def _slide_in(self):
        def step(frame=0, total=12):
            if frame > total:
                return
            t   = ease_out_cubic(frame / total)
            pad = int(16 * (1 - t))
            try:
                self.pack_configure(pady=(pad, 0))
            except Exception:
                return
            self.after(18, lambda: step(frame + 1, total))
        step()

    def flash(self, color):
        orig = self.cget("bg")
        self.configure(bg=color)
        self.after(220, lambda: self.configure(bg=orig))


# ─── MAIN APP ─────────────────────────────────────────────────────────────────
class MrSelfishTodo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MR. SELFISH — To-Do v2")
        self.root.geometry("940x780")
        self.root.minsize(780, 580)
        self.root.configure(bg=T["BG"])
        self.root.resizable(True, True)

        self._dark_mode  = False
        self.tasks       = []
        self._rows       = {}
        self._filter     = "all"
        self._tag_filter = None
        self._prio_sort  = False
        self._next_id    = 1
        self.toast       = Toast(self.root)

        self._pulse_val = AnimatedValue(0)
        self._pulse_dir = 1

        self._load_tasks()
        self._build_ui()
        self._refresh()
        self._pulse_loop()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    # ── persistence ──
    def _load_tasks(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.tasks    = data.get("tasks", [])
                self._next_id = data.get("next_id", 1)
                return
            except Exception:
                pass
        self._seed_demo()

    def _save_tasks(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"tasks": self.tasks, "next_id": self._next_id}, f,
                          ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

    def _on_close(self):
        self._save_tasks()
        self.root.destroy()

    def _seed_demo(self):
        demos = [
            ("Design new brand identity",   "high", "work",     "Due Friday",  "2025-03-20"),
            ("Morning run — 5 km",          "med",  "health",   "",            ""),
            ("Quarterly tax filing",        "high", "finance",  "⚠ Overdue",  "2025-03-01"),
            ("Call mom on her birthday",    "high", "personal", "Today!",      ""),
            ("Fix critical login bug",      "high", "urgent",   "ASAP",        "2025-03-15"),
            ("Read Deep Work ch. 4",        "low",  "personal", "30 min",      ""),
            ("Grocery run",                 "low",  "",         "",            ""),
        ]
        for text, prio, tag, note, due in demos:
            self.tasks.append({
                "id":       self._next_id,
                "text":     text,
                "priority": prio,
                "tag":      tag,
                "note":     note,
                "due":      due,
                "done":     False,
            })
            self._next_id += 1
        self.tasks[-1]["done"] = True
        self.tasks[-2]["done"] = True

    # ── UI build ──
    def _build_ui(self):
        # ── SIDEBAR ──
        self.sidebar = tk.Frame(self.root, bg=T["SIDEBAR"], width=218)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._sidebar_widgets = []

        self._sb_brand = tk.Label(self.sidebar, text="MR.\nSELFISH",
                                  bg=T["SIDEBAR"], fg=T["ACCENT"],
                                  font=FONT_TITLE, justify="left", anchor="w")
        self._sb_brand.pack(anchor="w", padx=22, pady=(28, 2))
        self._sb_sub = tk.Label(self.sidebar, text="task master pro",
                                bg=T["SIDEBAR"], fg=T["TEXT_DIM"],
                                font=FONT_BRAND)
        self._sb_sub.pack(anchor="w", padx=22)

        self._sb_div1 = tk.Frame(self.sidebar, bg=T["BORDER"], height=1)
        self._sb_div1.pack(fill="x", padx=16, pady=18)

        # Dark mode toggle
        toggle_row = tk.Frame(self.sidebar, bg=T["SIDEBAR"])
        toggle_row.pack(fill="x", padx=22, pady=(0, 14))
        tk.Label(toggle_row, text="Dark mode", bg=T["SIDEBAR"],
                 fg=T["TEXT_DIM"], font=FONT_HINT).pack(side="left")
        self._toggle_canvas = tk.Canvas(toggle_row, width=44, height=22,
                                        bg=T["SIDEBAR"], highlightthickness=0,
                                        cursor="hand2")
        self._toggle_canvas.pack(side="right")
        self._toggle_canvas.bind("<Button-1>", lambda e: self._toggle_dark())
        self._draw_toggle()

        # Stats ring
        ring_f = tk.Frame(self.sidebar, bg=T["SIDEBAR"])
        ring_f.pack(padx=22, anchor="w")
        self.ring = ProgressRing(ring_f, size=96)
        self.ring.pack()
        self._stat_lbl = tk.Label(ring_f, text="0 / 0 done",
                                  bg=T["SIDEBAR"], fg=T["TEXT_DIM"],
                                  font=FONT_SMALL)
        self._stat_lbl.pack(pady=4)

        self._sb_div2 = tk.Frame(self.sidebar, bg=T["BORDER"], height=1)
        self._sb_div2.pack(fill="x", padx=16, pady=16)

        # Filter
        self._sb_filt_lbl = tk.Label(self.sidebar, text="FILTER",
                                     bg=T["SIDEBAR"], fg=T["TEXT_DIM"],
                                     font=FONT_TAG)
        self._sb_filt_lbl.pack(anchor="w", padx=22, pady=(0, 6))

        self._filter_btns = {}
        for key, label in [("all", "All Tasks"), ("active", "Active"),
                            ("overdue", "Overdue"), ("done", "Completed")]:
            btn = tk.Label(self.sidebar, text=label, bg=T["SIDEBAR"],
                           fg=T["TEXT_DIM"], font=FONT_SMALL,
                           anchor="w", cursor="hand2", padx=22, pady=6)
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, k=key: self._set_filter(k))
            btn.bind("<Enter>",    lambda e, b=btn: b.configure(fg=T["ACCENT"]))
            btn.bind("<Leave>",    lambda e, b=btn, k=key: b.configure(
                fg=T["ACCENT"] if self._filter == k else T["TEXT_DIM"]))
            self._filter_btns[key] = btn

        self._sb_div3 = tk.Frame(self.sidebar, bg=T["BORDER"], height=1)
        self._sb_div3.pack(fill="x", padx=16, pady=14)

        # Tags
        self._sb_tag_lbl = tk.Label(self.sidebar, text="TAGS",
                                    bg=T["SIDEBAR"], fg=T["TEXT_DIM"],
                                    font=FONT_TAG)
        self._sb_tag_lbl.pack(anchor="w", padx=22, pady=(0, 6))

        tag_key_map = {
            "work":    "TAG_WORK",
            "personal":"TAG_PERS",
            "urgent":  "TAG_URG",
            "health":  "TAG_HLTH",
            "finance": "TAG_FIN",
        }
        for tag, tkey in tag_key_map.items():
            f = tk.Frame(self.sidebar, bg=T["SIDEBAR"], cursor="hand2")
            f.pack(fill="x", padx=22, pady=2)
            _, fg_c = T[tkey]
            dot = tk.Canvas(f, width=9, height=9,
                            bg=T["SIDEBAR"], highlightthickness=0)
            dot.create_oval(0, 0, 9, 9, fill=fg_c, outline="")
            dot.pack(side="left", padx=(0, 9))
            lbl = tk.Label(f, text=tag, bg=T["SIDEBAR"],
                           fg=T["TEXT_DIM"], font=FONT_SMALL)
            lbl.pack(side="left")
            for w in (f, dot, lbl):
                w.bind("<Button-1>", lambda e, t=tag: self._set_tag_filter(t))
                w.bind("<Enter>",    lambda e, l=lbl, tk2=tkey: l.configure(
                    fg=T[tk2][1]))
                w.bind("<Leave>",    lambda e, l=lbl: l.configure(
                    fg=T["ACCENT"] if self._tag_filter == tag else T["TEXT_DIM"]))

        clr = tk.Label(self.sidebar, text="✕ clear tag",
                       bg=T["SIDEBAR"], fg=T["TEXT_DIM"],
                       font=FONT_HINT, cursor="hand2", padx=22)
        clr.pack(anchor="w", pady=(8, 0))
        clr.bind("<Button-1>", lambda e: self._set_tag_filter(None))

        self._sb_bottom = tk.Label(self.sidebar, text="✦ by mr selfish",
                                   bg=T["SIDEBAR"], fg=T["BORDER"],
                                   font=FONT_HINT)
        self._sb_bottom.pack(side="bottom", pady=14)

        # ── MAIN AREA ──
        self.main = tk.Frame(self.root, bg=T["SURFACE"])
        self.main.pack(side="left", fill="both", expand=True)

        # animated top stripe
        self._top_canvas = tk.Canvas(self.main, height=4, bg=T["SURFACE"],
                                     highlightthickness=0)
        self._top_canvas.pack(fill="x")

        # input row
        inp = tk.Frame(self.main, bg=T["SURFACE"])
        inp.pack(fill="x", padx=22, pady=16)

        self._ef = tk.Frame(inp, bg=T["CARD"],
                            highlightbackground=T["BORDER"],
                            highlightthickness=1)
        self._ef.pack(fill="x", side="left", expand=True)
        self.entry = tk.Entry(self._ef, bg=T["CARD"], fg=T["TEXT"],
                              insertbackground=T["ACCENT"],
                              font=FONT_ITEM, bd=0, highlightthickness=0)
        self.entry.pack(fill="x", padx=14, pady=10)
        self._placeholder = "What needs to be done?"
        self.entry.insert(0, self._placeholder)
        self.entry.configure(fg=T["TEXT_DIM"])
        self.entry.bind("<FocusIn>",  self._entry_in)
        self.entry.bind("<FocusOut>", self._entry_out)
        self.entry.bind("<Return>",   self._quick_add)
        self._ef.bind("<Enter>",
                      lambda e: self._ef.configure(highlightbackground=T["ACCENT"]))
        self._ef.bind("<Leave>",
                      lambda e: self._ef.configure(highlightbackground=T["BORDER"]))

        add_btn = tk.Label(inp, text="  + ADD  ", bg=T["ACCENT"],
                           fg=T["TOAST_FG"], font=FONT_BTN,
                           padx=4, pady=8, cursor="hand2")
        add_btn.pack(side="left", padx=(8, 0))
        add_btn.bind("<Button-1>", lambda e: self._open_add_dialog())
        add_btn.bind("<Enter>",    lambda e: add_btn.configure(bg=T["ACCENT2"]))
        add_btn.bind("<Leave>",    lambda e: add_btn.configure(bg=T["ACCENT"]))
        self._add_btn = add_btn

        # sort toggle
        sort_btn = tk.Label(inp, text="⇅ Priority", bg=T["SURFACE"],
                            fg=T["TEXT_DIM"], font=FONT_HINT,
                            padx=8, cursor="hand2")
        sort_btn.pack(side="left", padx=(6, 0))
        sort_btn.bind("<Button-1>", lambda e: self._toggle_sort())
        sort_btn.bind("<Enter>",    lambda e: sort_btn.configure(fg=T["ACCENT"]))
        sort_btn.bind("<Leave>",    lambda e: sort_btn.configure(fg=T["TEXT_DIM"]))
        self._sort_btn = sort_btn

        # headline counter
        head = tk.Frame(self.main, bg=T["SURFACE"])
        head.pack(fill="x", padx=22, pady=(0, 12))

        self._count_lbl = tk.Label(head, text="0", bg=T["SURFACE"],
                                   fg=T["ACCENT"], font=FONT_COUNT)
        self._count_lbl.pack(side="left")
        self._count_sub = tk.Label(head, text="tasks remaining",
                                   bg=T["SURFACE"], fg=T["TEXT_DIM"],
                                   font=FONT_SMALL)
        self._count_sub.pack(side="left", padx=(8, 0), pady=(12, 0))

        bulk = tk.Frame(head, bg=T["SURFACE"])
        bulk.pack(side="right", pady=(12, 0))
        for label, cmd in [("Clear done ✕", self._clear_done),
                            ("All done ✓",  self._mark_all_done)]:
            b = tk.Label(bulk, text=label, bg=T["SURFACE"],
                         fg=T["TEXT_DIM"], font=FONT_HINT,
                         cursor="hand2", padx=8)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, fn=cmd: fn())
            b.bind("<Enter>",    lambda e, bb=b: bb.configure(fg=T["ACCENT"]))
            b.bind("<Leave>",    lambda e, bb=b: bb.configure(fg=T["TEXT_DIM"]))

        # save indicator
        self._save_lbl = tk.Label(self.main, text="", bg=T["SURFACE"],
                                  fg=T["TEXT_DIM"], font=FONT_HINT)
        self._save_lbl.pack(anchor="e", padx=22)

        # task list
        cont = tk.Frame(self.main, bg=T["SURFACE"])
        cont.pack(fill="both", expand=True, padx=22, pady=(0, 16))

        self.canvas = tk.Canvas(cont, bg=T["SURFACE"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(cont, orient="vertical", command=self.canvas.yview)
        sb.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=sb.set)

        self.task_frame = tk.Frame(self.canvas, bg=T["SURFACE"])
        self._win_id = self.canvas.create_window((0, 0), window=self.task_frame,
                                                 anchor="nw")
        self.task_frame.bind("<Configure>", self._on_frame_cfg)
        self.canvas.bind("<Configure>",     self._on_canvas_cfg)
        self.canvas.bind_all("<MouseWheel>", self._on_scroll)

    # ── dark mode toggle ──
    def _draw_toggle(self):
        c = self._toggle_canvas
        c.delete("all")
        on = self._dark_mode
        track_color = T["ACCENT"] if on else T["BORDER2"]
        c.create_rounded_rect = lambda x1,y1,x2,y2,r,**kw: c.create_polygon(
            x1+r,y1, x2-r,y1, x2,y1+r, x2,y2-r, x2-r,y2, x1+r,y2,
            x1,y2-r, x1,y1+r, smooth=True, **kw)
        c.create_rounded_rect(0, 0, 44, 22, 11, fill=track_color, outline="")
        knob_x = 33 if on else 11
        c.create_oval(knob_x-9, 2, knob_x+9, 20, fill=T["CARD"], outline="")

    def _toggle_dark(self):
        global T
        self._dark_mode = not self._dark_mode
        T = THEMES["dark"] if self._dark_mode else THEMES["light"]
        self._apply_theme()
        self._draw_toggle()
        self._refresh()
        self.toast.show("🌙 Dark mode on" if self._dark_mode else "☀ Light mode on",
                        T["ACCENT"])

    def _apply_theme(self):
        """Repaint all static widgets to new theme."""
        self.root.configure(bg=T["BG"])
        self.sidebar.configure(bg=T["SIDEBAR"])
        self.main.configure(bg=T["SURFACE"])
        self._sb_brand.configure(bg=T["SIDEBAR"], fg=T["ACCENT"])
        self._sb_sub.configure(bg=T["SIDEBAR"],   fg=T["TEXT_DIM"])
        self._sb_div1.configure(bg=T["BORDER"])
        self._sb_div2.configure(bg=T["BORDER"])
        self._sb_div3.configure(bg=T["BORDER"])
        self._sb_filt_lbl.configure(bg=T["SIDEBAR"], fg=T["TEXT_DIM"])
        self._sb_tag_lbl.configure(bg=T["SIDEBAR"],  fg=T["TEXT_DIM"])
        self._sb_bottom.configure(bg=T["SIDEBAR"],   fg=T["BORDER"])
        self._stat_lbl.configure(bg=T["SIDEBAR"],    fg=T["TEXT_DIM"])
        self.ring.configure(bg=T["BG"])
        self.ring.recolor()
        self._toggle_canvas.configure(bg=T["SIDEBAR"])
        self._top_canvas.configure(bg=T["SURFACE"])
        self.canvas.configure(bg=T["SURFACE"])
        self.task_frame.configure(bg=T["SURFACE"])
        self._ef.configure(bg=T["CARD"], highlightbackground=T["BORDER"])
        self.entry.configure(bg=T["CARD"], fg=T["TEXT_DIM"],
                             insertbackground=T["ACCENT"])
        self._add_btn.configure(bg=T["ACCENT"], fg=T["TOAST_FG"])
        self._count_lbl.configure(bg=T["SURFACE"], fg=T["ACCENT"])
        self._count_sub.configure(bg=T["SURFACE"], fg=T["TEXT_DIM"])
        self._save_lbl.configure(bg=T["SURFACE"],  fg=T["TEXT_DIM"])
        self._sort_btn.configure(bg=T["SURFACE"],  fg=T["TEXT_DIM"])
        for btn in self._filter_btns.values():
            btn.configure(bg=T["SIDEBAR"], fg=T["TEXT_DIM"])
        # highlight active filter
        if self._filter in self._filter_btns:
            self._filter_btns[self._filter].configure(fg=T["ACCENT"])

    # ── pulse animation ──
    def _pulse_loop(self):
        self._pulse_val.step()
        if self._pulse_val.settled:
            self._pulse_dir *= -1
            self._pulse_val.set_target(
                1 if self._pulse_dir > 0 else 0, speed=0.025)
        try:
            self._draw_top_bar()
        except Exception:
            pass
        self.root.after(30, self._pulse_loop)

    def _draw_top_bar(self):
        c = self._top_canvas
        c.update_idletasks()
        w = c.winfo_width()
        if w < 2:
            return
        t   = self._pulse_val.current
        c1  = T["BAR1"]
        c2  = T["BAR2"]
        seg = 48
        c.delete("all")
        for i in range(seg):
            x0    = int(w * i / seg)
            x1    = int(w * (i + 1) / seg)
            ratio = (i / seg + t * 0.5) % 1.0
            color = hex_lerp(c1, c2, ratio)
            c.create_rectangle(x0, 0, x1, 4, fill=color, outline="")

    # ── entry ──
    def _entry_in(self, e=None):
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=T["TEXT"])

    def _entry_out(self, e=None):
        if not self.entry.get():
            self.entry.insert(0, self._placeholder)
            self.entry.configure(fg=T["TEXT_DIM"])

    def _quick_add(self, e=None):
        text = self.entry.get().strip()
        if not text or text == self._placeholder:
            return
        self._do_add({"text": text, "priority": "med",
                      "tag": "", "due": "", "note": ""})
        self.entry.delete(0, "end")
        self._entry_out()

    def _open_add_dialog(self):
        text = self.entry.get().strip()
        pre  = "" if text == self._placeholder else text
        TaskDialog(self.root, title="Add Task",
                   task={"text": pre},
                   on_save=lambda r: (self._do_add(r),
                                      self.entry.delete(0, "end"),
                                      self._entry_out()))

    def _do_add(self, result):
        task = {"id": self._next_id, "done": False, **result}
        self._next_id += 1
        self.tasks.insert(0, task)
        self._refresh()
        self._save_tasks()
        self._flash_save("✦ Saved")
        self.toast.show(f"✦ Added: {result['text'][:30]}", T["ACCENT"])

    # ── CRUD ──
    def _toggle_task(self, tid):
        for t in self.tasks:
            if t["id"] == tid:
                t["done"] = not t["done"]
                if tid in self._rows:
                    col = T["SEL_BG"] if t["done"] else T["CARD_HOVER"]
                    self._rows[tid].flash(col)
                self._refresh()
                self._save_tasks()
                self._flash_save("✓ Saved")
                msg = "✓ Done!" if t["done"] else "↩ Reopened"
                self.toast.show(msg, T["ACCENT"] if t["done"] else T["ACCENT2"])
                break

    def _delete_task(self, tid):
        if messagebox.askyesno("Delete task",
                               "Remove this task permanently?",
                               parent=self.root):
            self.tasks = [t for t in self.tasks if t["id"] != tid]
            self._refresh()
            self._save_tasks()
            self._flash_save("✕ Deleted")
            self.toast.show("✕ Task removed", T["ACCENT2"])

    def _edit_task(self, tid):
        for t in self.tasks:
            if t["id"] == tid:
                TaskDialog(self.root, title="Edit Task", task=t,
                           on_save=lambda r, task=t: self._apply_edit(task, r))
                break

    def _apply_edit(self, task, result):
        task.update(result)
        self._refresh()
        self._save_tasks()
        self._flash_save("✎ Saved")
        self.toast.show("✎ Task updated", T["ACCENT"])

    def _clear_done(self):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t["done"]]
        n = before - len(self.tasks)
        if n:
            self._refresh()
            self._save_tasks()
            self._flash_save("✕ Saved")
            self.toast.show(f"✕ Cleared {n} task{'s' if n>1 else ''}", T["ACCENT2"])

    def _mark_all_done(self):
        for t in self.tasks:
            t["done"] = True
        self._refresh()
        self._save_tasks()
        self._flash_save("✓ All saved")
        self.toast.show("🎉 All tasks done!", T["ACCENT"])

    def _flash_save(self, msg):
        self._save_lbl.configure(text=msg, fg=T["ACCENT"])
        self.root.after(2500, lambda: self._save_lbl.configure(text=""))

    # ── filter / sort ──
    def _set_filter(self, key):
        self._filter = key
        for k, btn in self._filter_btns.items():
            btn.configure(fg=T["ACCENT"] if k == key else T["TEXT_DIM"])
        self._refresh()

    def _set_tag_filter(self, tag):
        self._tag_filter = tag
        self._refresh()

    def _toggle_sort(self):
        self._prio_sort = not self._prio_sort
        self._sort_btn.configure(fg=T["ACCENT"] if self._prio_sort else T["TEXT_DIM"])
        self._refresh()

    # ── scroll ──
    def _on_frame_cfg(self, e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_cfg(self, e=None):
        self.canvas.itemconfig(self._win_id, width=e.width)

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    # ── render ──
    def _refresh(self):
        visible = list(self.tasks)

        # filter
        if self._filter == "active":
            visible = [t for t in visible if not t["done"]]
        elif self._filter == "done":
            visible = [t for t in visible if t["done"]]
        elif self._filter == "overdue":
            visible = [t for t in visible
                       if not t["done"] and days_until(t.get("due")) is not None
                       and days_until(t.get("due")) < 0]
        if self._tag_filter:
            visible = [t for t in visible if t.get("tag") == self._tag_filter]

        # sort by priority
        if self._prio_sort:
            order = {"high": 0, "med": 1, "low": 2, "": 3}
            visible.sort(key=lambda t: (t.get("done", False),
                                        order.get(t.get("priority", ""), 3)))

        # stats
        total  = len(self.tasks)
        done   = sum(1 for t in self.tasks if t["done"])
        active = total - done
        pct    = (done / total * 100) if total else 0
        self.ring.set_percent(pct)
        self._stat_lbl.configure(text=f"{done} / {total} done")
        self._count_lbl.configure(text=str(active))
        self._count_sub.configure(
            text="task remaining" if active == 1 else "tasks remaining")

        # clear
        for w in self.task_frame.winfo_children():
            w.destroy()
        self._rows.clear()

        active_tasks = [t for t in visible if not t["done"]]
        done_tasks   = [t for t in visible if t["done"]]

        if active_tasks:
            self._section_lbl("● Active")
            for task in active_tasks:
                self._render_row(task)

        if done_tasks:
            self._section_lbl("✓ Completed")
            for task in done_tasks:
                self._render_row(task)

        if not visible:
            msg = ("No overdue tasks 🎉" if self._filter == "overdue"
                   else "Nothing here — add a task above!")
            tk.Label(self.task_frame, text=msg,
                     bg=T["SURFACE"], fg=T["TEXT_DIM"],
                     font=FONT_ITEM, justify="center").pack(pady=60)

    def _section_lbl(self, text):
        f = tk.Frame(self.task_frame, bg=T["SURFACE"])
        f.pack(fill="x", pady=(12, 4))
        tk.Label(f, text=text, bg=T["SURFACE"], fg=T["TEXT_DIM"],
                 font=FONT_TAG).pack(side="left")
        tk.Frame(f, bg=T["BORDER"], height=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0), pady=7)

    def _render_row(self, task):
        row = TaskRow(self.task_frame, task,
                      on_toggle=self._toggle_task,
                      on_delete=self._delete_task,
                      on_edit=self._edit_task)
        row.pack(fill="x", pady=(0, 2))
        tk.Frame(self.task_frame, bg=T["BORDER"], height=1).pack(fill="x")
        self._rows[task["id"]] = row


# ─── RUN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    MrSelfishTodo()