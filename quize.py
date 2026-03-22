import tkinter as tk
from tkinter import messagebox
import random

# ═══════════════════════════════════════════════
#  QUIZ DATA
# ═══════════════════════════════════════════════
QUESTIONS = [
    {
        "question": "What is Python?",
        "options": ["Programming Language", "Animal", "Car", "Game"],
        "answer": "Programming Language"
    },
    {
        "question": "Which keyword is used to define a function in Python?",
        "options": ["func", "define", "def", "function"],
        "answer": "def"
    },
    {
        "question": "Which data type stores key-value pairs?",
        "options": ["List", "Tuple", "Set", "Dictionary"],
        "answer": "Dictionary"
    },
    {
        "question": "What does 'len()' function do?",
        "options": ["Deletes items", "Returns length", "Sorts list", "Copies object"],
        "answer": "Returns length"
    },
    {
        "question": "Which symbol is used for single-line comments in Python?",
        "options": ["//", "/*", "#", "--"],
        "answer": "#"
    },
    {
        "question": "What is the output of: print(2 ** 3)?",
        "options": ["6", "8", "9", "5"],
        "answer": "8"
    },
    {
        "question": "Which of these is a mutable data type?",
        "options": ["Tuple", "String", "List", "Integer"],
        "answer": "List"
    },
    {
        "question": "What does 'import' keyword do?",
        "options": ["Exports a module", "Deletes a module", "Loads a module", "Renames a variable"],
        "answer": "Loads a module"
    },
]

# ═══════════════════════════════════════════════
#  COLOR PALETTE
# ═══════════════════════════════════════════════
BG_MAIN         = "#F0F4FF"
BG_CARD         = "#FFFFFF"
BG_HEADER       = "#E8EEFF"
ACCENT          = "#5B6EF5"
ACCENT_HOVER    = "#4454D4"
TEXT_DARK       = "#1E2245"
TEXT_MID        = "#5A5F80"
TEXT_LIGHT      = "#9AA0C0"
SUCCESS         = "#22C55E"
SUCCESS_BG      = "#EDFFF4"
SUCCESS_BORDER  = "#86EFAC"
DANGER          = "#EF4444"
DANGER_BG       = "#FFF1F1"
DANGER_BORDER   = "#FCA5A5"
OPTION_NORMAL   = "#F5F6FF"
OPTION_HOVER    = "#EEF0FF"
OPTION_SELECT   = "#DDE1FF"
BORDER          = "#D5D9F5"

# ═══════════════════════════════════════════════
#  FONT SIZES  (bigger)
# ═══════════════════════════════════════════════
F_TITLE     = ("Segoe UI", 22, "bold")
F_HEADER    = ("Segoe UI", 20, "bold")
F_QUESTION  = ("Segoe UI", 17, "bold")
F_OPTION    = ("Segoe UI", 14)
F_OPTION_B  = ("Segoe UI", 14, "bold")
F_BODY      = ("Segoe UI", 13)
F_SMALL     = ("Segoe UI", 12)
F_TAG       = ("Segoe UI", 11, "bold")
F_BTN       = ("Segoe UI", 13, "bold")
F_BTN_SM    = ("Segoe UI", 12)
F_SCORE_BIG = ("Segoe UI", 44, "bold")
F_EMOJI     = ("Segoe UI", 56)


# ═══════════════════════════════════════════════
#  MAIN APP CLASS
# ═══════════════════════════════════════════════
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠  Python Quiz App")
        self.root.geometry("700x680")
        self.root.minsize(560, 540)
        self.root.resizable(True, True)   # ✅ maximize / minimize / resize
        self.root.configure(bg=BG_MAIN)

        # State
        self.questions      = random.sample(QUESTIONS, len(QUESTIONS))
        self.current_index  = 0
        self.score          = 0
        self.selected_var   = tk.StringVar(value="")
        self.option_buttons = []
        self.user_answers   = []  # stores each Q's result for review

        self._build_ui()
        self._load_question()

    # ─────────────────────────────────────────
    #  BUILD QUIZ UI
    # ─────────────────────────────────────────
    def _build_ui(self):
        # Header
        self.header_frame = tk.Frame(self.root, bg=BG_HEADER, pady=16)
        self.header_frame.pack(fill="x")

        tk.Label(
            self.header_frame, text="🧠  Python Quiz",
            font=F_TITLE, bg=BG_HEADER, fg=ACCENT
        ).pack(side="left", padx=28)

        self.progress_label = tk.Label(
            self.header_frame, text="",
            font=F_BODY, bg=BG_HEADER, fg=TEXT_MID
        )
        self.progress_label.pack(side="right", padx=28)

        # Progress bar
        self.progress_canvas = tk.Canvas(
            self.root, height=7, bg=BORDER, highlightthickness=0
        )
        self.progress_canvas.pack(fill="x")
        self.progress_fill = self.progress_canvas.create_rectangle(
            0, 0, 0, 7, fill=ACCENT, outline=""
        )

        # Card outer (resizes with window)
        self.card_outer = tk.Frame(self.root, bg=BG_MAIN, padx=30, pady=20)
        self.card_outer.pack(fill="both", expand=True)

        self.card = tk.Frame(
            self.card_outer, bg=BG_CARD,
            relief="flat", bd=0,
            highlightbackground=BORDER, highlightthickness=1
        )
        self.card.pack(fill="both", expand=True)

        # Q number tag
        self.q_num_label = tk.Label(
            self.card, text="",
            font=F_TAG, bg=ACCENT, fg="white",
            padx=12, pady=4
        )
        self.q_num_label.pack(anchor="nw", padx=24, pady=(20, 6))

        # Question text
        self.question_label = tk.Label(
            self.card, text="",
            font=F_QUESTION, bg=BG_CARD, fg=TEXT_DARK,
            wraplength=580, justify="left"
        )
        self.question_label.pack(anchor="w", padx=24, pady=(4, 18))

        tk.Frame(self.card, bg=BORDER, height=1).pack(fill="x", padx=24)

        # Options frame
        self.options_frame = tk.Frame(self.card, bg=BG_CARD)
        self.options_frame.pack(fill="x", padx=24, pady=14)

        # Bottom bar
        self.bottom = tk.Frame(self.root, bg=BG_MAIN, pady=14)
        self.bottom.pack(fill="x", padx=30)

        self.feedback_label = tk.Label(
            self.bottom, text="",
            font=("Segoe UI", 12, "italic"),
            bg=BG_MAIN, fg=TEXT_MID
        )
        self.feedback_label.pack(side="left")

        self.next_btn = tk.Button(
            self.bottom, text="Next  →",
            font=F_BTN,
            bg=ACCENT, fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat", bd=0,
            padx=28, pady=12,
            cursor="hand2",
            command=self._next_question
        )
        self.next_btn.pack(side="right")
        self._bind_hover(self.next_btn, ACCENT_HOVER, ACCENT)

        # Resize → update wraplength
        self.root.bind("<Configure>", self._on_resize)

    # ─────────────────────────────────────────
    #  WINDOW RESIZE
    # ─────────────────────────────────────────
    def _on_resize(self, event=None):
        w = self.root.winfo_width()
        try:
            self.question_label.config(wraplength=max(300, w - 160))
        except Exception:
            pass
        try:
            total = len(self.questions)
            idx   = self.current_index
            self.progress_canvas.update_idletasks()
            bar_w  = self.progress_canvas.winfo_width()
            fill_w = int(bar_w * (idx + 1) / total)
            self.progress_canvas.coords(self.progress_fill, 0, 0, fill_w, 7)
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  LOAD QUESTION
    # ─────────────────────────────────────────
    def _load_question(self):
        self.selected_var.set("")
        self.feedback_label.config(text="")

        for w in self.options_frame.winfo_children():
            w.destroy()
        self.option_buttons.clear()

        total = len(self.questions)
        idx   = self.current_index
        q     = self.questions[idx]

        self.progress_label.config(text=f"Question  {idx + 1}  /  {total}")
        self.q_num_label.config(text=f"  Q{idx + 1}  ")
        self.question_label.config(text=q["question"])

        self.progress_canvas.update_idletasks()
        bar_w  = self.progress_canvas.winfo_width()
        fill_w = int(bar_w * (idx + 1) / total)
        self.progress_canvas.coords(self.progress_fill, 0, 0, fill_w, 7)

        # Option buttons
        for opt in q["options"]:
            btn_frame = tk.Frame(
                self.options_frame,
                bg=OPTION_NORMAL,
                highlightbackground=BORDER,
                highlightthickness=1,
                cursor="hand2"
            )
            btn_frame.pack(fill="x", pady=5)

            radio_dot = tk.Label(
                btn_frame, text="○",
                font=("Segoe UI", 16),
                bg=OPTION_NORMAL, fg=TEXT_MID, width=2
            )
            radio_dot.pack(side="left", padx=(12, 6), pady=10)

            lbl = tk.Label(
                btn_frame, text=opt,
                font=F_OPTION,
                bg=OPTION_NORMAL, fg=TEXT_DARK,
                anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)

            for widget in (btn_frame, radio_dot, lbl):
                widget.bind("<Button-1>",
                            lambda e, o=opt, f=btn_frame, d=radio_dot, l=lbl:
                            self._select_option(o, f, d, l))
                widget.bind("<Enter>",
                            lambda e, f=btn_frame, d=radio_dot, l=lbl:
                            self._hover_option(f, d, l, True))
                widget.bind("<Leave>",
                            lambda e, f=btn_frame, d=radio_dot, l=lbl:
                            self._hover_option(f, d, l, False))

            self.option_buttons.append((opt, btn_frame, radio_dot, lbl))

        is_last = (idx == total - 1)
        self.next_btn.config(text="Submit  ✓" if is_last else "Next  →")

    # ─────────────────────────────────────────
    #  SELECT / HOVER
    # ─────────────────────────────────────────
    def _select_option(self, opt, frame, dot, lbl):
        for _, f, d, l in self.option_buttons:
            f.config(bg=OPTION_NORMAL, highlightbackground=BORDER)
            d.config(bg=OPTION_NORMAL, fg=TEXT_MID, text="○")
            l.config(bg=OPTION_NORMAL, fg=TEXT_DARK)

        frame.config(bg=OPTION_SELECT, highlightbackground=ACCENT)
        dot.config(bg=OPTION_SELECT, fg=ACCENT, text="●")
        lbl.config(bg=OPTION_SELECT, fg=ACCENT)

        self.selected_var.set(opt)
        self.feedback_label.config(text="✔  Option selected", fg=TEXT_MID)

    def _hover_option(self, frame, dot, lbl, entering):
        selected = self.selected_var.get()
        is_selected = any(
            o == selected and f is frame
            for o, f, *_ in self.option_buttons
        )
        if not is_selected:
            color = OPTION_HOVER if entering else OPTION_NORMAL
            frame.config(bg=color)
            dot.config(bg=color)
            lbl.config(bg=color)

    # ─────────────────────────────────────────
    #  NEXT / SUBMIT
    # ─────────────────────────────────────────
    def _next_question(self):
        selected = self.selected_var.get()

        if not selected:
            self.feedback_label.config(
                text="⚠  Please select an option first!", fg=DANGER
            )
            self._shake(self.next_btn)
            return

        correct    = self.questions[self.current_index]["answer"]
        is_correct = (selected == correct)
        if is_correct:
            self.score += 1

        # Store for review
        self.user_answers.append({
            "question"   : self.questions[self.current_index]["question"],
            "options"    : self.questions[self.current_index]["options"],
            "selected"   : selected,
            "correct"    : correct,
            "is_correct" : is_correct,
        })

        self.current_index += 1
        if self.current_index < len(self.questions):
            self._load_question()
        else:
            self._show_result()

    # ─────────────────────────────────────────
    #  RESULT SCREEN
    # ─────────────────────────────────────────
    def _show_result(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        total     = len(self.questions)
        pct       = round(self.score / total * 100)
        emoji     = "🎉" if pct >= 80 else "👍" if pct >= 50 else "😅"
        grade_txt = "Excellent!" if pct >= 80 else "Good Job!" if pct >= 50 else "Keep Practicing!"
        bar_color = SUCCESS if pct >= 60 else DANGER

        self.root.configure(bg=BG_MAIN)

        # Header
        hdr = tk.Frame(self.root, bg=BG_HEADER, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🧠  Python Quiz  —  Results",
                 font=F_HEADER, bg=BG_HEADER, fg=ACCENT).pack()

        # Scrollable container
        outer = tk.Frame(self.root, bg=BG_MAIN)
        outer.pack(fill="both", expand=True, padx=30, pady=16)

        canvas    = tk.Canvas(outer, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner  = tk.Frame(canvas, bg=BG_MAIN)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        def _scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        # ── Score summary card ──
        sc = tk.Frame(inner, bg=BG_CARD,
                      highlightbackground=BORDER, highlightthickness=1)
        sc.pack(fill="x", pady=(0, 18))

        tk.Label(sc, text=emoji, font=F_EMOJI, bg=BG_CARD).pack(pady=(24, 4))
        tk.Label(sc, text=grade_txt, font=F_HEADER, bg=BG_CARD, fg=ACCENT).pack()
        tk.Label(sc, text=f"You scored  {self.score}  out of  {total}",
                 font=("Segoe UI", 15), bg=BG_CARD, fg=TEXT_DARK).pack(pady=(8, 4))
        tk.Label(sc, text=f"{pct}%",
                 font=F_SCORE_BIG, bg=BG_CARD, fg=bar_color).pack(pady=(4, 14))

        # Score bar
        bar = tk.Canvas(sc, height=12, bg=BORDER,
                        highlightthickness=0, width=360)
        bar.pack(pady=(0, 18))
        bar.update_idletasks()
        bar.create_rectangle(0, 0, int(360 * self.score / total), 12,
                              fill=bar_color, outline="")

        # Counts
        row = tk.Frame(sc, bg=BG_CARD)
        row.pack(pady=(0, 14))
        tk.Label(row, text=f"✅  Correct:  {self.score}",
                 font=("Segoe UI", 13), bg=BG_CARD, fg=SUCCESS
                 ).pack(side="left", padx=24)
        tk.Label(row, text=f"❌  Wrong:  {total - self.score}",
                 font=("Segoe UI", 13), bg=BG_CARD, fg=DANGER
                 ).pack(side="left", padx=24)

        # Buttons
        btn_row = tk.Frame(sc, bg=BG_CARD)
        btn_row.pack(pady=(6, 26))

        retry = tk.Button(btn_row, text="🔄  Retry Quiz",
                          font=F_BTN, bg=ACCENT, fg="white",
                          activebackground=ACCENT_HOVER,
                          relief="flat", padx=22, pady=12,
                          cursor="hand2", command=self._restart)
        retry.pack(side="left", padx=10)
        self._bind_hover(retry, ACCENT_HOVER, ACCENT)

        tk.Button(btn_row, text="✖  Quit",
                  font=F_BTN_SM, bg=BG_MAIN, fg=TEXT_MID,
                  activebackground=BORDER,
                  relief="flat", padx=22, pady=12,
                  cursor="hand2", command=self.root.destroy
                  ).pack(side="left", padx=10)

        # ── REVIEW SECTION HEADER ──
        rev_hdr = tk.Frame(inner, bg=BG_MAIN)
        rev_hdr.pack(fill="x", pady=(6, 8))

        tk.Label(rev_hdr, text="📋  Review Your Answers",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG_MAIN, fg=TEXT_DARK).pack(side="left")

        tk.Label(rev_hdr,
                 text=f"   {self.score} correct  •  {total - self.score} wrong",
                 font=F_BODY, bg=BG_MAIN, fg=TEXT_MID).pack(side="left", pady=2)

        # ── One card per question ──
        for i, ans in enumerate(self.user_answers):
            self._build_review_card(inner, i + 1, ans)

        # Bottom padding
        tk.Frame(inner, bg=BG_MAIN, height=20).pack()

    # ─────────────────────────────────────────
    #  REVIEW CARD (one per question)
    # ─────────────────────────────────────────
    def _build_review_card(self, parent, num, ans):
        is_correct   = ans["is_correct"]
        card_border  = SUCCESS_BORDER if is_correct else DANGER_BORDER
        card_bg      = SUCCESS_BG     if is_correct else DANGER_BG
        status_icon  = "✅" if is_correct else "❌"
        status_text  = "Correct" if is_correct else "Wrong"
        status_color = SUCCESS if is_correct else DANGER

        card = tk.Frame(parent, bg=card_bg,
                        highlightbackground=card_border,
                        highlightthickness=2)
        card.pack(fill="x", pady=6)

        # Top row
        top = tk.Frame(card, bg=card_bg)
        top.pack(fill="x", padx=16, pady=(14, 4))

        tk.Label(top, text=f"Q{num}", font=F_TAG,
                 bg=ACCENT, fg="white", padx=10, pady=3).pack(side="left")

        tk.Label(top, text=f"  {status_icon}  {status_text}  ",
                 font=("Segoe UI", 12, "bold"),
                 bg=status_color, fg="white",
                 padx=8, pady=3).pack(side="right")

        # Question text
        tk.Label(card, text=ans["question"],
                 font=("Segoe UI", 14, "bold"),
                 bg=card_bg, fg=TEXT_DARK,
                 wraplength=560, justify="left", anchor="w"
                 ).pack(fill="x", padx=16, pady=(6, 10))

        tk.Frame(card, bg=card_border, height=1).pack(fill="x", padx=16)

        # Options
        opts_frame = tk.Frame(card, bg=card_bg)
        opts_frame.pack(fill="x", padx=16, pady=(10, 4))

        for opt in ans["options"]:
            is_user_pick    = (opt == ans["selected"])
            is_correct_ans  = (opt == ans["correct"])

            if is_correct_ans and is_user_pick:
                icon = "✅"; bg = SUCCESS_BG; fg = SUCCESS; font = F_OPTION_B; bdr = SUCCESS_BORDER
            elif is_correct_ans:
                icon = "✔ "; bg = SUCCESS_BG; fg = SUCCESS; font = F_OPTION_B; bdr = SUCCESS_BORDER
            elif is_user_pick:
                icon = "❌"; bg = DANGER_BG;  fg = DANGER;  font = F_OPTION_B; bdr = DANGER_BORDER
            else:
                icon = "  ○"; bg = card_bg;  fg = TEXT_MID; font = F_OPTION;  bdr = BORDER

            row = tk.Frame(opts_frame, bg=bg,
                           highlightbackground=bdr, highlightthickness=1)
            row.pack(fill="x", pady=3)

            tk.Label(row, text=icon, font=("Segoe UI", 13),
                     bg=bg, fg=fg, width=3).pack(side="left", padx=(8, 4), pady=7)
            tk.Label(row, text=opt, font=font,
                     bg=bg, fg=fg, anchor="w"
                     ).pack(side="left", fill="x", expand=True,
                            padx=(0, 10), pady=7)

        # "Correct Answer" note for wrong answers
        if not is_correct:
            note = tk.Frame(card, bg="#EDFFF4",
                            highlightbackground=SUCCESS_BORDER,
                            highlightthickness=1)
            note.pack(fill="x", padx=16, pady=(6, 14))
            tk.Label(note,
                     text=f"  ✔  Correct Answer:   {ans['correct']}",
                     font=("Segoe UI", 13, "bold"),
                     bg="#EDFFF4", fg=SUCCESS, anchor="w"
                     ).pack(fill="x", padx=10, pady=8)
        else:
            tk.Frame(card, bg=card_bg, height=10).pack()

    # ─────────────────────────────────────────
    #  RESTART
    # ─────────────────────────────────────────
    def _restart(self):
        try:
            self.root.unbind_all("<MouseWheel>")
        except Exception:
            pass
        for w in self.root.winfo_children():
            w.destroy()
        self.questions      = random.sample(QUESTIONS, len(QUESTIONS))
        self.current_index  = 0
        self.score          = 0
        self.selected_var   = tk.StringVar(value="")
        self.option_buttons = []
        self.user_answers   = []
        self._build_ui()
        self._load_question()

    # ─────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────
    def _bind_hover(self, widget, hover_color, normal_color):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color))

    def _shake(self, widget, times=6, distance=6):
        def move(count, direction):
            if count <= 0:
                return
            widget.config(padx=28 + direction * distance)
            self.root.after(40, lambda: move(count - 1, -direction))
        move(times, 1)


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = QuizApp(root)
    root.mainloop()