import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.database import Database

class ProductsView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Gestion des Produits", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)

        # Add button
        ttk.Button(title_frame, text="+ Nouveau Produit", command=self.add_product).pack(side=tk.RIGHT)

        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        # Products table
        self.tree = ttk.Treeview(self.parent, columns=('ID', 'Nom', 'Prix', 'Stock', 'Catégorie'),
                                show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nom', text='Nom')
        self.tree.heading('Prix', text='Prix')
        self.tree.heading('Stock', text='Stock')
        self.tree.heading('Catégorie', text='Catégorie')

        self.tree.column('ID', width=50)
        self.tree.column('Nom', width=200)
        self.tree.column('Prix', width=100)
        self.tree.column('Stock', width=100)
        self.tree.column('Catégorie', width=150)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_products(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.stock, c.name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id
        ''')

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in cursor.fetchall():
            row_data = dict(row)
            self.tree.insert('', 'end', values=(
                row_data['id'],
                row_data['name'],
                row_data['price'],
                row_data['stock'],
                row_data.get('name', '')  # Category name
            ))

    def filter_products(self, *args):
        search_term = self.search_var.get().lower()
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.stock, c.name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE LOWER(p.name) LIKE ?
        ''', (f'%{search_term}%',))

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in cursor.fetchall():
            row_data = dict(row)
            self.tree.insert('', 'end', values=(
                row_data['id'],
                row_data['name'],
                row_data['price'],
                row_data['stock'],
                row_data.get('name', '')  # Category name
            ))

    def add_product(self):
        dialog = ProductDialog(self.parent, self.db)
        self.parent.wait_window(dialog.top)
        self.load_products()

class ProductDialog:
    def __init__(self, parent, db):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.top.title("Nouveau Produit")

        # Center the dialog on screen
        window_width = 400
        window_height = 300
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Main container frame
        main_frame = ttk.Frame(self.top, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Nom:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=30).pack(side=tk.LEFT, padx=(10, 0))

        # Price
        price_frame = ttk.Frame(main_frame)
        price_frame.pack(fill=tk.X, pady=5)
        ttk.Label(price_frame, text="Prix:").pack(side=tk.LEFT)
        self.price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=self.price_var, width=30).pack(side=tk.LEFT, padx=(10, 0))

        # Stock
        stock_frame = ttk.Frame(main_frame)
        stock_frame.pack(fill=tk.X, pady=5)
        ttk.Label(stock_frame, text="Stock:").pack(side=tk.LEFT)
        self.stock_var = tk.StringVar()
        ttk.Entry(stock_frame, textvariable=self.stock_var, width=30).pack(side=tk.LEFT, padx=(10, 0))

        # Category
        category_frame = ttk.Frame(main_frame)
        category_frame.pack(fill=tk.X, pady=5)
        ttk.Label(category_frame, text="Catégorie:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, width=27)
        self.load_categories()
        self.category_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.LEFT)

    def load_categories(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM categories')
        categories = [row[0] for row in cursor.fetchall()]
        self.category_combo['values'] = categories

    def save(self):
        try:
            name = self.name_var.get()
            price = float(self.price_var.get())
            stock = float(self.stock_var.get())
            category = self.category_var.get()

            cursor = self.db.conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
            category_id = cursor.fetchone()[0]

            cursor.execute('''
                INSERT INTO products (name, price, stock, category_id)
                VALUES (?, ?, ?, ?)
            ''', (name, price, stock, category_id))

            self.db.conn.commit()
            self.top.destroy()

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))