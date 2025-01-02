import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database

class LoginWindow:
    def __init__(self, callback=None):
        self.window = tk.Toplevel()
        self.window.title("Connexion")
        self.db = Database()
        self.callback = callback

        # Configure window style
        self.window.configure(bg="#1a1a2e")
        style = ttk.Style()
        style.configure("Login.TFrame", background="#1a1a2e")
        style.configure("Login.TLabel", background="#1a1a2e", foreground="white")
        style.configure("Login.TButton", padding=10)

        self.setup_ui()

        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make it modal
        self.window.transient()
        self.window.grab_set()

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.window, style="Login.TFrame", padding=40)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_frame = ttk.Frame(main_frame, style="Login.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 30))
        ttk.Label(title_frame, 
                 text="AL FOURQANE",
                 font=('Helvetica', 24, 'bold'),
                 style="Login.TLabel").pack(anchor=tk.CENTER)
        ttk.Label(title_frame,
                 text="Connexion",
                 font=('Helvetica', 16),
                 style="Login.TLabel").pack(anchor=tk.CENTER)

        # Username
        username_frame = ttk.Frame(main_frame, style="Login.TFrame")
        username_frame.pack(fill=tk.X, pady=10)
        ttk.Label(username_frame, 
                 text="Utilisateur:",
                 style="Login.TLabel").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        ttk.Entry(username_frame, 
                 textvariable=self.username_var,
                 width=30).pack(fill=tk.X, pady=(5, 0))

        # Password
        password_frame = ttk.Frame(main_frame, style="Login.TFrame")
        password_frame.pack(fill=tk.X, pady=10)
        ttk.Label(password_frame, 
                 text="Mot de passe:",
                 style="Login.TLabel").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(password_frame,
                 textvariable=self.password_var,
                 show="*",
                 width=30).pack(fill=tk.X, pady=(5, 0))

        # Buttons
        btn_frame = ttk.Frame(main_frame, style="Login.TFrame")
        btn_frame.pack(fill=tk.X, pady=(30, 0))

        ttk.Button(btn_frame,
                  text="Connexion",
                  command=self.login,
                  style="Login.TButton",
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame,
                  text="Annuler",
                  command=self.window.destroy,
                  style="Login.TButton",
                  width=15).pack(side=tk.LEFT)

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