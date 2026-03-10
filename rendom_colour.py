import tkinter as tk
import random
import colorsys

# ── Mr. Selfish Color Generator ──────────────────────────────────────────────

BG_DARK    = "#0a0a0f"
FONT_TITLE = ("Georgia", 42, "bold")
FONT_SUB   = ("Georgia", 14, "italic")
FONT_HEX   = ("Courier New", 28, "bold")
FONT_BTN   = ("Georgia", 16, "bold")
FONT_BRAND = ("Georgia", 11)
FONT_LABEL = ("Georgia", 10)
FONT_RGB   = ("Courier New", 13, "bold")

def random_color():
    h = random.random()
    s = random.uniform(0.55, 1.0)
    v = random.uniform(0.65, 1.0)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return f"#{r:02X}{g:02X}{b:02X}", r, g, b

def luminance(r, g, b):
    def c(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126*c(r) + 0.7152*c(g) + 0.0722*c(b)

def text_color(r, g, b):
    return "#ffffff" if luminance(r, g, b) < 0.45 else "#111111"

def mix(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = int(r1 + (r2-r1)*t)
    g = int(g1 + (g2-g1)*t)
    b = int(b1 + (b2-b1)*t)
    return f"#{r:02X}{g:02X}{b:02X}"

class ColorApp:
    def __init__(self, root):
        self.root = root
        root.title("Mr. Selfish — Color Generator")
        root.geometry("700x700")
        root.resizable(False, False)
        root.configure(bg=BG_DARK)
        self.current_hex = "#7C3AED"
        self.current_rgb = (124, 58, 237)
        self._build_ui()
        self.generate_color()

    def _build_ui(self):
        root = self.root

        tk.Label(root, text="✦   M R .   S E L F I S H   ✦",
                 font=FONT_BRAND, bg=BG_DARK, fg="#555566").pack(pady=(22, 0))

        tk.Label(root, text="COLOR\nGENERATOR",
                 font=FONT_TITLE, bg=BG_DARK, fg="#f0eeff",
                 justify="center").pack(pady=(4, 0))

        tk.Label(root, text="— crafted with obsession —",
                 font=FONT_SUB, bg=BG_DARK, fg="#44445a").pack(pady=(0, 14))

        self.card = tk.Canvas(root, width=580, height=180,
                              bg="#141422", highlightthickness=2,
                              highlightbackground="#2a2a4a")
        self.card.pack(pady=6)
        self._draw_card()

        hex_frame = tk.Frame(root, bg=BG_DARK)
        hex_frame.pack(pady=(18, 4))
        tk.Label(hex_frame, text="HEX", font=FONT_LABEL,
                 bg=BG_DARK, fg="#555566").pack()
        self.hex_var = tk.StringVar(value="#7C3AED")
        self.hex_label = tk.Label(hex_frame, textvariable=self.hex_var,
                                  font=FONT_HEX, bg=BG_DARK, fg="#ffffff",
                                  cursor="hand2")
        self.hex_label.pack()
        self.hex_label.bind("<Button-1>", self._copy_hex)
        self.copy_flash = tk.Label(hex_frame, text="",
                                   font=("Georgia", 9, "italic"),
                                   bg=BG_DARK, fg="#7fffb0")
        self.copy_flash.pack()

        rgb_frame = tk.Frame(root, bg=BG_DARK)
        rgb_frame.pack(pady=(4, 18))
        tk.Label(rgb_frame, text="RGB", font=FONT_LABEL,
                 bg=BG_DARK, fg="#555566").pack()
        self.rgb_var = tk.StringVar(value="124  .  58  .  237")
        tk.Label(rgb_frame, textvariable=self.rgb_var,
                 font=FONT_RGB, bg=BG_DARK, fg="#aaaacc").pack()

        self.btn_canvas = tk.Canvas(root, width=340, height=66,
                                    bg=BG_DARK, highlightthickness=0)
        self.btn_canvas.pack(pady=8)
        self._draw_btn(hover=False)
        self.btn_canvas.bind("<Enter>",    lambda e: self._draw_btn(True))
        self.btn_canvas.bind("<Leave>",    lambda e: self._draw_btn(False))
        self.btn_canvas.bind("<Button-1>", lambda e: self.generate_color())

        tk.Label(root, text="RECENT PALETTE",
                 font=FONT_LABEL, bg=BG_DARK, fg="#555566").pack(pady=(18, 4))
        self.hist_frame = tk.Frame(root, bg=BG_DARK)
        self.hist_frame.pack()
        self.history = []
        self._build_history_swatches()

        tk.Label(root, text="click hex to copy  .  designed by mr. selfish",
                 font=("Georgia", 9, "italic"), bg=BG_DARK, fg="#33334a").pack(pady=(20, 10))

    def _draw_card(self, color="#7C3AED"):
        c = self.card
        c.delete("all")
        W, H = 580, 180

        c.create_rectangle(0, 0, W, H, fill="#18182a", outline="")

        steps = 80
        for i in range(steps):
            t   = i / steps
            col = mix(color, "#18182a", t * 0.72)
            x0  = int(W * (1 - t) * 0.62)
            x1  = int(W * (1 - (i-1)/steps) * 0.62) + 2
            c.create_rectangle(x0, 0, x1, H, fill=col, outline="")

        slab_w = int(W * 0.38)
        c.create_rectangle(0, 0, slab_w, H, fill=color, outline="")
        c.create_rectangle(0, 0, W-1, H-1, outline="#333355", width=1)
        c.create_line(1, 1, W-1, 1, fill="#666688", width=1)

        c.create_text(slab_w + (W-slab_w)//2, H//2,
                      text="YOUR\nCOLOR", font=("Georgia", 28, "bold"),
                      fill="#222235", anchor="center", justify="center")

    def _draw_btn(self, hover=False):
        c = self.btn_canvas
        c.delete("all")
        W, H, r = 340, 66, 33

        if hover:
            c.create_oval(14, 14, W-14, H+4, fill="#111122", outline="")

        fill = "#2a2a40" if not hover else "#32325a"
        self._round_rect(c, 0, 0, W, H, r, fill=fill, outline="")

        shimmer = mix(fill, "#ffffff", 0.08)
        self._round_rect(c, 1, 1, W-1, H//2, r, fill=shimmer, outline="")

        border_col = "#4a4a6a" if not hover else "#6a6aaa"
        self._round_rect(c, 0, 0, W, H, r, fill="", outline=border_col, width=1)

        accent = "#8888bb" if not hover else "#aaaadd"
        c.create_line(r, 1, W-r, 1, fill=accent, width=1)

        col = "#ffffee" if hover else "#e0deff"
        c.create_text(W//2, H//2, text="*  GENERATE  *",
                      font=FONT_BTN, fill=col, anchor="center")
        c.configure(cursor="hand2" if hover else "arrow")

    def _round_rect(self, canvas, x1, y1, x2, y2, r,
                    fill="", outline="", width=1):
        canvas.create_arc(x1, y1, x1+2*r, y1+2*r,
                          start=90,  extent=90, fill=fill,
                          outline=outline, width=width, style="pieslice")
        canvas.create_arc(x2-2*r, y1, x2, y1+2*r,
                          start=0,   extent=90, fill=fill,
                          outline=outline, width=width, style="pieslice")
        canvas.create_arc(x1, y2-2*r, x1+2*r, y2,
                          start=180, extent=90, fill=fill,
                          outline=outline, width=width, style="pieslice")
        canvas.create_arc(x2-2*r, y2-2*r, x2, y2,
                          start=270, extent=90, fill=fill,
                          outline=outline, width=width, style="pieslice")
        canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline="")
        canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline="")
        if outline:
            canvas.create_line(x1+r, y1,   x2-r, y1,   fill=outline, width=width)
            canvas.create_line(x1+r, y2,   x2-r, y2,   fill=outline, width=width)
            canvas.create_line(x1,   y1+r, x1,   y2-r, fill=outline, width=width)
            canvas.create_line(x2,   y1+r, x2,   y2-r, fill=outline, width=width)

    def _build_history_swatches(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()
        for hx in self.history[-10:]:
            swatch = tk.Canvas(self.hist_frame, width=42, height=42,
                               bg=BG_DARK, highlightthickness=0, cursor="hand2")
            swatch.create_rectangle(3, 3, 39, 39, fill=hx,
                                    outline="#333355", width=1)
            swatch.bind("<Button-1>", lambda e, h=hx: self._apply_color(h))
            swatch.pack(side="left", padx=3)

    def generate_color(self):
        hex_val, r, g, b = random_color()
        self.history.append(hex_val)
        self._apply_color(hex_val, (r, g, b))

    def _apply_color(self, hex_val, rgb=None):
        if rgb is None:
            r = int(hex_val[1:3], 16)
            g = int(hex_val[3:5], 16)
            b = int(hex_val[5:7], 16)
            rgb = (r, g, b)
        self.current_hex = hex_val
        self.current_rgb = rgb
        self.hex_var.set(hex_val)
        self.rgb_var.set(f"{rgb[0]}  .  {rgb[1]}  .  {rgb[2]}")
        self._draw_card(hex_val)
        self._build_history_swatches()

    def _copy_hex(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_hex)
        self.copy_flash.config(text="+ copied to clipboard")
        self.root.after(1800, lambda: self.copy_flash.config(text=""))

if __name__ == "__main__":
    root = tk.Tk()
    app  = ColorApp(root)
    root.mainloop()