import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


class LogAnalyzerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("📊 Log File Analyzer")
        self.root.geometry("900x650")
        self.root.configure(bg="#e3f2fd")

        self.lines = []
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0

        self.build_ui()

    # ---------- BUTTON STYLE ----------
    def style_button(self, btn, color, hover):
        btn.config(bg=color, fg="white", relief="flat",
                   font=("Segoe UI", 10, "bold"), padx=10, pady=5)

        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))

    # ---------- UI ----------
    def build_ui(self):

        # Header
        tk.Label(
            self.root,
            text="📊 Log File Analyzer",
            font=("Segoe UI", 20, "bold"),
            bg="#2196f3",
            fg="white",
            pady=12
        ).pack(fill="x")

        # File section
        file_frame = tk.Frame(self.root, bg="#e3f2fd")
        file_frame.pack(pady=10)

        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=("Segoe UI", 11),
            bg="#e3f2fd"
        )
        self.file_label.pack(side="left", padx=10)

        btn = tk.Button(file_frame, text="📂 Select File",
                        command=self.select_file)
        btn.pack(side="right")
        self.style_button(btn, "#1976d2", "#1565c0")

        # Control buttons
        control_frame = tk.Frame(self.root, bg="#e3f2fd")
        control_frame.pack(pady=5)

        btn1 = tk.Button(control_frame, text="🔍 Analyze",
                         command=self.analyze_file)
        btn1.pack(side="left", padx=5)
        self.style_button(btn1, "#43a047", "#2e7d32")

        btn2 = tk.Button(control_frame, text="🔄 Clear",
                         command=self.clear_all)
        btn2.pack(side="left", padx=5)
        self.style_button(btn2, "#e53935", "#b71c1c")

        # Stats
        stats_frame = tk.Frame(self.root, bg="#e3f2fd")
        stats_frame.pack(pady=10)

        self.error_label = tk.Label(stats_frame, text="0",
                                   font=("Segoe UI", 16, "bold"),
                                   fg="red", bg="#e3f2fd")
        self.error_label.grid(row=0, column=0, padx=20)

        self.warning_label = tk.Label(stats_frame, text="0",
                                     font=("Segoe UI", 16, "bold"),
                                     fg="orange", bg="#e3f2fd")
        self.warning_label.grid(row=0, column=1, padx=20)

        self.info_label = tk.Label(stats_frame, text="0",
                                  font=("Segoe UI", 16, "bold"),
                                  fg="blue", bg="#e3f2fd")
        self.info_label.grid(row=0, column=2, padx=20)

        tk.Label(stats_frame, text="Errors",
                 bg="#e3f2fd").grid(row=1, column=0)
        tk.Label(stats_frame, text="Warnings",
                 bg="#e3f2fd").grid(row=1, column=1)
        tk.Label(stats_frame, text="Info",
                 bg="#e3f2fd").grid(row=1, column=2)

        # Preview
        self.text = tk.Text(
            self.root,
            height=20,
            bg="#0d47a1",
            fg="white",
            font=("Courier", 10)
        )
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        # Footer
        tk.Label(
            self.root,
            text="✨ Designed by Mr. Selfish 😎",
            font=("Segoe UI", 10, "italic"),
            bg="#e3f2fd",
            fg="#555"
        ).pack(pady=5)

    # ---------- FILE SELECT ----------
    def select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Log Files", "*.txt *.log"), ("All Files", "*.*")]
        )

        if path:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                self.lines = f.readlines()

            self.file_label.config(text=Path(path).name)
            self.show_preview()

    # ---------- ANALYZE ----------
    def analyze_file(self):
        if not self.lines:
            messagebox.showwarning("Error", "Select file first")
            return

        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0

        for line in self.lines:
            l = line.lower()
            if "error" in l:
                self.error_count += 1
            elif "warning" in l:
                self.warning_count += 1
            elif "info" in l:
                self.info_count += 1

        # Animation
        self.animate(self.error_label, self.error_count)
        self.animate(self.warning_label, self.warning_count)
        self.animate(self.info_label, self.info_count)

    # ---------- ANIMATION ----------
    def animate(self, label, target):
        current = int(label["text"])
        if current < target:
            label.config(text=str(current + 1))
            self.root.after(20, self.animate, label, target)

    # ---------- PREVIEW ----------
    def show_preview(self):
        self.text.delete("1.0", "end")
        for line in self.lines[:50]:
            self.text.insert("end", line)

    # ---------- CLEAR ----------
    def clear_all(self):
        self.lines = []
        self.text.delete("1.0", "end")
        self.file_label.config(text="No file selected")

        self.error_label.config(text="0")
        self.warning_label.config(text="0")
        self.info_label.config(text="0")


# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalyzerGUI(root)
    root.mainloop()