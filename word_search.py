import tkinter as tk
from tkinter import filedialog, ttk
import re

# ─────────────────────────────────────────────
#  Text Search Tool  —  Full Featured GUI App
# ─────────────────────────────────────────────

class TextSearchTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Text Search Tool")
        self.root.geometry("780x620")
        self.root.resizable(True, True)
        self.root.configure(bg="#0f1117")

        self.file_path = None
        self.file_lines = []

        self._build_ui()

    # ── UI Construction ──────────────────────
    def _build_ui(self):
        # ---- Header ----
        header = tk.Frame(self.root, bg="#0f1117")
        header.pack(fill="x", padx=24, pady=(22, 0))

        tk.Label(
            header, text="🔍 Text Search Tool",
            font=("Courier New", 20, "bold"),
            fg="#00e5ff", bg="#0f1117"
        ).pack(side="left")

        # ---- File Section ----
        file_frame = tk.Frame(self.root, bg="#1a1d27", bd=0, relief="flat")
        file_frame.pack(fill="x", padx=24, pady=(18, 0))
        file_frame.pack_propagate(False)
        file_frame.configure(height=60)

        self.file_label = tk.Label(
            file_frame, text="  📂  No file selected",
            font=("Courier New", 10), fg="#6b7280", bg="#1a1d27",
            anchor="w"
        )
        self.file_label.pack(side="left", fill="both", expand=True, padx=10)

        tk.Button(
            file_frame, text="Select File",
            font=("Courier New", 10, "bold"),
            fg="#0f1117", bg="#00e5ff",
            activebackground="#00bcd4", activeforeground="#0f1117",
            relief="flat", cursor="hand2", padx=16,
            command=self._select_file
        ).pack(side="right", padx=10, pady=10)

        # ---- Search Bar ----
        search_frame = tk.Frame(self.root, bg="#0f1117")
        search_frame.pack(fill="x", padx=24, pady=(14, 0))

        tk.Label(
            search_frame, text="Search:",
            font=("Courier New", 11), fg="#9ca3af", bg="#0f1117"
        ).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=("Courier New", 12),
            fg="#f9fafb", bg="#1a1d27",
            insertbackground="#00e5ff",
            relief="flat", bd=0
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(10, 10))
        self.search_entry.bind("<Return>", lambda e: self._search())

        # ---- Options Row ----
        opts_frame = tk.Frame(self.root, bg="#0f1117")
        opts_frame.pack(fill="x", padx=24, pady=(10, 0))

        self.case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opts_frame, text="Case Insensitive",
            variable=self.case_var,
            font=("Courier New", 9), fg="#9ca3af",
            bg="#0f1117", selectcolor="#1a1d27",
            activebackground="#0f1117", activeforeground="#00e5ff"
        ).pack(side="left")

        self.regex_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opts_frame, text="Regex Search",
            variable=self.regex_var,
            font=("Courier New", 9), fg="#9ca3af",
            bg="#0f1117", selectcolor="#1a1d27",
            activebackground="#0f1117", activeforeground="#00e5ff"
        ).pack(side="left", padx=(16, 0))

        # Search button
        tk.Button(
            opts_frame, text="⚡ Search",
            font=("Courier New", 11, "bold"),
            fg="#0f1117", bg="#00e5ff",
            activebackground="#00bcd4", activeforeground="#0f1117",
            relief="flat", cursor="hand2", padx=20, pady=4,
            command=self._search
        ).pack(side="right")

        # ---- Divider ----
        tk.Frame(self.root, bg="#2d3147", height=1).pack(fill="x", padx=24, pady=(14, 0))

        # ---- Stats Bar ----
        self.stats_label = tk.Label(
            self.root, text="Results will appear here after search.",
            font=("Courier New", 10), fg="#6b7280", bg="#0f1117", anchor="w"
        )
        self.stats_label.pack(fill="x", padx=28, pady=(8, 0))

        # ---- Results Box ----
        result_outer = tk.Frame(self.root, bg="#0f1117")
        result_outer.pack(fill="both", expand=True, padx=24, pady=(6, 20))

        self.results_text = tk.Text(
            result_outer,
            font=("Courier New", 11),
            fg="#e5e7eb", bg="#1a1d27",
            insertbackground="#00e5ff",
            relief="flat", bd=0,
            wrap="none",
            state="disabled"
        )
        self.results_text.pack(side="left", fill="both", expand=True)

        # Configure tags for syntax-style highlighting
        self.results_text.tag_configure("line_num",  foreground="#4b5563")
        self.results_text.tag_configure("separator", foreground="#2d3147")
        self.results_text.tag_configure("match",     foreground="#fde68a", font=("Courier New", 11, "bold"))
        self.results_text.tag_configure("no_match",  foreground="#ef4444")
        self.results_text.tag_configure("header",    foreground="#00e5ff", font=("Courier New", 11, "bold"))

        # Scrollbars
        sy = tk.Scrollbar(result_outer, orient="vertical",   command=self.results_text.yview)
        sx = tk.Scrollbar(self.root,    orient="horizontal",  command=self.results_text.xview)
        self.results_text.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x", padx=24, pady=(0, 4))

    # ── File Selection ───────────────────────
    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Select a text file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not path:
            return
        self.file_path = path
        short = path if len(path) <= 60 else "…" + path[-57:]
        self.file_label.config(text=f"  📄  {short}", fg="#d1d5db")

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.file_lines = f.readlines()
            total = len(self.file_lines)
            self.stats_label.config(
                text=f"File loaded  ·  {total} line{'s' if total != 1 else ''}  ·  Ready to search.",
                fg="#6b7280"
            )
        except Exception as e:
            self._show_error(f"Could not read file:\n{e}")

    # ── Search Logic ─────────────────────────
    def _search(self):
        word = self.search_var.get().strip()

        if not self.file_path:
            self._show_error("Please select a file first.")
            return
        if not word:
            self._show_error("Please enter a search word or phrase.")
            return
        if not self.file_lines:
            self._show_error("The selected file is empty.")
            return

        use_regex = self.regex_var.get()
        case_flag = re.IGNORECASE if self.case_var.get() else 0

        matches = []  # list of (line_number, line_text, [(start, end), ...])

        for idx, line in enumerate(self.file_lines, start=1):
            line_stripped = line.rstrip("\n")
            try:
                if use_regex:
                    found = [(m.start(), m.end()) for m in re.finditer(word, line_stripped, case_flag)]
                else:
                    pattern = re.escape(word)
                    found = [(m.start(), m.end()) for m in re.finditer(pattern, line_stripped, case_flag)]
            except re.error as e:
                self._show_error(f"Invalid regex pattern:\n{e}")
                return

            if found:
                matches.append((idx, line_stripped, found))

        self._display_results(word, matches)

    # ── Display Results ──────────────────────
    def _display_results(self, word, matches):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        if not matches:
            self.stats_label.config(
                text=f'❌  "{word}"  —  Not found in file.',
                fg="#ef4444"
            )
            self.results_text.insert("end", f'\n  No matches found for "{word}".\n', "no_match")
            self.results_text.configure(state="disabled")
            return

        total_hits = sum(len(m[2]) for m in matches)
        self.stats_label.config(
            text=f'✅  "{word}"  —  {total_hits} occurrence{"s" if total_hits != 1 else ""} in {len(matches)} line{"s" if len(matches) != 1 else ""}.',
            fg="#86efac"
        )

        self.results_text.insert("end", f"  Found {total_hits} match{'es' if total_hits != 1 else ''}\n\n", "header")

        for line_no, line_text, positions in matches:
            # Line number prefix
            prefix = f"  Line {line_no:<5}│  "
            self.results_text.insert("end", prefix, "line_num")

            # Highlight match spans inside the line
            cursor = 0
            for start, end in positions:
                if cursor < start:
                    self.results_text.insert("end", line_text[cursor:start])
                self.results_text.insert("end", line_text[start:end], "match")
                cursor = end
            if cursor < len(line_text):
                self.results_text.insert("end", line_text[cursor:])
            self.results_text.insert("end", "\n")

        self.results_text.configure(state="disabled")

    # ── Error Helper ─────────────────────────
    def _show_error(self, msg):
        self.stats_label.config(text=f"⚠  {msg}", fg="#f87171")
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("end", f"\n  ⚠  {msg}\n", "no_match")
        self.results_text.configure(state="disabled")


# ── Entry Point ──────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TextSearchTool(root)
    root.mainloop()