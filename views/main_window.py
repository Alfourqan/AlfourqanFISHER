import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from views import products, sales, customers, invoices, suppliers, categories, inventory, cashier, reports, settings, home, auth

class SplashScreen:
    """
    Écran de démarrage qui s'affiche au lancement de l'application.
    Affiche le logo, le titre et une barre de progression.
    """
    def __init__(self, parent):
        self.parent = parent
        self.splash = tk.Toplevel(parent)
        self.splash.title("AL FOURQANE")

        # Configuration de la taille de la fenêtre (taille fixe au lieu de plein écran)
        width = 600
        height = 400
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        # Configuration des couleurs du thème
        self.splash.configure(bg="#1a1a2e")

        # Rendre la fenêtre modale et supprimer les décorations
        self.splash.transient()
        self.splash.grab_set()
        self.splash.overrideredirect(True)

        # Centrer le contenu
        content_frame = tk.Frame(self.splash, bg="#1a1a2e")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo et titre
        tk.Label(
            content_frame,
            text="🐟",
            font=('Helvetica', 100),
            bg="#1a1a2e",
            fg="white"
        ).pack()

        tk.Label(
            content_frame,
            text="AL FOURQANE",
            font=('Helvetica', 36, 'bold'),
            bg="#1a1a2e",
            fg="white"
        ).pack(pady=20)

        # Barre de progression
        self.progress = ttk.Progressbar(
            content_frame,
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=30)

        # Démarrer l'animation
        self.progress['maximum'] = 100
        self.progress['value'] = 0
        self.animate()

    def animate(self):
        """Anime la barre de progression jusqu'à 100%"""
        if self.progress['value'] < 100:
            self.progress['value'] += 5
            self.splash.after(50, self.animate)
        else:
            self.splash.after(500, self.finish)

    def finish(self):
        """Ferme l'écran de démarrage et affiche la fenêtre principale"""
        self.splash.destroy()
        self.parent.deiconify()

class MainWindow:
    """
    Fenêtre principale de l'application.
    Gère l'interface utilisateur, la navigation et l'authentification.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AL FOURQANE")
        self.root.geometry("1200x800")
        self.current_user = None
        self.root.update_idletasks()

        # Cacher la fenêtre principale initialement
        self.root.withdraw()

        # Configuration des couleurs et du thème
        self.root.configure(bg="#1a1a2e")
        sv_ttk.set_theme("dark")
        style = ttk.Style()
        style.configure(".", background="#1a1a2e", foreground="white")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="white")
        style.configure("TButton", padding=5)

        # Configuration du style de la barre latérale
        style.configure("Sidebar.TFrame", background="#16213e")
        style.configure("Menu.TButton", 
                       background="#16213e",
                       foreground="white",
                       padding=(20, 10, 20, 10),
                       width=20,
                       anchor="w")

        self.setup_ui()

        # Afficher l'écran de démarrage
        splash = SplashScreen(self.root)
        self.root.after(1500, self.show_login)

    def setup_ui(self):
        """Configure l'interface utilisateur principale"""
        # Conteneur principal
        self.main_container = ttk.Frame(self.root, style="TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Barre latérale avec fond bleu foncé
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Titre de l'application dans la barre latérale
        title_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        title_frame.pack(fill=tk.X, pady=(20, 30))
        ttk.Label(title_frame, 
                 text="AL FOURQANE",
                 font=('Helvetica', 16, 'bold'),
                 foreground="white",
                 background="#16213e").pack(anchor=tk.W, padx=20)

        # Cadre des boutons du menu
        menu_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        menu_frame.pack(fill=tk.X, expand=False)

        # Boutons du menu avec icônes
        self.menu_items = [
            ("Accueil", "🏠", self.show_home),
            ("Produits", "🐟", self.show_products),
            ("Ventes", "💰", self.show_sales),
            ("Clients", "👥", self.show_customers),
            ("Factures", "📄", self.show_invoices),
            ("Fournisseurs", "🏭", self.show_suppliers),
            ("Catégories", "📁", self.show_categories),
            ("Inventaire", "📦", self.show_inventory),
            ("Caisse", "💵", self.show_cashier),
            ("Report", "📊", self.show_reports),
            ("Réglages", "⚙️", self.show_settings),
        ]

        # Création des boutons du menu
        self.menu_buttons = []
        for text, icon, command in self.menu_items:
            btn = ttk.Button(menu_frame, 
                          text=f"{icon}  {text}", 
                          command=command,
                          style="Menu.TButton")
            btn.pack(pady=1, fill=tk.X)
            self.menu_buttons.append(btn)
            btn.configure(state="disabled")  # Désactivé jusqu'à la connexion

        # Bouton de déconnexion en bas de la barre latérale
        logout_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        logout_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        self.logout_btn = ttk.Button(logout_frame, 
                                  text="🚪  Déconnexion",
                                  command=self.logout,
                                  style="Menu.TButton")
        self.logout_btn.pack(fill=tk.X)
        self.logout_btn.configure(state="disabled")

        # Zone de contenu principal
        self.content = ttk.Frame(self.main_container, style="TFrame")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30, pady=30)

    def show_login(self):
        """Affiche la fenêtre de connexion"""
        self.clear_content()
        login_window = auth.LoginWindow(callback=self.on_login_success)
        self.root.wait_window(login_window.window)
        if not self.current_user:
            self.root.quit()

    def on_login_success(self, user):
        """Callback appelé après une connexion réussie"""
        self.current_user = user
        # Activer tous les boutons du menu
        for btn in self.menu_buttons:
            btn.configure(state="normal")
        self.logout_btn.configure(state="normal")
        self.show_home()

    def logout(self):
        """Gère la déconnexion de l'utilisateur"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?"):
            self.current_user = None
            # Désactiver tous les boutons du menu
            for btn in self.menu_buttons:
                btn.configure(state="disabled")
            self.logout_btn.configure(state="disabled")
            self.show_login()

    # Méthodes de navigation pour chaque section
    def show_home(self):
        """Affiche la page d'accueil"""
        self.clear_content()
        home.HomeView(self.content)

    def show_products(self):
        """Affiche la gestion des produits"""
        self.clear_content()
        products.ProductsView(self.content)

    def show_sales(self):
        """Affiche la gestion des ventes"""
        self.clear_content()
        sales.SalesView(self.content)

    def show_customers(self):
        """Affiche la gestion des clients"""
        self.clear_content()
        customers.CustomersView(self.content)

    def show_invoices(self):
        """Affiche la gestion des factures"""
        self.clear_content()
        invoices.InvoicesView(self.content)

    def show_suppliers(self):
        """Affiche la gestion des fournisseurs"""
        self.clear_content()
        suppliers.SuppliersView(self.content)

    def show_categories(self):
        """Affiche la gestion des catégories"""
        self.clear_content()
        categories.CategoriesView(self.content)

    def show_inventory(self):
        """Affiche la gestion de l'inventaire"""
        self.clear_content()
        inventory.InventoryView(self.content)

    def show_cashier(self):
        """Affiche la caisse"""
        self.clear_content()
        cashier.CashierView(self.content)

    def show_reports(self):
        """Affiche les rapports"""
        self.clear_content()
        reports.ReportsView(self.content)

    def show_settings(self):
        """Affiche les paramètres"""
        self.clear_content()
        settings.SettingsView(self.content)

    def clear_content(self):
        """Nettoie la zone de contenu principal de manière optimisée"""
        if hasattr(self, '_current_view'):
            if hasattr(self._current_view, 'destroy'):
                self._current_view.destroy()
        for widget in self.content.winfo_children():
            widget.destroy()
        self.content.update_idletasks()

    def run(self):
        """Lance l'application"""
        self.root.mainloop()