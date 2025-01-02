import tkinter as tk
from tkinter import messagebox
from models.database import Database

class LoginWindow:
    def __init__(self, callback=None):
        self.window = tk.Toplevel()
        self.window.title("Connexion")
        self.db = Database()
        self.callback = callback

        # Configure window
        self.window.configure(bg="#1a1a2e")
        self.window.geometry("600x400")

        # Center window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        self.window.geometry(f"+{x}+{y}")

        # Make it modal
        self.window.transient()
        self.window.grab_set()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.window, bg="#1a1a2e", padx=60, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(main_frame, 
                text="AL FOURQANE",
                font=('Helvetica', 32, 'bold'),
                bg="#1a1a2e",
                fg="white").pack(pady=(0, 10))

        tk.Label(main_frame,
                text="Connexion",
                font=('Helvetica', 24),
                bg="#1a1a2e",
                fg="white").pack(pady=(0, 40))

        # Username
        tk.Label(main_frame,
                text="Utilisateur:",
                font=('Helvetica', 14),
                bg="#1a1a2e",
                fg="white").pack(anchor=tk.W)

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(main_frame,
                                     textvariable=self.username_var,
                                     font=('Helvetica', 12),
                                     bg="#16213e",
                                     fg="white",
                                     insertbackground="white",
                                     relief=tk.SOLID,
                                     bd=1)
        self.username_entry.pack(fill=tk.X, pady=(5, 20))

        # Password
        tk.Label(main_frame,
                text="Mot de passe:",
                font=('Helvetica', 14),
                bg="#1a1a2e",
                fg="white").pack(anchor=tk.W)

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(main_frame,
                                     textvariable=self.password_var,
                                     show="*",
                                     font=('Helvetica', 12),
                                     bg="#16213e",
                                     fg="white",
                                     insertbackground="white",
                                     relief=tk.SOLID,
                                     bd=1)
        self.password_entry.pack(fill=tk.X, pady=(5, 40))

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X)

        login_btn = tk.Button(btn_frame,
                            text="Connexion",
                            command=self.login,
                            font=('Helvetica', 12),
                            bg="#16213e",
                            fg="white",
                            relief=tk.SOLID,
                            bd=1,
                            padx=20,
                            pady=10)
        login_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = tk.Button(btn_frame,
                             text="Annuler",
                             command=self.window.destroy,
                             font=('Helvetica', 12),
                             bg="#16213e",
                             fg="white",
                             relief=tk.SOLID,
                             bd=1,
                             padx=20,
                             pady=10)
        cancel_btn.pack(side=tk.LEFT)

        # Bind enter key to login
        self.window.bind('<Return>', lambda e: self.login())

        # Initial focus
        self.username_entry.focus_set()

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return

        user = self.db.authenticate_user(username, password)
        if user:
            if self.callback:
                self.callback(user)
            self.window.destroy()
        else:
            messagebox.showerror("Erreur", "Identifiants invalides")