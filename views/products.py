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
            self.tree.insert('', 'end', values=row)

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
            self.tree.insert('', 'end', values=row)

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
        
        # Name
        ttk.Label(self.top, text="Nom:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        # Price
        ttk.Label(self.top, text="Prix:").grid(row=1, column=0, padx=5, pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.price_var).grid(row=1, column=1, padx=5, pady=5)

        # Stock
        ttk.Label(self.top, text="Stock:").grid(row=2, column=0, padx=5, pady=5)
        self.stock_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.stock_var).grid(row=2, column=1, padx=5, pady=5)

        # Category
        ttk.Label(self.top, text="Catégorie:").grid(row=3, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.top, textvariable=self.category_var)
        self.load_categories()
        self.category_combo.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.LEFT, padx=5)

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
