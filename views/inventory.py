import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database

class InventoryView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Inventaire", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="Ajuster Stock", command=self.adjust_stock).pack(side=tk.RIGHT)

        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_inventory)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        # Filter by category
        ttk.Label(search_frame, text="Catégorie:").pack(side=tk.LEFT, padx=(20,5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var)
        self.load_categories()
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_var.trace('w', self.filter_inventory)

        # Inventory table
        self.tree = ttk.Treeview(self.parent, 
                                columns=('ID', 'Produit', 'Catégorie', 'Stock', 'Prix'),
                                show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Produit', text='Produit')
        self.tree.heading('Catégorie', text='Catégorie')
        self.tree.heading('Stock', text='Stock')
        self.tree.heading('Prix', text='Prix')
        
        self.tree.column('ID', width=50)
        self.tree.column('Produit', width=200)
        self.tree.column('Catégorie', width=150)
        self.tree.column('Stock', width=100)
        self.tree.column('Prix', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_categories(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM categories')
        categories = ['Toutes'] + [row[0] for row in cursor.fetchall()]
        self.category_combo['values'] = categories
        self.category_var.set('Toutes')

    def load_inventory(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, c.name, p.stock, p.price 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        ''')
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def filter_inventory(self, *args):
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        
        cursor = self.db.conn.cursor()
        
        if category == 'Toutes':
            cursor.execute('''
                SELECT p.id, p.name, c.name, p.stock, p.price 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE LOWER(p.name) LIKE ?
            ''', (f'%{search_term}%',))
        else:
            cursor.execute('''
                SELECT p.id, p.name, c.name, p.stock, p.price 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE LOWER(p.name) LIKE ? AND c.name = ?
            ''', (f'%{search_term}%', category))
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def adjust_stock(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un produit")
            return

        product_id = self.tree.item(selection[0])['values'][0]
        dialog = StockAdjustmentDialog(self.parent, self.db, product_id)
        self.parent.wait_window(dialog.top)
        self.load_inventory()

class StockAdjustmentDialog:
    def __init__(self, parent, db, product_id):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.product_id = product_id
        self.setup_ui()
        self.load_product()

    def setup_ui(self):
        self.top.title("Ajuster le stock")
        
        # Product info
        ttk.Label(self.top, text="Produit:").grid(row=0, column=0, padx=5, pady=5)
        self.product_label = ttk.Label(self.top, text="")
        self.product_label.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.top, text="Stock actuel:").grid(row=1, column=0, padx=5, pady=5)
        self.current_stock_label = ttk.Label(self.top, text="")
        self.current_stock_label.grid(row=1, column=1, padx=5, pady=5)
        
        # Adjustment
        ttk.Label(self.top, text="Ajustement:").grid(row=2, column=0, padx=5, pady=5)
        self.adjustment_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.adjustment_var).grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.LEFT, padx=5)

    def load_product(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name, stock FROM products WHERE id = ?', (self.product_id,))
        product = cursor.fetchone()
        
        if product:
            product_data = dict(product)
            self.product_label.config(text=product_data['name'])
            self.current_stock_label.config(text=str(product_data['stock']))
        else:
            messagebox.showerror("Erreur", "Produit non trouvé")
            self.top.destroy()

    def save(self):
        try:
            adjustment = float(self.adjustment_var.get())
            
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE products 
                SET stock = stock + ?
                WHERE id = ?
            ''', (adjustment, self.product_id))
            
            self.db.conn.commit()
            self.top.destroy()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
