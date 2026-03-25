import tkinter as tk
from tkinter import ttk, messagebox


class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("650x550")
        self.root.configure(bg="#f0f4ff")

        self.data = []  # store real passwords

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="🔐 Password Manager",
                 font=("Arial", 20, "bold"),
                 bg="#4a69bd", fg="white", pady=12).pack(fill="x")

        frame = tk.Frame(self.root, bg="#f0f4ff")
        frame.pack(pady=20)

        # Inputs
        tk.Label(frame, text="Website:", font=("Arial", 13),
                 bg="#f0f4ff").grid(row=0, column=0)
        self.site_entry = tk.Entry(frame, font=("Arial", 13))
        self.site_entry.grid(row=0, column=1)

        tk.Label(frame, text="Username:", font=("Arial", 13),
                 bg="#f0f4ff").grid(row=1, column=0)
        self.user_entry = tk.Entry(frame, font=("Arial", 13))
        self.user_entry.grid(row=1, column=1)

        tk.Label(frame, text="Password:", font=("Arial", 13),
                 bg="#f0f4ff").grid(row=2, column=0)
        self.pass_entry = tk.Entry(frame, font=("Arial", 13), show="*")
        self.pass_entry.grid(row=2, column=1)

        # Buttons
        tk.Button(frame, text="💾 Save", command=self.save_data,
                  bg="#38ada9", fg="white", font=("Arial", 12)).grid(row=3, column=0, pady=10)

        # Table
        self.tree = ttk.Treeview(
            self.root,
            columns=("site", "user", "pass"),
            show="headings"
        )

        self.tree.heading("site", text="Website")
        self.tree.heading("user", text="Username")
        self.tree.heading("pass", text="Password")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Action buttons
        action_frame = tk.Frame(self.root, bg="#f0f4ff")
        action_frame.pack()

        tk.Button(action_frame, text="👁 Show",
                  command=self.show_password,
                  bg="#f6b93b", width=12).grid(row=0, column=0, padx=5)

        tk.Button(action_frame, text="🙈 Hide",
                  command=self.hide_password,
                  bg="#60a3bc", width=12).grid(row=0, column=1, padx=5)

        tk.Button(action_frame, text="✏ Rename",
                  command=self.rename_entry,
                  bg="#78e08f", width=12).grid(row=0, column=2, padx=5)

        tk.Button(action_frame, text="🗑 Delete",
                  command=self.delete_data,
                  bg="#e55039", fg="white", width=12).grid(row=0, column=3, padx=5)

        # Footer
        tk.Label(self.root,
                 text="✨ Designed by Mr. Selfish 😎",
                 font=("Arial", 11),
                 bg="#f0f4ff").pack(pady=10)

    # Save data
    def save_data(self):
        site = self.site_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()

        if not site or not user or not pwd:
            messagebox.showwarning("Error", "Fill all fields")
            return

        self.data.append({"site": site, "user": user, "pass": pwd})
        self.refresh_table()
        self.clear_fields()

    # Refresh table (hidden password)
    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in self.data:
            self.tree.insert("", tk.END,
                             values=(item["site"], item["user"], "******"))

    def clear_fields(self):
        self.site_entry.delete(0, tk.END)
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)

    # Show password
    def show_password(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.data[index]

        self.tree.item(selected[0],
                       values=(item["site"], item["user"], item["pass"]))

    # Hide password
    def hide_password(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.data[index]

        self.tree.item(selected[0],
                       values=(item["site"], item["user"], "******"))

    # Delete
    def delete_data(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.data[index]
        self.refresh_table()

    # Rename (edit website name)
    def rename_entry(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])

        new_name = tk.simpledialog.askstring("Rename", "Enter new website name:")
        if new_name:
            self.data[index]["site"] = new_name
            self.refresh_table()


# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()