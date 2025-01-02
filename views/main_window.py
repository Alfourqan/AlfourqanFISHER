import tkinter as tk
from tkinter import ttk
import sv_ttk
from views import products, sales, customers, invoices, suppliers, categories, inventory, cashier, reports, settings

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AL FOURQANE - Gestion de Poissonnerie")
        self.root.geometry("1200x800")

        # Configure theme colors
        self.root.configure(bg="#00796b")
        sv_ttk.set_theme("dark")

        self.setup_ui()

    def setup_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self.sidebar = ttk.Frame(self.main_container)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Menu buttons frame (for all buttons except logout)
        menu_frame = ttk.Frame(self.sidebar)
        menu_frame.pack(fill=tk.X, expand=False, pady=5)

        # Menu buttons with icons
        menu_items = [
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

        for text, icon, command in menu_items:
            btn = ttk.Button(menu_frame, text=f"{icon} {text}", command=command, width=20)
            btn.pack(pady=2, padx=5)

        # Create a frame for the logout button at the bottom
        logout_frame = ttk.Frame(self.sidebar)
        logout_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Add logout button at the bottom
        logout_btn = ttk.Button(logout_frame, text="🚪 Déconnexion", command=self.logout, width=20)
        logout_btn.pack(pady=5, padx=5)

        # Content area
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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

    def logout(self):
        self.root.quit()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()