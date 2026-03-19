import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# ─────────────────────────────────────────────
#  Supported image formats
# ─────────────────────────────────────────────
SUPPORTED = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff")

# ─────────────────────────────────────────────
#  🎨 PREMIUM LIGHT COLOUR PALETTE
# ─────────────────────────────────────────────
C = {
    "bg_main"       : "#F0F4FF",   # soft lavender-white (main background)
    "bg_toolbar"    : "#FFFFFF",   # crisp white toolbar
    "bg_canvas"     : "#EEF2FF",   # very light periwinkle canvas
    "bg_info"       : "#FFFFFF",   # white info bar
    "bg_nav"        : "#F7F9FF",   # near-white nav strip
    "bg_footer"     : "#E8EDFF",   # slightly deeper lavender footer

    "btn_primary"   : "#6C8EF5",   # royal-blue button (open / nav)
    "btn_primary_h" : "#5274E0",   # hover
    "btn_soft"      : "#DDE4FF",   # soft-blue toolbar buttons
    "btn_soft_h"    : "#BEC9FF",   # hover

    "accent"        : "#8B5CF6",   # violet accent (slideshow active)
    "accent2"       : "#F59E0B",   # amber (warnings / flash)

    "text_dark"     : "#1E2A5E",   # deep navy text
    "text_mid"      : "#5A6A9A",   # medium-blue-grey
    "text_light"    : "#99AACF",   # light hint text
    "text_brand"    : "#8B5CF6",   # brand violet

    "border"        : "#C7D2F7",   # soft border
    "canvas_border" : "#A5B4FC",   # canvas highlight ring
}


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("✨  Image Viewer  —  Premium Edition")
        self.root.geometry("940x720")
        self.root.configure(bg=C["bg_main"])
        self.root.resizable(True, True)

        self.images       = []
        self.index        = 0
        self.photo        = None
        self.zoom_factor  = 1.0
        self.slideshow_id = None

        self._build_ui()

    # ──────────────────────────────────────────
    #  UI Construction
    # ──────────────────────────────────────────
    def _build_ui(self):

        # ══════════════════════════════════════
        #  HEADER  (gradient-feel title strip)
        # ══════════════════════════════════════
        header = tk.Frame(self.root, bg=C["btn_primary"], pady=11)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🖼️   IMAGE  VIEWER",
            font=("Georgia", 15, "bold"),
            bg=C["btn_primary"], fg="#FFFFFF"
        ).pack(side="left", padx=22)

        self.counter_var = tk.StringVar(value="No images loaded")
        tk.Label(
            header,
            textvariable=self.counter_var,
            font=("Consolas", 10),
            bg=C["btn_primary"], fg="#D0DAFF"
        ).pack(side="right", padx=22)

        # ══════════════════════════════════════
        #  TOOLBAR
        # ══════════════════════════════════════
        toolbar = tk.Frame(
            self.root, bg=C["bg_toolbar"], pady=10, padx=14,
            highlightthickness=1, highlightbackground=C["border"]
        )
        toolbar.pack(fill="x")

        p_btn = dict(
            font=("Segoe UI", 10, "bold"),
            bg=C["btn_primary"], fg="#FFFFFF",
            activebackground=C["btn_primary_h"], activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", padx=14, pady=5, bd=0
        )
        s_btn = dict(
            font=("Segoe UI", 10),
            bg=C["btn_soft"], fg=C["text_dark"],
            activebackground=C["btn_soft_h"], activeforeground=C["text_dark"],
            relief="flat", cursor="hand2", padx=12, pady=5, bd=0
        )

        self.open_btn = tk.Button(toolbar, text="📂  Open Image",
                                  command=self.open_image, **p_btn)
        self.open_btn.pack(side="left", padx=(0, 10))

        self.slide_btn = tk.Button(toolbar, text="▶  Slideshow",
                                   command=self.toggle_slideshow, **s_btn)
        self.slide_btn.pack(side="left", padx=(0, 4))

        # divider
        tk.Frame(toolbar, width=1, bg=C["border"]).pack(
            side="left", fill="y", padx=10, pady=3)

        self.zoom_in_btn = tk.Button(toolbar, text="🔍+",
                                     command=self.zoom_in, **s_btn)
        self.zoom_in_btn.pack(side="left", padx=(0, 4))

        self.zoom_out_btn = tk.Button(toolbar, text="🔍−",
                                      command=self.zoom_out, **s_btn)
        self.zoom_out_btn.pack(side="left", padx=(0, 4))

        self.reset_zoom_btn = tk.Button(toolbar, text="⊡  Fit",
                                        command=self.reset_zoom, **s_btn)
        self.reset_zoom_btn.pack(side="left", padx=(0, 8))

        self.zoom_var = tk.StringVar(value="100%")
        tk.Label(
            toolbar, textvariable=self.zoom_var,
            font=("Consolas", 9),
            bg=C["bg_toolbar"], fg=C["text_mid"]
        ).pack(side="left", padx=4)

        # ══════════════════════════════════════
        #  CANVAS AREA
        # ══════════════════════════════════════
        canvas_wrap = tk.Frame(self.root, bg=C["bg_main"], padx=18, pady=12)
        canvas_wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_wrap,
            bg=C["bg_canvas"],
            highlightthickness=2,
            highlightbackground=C["canvas_border"]
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_text(
            460, 280,
            text="📂   Open an image to get started",
            font=("Segoe UI", 15),
            fill=C["text_light"],
            tags="placeholder"
        )

        # ══════════════════════════════════════
        #  INFO BAR
        # ══════════════════════════════════════
        info_strip = tk.Frame(
            self.root, bg=C["bg_info"], pady=7, padx=18,
            highlightthickness=1, highlightbackground=C["border"]
        )
        info_strip.pack(fill="x")

        self.info_var = tk.StringVar(value="")
        tk.Label(
            info_strip, textvariable=self.info_var,
            font=("Consolas", 9),
            bg=C["bg_info"], fg=C["text_mid"], anchor="w"
        ).pack(side="left")

        # ══════════════════════════════════════
        #  NAVIGATION BAR
        # ══════════════════════════════════════
        nav = tk.Frame(self.root, bg=C["bg_nav"], pady=13)
        nav.pack(fill="x")

        nav_btn = dict(
            font=("Segoe UI", 12, "bold"),
            bg=C["btn_primary"], fg="#FFFFFF",
            activebackground=C["btn_primary_h"], activeforeground="#FFFFFF",
            relief="flat", cursor="hand2",
            width=13, pady=7, bd=0
        )

        self.prev_btn = tk.Button(nav, text="◀   Prev",
                                  command=self.prev_image, **nav_btn)
        self.prev_btn.pack(side="left", padx=(50, 0))

        self.next_btn = tk.Button(nav, text="Next   ▶",
                                  command=self.next_image, **nav_btn)
        self.next_btn.pack(side="right", padx=(0, 50))

        # ══════════════════════════════════════
        #  FOOTER  ✦  Design by Mr Selfish  ✦
        # ══════════════════════════════════════
        footer = tk.Frame(self.root, bg=C["bg_footer"], pady=7)
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text="✦   Design by  Mr Selfish   ✦",
            font=("Georgia", 9, "italic"),
            bg=C["bg_footer"],
            fg=C["text_brand"]
        ).pack()

        # ── Keyboard shortcuts ────────────────
        self.root.bind("<Left>",      lambda e: self.prev_image())
        self.root.bind("<Right>",     lambda e: self.next_image())
        self.root.bind("<plus>",      lambda e: self.zoom_in())
        self.root.bind("<minus>",     lambda e: self.zoom_out())
        self.root.bind("<r>",         lambda e: self.reset_zoom())
        self.root.bind("<Configure>", self._on_resize)

    # ──────────────────────────────────────────
    #  File Operations
    # ──────────────────────────────────────────
    def open_image(self):
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff"),
                ("All Files", "*.*")
            ]
        )
        if not path:
            return

        folder = os.path.dirname(path)
        self._load_folder(folder)

        filename = os.path.basename(path)
        names = [os.path.basename(p) for p in self.images]
        self.index = names.index(filename) if filename in names else 0
        self.zoom_factor = 1.0
        self._display_current()

    def _load_folder(self, folder):
        self.images = sorted([
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(SUPPORTED)
        ])
        if not self.images:
            messagebox.showwarning(
                "No Images",
                "This folder has no supported images.\n"
                "Supported: JPG, PNG, GIF, BMP, WEBP, TIFF"
            )

    # ──────────────────────────────────────────
    #  Display
    # ──────────────────────────────────────────
    def _display_current(self):
        if not self.images:
            self.canvas.delete("img")
            self.info_var.set("")
            self.zoom_var.set("100%")
            self.counter_var.set("No images loaded")
            return

        path = self.images[self.index]
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image:\n{e}")
            return

        orig_w, orig_h = img.size
        cw = self.canvas.winfo_width()  or 860
        ch = self.canvas.winfo_height() or 460

        if self.zoom_factor == 1.0:
            scale = min(cw / orig_w, ch / orig_h, 1.0)
            dw, dh = int(orig_w * scale), int(orig_h * scale)
        else:
            dw = int(orig_w * self.zoom_factor)
            dh = int(orig_h * self.zoom_factor)

        img = img.resize((max(1, dw), max(1, dh)), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)

        self.canvas.delete("img", "placeholder")
        self.canvas.create_image(
            cw // 2, ch // 2,
            anchor="center",
            image=self.photo,
            tags="img"
        )

        name    = os.path.basename(path)
        size_kb = os.path.getsize(path) // 1024
        self.info_var.set(
            f"📄 {name}   |   🖼  {orig_w} × {orig_h} px   |   💾 {size_kb} KB"
        )
        self.zoom_var.set(f"{int(self.zoom_factor * 100)}%")
        self.counter_var.set(f"{self.index + 1}  /  {len(self.images)}")

    def _on_resize(self, event=None):
        if self.images:
            self._display_current()

    # ──────────────────────────────────────────
    #  Navigation
    # ──────────────────────────────────────────
    def next_image(self):
        if not self.images:
            return
        if self.index < len(self.images) - 1:
            self.index      += 1
            self.zoom_factor = 1.0
            self._display_current()
        else:
            self._flash(self.next_btn, "Last image!")

    def prev_image(self):
        if not self.images:
            return
        if self.index > 0:
            self.index      -= 1
            self.zoom_factor = 1.0
            self._display_current()
        else:
            self._flash(self.prev_btn, "First image!")

    def _flash(self, widget, msg):
        original = widget.cget("text")
        widget.config(text=msg, bg=C["accent2"], fg="#fff")
        self.root.after(800, lambda: widget.config(
            text=original, bg=C["btn_primary"], fg="#fff"))

    # ──────────────────────────────────────────
    #  Zoom
    # ──────────────────────────────────────────
    def zoom_in(self):
        if self.images:
            self.zoom_factor = min(self.zoom_factor * 1.25, 5.0)
            self._display_current()

    def zoom_out(self):
        if self.images:
            self.zoom_factor = max(self.zoom_factor / 1.25, 0.1)
            self._display_current()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        if self.images:
            self._display_current()

    # ──────────────────────────────────────────
    #  Slideshow
    # ──────────────────────────────────────────
    def toggle_slideshow(self):
        if self.slideshow_id:
            self.root.after_cancel(self.slideshow_id)
            self.slideshow_id = None
            self.slide_btn.config(
                text="▶  Slideshow", bg=C["btn_soft"], fg=C["text_dark"])
        else:
            if not self.images:
                messagebox.showinfo("Slideshow", "Open images first!")
                return
            self.slide_btn.config(text="⏸  Stop", bg=C["accent"], fg="#fff")
            self._slideshow_tick()

    def _slideshow_tick(self):
        self.index       = (self.index + 1) % len(self.images)
        self.zoom_factor = 1.0
        self._display_current()
        self.slideshow_id = self.root.after(2500, self._slideshow_tick)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ImageViewer(root)
    root.mainloop()