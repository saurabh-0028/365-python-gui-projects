import tkinter as tk
from tkinter import messagebox


class HabitTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Habit Tracker Pro Max")
        self.root.geometry("520x620")
        self.root.configure(bg="#cfe9ff")

        self.habits = []

        self.build_ui()

    # ---------- GLASS BUTTON ----------
    def glass_btn(self, btn):
        btn.config(
            bg="#ffffff",
            fg="#0d47a1",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#90caf9",
            padx=12,
            pady=6
        )

        # Hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg="#e3f2fd"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#ffffff"))

    # ---------- UI ----------
    def build_ui(self):

        # HEADER
        tk.Label(
            self.root,
            text="📅 Habit Tracker Pro Max",
            font=("Segoe UI", 22, "bold"),
            bg="#2196f3",
            fg="white",
            pady=15
        ).pack(fill="x")

        # INPUT
        frame = tk.Frame(self.root, bg="#cfe9ff")
        frame.pack(pady=15)

        self.entry = tk.Entry(
            frame,
            font=("Segoe UI", 13),
            width=25,
            bd=0,
            highlightthickness=2,
            highlightcolor="#2196f3"
        )
        self.entry.pack(side="left", padx=5)

        add_btn = tk.Button(frame, text="➕ Add Habit", command=self.add_habit)
        add_btn.pack(side="left", padx=5)
        self.glass_btn(add_btn)

        # PREDEFINED HABITS
        pre_frame = tk.Frame(self.root, bg="#cfe9ff")
        pre_frame.pack(pady=10)

        tk.Label(pre_frame, text="Quick Add:",
                 font=("Segoe UI", 12, "bold"),
                 bg="#cfe9ff").pack()

        habits = ["💧 Drink Water", "📚 Study", "🏃 Exercise", "🧘 Meditation"]

        for h in habits:
            btn = tk.Button(pre_frame, text=h,
                            command=lambda x=h: self.quick_add(x))
            btn.pack(pady=3)
            self.glass_btn(btn)

        # LIST FRAME
        self.list_frame = tk.Frame(self.root, bg="#cfe9ff")
        self.list_frame.pack(fill="both", expand=True)

        # PROGRESS BAR
        self.canvas = tk.Canvas(
            self.root,
            height=25,
            bg="#bbdefb",
            highlightthickness=0
        )
        self.canvas.pack(fill="x", padx=20, pady=10)

        self.progress_bar = self.canvas.create_rectangle(
            0, 0, 0, 25, fill="#1976d2"
        )

        self.progress_label = tk.Label(
            self.root,
            text="Progress: 0%",
            font=("Segoe UI", 12, "bold"),
            bg="#cfe9ff"
        )
        self.progress_label.pack()

        # DELETE
        del_btn = tk.Button(self.root, text="🗑 Delete Selected",
                            command=self.delete_habit)
        del_btn.pack(pady=10)
        self.glass_btn(del_btn)

        # FOOTER
        tk.Label(
            self.root,
            text="✨ Designed by Mr. Selfish 😎",
            font=("Segoe UI", 10, "italic"),
            bg="#cfe9ff",
            fg="#333"
        ).pack(pady=10)

    # ---------- QUICK ADD ----------
    def quick_add(self, name):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, name)
        self.add_habit()

    # ---------- ADD ----------
    def add_habit(self):
        name = self.entry.get().strip()

        if not name:
            messagebox.showwarning("Error", "Enter habit")
            return

        var = tk.BooleanVar()

        frame = tk.Frame(self.list_frame, bg="#cfe9ff")
        frame.pack(fill="x", pady=3)

        cb = tk.Checkbutton(
            frame,
            text=name,
            variable=var,
            font=("Segoe UI", 12),
            bg="#cfe9ff",
            command=self.update_progress
        )
        cb.pack(side="left", padx=10)

        self.habits.append((frame, var))
        self.entry.delete(0, tk.END)

        self.update_progress()

    # ---------- DELETE ----------
    def delete_habit(self):
        removed = False

        for frame, var in self.habits[:]:
            if var.get():
                frame.destroy()
                self.habits.remove((frame, var))
                removed = True

        if not removed:
            messagebox.showwarning("Error", "Select habit")

        self.update_progress()

    # ---------- ANIMATION ----------
    def animate_bar(self, target):
        current = self.canvas.coords(self.progress_bar)[2]

        if current < target:
            current += 4
            self.canvas.coords(self.progress_bar, 0, 0, current, 25)
            self.root.after(10, self.animate_bar, target)

    # ---------- UPDATE ----------
    def update_progress(self):
        total = len(self.habits)

        if total == 0:
            self.canvas.coords(self.progress_bar, 0, 0, 0, 25)
            self.progress_label.config(text="Progress: 0%")
            return

        completed = sum(1 for _, var in self.habits if var.get())

        percent = int((completed / total) * 100)
        width = int((percent / 100) * 480)

        self.animate_bar(width)

        self.progress_label.config(
            text=f"Progress: {completed}/{total} ({percent}%)"
        )


# RUN
if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTracker(root)
    root.mainloop()