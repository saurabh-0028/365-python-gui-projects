import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class UnitConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 Unit Converter Pro Max")
        self.root.geometry("550x600")

        self.dark_mode = False
        self.history = []

        self.set_theme()
        self.build_ui()

    # ---------- THEME ----------
    def set_theme(self):
        if self.dark_mode:
            self.bg = "#121212"
            self.fg = "white"
            self.btn = "#1e1e1e"
        else:
            self.bg = "#e3f2fd"
            self.fg = "black"
            self.btn = "#ffffff"

        self.root.configure(bg=self.bg)

    # ---------- BUTTON STYLE ----------
    def style_btn(self, btn):
        btn.config(bg=self.btn, fg=self.fg,
                   font=("Segoe UI", 11, "bold"),
                   relief="flat", bd=0, padx=10, pady=6)

        btn.bind("<Enter>", lambda e: btn.config(bg="#90caf9"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.btn))

    # ---------- UI ----------
    def build_ui(self):

        # Header
        self.header = tk.Label(
            self.root,
            text="🔄 Unit Converter Pro Max",
            font=("Segoe UI", 20, "bold"),
            bg="#2196f3",
            fg="white",
            pady=12
        )
        self.header.pack(fill="x")

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(pady=15)

        # Type
        tk.Label(frame, text="Type:", bg=self.bg, fg=self.fg).grid(row=0, column=0)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var,
                                      values=["Length", "Weight", "Temperature"],
                                      state="readonly")
        self.type_combo.grid(row=0, column=1)
        self.type_combo.bind("<<ComboboxSelected>>", self.update_units)

        # From / To
        tk.Label(frame, text="From:", bg=self.bg, fg=self.fg).grid(row=1, column=0)
        self.from_var = tk.StringVar()
        self.from_combo = ttk.Combobox(frame, textvariable=self.from_var)
        self.from_combo.grid(row=1, column=1)

        tk.Label(frame, text="To:", bg=self.bg, fg=self.fg).grid(row=2, column=0)
        self.to_var = tk.StringVar()
        self.to_combo = ttk.Combobox(frame, textvariable=self.to_var)
        self.to_combo.grid(row=2, column=1)

        # Value
        tk.Label(frame, text="Value:", bg=self.bg, fg=self.fg).grid(row=3, column=0)
        self.value_entry = tk.Entry(frame)
        self.value_entry.grid(row=3, column=1)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=self.bg)
        btn_frame.pack(pady=10)

        convert_btn = tk.Button(btn_frame, text="⚡ Convert", command=self.convert)
        convert_btn.grid(row=0, column=0, padx=5)
        self.style_btn(convert_btn)

        theme_btn = tk.Button(btn_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        theme_btn.grid(row=0, column=1, padx=5)
        self.style_btn(theme_btn)

        history_btn = tk.Button(btn_frame, text="📜 History", command=self.show_history)
        history_btn.grid(row=0, column=2, padx=5)
        self.style_btn(history_btn)

        # Result
        self.result_label = tk.Label(self.root, text="Result:",
                                     font=("Segoe UI", 14, "bold"),
                                     bg=self.bg, fg=self.fg)
        self.result_label.pack(pady=10)

        # Footer
        self.footer = tk.Label(
            self.root,
            text="✨ Designed by Mr. Selfish 😎",
            font=("Segoe UI", 14, "bold italic"),
            bg=self.bg,
            fg="#555"
        )
        self.footer.pack(pady=10)

    # ---------- UPDATE UNITS ----------
    def update_units(self, event=None):
        t = self.type_var.get()

        if t == "Length":
            units = ["km", "m", "cm"]
            self.animate_bg("#e3f2fd")

        elif t == "Weight":
            units = ["kg", "g"]
            self.animate_bg("#e8f5e9")

        elif t == "Temperature":
            units = ["C", "F"]
            self.animate_bg("#fff3e0")

        self.from_combo["values"] = units
        self.to_combo["values"] = units

    # ---------- CONVERT ----------
    def convert(self):
        try:
            val = float(self.value_entry.get())
            f = self.from_var.get()
            t = self.to_var.get()
            typ = self.type_var.get()

            res = val

            if typ == "Length":
                if f == "km" and t == "m":
                    res = val * 1000
                elif f == "m" and t == "km":
                    res = val / 1000
                elif f == "cm" and t == "m":
                    res = val / 100
                elif f == "m" and t == "cm":
                    res = val * 100

            elif typ == "Weight":
                if f == "kg" and t == "g":
                    res = val * 1000
                elif f == "g" and t == "kg":
                    res = val / 1000

            elif typ == "Temperature":
                if f == "C" and t == "F":
                    res = (val * 9/5) + 32
                elif f == "F" and t == "C":
                    res = (val - 32) * 5/9

            result_text = f"{val} {f} → {round(res,2)} {t}"
            self.result_label.config(text=result_text)

            self.history.append(result_text)
            self.save_history()

        except:
            messagebox.showerror("Error", "Invalid input")

    # ---------- HISTORY ----------
    def save_history(self):
        with open("history.json", "w") as f:
            json.dump(self.history, f)

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("History")
        text = tk.Text(win)
        text.pack()
        for item in self.history:
            text.insert("end", item + "\n")

    # ---------- DARK MODE ----------
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.set_theme()
        self.build_ui()

    # ---------- ANIMATION ----------
    def animate_bg(self, color):
        self.root.configure(bg=color)


# RUN
if __name__ == "__main__":
    root = tk.Tk()
    app = UnitConverter(root)
    root.mainloop()