import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pikepdf
import threading
import os

class PDFSecurityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Security Manager")
        self.root.geometry("580x560")
        self.root.resizable(False, False)
        
        # Modernize the standard Tkinter UI slightly using ttk themes
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
            
        # State variables
        self.file_path = tk.StringVar()
        self.action_var = tk.StringVar(value="remove")
        
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="PDF Security Suite", font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))
        
        # --- ACTION TOGGLE ---
        action_frame = ttk.LabelFrame(main_frame, text="Select Action", padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(action_frame, text="Unlock PDF (Remove Password)", variable=self.action_var, value="remove", command=self.toggle_action).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(action_frame, text="Protect PDF (Add Password)", variable=self.action_var, value="add", command=self.toggle_action).pack(side=tk.LEFT, padx=10)
        
        # --- FILE SELECTION ---
        file_frame = ttk.LabelFrame(main_frame, text="Select PDF File", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(file_frame, textvariable=self.file_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT)
        
        # --- DYNAMIC CONTAINER ---
        self.container = ttk.Frame(main_frame)
        self.container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 1. UNLOCK FRAME
        self.unlock_frame = ttk.Frame(self.container)
        self.notebook = ttk.Notebook(self.unlock_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sub-tab: Single Password
        self.tab_single = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_single, text="Single Password")
        ttk.Label(self.tab_single, text="Enter Current Password:").pack(anchor=tk.W, pady=5)
        self.ent_single_pass = ttk.Entry(self.tab_single, show="*")
        self.ent_single_pass.pack(fill=tk.X, pady=5)
        
        # Sub-tab: Dictionary
        self.tab_dict = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_dict, text="Dictionary Recovery")
        self.dict_path = tk.StringVar()
        dict_top = ttk.Frame(self.tab_dict)
        dict_top.pack(fill=tk.X, pady=5)
        ttk.Entry(dict_top, textvariable=self.dict_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(dict_top, text="Browse .txt", command=self.browse_dict).pack(side=tk.RIGHT)
        
        self.progress = ttk.Progressbar(self.tab_dict, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)
        self.lbl_prog = ttk.Label(self.tab_dict, text="")
        self.lbl_prog.pack(anchor=tk.W)
        
        # 2. PROTECT FRAME
        self.protect_frame = ttk.Frame(self.container)
        ttk.Label(self.protect_frame, text="Set New Secure Password:").pack(anchor=tk.W, pady=5)
        self.ent_new_pass = ttk.Entry(self.protect_frame, show="*")
        self.ent_new_pass.pack(fill=tk.X, pady=5)
        ttk.Label(self.protect_frame, text="* File will be protected with AES-256 encryption.", font=("Segoe UI", 9, "italic"), foreground="gray").pack(anchor=tk.W, pady=5)
        
        # --- PROCESS BUTTON ---
        self.btn_process = ttk.Button(main_frame, text="Process PDF", command=self.process_action)
        self.btn_process.pack(fill=tk.X, pady=10)
        
        self.lbl_status = ttk.Label(main_frame, text="Ready", foreground="blue", font=("Segoe UI", 10))
        self.lbl_status.pack()

        # Initialize visibility (must happen after btn_process is created)
        self.toggle_action()

    def toggle_action(self):
        """Switches the UI between Add and Remove modes"""
        if self.action_var.get() == "remove":
            self.protect_frame.pack_forget()
            self.unlock_frame.pack(fill=tk.BOTH, expand=True)
            self.btn_process.config(text="Unlock PDF")
        else:
            self.unlock_frame.pack_forget()
            self.protect_frame.pack(fill=tk.BOTH, expand=True)
            self.btn_process.config(text="Protect PDF")

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path: self.file_path.set(path)

    def browse_dict(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path: self.dict_path.set(path)

    def process_action(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
        
        self.btn_process.config(state=tk.DISABLED)
        
        if self.action_var.get() == "remove":
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab == 0:
                threading.Thread(target=self.do_unlock_single, daemon=True).start()
            else:
                threading.Thread(target=self.do_unlock_dict, daemon=True).start()
        else:
            threading.Thread(target=self.do_protect, daemon=True).start()

    def do_unlock_single(self):
        password = self.ent_single_pass.get()
        out_path = self.file_path.get().replace(".pdf", "_unlocked.pdf")
        try:
            with pikepdf.open(self.file_path.get(), password=password) as pdf:
                pdf.save(out_path)
            self.lbl_status.config(text="Unlocked successfully!", foreground="green")
            messagebox.showinfo("Success", f"File unlocked successfully!\nSaved to: {out_path}")
        except pikepdf.PasswordError:
            self.lbl_status.config(text="Error: Incorrect password.", foreground="red")
        except Exception as e:
            self.lbl_status.config(text="Error occurred.", foreground="red")
        finally:
            self.btn_process.config(state=tk.NORMAL)

    def do_unlock_dict(self):
        if not self.dict_path.get():
            messagebox.showerror("Error", "Please select a dictionary file.")
            self.btn_process.config(state=tk.NORMAL)
            return
        
        out_path = self.file_path.get().replace(".pdf", "_unlocked.pdf")
        try:
            with open(self.dict_path.get(), 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            total = len(passwords)
            for i, pwd in enumerate(passwords):
                self.progress['value'] = (i / total) * 100
                self.lbl_prog.config(text=f"Trying: {pwd} ({i+1}/{total})")
                try:
                    with pikepdf.open(self.file_path.get(), password=pwd) as pdf:
                        pdf.save(out_path)
                    
                    self.lbl_status.config(text=f"Success! Password is: {pwd}", foreground="green")
                    self.progress['value'] = 100
                    messagebox.showinfo("Success", f"Password found: {pwd}\nUnlocked file saved to: {out_path}")
                    self.btn_process.config(state=tk.NORMAL)
                    return
                except pikepdf.PasswordError:
                    continue
            
            self.lbl_status.config(text="Dictionary exhausted. No match.", foreground="red")
        except Exception as e:
            self.lbl_status.config(text="Error occurred.", foreground="red")
        
        self.btn_process.config(state=tk.NORMAL)
        self.lbl_prog.config(text="")
        self.progress['value'] = 0

    def do_protect(self):
        password = self.ent_new_pass.get()
        if not password:
            messagebox.showerror("Error", "Please enter a new password.")
            self.btn_process.config(state=tk.NORMAL)
            return
            
        out_path = self.file_path.get().replace(".pdf", "_protected.pdf")
        try:
            # Open unencrypted file
            with pikepdf.open(self.file_path.get()) as pdf:
                # Save with AES-256 encryption. We set both Owner and User password to the same value
                pdf.save(out_path, encryption=pikepdf.Encryption(user=password, owner=password, allow=pikepdf.Permissions(extract=False)))
                
            self.lbl_status.config(text="Protected successfully!", foreground="green")
            messagebox.showinfo("Success", f"Encrypted file saved securely to:\n{out_path}")
            
        except pikepdf.PasswordError:
            self.lbl_status.config(text="File is already encrypted.", foreground="red")
            messagebox.showerror("Error", "This file is already encrypted. Please unlock it first before re-encrypting.")
        except Exception as e:
            self.lbl_status.config(text=f"Error: {e}", foreground="red")
        finally:
            self.btn_process.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSecurityApp(root)
    root.mainloop()