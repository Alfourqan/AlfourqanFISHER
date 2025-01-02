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
        style.configure("Login.TButton", 
                       background="#16213e",
                       foreground="white",
                       padding=(10, 5, 10, 5))

        self.setup_ui()

        # Center the window
        window_width = 600  # Increased from 400
        window_height = 400  # Increased from 300
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
        main_frame = ttk.Frame(self.window, style="Login.TFrame", padding=60)  # Increased padding
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_frame = ttk.Frame(main_frame, style="Login.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 50))  # Increased spacing
        ttk.Label(title_frame, 
                 text="AL FOURQANE",
                 font=('Helvetica', 32, 'bold'),  # Increased font size
                 style="Login.TLabel").pack(anchor=tk.CENTER)
        ttk.Label(title_frame,
                 text="Connexion",
                 font=('Helvetica', 24),  # Increased font size
                 style="Login.TLabel").pack(anchor=tk.CENTER)

        # Username
        username_frame = ttk.Frame(main_frame, style="Login.TFrame")
        username_frame.pack(fill=tk.X, pady=15)  # Increased spacing
        ttk.Label(username_frame, 
                 text="Utilisateur:",
                 font=('Helvetica', 14),  # Added font size
                 style="Login.TLabel").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        ttk.Entry(username_frame, 
                 textvariable=self.username_var,
                 width=50).pack(fill=tk.X, pady=(5, 0))  # Increased width

        # Password
        password_frame = ttk.Frame(main_frame, style="Login.TFrame")
        password_frame.pack(fill=tk.X, pady=15)  # Increased spacing
        ttk.Label(password_frame, 
                 text="Mot de passe:",
                 font=('Helvetica', 14),  # Added font size
                 style="Login.TLabel").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(password_frame,
                 textvariable=self.password_var,
                 show="*",
                 width=50).pack(fill=tk.X, pady=(5, 0))  # Increased width

        # Buttons
        btn_frame = ttk.Frame(main_frame, style="Login.TFrame")
        btn_frame.pack(fill=tk.X, pady=(40, 0))  # Increased spacing

        ttk.Button(btn_frame,
                  text="Connexion",
                  command=self.login,
                  style="Login.TButton",
                  width=20).pack(side=tk.LEFT, padx=5)  # Increased width
        ttk.Button(btn_frame,
                  text="Annuler",
                  command=self.window.destroy,
                  style="Login.TButton",
                  width=20).pack(side=tk.LEFT)  # Increased width

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