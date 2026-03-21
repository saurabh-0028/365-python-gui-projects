import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import re

# ══════════════════════════════════════════════════════════
#   COLOR PALETTE  —  White / Light-Blue Glass Theme
# ══════════════════════════════════════════════════════════
BG_WHITE    = "#f0f6ff"
BG_PANEL    = "#e3edf7"
BG_EDITOR   = "#ffffff"
FG_DARK     = "#1a2540"
FG_MID      = "#4a6080"
FG_LIGHT    = "#7a90b0"

BTN_TOP     = "#daf0ff"
BTN_MID     = "#a8d8f0"
BTN_BOT     = "#6ab8e0"
BTN_BORDER  = "#5aaad0"
BTN_FG      = "#0d3a6e"
BTN_HOVER   = "#bce8ff"
BTN_PRESS   = "#82c4e8"

ACCENT_BLUE = "#1e7fc9"
ACCENT_GRN  = "#1a9e5c"
ERR_RED     = "#d9363e"
BORDER_LN   = "#b8cfe0"

C_KEY       = "#0550ae"
C_STR       = "#0a6640"
C_NUM       = "#b5450b"
C_BOOL      = "#7c3aed"
C_BRACKET   = "#334155"


# ══════════════════════════════════════════════════════════
#   GLASS BUTTON  (Canvas-based 3-D glass effect)
# ══════════════════════════════════════════════════════════
class GlassButton(tk.Frame):
    """3-D glass button using a Canvas inside a Frame."""

    def __init__(self, parent, text="", command=None,
                 btn_width=178, btn_height=44, icon=""):
        super().__init__(parent, bg=BG_PANEL)
        self._text     = text
        self._icon     = icon
        self._cmd      = command
        self._bw       = int(btn_width)
        self._bh       = int(btn_height)
        self._pressed  = False

        self._canvas = tk.Canvas(
            self,
            width=self._bw,
            height=self._bh,
            bg=BG_PANEL,
            highlightthickness=0,
            cursor="hand2"
        )
        self._canvas.pack()
        self._draw()

        self._canvas.bind("<ButtonPress-1>",   self._on_press)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Enter>",           self._on_enter)
        self._canvas.bind("<Leave>",           self._on_leave)

    # ── drawing ──────────────────────────────────────────
    def _draw(self, state="normal"):
        c = self._canvas
        c.delete("all")
        w, h, r = self._bw, self._bh, 12

        if state == "pressed":
            top, mid, bot, brd, dy = BTN_PRESS, BTN_BOT, BTN_MID, BTN_BORDER, 2
        elif state == "hover":
            top, mid, bot, brd, dy = BTN_HOVER, BTN_MID, BTN_BOT, BTN_BORDER, 0
        else:
            top, mid, bot, brd, dy = BTN_TOP, BTN_MID, BTN_BOT, BTN_BORDER, 0

        # Shadow
        self._rrect(c, 3, 3, w-1, h-1, r, fill="#9bbfd8", outline="")
        # Dark base
        self._rrect(c, 1, 1, w-3, h-3, r, fill=bot,       outline="")
        # Main body
        self._rrect(c, 1, 1, w-4, h-5, r, fill=mid,       outline="")
        # Top highlight
        self._rrect(c, 3, 3, w-6, h//2, max(r-2,1), fill=top, outline="")
        # Gloss arc
        c.create_arc(6, 4, w-6, 20, start=0, extent=180,
                     fill="", outline="#ffffff", width=1.5)
        # Border
        self._rrect(c, 1, 1, w-3, h-3, r, fill="", outline=brd, width=1.5)

        # Label
        label = "{icon}  {text}".format(icon=self._icon, text=self._text) \
                if self._icon else self._text
        c.create_text(w // 2, h // 2 + dy + 1,
                      text=label,
                      font=("Segoe UI", 11, "bold"),
                      fill=BTN_FG, anchor="center")

    def _rrect(self, c, x1, y1, x2, y2, r, **kw):
        c.create_arc(x1,      y1,      x1+2*r, y1+2*r, start=90,  extent=90,  **kw)
        c.create_arc(x2-2*r,  y1,      x2,     y1+2*r, start=0,   extent=90,  **kw)
        c.create_arc(x1,      y2-2*r,  x1+2*r, y2,     start=180, extent=90,  **kw)
        c.create_arc(x2-2*r,  y2-2*r,  x2,     y2,     start=270, extent=90,  **kw)
        c.create_rectangle(x1+r, y1,   x2-r, y2,   **kw)
        c.create_rectangle(x1,   y1+r, x2,   y2-r, **kw)

    # ── events ────────────────────────────────────────────
    def _on_press(self, _):
        self._pressed = True
        self._draw("pressed")

    def _on_release(self, _):
        self._pressed = False
        self._draw("hover")
        if self._cmd:
            self._cmd()

    def _on_enter(self, _):
        if not self._pressed:
            self._draw("hover")

    def _on_leave(self, _):
        self._pressed = False
        self._draw("normal")


# ══════════════════════════════════════════════════════════
#   MAIN APP
# ══════════════════════════════════════════════════════════
class JSONViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Viewer  .  Mr. Selfish  -  Day 23")
        self.root.geometry("980x700")
        self.root.minsize(750, 550)
        self.root.configure(bg=BG_WHITE)
        self._current_file = None
        self._raw_data     = None
        self._build_ui()

    # ──────────────────────────────────────────────────────
    def _build_ui(self):

        # ── TOP BAR ───────────────────────────────────────
        topbar = tk.Frame(self.root, bg="#c9e4f8", height=64)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Frame(topbar, bg=ACCENT_BLUE, width=6).pack(side="left", fill="y")
        tk.Label(topbar, text="{ }  JSON Viewer",
                 font=("Segoe UI", 20, "bold"),
                 bg="#c9e4f8", fg=ACCENT_BLUE
                 ).pack(side="left", padx=18, pady=10)
        tk.Label(topbar, text=" Day 23 ",
                 font=("Segoe UI", 10, "bold"),
                 bg=ACCENT_BLUE, fg="white", padx=4, pady=2
                 ).pack(side="left", pady=20)

        # ── BOTTOM FOOTER + STATUS ─────────────────────────
        foot_frame = tk.Frame(self.root, bg=BG_PANEL)
        foot_frame.pack(fill="x", side="bottom")

        tk.Frame(foot_frame, bg=BORDER_LN, height=2).pack(fill="x")

        status_row = tk.Frame(foot_frame, bg=BG_PANEL, height=30)
        status_row.pack(fill="x")
        status_row.pack_propagate(False)

        self.status_label = tk.Label(
            status_row, text="  No file loaded",
            font=("Segoe UI", 11), bg=BG_PANEL, fg=FG_LIGHT, anchor="w")
        self.status_label.pack(side="left", padx=14)

        self.size_label = tk.Label(
            status_row, text="",
            font=("Segoe UI", 11), bg=BG_PANEL, fg=FG_MID, anchor="e")
        self.size_label.pack(side="right", padx=14)

        # Designer credit
        footer = tk.Frame(foot_frame, bg="#c5dff5", height=30)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        tk.Label(footer,
                 text="  Designed by  Mr. Selfish     |   Python Tkinter GUI   |   Day 23 Project",
                 font=("Segoe UI", 10, "italic"),
                 bg="#c5dff5", fg=ACCENT_BLUE
                 ).pack(expand=True, pady=5)

        # ── SIDEBAR ───────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=BG_PANEL, width=210)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=BORDER_LN, height=2).pack(fill="x")
        tk.Label(sidebar, text="CONTROLS",
                 font=("Segoe UI", 12, "bold"),
                 bg=BG_PANEL, fg=FG_MID
                 ).pack(anchor="w", padx=18, pady=(16, 8))

        buttons = [
            ("Select JSON File",  self._select_file, "File"),
            ("Copy to Clipboard", self._copy_json,   "Copy"),
            ("Search Key",        self._open_search, "Search"),
            ("Clear",             self._clear,       "Clear"),
        ]
        for label, cmd, _ in buttons:
            GlassButton(sidebar, text=label, command=cmd,
                        btn_width=178, btn_height=44
                        ).pack(padx=16, pady=6)

        tk.Frame(sidebar, bg=BORDER_LN, height=1).pack(fill="x", padx=14, pady=12)
        tk.Label(sidebar, text="FILE INFO",
                 font=("Segoe UI", 12, "bold"),
                 bg=BG_PANEL, fg=FG_MID
                 ).pack(anchor="w", padx=18, pady=(0, 6))

        info_bg = tk.Frame(sidebar, bg="#ddeef8",
                           highlightbackground=BORDER_LN,
                           highlightthickness=1)
        info_bg.pack(fill="x", padx=14, pady=4)

        self.info_text = tk.Text(
            info_bg, font=("Segoe UI", 11),
            bg="#ddeef8", fg=FG_DARK,
            bd=0, relief="flat",
            wrap="word", state="disabled",
            height=9, width=22, padx=8, pady=6)
        self.info_text.pack(fill="x")

        # ── EDITOR ────────────────────────────────────────
        editor_frame = tk.Frame(self.root, bg=BG_WHITE)
        editor_frame.pack(fill="both", expand=True, side="right")

        toolbar = tk.Frame(editor_frame, bg="#ddeef8", height=42)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        tk.Frame(toolbar, bg=BORDER_LN, width=1).pack(side="left", fill="y")
        self.filename_label = tk.Label(
            toolbar, text="  no file selected  ",
            font=("Segoe UI", 12), bg="#ddeef8", fg=FG_LIGHT)
        self.filename_label.pack(side="left", padx=16, pady=8)

        tk.Label(toolbar, text="Indent:",
                 font=("Segoe UI", 11), bg="#ddeef8", fg=FG_MID
                 ).pack(side="right", padx=(0, 4), pady=10)

        self.indent_var = tk.IntVar(value=4)
        tk.Spinbox(toolbar, from_=1, to=8,
                   textvariable=self.indent_var,
                   font=("Segoe UI", 12, "bold"), width=3,
                   bg=BTN_MID, fg=ACCENT_BLUE,
                   relief="groove", bd=1,
                   buttonbackground=BTN_BOT,
                   command=self._reformat
                   ).pack(side="right", padx=(0, 16), pady=8)

        text_container = tk.Frame(editor_frame, bg=BG_WHITE)
        text_container.pack(fill="both", expand=True)

        v_scroll = tk.Scrollbar(text_container, orient="vertical",
                                bg=BG_PANEL, troughcolor="#e0eef8",
                                activebackground=ACCENT_BLUE)
        v_scroll.pack(side="right", fill="y")

        h_scroll = tk.Scrollbar(text_container, orient="horizontal",
                                bg=BG_PANEL, troughcolor="#e0eef8",
                                activebackground=ACCENT_BLUE)
        h_scroll.pack(side="bottom", fill="x")

        self.text = tk.Text(
            text_container,
            font=("Consolas", 13),
            bg=BG_EDITOR, fg=FG_DARK,
            insertbackground=ACCENT_BLUE,
            selectbackground="#bde0ff",
            selectforeground=FG_DARK,
            bd=0, relief="flat",
            wrap="none", state="disabled",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            padx=18, pady=14,
            spacing1=3, spacing2=2)
        self.text.pack(fill="both", expand=True, padx=(8, 0), pady=6)
        v_scroll.config(command=self.text.yview)
        h_scroll.config(command=self.text.xview)

        # Syntax tags
        self.text.tag_config("key",      foreground=C_KEY,     font=("Consolas", 13, "bold"))
        self.text.tag_config("string",   foreground=C_STR)
        self.text.tag_config("number",   foreground=C_NUM,     font=("Consolas", 13, "bold"))
        self.text.tag_config("boolean",  foreground=C_BOOL,    font=("Consolas", 13, "bold"))
        self.text.tag_config("bracket",  foreground=C_BRACKET, font=("Consolas", 13, "bold"))
        self.text.tag_config("search_hi",background="#fff176", foreground="#1a2540")

    # ──────────────────────────────────────────────────────
    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Select a JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        self._current_file = path
        self._load_and_display(path)

    def _load_and_display(self, path):
        try:
            file_size = os.path.getsize(path)
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            if not raw.strip():
                raise ValueError("File is empty.")
            data    = json.loads(raw)
            self._raw_data = data
            fmt     = json.dumps(data, indent=self.indent_var.get(), ensure_ascii=False)
            self._show_text(fmt)
            self._apply_syntax_highlight(fmt)
            fname   = os.path.basename(path)
            self.filename_label.config(text="  " + fname, fg=FG_DARK)
            self._set_status("  " + fname + "  loaded successfully", ACCENT_GRN)
            self.size_label.config(
                text=str(self._count_keys(data)) + " keys  .  " +
                     "{:.1f}".format(file_size / 1024) + " KB")
            self._update_info(data, fname, file_size)
        except json.JSONDecodeError as e:
            self._show_error("Invalid JSON\n\nDetails: " + str(e))
        except ValueError as e:
            self._show_error(str(e))
        except UnicodeDecodeError:
            self._show_error("Encoding error - not UTF-8.")
        except Exception as e:
            self._show_error("Unexpected error:\n" + str(e))

    def _show_text(self, content):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.config(state="disabled")

    def _show_error(self, msg):
        self._show_text(msg)
        self._set_status(msg.split("\n")[0], ERR_RED)
        self.filename_label.config(text="  error", fg=ERR_RED)
        self.size_label.config(text="")
        self._update_info_raw("")

    def _set_status(self, msg, color=None):
        self.status_label.config(text=msg, fg=color if color else FG_LIGHT)

    def _update_info(self, data, fname, size):
        self._update_info_raw(
            "Name  :  " + fname + "\n" +
            "Size  :  " + "{:.1f}".format(size / 1024) + " KB\n" +
            "Type  :  " + type(data).__name__ + "\n" +
            "Keys  :  " + str(self._count_keys(data)) + "\n" +
            "Indent :  " + str(self.indent_var.get()))

    def _update_info_raw(self, text):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", text)
        self.info_text.config(state="disabled")

    def _apply_syntax_highlight(self, text):
        self.text.config(state="normal")
        for lineno, line in enumerate(text.split("\n"), 1):
            for m in re.finditer(r'"([^"\\]|\\.)*"\s*:', line):
                self.text.tag_add("key",
                    str(lineno) + "." + str(m.start()),
                    str(lineno) + "." + str(m.end() - 1))
            for m in re.finditer(r':\s*"([^"\\]|\\.)*"', line):
                inner = re.search(r'"([^"\\]|\\.)*"', m.group())
                if inner:
                    col = m.start() + inner.start()
                    self.text.tag_add("string",
                        str(lineno) + "." + str(col),
                        str(lineno) + "." + str(col + len(inner.group())))
            for m in re.finditer(r':\s*(-?\d+\.?\d*([eE][+-]?\d+)?)', line):
                num = re.search(r'-?\d', m.group())
                if num:
                    col = m.start() + num.start()
                    val = m.group().strip(": \t")
                    self.text.tag_add("number",
                        str(lineno) + "." + str(col),
                        str(lineno) + "." + str(col + len(val)))
            for m in re.finditer(r'\b(true|false|null)\b', line):
                self.text.tag_add("boolean",
                    str(lineno) + "." + str(m.start()),
                    str(lineno) + "." + str(m.end()))
            for m in re.finditer(r'[{}\[\]]', line):
                self.text.tag_add("bracket",
                    str(lineno) + "." + str(m.start()),
                    str(lineno) + "." + str(m.end()))
        self.text.config(state="disabled")

    def _reformat(self):
        if self._raw_data is None:
            return
        fmt = json.dumps(self._raw_data,
                         indent=self.indent_var.get(), ensure_ascii=False)
        self._show_text(fmt)
        self._apply_syntax_highlight(fmt)

    def _copy_json(self):
        content = self.text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Copy", "Nothing to copy!")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self._set_status("  Copied to clipboard!", ACCENT_GRN)
        self.root.after(3000, lambda: self._set_status("  Ready"))

    def _open_search(self):
        win = tk.Toplevel(self.root)
        win.title("Search")
        win.geometry("380x140")
        win.configure(bg=BG_WHITE)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Search key or value:",
                 font=("Segoe UI", 12), bg=BG_WHITE, fg=FG_DARK
                 ).pack(anchor="w", padx=18, pady=(16, 5))

        entry_var = tk.StringVar()
        entry = tk.Entry(win, textvariable=entry_var,
                         font=("Segoe UI", 13),
                         bg="#e8f4fd", fg=ACCENT_BLUE,
                         insertbackground=ACCENT_BLUE,
                         relief="groove", bd=2)
        entry.pack(fill="x", padx=18, ipady=4)
        entry.focus()

        def do_search():
            self.text.tag_remove("search_hi", "1.0", "end")
            q = entry_var.get().strip()
            if not q:
                return
            start, count = "1.0", 0
            while True:
                pos = self.text.search(q, start, stopindex="end", nocase=True)
                if not pos:
                    break
                end_pos = pos + "+" + str(len(q)) + "c"
                self.text.tag_add("search_hi", pos, end_pos)
                start = end_pos
                count += 1
            if count:
                first = self.text.search(q, "1.0", nocase=True)
                if first:
                    self.text.see(first)
                self._set_status(
                    str(count) + " match(es) found for: " + q, ACCENT_BLUE)
            else:
                self._set_status("No matches for: " + q, ERR_RED)
            win.destroy()

        entry.bind("<Return>", lambda e: do_search())
        GlassButton(win, text="Search", command=do_search,
                    btn_width=130, btn_height=40).pack(pady=10)

    def _clear(self):
        self._current_file = None
        self._raw_data     = None
        self._show_text("")
        self.filename_label.config(text="  no file selected  ", fg=FG_LIGHT)
        self._set_status("  Cleared", FG_LIGHT)
        self.size_label.config(text="")
        self._update_info_raw("")

    def _count_keys(self, obj, count=0):
        if isinstance(obj, dict):
            count += len(obj)
            for v in obj.values():
                count = self._count_keys(v, count)
        elif isinstance(obj, list):
            for item in obj:
                count = self._count_keys(item, count)
        return count


# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.25)
    except Exception:
        pass
    JSONViewerApp(root)
    root.mainloop()