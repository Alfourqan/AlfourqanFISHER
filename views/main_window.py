import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from views import products, sales, customers, invoices, suppliers, categories, inventory, cashier, reports, settings, home, auth

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AL FOURQANE - Gestion de Poissonnerie")
        self.root.geometry("1200x800")
        self.current_user = None

        # Configure theme colors
        self.root.configure(bg="#004d40")
        sv_ttk.set_theme("dark")
        style = ttk.Style()
        style.configure(".", background="#004d40")
        style.configure("TFrame", background="#004d40")
        style.configure("TLabel", background="#004d40", foreground="white")
        style.configure("TButton", padding=5)

        self.setup_ui()
        self.show_login()

    def setup_ui(self):
        # Create main container with centered content
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self.sidebar = ttk.Frame(self.main_container)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Menu buttons frame (for all buttons except logout)
        menu_frame = ttk.Frame(self.sidebar)
        menu_frame.pack(fill=tk.X, expand=False, pady=5)

        # Menu buttons with icons
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
            ("Rapport", "📊", self.show_reports),
            ("Réglages", "⚙️", self.show_settings),
        ]

        self.menu_buttons = []
        for text, icon, command in self.menu_items:
            btn = ttk.Button(menu_frame, text=f"{icon} {text}", command=command, width=20)
            btn.pack(pady=2, padx=5)
            self.menu_buttons.append(btn)
            btn.configure(state="disabled")  # Initially disabled

        # Create a frame for the logout button at the bottom
        logout_frame = ttk.Frame(self.sidebar)
        logout_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Add logout button at the bottom
        self.logout_btn = ttk.Button(logout_frame, text="🚪 Déconnexion", command=self.logout, width=20)
        self.logout_btn.pack(pady=5, padx=5)
        self.logout_btn.configure(state="disabled")  # Initially disabled

        # Content area with centered content
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

    def show_login(self):
        self.clear_content()
        login_window = auth.LoginWindow(callback=self.on_login_success)
        self.root.wait_window(login_window.window)
        if not self.current_user:
            self.root.quit()

    def on_login_success(self, user):
        self.current_user = user
        # Enable all menu buttons
        for btn in self.menu_buttons:
            btn.configure(state="normal")
        self.logout_btn.configure(state="normal")
        self.show_home()

    def logout(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vous déconnecter ?"):
            self.current_user = None
            # Disable all menu buttons
            for btn in self.menu_buttons:
                btn.configure(state="disabled")
            self.logout_btn.configure(state="disabled")
            self.show_login()

    def show_home(self):
        self.clear_content()
        home.HomeView(self.content)

    def show_products(self):
        self.clear_content()
        products.ProductsView(self.content)

    def show_sales(self):
        self.clear_content()
        sales.SalesView(self.content)

    def show_customers(self):
        self.clear_content()
        customers.CustomersView(self.content)

    def show_invoices(self):
        self.clear_content()
        invoices.InvoicesView(self.content)

    def show_suppliers(self):
        self.clear_content()
        suppliers.SuppliersView(self.content)

    def show_categories(self):
        self.clear_content()
        categories.CategoriesView(self.content)

    def show_inventory(self):
        self.clear_content()
        inventory.InventoryView(self.content)

    def show_cashier(self):
        self.clear_content()
        cashier.CashierView(self.content)

    def show_reports(self):
        self.clear_content()
        reports.ReportsView(self.content)

    def show_settings(self):
        self.clear_content()
        settings.SettingsView(self.content)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()