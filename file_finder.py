import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder | MR. SELFISH EDITION")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e") # Dark Theme

        self.selected_path = tk.StringVar()
        self.files_dict = {} 

        self.setup_ui()

    def setup_ui(self):
        # Header - Stylish Dark Look
        header = tk.Label(self.root, text="🔍 DUPLICATE FILE FINDER", font=("Impact", 24), 
                         fg="#00ffcc", bg="#1e1e1e", pady=20)
        header.pack()

        # Selection Frame
        frame_top = tk.Frame(self.root, bg="#1e1e1e")
        frame_top.pack(pady=10, fill="x", padx=20) # Fixed 'px' to 'padx'

        self.path_entry = tk.Entry(frame_top, textvariable=self.selected_path, font=("Consolas", 11), 
                                  bg="#2d2d2d", fg="white", insertbackground="white", width=60)
        self.path_entry.pack(side="left", padx=10, ipady=5)

        btn_browse = tk.Button(frame_top, text="📂 BROWSE", command=self.browse_folder, 
                              bg="#444", fg="white", relief="flat", padx=15, cursor="hand2")
        btn_browse.pack(side="left")

        # Control Buttons Frame
        frame_btns = tk.Frame(self.root, bg="#1e1e1e")
        frame_btns.pack(pady=15)

        self.btn_scan = tk.Button(frame_btns, text="🚀 START SCAN", command=self.start_scan_thread, 
                                bg="#00ffcc", fg="black", font=("Arial", 10, "bold"), padx=20, pady=7, relief="flat")
        self.btn_scan.pack(side="left", padx=10)

        self.btn_select_all = tk.Button(frame_btns, text="☑ SELECT DUPLICATES", command=self.select_all_duplicates, 
                                   bg="#f1c40f", fg="black", font=("Arial", 10, "bold"), padx=20, pady=7, relief="flat")
        self.btn_select_all.pack(side="left", padx=10)

        self.btn_delete = tk.Button(frame_btns, text="🗑 DELETE SELECTED", command=self.delete_selected, 
                                   bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), padx=20, pady=7, relief="flat")
        self.btn_delete.pack(side="left", padx=10)

        # Result Treeview with Scrollbar
        list_frame = tk.Frame(self.root, bg="#1e1e1e")
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("Path", "Size"), show="headings", selectmode="extended")
        self.tree.heading("Path", text="FILE PATH")
        self.tree.heading("Size", text="SIZE (KB)")
        self.tree.column("Path", width=700)
        self.tree.column("Size", width=100, anchor="center")
        
        # Scrollbar
        scroller = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroller.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroller.pack(side="right", fill="y")

        # Status Bar
        self.status_label = tk.Label(self.root, text="Status: Ready to use", bd=1, relief="flat", 
                                    anchor="w", bg="#333", fg="#00ffcc", font=("Arial", 9))
        self.status_label.pack(side="bottom", fill="x")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_path.set(folder)

    def calculate_hash(self, path):
        hasher = hashlib.md5()
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except: return None

    def start_scan_thread(self):
        path = self.selected_path.get()
        if not path:
            messagebox.showwarning("Error", "Bhai, folder toh select karlo pehle!")
            return
        
        self.btn_scan.config(state="disabled", text="Scanning...")
        self.tree.delete(*self.tree.get_children())
        threading.Thread(target=self.scan_files, args=(path,), daemon=True).start()

    def scan_files(self, path):
        self.status_label.config(text="Status: Looking for duplicates...")
        self.files_dict = {}
        
        for root_dir, _, files in os.walk(path):
            for file in files:
                full_path = os.path.normpath(os.path.join(root_dir, file))
                file_hash = self.calculate_hash(full_path)
                
                if file_hash:
                    if file_hash in self.files_dict:
                        self.files_dict[file_hash].append(full_path)
                    else:
                        self.files_dict[file_hash] = [full_path]

        self.root.after(0, self.display_results)

    def display_results(self):
        found = False
        for file_hash, paths in self.files_dict.items():
            if len(paths) > 1:
                found = True
                # Display Original
                self.tree.insert("", "end", values=(f"⭐ ORIGINAL: {paths[0]}", round(os.path.getsize(paths[0])/1024, 2)), tags=('original',))
                # Display Duplicates
                for p in paths[1:]:
                    self.tree.insert("", "end", values=(f"📋 DUPLICATE: {p}", round(os.path.getsize(p)/1024, 2)), tags=('duplicate',))

        self.tree.tag_configure('original', foreground="#00ffcc")
        self.tree.tag_configure('duplicate', foreground="#ff7675")
        
        self.btn_scan.config(state="normal", text="🚀 START SCAN")
        if not found:
            self.status_label.config(text="Status: No duplicates found. Your PC is clean!")
        else:
            self.status_label.config(text=f"Status: Found duplicates! Use buttons to clean up.")

    def select_all_duplicates(self):
        """Automatically selects only the rows marked as DUPLICATE."""
        self.tree.selection_remove(self.tree.selection()) # Clear current selection
        for item in self.tree.get_children():
            val = self.tree.item(item)['values'][0]
            if "📋 DUPLICATE:" in val:
                self.tree.selection_add(item)

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Wait", "Select toh karo kya delete karna hai!")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {len(selected_items)} files?"):
            for item in selected_items:
                raw_path = self.tree.item(item)['values'][0]
                # Clean path string
                path = raw_path.replace("⭐ ORIGINAL: ", "").replace("📋 DUPLICATE: ", "")
                try:
                    os.remove(path)
                    self.tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete {path}\nError: {e}")
            self.status_label.config(text="Status: Selected files deleted.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()