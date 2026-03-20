#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║        IMAGE RESIZER PRO  🖼️                 ║
║   Python GUI Tool using Tkinter + Pillow     ║
╚══════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading


# ─────────────────────────────────────────────
#  CONSTANTS & THEME
# ─────────────────────────────────────────────
BG_DARK     = "#0f0f13"
BG_CARD     = "#1a1a24"
BG_SURFACE  = "#22222f"
ACCENT      = "#7c6af7"
ACCENT_HOV  = "#9d8fff"
ACCENT2     = "#f76a8c"
TEXT_PRI    = "#e8e8f0"
TEXT_SEC    = "#8888aa"
BORDER      = "#33334a"
SUCCESS     = "#4ade80"
ERROR_COL   = "#f87171"
WARNING     = "#fbbf24"

FONT_HEAD   = ("Courier New", 20, "bold")
FONT_TITLE  = ("Courier New", 11, "bold")
FONT_LABEL  = ("Courier New", 9)
FONT_SMALL  = ("Courier New", 8)
FONT_BTN    = ("Courier New", 10, "bold")
FONT_MONO   = ("Courier New", 9)


class ToolTip:
    """Simple tooltip widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tw, text=self.text, bg="#2a2a3a", fg=TEXT_SEC,
                       font=FONT_SMALL, relief="flat", padx=6, pady=3,
                       bd=1, highlightbackground=BORDER, highlightthickness=1)
        lbl.pack()

    def hide(self, _=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ImageResizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Resizer PRO")
        self.root.geometry("900x680")
        self.root.minsize(800, 580)
        self.root.configure(bg=BG_DARK)

        # State
        self.original_image: Image.Image | None = None
        self.resized_image:  Image.Image | None = None
        self.image_path: str = ""
        self.preview_photo = None
        self.keep_ratio = tk.BooleanVar(value=True)
        self.output_format = tk.StringVar(value="Same as Input")
        self._updating_ratio = False

        self._build_ui()
        self._animate_header()

    # ─────────────────────────────────────────
    #  UI BUILDER
    # ─────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────
        hdr = tk.Frame(self.root, bg=BG_DARK)
        hdr.pack(fill="x", padx=0, pady=0)

        header_bar = tk.Frame(hdr, bg=BG_CARD, height=64)
        header_bar.pack(fill="x")
        header_bar.pack_propagate(False)

        accent_line = tk.Frame(header_bar, bg=ACCENT, height=3)
        accent_line.pack(fill="x", side="top")

        inner_hdr = tk.Frame(header_bar, bg=BG_CARD)
        inner_hdr.pack(fill="both", expand=True, padx=20)

        self.title_label = tk.Label(inner_hdr, text="⬡ IMAGE RESIZER PRO",
                                    font=FONT_HEAD, bg=BG_CARD, fg=ACCENT)
        self.title_label.pack(side="left", pady=12)

        self.status_dot = tk.Label(inner_hdr, text="●  READY",
                                   font=FONT_SMALL, bg=BG_CARD, fg=SUCCESS)
        self.status_dot.pack(side="right", pady=12)

        # ── Main body ───────────────────────
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=16, pady=(10, 0))

        # Left panel
        left = tk.Frame(body, bg=BG_DARK)
        left.pack(side="left", fill="y", padx=(0, 8))

        self._build_left_panel(left)

        # Right panel (preview)
        right = tk.Frame(body, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        self._build_preview_panel(right)

        # ── Status bar ──────────────────────
        self._build_statusbar()

    def _card(self, parent, title):
        wrapper = tk.Frame(parent, bg=BG_DARK)
        wrapper.pack(fill="x", pady=(0, 10))

        card = tk.Frame(wrapper, bg=BG_CARD, bd=0,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        # card title
        t_row = tk.Frame(card, bg=BG_SURFACE)
        t_row.pack(fill="x")
        tk.Label(t_row, text=f"  {title}", font=FONT_TITLE,
                 bg=BG_SURFACE, fg=TEXT_SEC, anchor="w").pack(fill="x", ipady=5)

        body = tk.Frame(card, bg=BG_CARD)
        body.pack(fill="x", padx=14, pady=10)
        return body

    def _build_left_panel(self, parent):
        # ── SELECT IMAGE ────────────────────
        sec = self._card(parent, "01 // SELECT IMAGE")

        self.select_btn = self._fancy_btn(
            sec, "📂  Browse Image", self._select_image, ACCENT)
        self.select_btn.pack(fill="x", pady=(0, 8))

        self.file_label = tk.Label(sec, text="No file selected",
                                   font=FONT_SMALL, bg=BG_CARD,
                                   fg=TEXT_SEC, anchor="w", wraplength=220)
        self.file_label.pack(fill="x")

        # ── FILE INFO ───────────────────────
        info_sec = self._card(parent, "02 // FILE INFO")
        self.info_text = tk.Text(info_sec, height=5, bg=BG_SURFACE,
                                 fg=TEXT_SEC, font=FONT_MONO, bd=0,
                                 relief="flat", state="disabled",
                                 highlightthickness=0, wrap="word")
        self.info_text.pack(fill="x")

        # ── RESIZE OPTIONS ──────────────────
        opt_sec = self._card(parent, "03 // RESIZE OPTIONS")

        # Width
        self._field_row(opt_sec, "Width (px)", "width_var", "800")
        # Height
        self._field_row(opt_sec, "Height (px)", "height_var", "600")

        # Aspect ratio
        ratio_row = tk.Frame(opt_sec, bg=BG_CARD)
        ratio_row.pack(fill="x", pady=(6, 0))

        cb = tk.Checkbutton(ratio_row, text="Lock Aspect Ratio 🔒",
                            variable=self.keep_ratio, bg=BG_CARD,
                            fg=TEXT_PRI, selectcolor=BG_SURFACE,
                            activebackground=BG_CARD, activeforeground=ACCENT,
                            font=FONT_SMALL, command=self._ratio_toggled,
                            cursor="hand2")
        cb.pack(side="left")

        # Output format
        fmt_sec = self._card(parent, "04 // OUTPUT FORMAT")
        formats = ["Same as Input", "JPEG", "PNG", "WEBP", "BMP", "TIFF"]
        self.fmt_menu = ttk.Combobox(fmt_sec, values=formats,
                                     textvariable=self.output_format,
                                     state="readonly", font=FONT_MONO)
        self.fmt_menu.pack(fill="x")
        self._style_combobox()

        # ── ACTION BUTTONS ──────────────────
        act_sec = self._card(parent, "05 // ACTIONS")

        self.resize_btn = self._fancy_btn(
            act_sec, "⚡  Resize Image", self._resize_image, ACCENT)
        self.resize_btn.pack(fill="x", pady=(0, 6))
        self.resize_btn.config(state="disabled")

        self.save_btn = self._fancy_btn(
            act_sec, "💾  Save Image", self._save_image, ACCENT2)
        self.save_btn.pack(fill="x")
        self.save_btn.config(state="disabled")

    def _field_row(self, parent, label, attr, default):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=FONT_LABEL, bg=BG_CARD,
                 fg=TEXT_SEC, width=12, anchor="w").pack(side="left")
        var = tk.StringVar(value=default)
        setattr(self, attr, var)
        entry = tk.Entry(row, textvariable=var, font=FONT_MONO,
                         bg=BG_SURFACE, fg=TEXT_PRI, bd=0, relief="flat",
                         insertbackground=ACCENT, width=8,
                         highlightthickness=1,
                         highlightbackground=BORDER,
                         highlightcolor=ACCENT)
        entry.pack(side="left", padx=(6, 0), ipady=4)
        # bind ratio update
        if attr == "width_var":
            var.trace_add("write", self._on_width_change)
        elif attr == "height_var":
            var.trace_add("write", self._on_height_change)

    def _build_preview_panel(self, parent):
        # preview card
        preview_card = tk.Frame(parent, bg=BG_CARD,
                                highlightbackground=BORDER, highlightthickness=1)
        preview_card.pack(fill="both", expand=True)

        t_row = tk.Frame(preview_card, bg=BG_SURFACE)
        t_row.pack(fill="x")
        tk.Label(t_row, text="  PREVIEW", font=FONT_TITLE,
                 bg=BG_SURFACE, fg=TEXT_SEC, anchor="w").pack(side="left",
                                                               ipady=5)

        self.prev_size_lbl = tk.Label(t_row, text="",
                                      font=FONT_SMALL, bg=BG_SURFACE, fg=ACCENT)
        self.prev_size_lbl.pack(side="right", padx=10, ipady=5)

        # canvas
        self.canvas = tk.Canvas(preview_card, bg=BG_DARK, bd=0,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", self._redraw_preview)

        # placeholder
        self._draw_placeholder()

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG_SURFACE, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_lbl = tk.Label(bar, text="Ready — Select an image to begin",
                                   font=FONT_SMALL, bg=BG_SURFACE, fg=TEXT_SEC,
                                   anchor="w")
        self.status_lbl.pack(side="left", padx=12)

        self.progress = ttk.Progressbar(bar, length=120, mode="indeterminate")
        self.progress.pack(side="right", padx=12, pady=4)

    # ─────────────────────────────────────────
    #  WIDGET HELPERS
    # ─────────────────────────────────────────
    def _fancy_btn(self, parent, text, cmd, color):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=FONT_BTN, bg=color, fg="white",
                        activebackground=ACCENT_HOV, activeforeground="white",
                        bd=0, relief="flat", cursor="hand2",
                        padx=10, pady=8)
        btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self._lighten(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        return btn

    def _lighten(self, hex_color):
        """Lighten a hex color slightly for hover."""
        r = min(255, int(hex_color[1:3], 16) + 20)
        g = min(255, int(hex_color[3:5], 16) + 20)
        b = min(255, int(hex_color[5:7], 16) + 20)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _style_combobox(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox",
                        fieldbackground=BG_SURFACE,
                        background=BG_SURFACE,
                        foreground=TEXT_PRI,
                        selectbackground=ACCENT,
                        selectforeground="white",
                        borderwidth=0)

    def _draw_placeholder(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 400
        h = self.canvas.winfo_height() or 300
        cx, cy = w // 2, h // 2
        # dashed border box
        self.canvas.create_rectangle(cx - 100, cy - 70, cx + 100, cy + 70,
                                     outline=BORDER, dash=(6, 4), width=1)
        self.canvas.create_text(cx, cy - 20, text="🖼", font=("Arial", 36),
                                fill=BORDER)
        self.canvas.create_text(cx, cy + 28, text="Select an image to preview",
                                font=FONT_SMALL, fill=TEXT_SEC)

    def _set_info(self, text):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("end", text)
        self.info_text.config(state="disabled")

    def _set_status(self, text, color=TEXT_SEC):
        self.status_lbl.config(text=text, fg=color)

    def _set_status_dot(self, text, color):
        self.status_dot.config(text=f"●  {text}", fg=color)

    # ─────────────────────────────────────────
    #  ASPECT RATIO LOGIC
    # ─────────────────────────────────────────
    def _ratio_toggled(self):
        pass  # Just for the checkbox

    def _on_width_change(self, *_):
        if self._updating_ratio or not self.keep_ratio.get():
            return
        if self.original_image is None:
            return
        try:
            new_w = int(self.width_var.get())
            if new_w <= 0:
                return
            ow, oh = self.original_image.size
            new_h = int(new_w * oh / ow)
            self._updating_ratio = True
            self.height_var.set(str(new_h))
        except ValueError:
            pass
        finally:
            self._updating_ratio = False

    def _on_height_change(self, *_):
        if self._updating_ratio or not self.keep_ratio.get():
            return
        if self.original_image is None:
            return
        try:
            new_h = int(self.height_var.get())
            if new_h <= 0:
                return
            ow, oh = self.original_image.size
            new_w = int(new_h * ow / oh)
            self._updating_ratio = True
            self.width_var.set(str(new_w))
        except ValueError:
            pass
        finally:
            self._updating_ratio = False

    # ─────────────────────────────────────────
    #  ACTIONS
    # ─────────────────────────────────────────
    def _select_image(self):
        path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("All Files", "*.*"),
            ]
        )
        if not path:
            return

        # Validate it's actually an image
        try:
            img = Image.open(path)
            img.verify()          # quick verify
            img = Image.open(path)  # re-open after verify
        except Exception as exc:
            messagebox.showerror("Invalid File",
                                 f"Cannot open as image:\n{exc}")
            return

        self.image_path = path
        self.original_image = img
        self.resized_image = None

        # Update UI
        fname = os.path.basename(path)
        self.file_label.config(
            text=fname[:36] + ("…" if len(fname) > 36 else ""), fg=TEXT_PRI)

        w, h = img.size
        size_kb = os.path.getsize(path) / 1024
        mode = img.mode
        fmt  = img.format or "Unknown"

        self._set_info(
            f"Name   : {fname}\n"
            f"Size   : {w} × {h} px\n"
            f"Mode   : {mode}\n"
            f"Format : {fmt}\n"
            f"File   : {size_kb:.1f} KB"
        )

        # Prefill width / height
        self._updating_ratio = True
        self.width_var.set(str(w))
        self.height_var.set(str(h))
        self._updating_ratio = False

        self.resize_btn.config(state="normal")
        self.save_btn.config(state="disabled")
        self._set_status(f"Loaded: {fname}", SUCCESS)
        self._set_status_dot("IMAGE LOADED", SUCCESS)

        self._show_preview(img)

    def _resize_image(self):
        if self.original_image is None:
            return

        # Validate inputs
        try:
            w = int(self.width_var.get())
            h = int(self.height_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Width and Height must be integers.")
            return

        if w <= 0 or h <= 0:
            messagebox.showerror("Invalid Size",
                                 "Width and Height must be greater than 0.")
            return

        if w > 20000 or h > 20000:
            if not messagebox.askyesno("Large Size Warning",
                                       f"Requested size {w}×{h} is very large.\n"
                                       "This may take a while. Continue?"):
                return

        # Run in thread to keep UI responsive
        self._set_status("Resizing…", WARNING)
        self._set_status_dot("PROCESSING", WARNING)
        self.progress.start(10)
        self.resize_btn.config(state="disabled")

        def _do_resize():
            try:
                resized = self.original_image.resize((w, h), Image.LANCZOS)
                self.resized_image = resized
                self.root.after(0, lambda: self._resize_done(w, h))
            except Exception as exc:
                self.root.after(0, lambda: self._resize_error(str(exc)))

        threading.Thread(target=_do_resize, daemon=True).start()

    def _resize_done(self, w, h):
        self.progress.stop()
        self.resize_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self._set_status(f"Resized to {w} × {h} px — Ready to save", SUCCESS)
        self._set_status_dot("RESIZED", SUCCESS)
        self._show_preview(self.resized_image)
        self.prev_size_lbl.config(text=f"{w} × {h} px")

    def _resize_error(self, msg):
        self.progress.stop()
        self.resize_btn.config(state="normal")
        self._set_status(f"Error: {msg}", ERROR_COL)
        self._set_status_dot("ERROR", ERROR_COL)
        messagebox.showerror("Resize Error", msg)

    def _save_image(self):
        if self.resized_image is None:
            messagebox.showwarning("Nothing to Save",
                                   "Please resize an image first.")
            return

        # Determine extension
        fmt_map = {
            "Same as Input": None,
            "JPEG": ".jpg",
            "PNG":  ".png",
            "WEBP": ".webp",
            "BMP":  ".bmp",
            "TIFF": ".tiff",
        }
        chosen_ext = fmt_map[self.output_format.get()]
        orig_name   = os.path.splitext(os.path.basename(self.image_path))[0]
        default_ext = chosen_ext or os.path.splitext(self.image_path)[1]

        save_path = filedialog.asksaveasfilename(
            title="Save Resized Image",
            defaultextension=default_ext,
            initialfile=f"{orig_name}_resized{default_ext}",
            filetypes=[
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG",  "*.png"),
                ("WEBP", "*.webp"),
                ("BMP",  "*.bmp"),
                ("TIFF", "*.tiff"),
                ("All Files", "*.*"),
            ]
        )
        if not save_path:
            return

        try:
            img_to_save = self.resized_image
            # JPEG doesn't support RGBA
            if save_path.lower().endswith((".jpg", ".jpeg")):
                if img_to_save.mode in ("RGBA", "P"):
                    img_to_save = img_to_save.convert("RGB")

            img_to_save.save(save_path)
            size_kb = os.path.getsize(save_path) / 1024
            self._set_status(
                f"Saved: {os.path.basename(save_path)}  ({size_kb:.1f} KB)",
                SUCCESS)
            self._set_status_dot("SAVED ✓", SUCCESS)
            messagebox.showinfo("Saved!",
                                f"Image saved successfully:\n{save_path}\n"
                                f"({size_kb:.1f} KB)")
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))
            self._set_status(f"Save failed: {exc}", ERROR_COL)

    # ─────────────────────────────────────────
    #  PREVIEW
    # ─────────────────────────────────────────
    def _show_preview(self, img: Image.Image):
        self._preview_source = img
        self._redraw_preview()

    def _redraw_preview(self, _=None):
        if not hasattr(self, "_preview_source") or self._preview_source is None:
            self._draw_placeholder()
            return

        self.canvas.update_idletasks()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 2 or ch < 2:
            return

        img = self._preview_source.copy()
        img.thumbnail((cw - 20, ch - 20), Image.LANCZOS)

        self.preview_photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2,
                                 anchor="center", image=self.preview_photo)

        # Checkerboard hint for transparent images
        if self._preview_source.mode == "RGBA":
            self.canvas.create_text(cw - 6, ch - 6,
                                    text="RGBA", font=FONT_SMALL,
                                    fill=BORDER, anchor="se")

    # ─────────────────────────────────────────
    #  ANIMATION
    # ─────────────────────────────────────────
    def _animate_header(self):
        colors = [ACCENT, ACCENT_HOV, "#a89aff", ACCENT_HOV, ACCENT]
        def _cycle(i=0):
            self.title_label.config(fg=colors[i % len(colors)])
            self.root.after(800, _cycle, i + 1)
        _cycle()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    try:
        from PIL import Image  # noqa
    except ImportError:
        import sys
        print("ERROR: Pillow is not installed.")
        print("Run: pip install Pillow")
        sys.exit(1)

    root = tk.Tk()
    root.resizable(True, True)

    # Center window
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"900x680+{(sw-900)//2}+{(sh-680)//2}")

    app = ImageResizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()