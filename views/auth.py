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
        self.window.geometry("400x500")

        # Center window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 500) // 2
        self.window.geometry(f"+{x}+{y}")

        # Make it modal
        self.window.transient()
        self.window.grab_set()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.window, bg="#1a1a2e")
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # Title
        tk.Label(
            main_frame,
            text="🐟 AL FOURQANE",
            font=('Helvetica', 24, 'bold'),
            bg="#1a1a2e",
            fg="white"
        ).pack(pady=(0, 20))

        # Subtitle
        tk.Label(
            main_frame,
            text="Connexion",
            font=('Helvetica', 18),
            bg="#1a1a2e",
            fg="white"
        ).pack(pady=(0, 40))

        # Username
        tk.Label(
            main_frame,
            text="Utilisateur:",
            font=('Helvetica', 12),
            bg="#1a1a2e",
            fg="white"
        ).pack(anchor='w')

        self.username_var = tk.StringVar()
        tk.Entry(
            main_frame,
            textvariable=self.username_var,
            font=('Helvetica', 12),
            bg="#16213e",
            fg="white",
            insertbackground="white"
        ).pack(fill='x', pady=(5, 20))

        # Password
        tk.Label(
            main_frame,
            text="Mot de passe:",
            font=('Helvetica', 12),
            bg="#1a1a2e",
            fg="white"
        ).pack(anchor='w')

        self.password_var = tk.StringVar()
        tk.Entry(
            main_frame,
            textvariable=self.password_var,
            show="*",
            font=('Helvetica', 12),
            bg="#16213e",
            fg="white",
            insertbackground="white"
        ).pack(fill='x', pady=(5, 40))

        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#1a1a2e")
        button_frame.pack(fill='x', pady=(0, 20))

        # Login button with hover effect
        login_button = tk.Button(
            button_frame,
            text="Se connecter",
            command=self.login,
            font=('Helvetica', 12, 'bold'),
            bg="#00a8e8",
            fg="white",
            activebackground="#0077b6",
            activeforeground="white",
            cursor="hand2"
        )
        login_button.pack(side=tk.LEFT, expand=True, padx=5, pady=5, fill='x')

        # Cancel button with hover effect
        cancel_button = tk.Button(
            button_frame,
            text="Annuler",
            command=self.window.destroy,
            font=('Helvetica', 12),
            bg="#dc3545",
            fg="white",
            activebackground="#c82333",
            activeforeground="white",
            cursor="hand2"
        )
        cancel_button.pack(side=tk.LEFT, expand=True, padx=5, pady=5, fill='x')

        # Bind enter key to login
        self.window.bind('<Return>', lambda e: self.login())

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