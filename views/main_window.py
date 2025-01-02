import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from views import products, sales, customers, invoices, suppliers, categories, inventory, cashier, reports, settings, home, auth

class SplashScreen:
    def __init__(self, parent):
        self.parent = parent
        self.splash = tk.Toplevel(parent)
        self.splash.title("AL FOURQANE")

        # Configure window size (fixed size instead of fullscreen)
        width = 600
        height = 400
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        # Configure theme colors
        self.splash.configure(bg="#1a1a2e")

        # Make it modal and remove decorations
        self.splash.transient(parent)
        self.splash.grab_set()
        self.splash.overrideredirect(True)

        # Center the content
        content_frame = tk.Frame(self.splash, bg="#1a1a2e")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo and title
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

        # Progress bar
        self.progress = ttk.Progressbar(
            content_frame,
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=30)

        # Start animation
        self.progress['maximum'] = 100
        self.progress['value'] = 0
        self.animate()

    def animate(self):
        if self.progress['value'] < 100:
            self.progress['value'] += 5
            self.splash.after(50, self.animate)
        else:
            self.splash.after(500, self.finish)

    def finish(self):
        self.splash.destroy()
        self.parent.deiconify()

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AL FOURQANE")
        self.root.geometry("1200x800")
        self.current_user = None

        # Hide main window initially
        self.root.withdraw()

        # Configure theme colors
        self.root.configure(bg="#1a1a2e")
        sv_ttk.set_theme("dark")
        style = ttk.Style()
        style.configure(".", background="#1a1a2e", foreground="white")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="white")
        style.configure("TButton", padding=5)

        # Configure sidebar style
        style.configure("Sidebar.TFrame", background="#16213e")
        style.configure("Menu.TButton", 
                       background="#16213e",
                       foreground="white",
                       padding=(20, 10, 20, 10),
                       width=20,
                       anchor="w")

        self.setup_ui()

        # Show splash screen and schedule login
        self.root.after(100, lambda: SplashScreen(self.root))
        self.root.after(3000, self.show_login)

    def setup_ui(self):
        # Main container
        self.main_container = ttk.Frame(self.root, style="TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar with dark blue background
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Add app title to sidebar
        title_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        title_frame.pack(fill=tk.X, pady=(20, 30))
        ttk.Label(title_frame, 
                 text="AL FOURQANE",
                 font=('Helvetica', 16, 'bold'),
                 foreground="white",
                 background="#16213e").pack(anchor=tk.W, padx=20)

        # Menu buttons frame
        menu_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        menu_frame.pack(fill=tk.X, expand=False)

        # Top menu frame (dots)
        top_menu = ttk.Frame(self.main_container, style="TFrame")
        top_menu.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        ttk.Label(top_menu, text="○ ○ ○", font=('Helvetica', 12), foreground="white").pack(side=tk.RIGHT, padx=10)

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
            ("Report", "📊", self.show_reports),
            ("Réglages", "⚙️", self.show_settings),
        ]

        self.menu_buttons = []
        for text, icon, command in self.menu_items:
            btn = ttk.Button(menu_frame, 
                           text=f"{icon}  {text}", 
                           command=command,
                           style="Menu.TButton")
            btn.pack(pady=1, fill=tk.X)
            self.menu_buttons.append(btn)
            btn.configure(state="disabled")

        # Logout button frame at bottom
        logout_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        logout_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        self.logout_btn = ttk.Button(logout_frame, 
                                  text="🚪  Déconnexion",
                                  command=self.logout,
                                  style="Menu.TButton")
        self.logout_btn.pack(fill=tk.X)
        self.logout_btn.configure(state="disabled")

        # Content area
        self.content = ttk.Frame(self.main_container, style="TFrame")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30, pady=30)

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