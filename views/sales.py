import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database
from datetime import datetime

class SalesView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.setup_ui()
        self.load_sales()

    def setup_ui(self):
        # Title frame
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Gestion des Ventes", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="+ Nouvelle Vente", command=self.new_sale).pack(side=tk.RIGHT)

        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_sales)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        # Sales table
        self.tree = ttk.Treeview(self.parent, columns=('ID', 'Date', 'Client', 'Total'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Client', text='Client')
        self.tree.heading('Total', text='Total')
        
        self.tree.column('ID', width=50)
        self.tree.column('Date', width=150)
        self.tree.column('Client', width=200)
        self.tree.column('Total', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind double click
        self.tree.bind('<Double-1>', self.view_sale_details)

    def load_sales(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.date, c.name, s.total 
            FROM sales s 
            LEFT JOIN customers c ON s.customer_id = c.id
            ORDER BY s.date DESC
        ''')
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def filter_sales(self, *args):
        search_term = self.search_var.get().lower()
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.date, c.name, s.total 
            FROM sales s 
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE LOWER(c.name) LIKE ?
            ORDER BY s.date DESC
        ''', (f'%{search_term}%',))
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def new_sale(self):
        dialog = SaleDialog(self.parent, self.db)
        self.parent.wait_window(dialog.top)
        self.load_sales()

    def view_sale_details(self, event):
        item = self.tree.selection()[0]
        sale_id = self.tree.item(item)['values'][0]
        dialog = SaleDetailsDialog(self.parent, self.db, sale_id)
        self.parent.wait_window(dialog.top)

class SaleDialog:
    def __init__(self, parent, db):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.top.title("Nouvelle Vente")
        self.top.geometry("600x400")

        # Customer selection
        customer_frame = ttk.Frame(self.top)
        customer_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(customer_frame, text="Client:").pack(side=tk.LEFT)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var)
        self.load_customers()
        self.customer_combo.pack(side=tk.LEFT, padx=5)

        # Products
        products_frame = ttk.Frame(self.top)
        products_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Product selection
        product_select_frame = ttk.Frame(products_frame)
        product_select_frame.pack(fill=tk.X)
        ttk.Label(product_select_frame, text="Produit:").pack(side=tk.LEFT)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(product_select_frame, textvariable=self.product_var)
        self.load_products()
        self.product_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_select_frame, text="Quantité (kg):").pack(side=tk.LEFT)
        self.quantity_var = tk.StringVar()
        ttk.Entry(product_select_frame, textvariable=self.quantity_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(product_select_frame, text="Ajouter", command=self.add_product).pack(side=tk.LEFT, padx=5)

        # Products list
        self.products_tree = ttk.Treeview(products_frame, 
                                        columns=('Produit', 'Quantité', 'Prix', 'Total'),
                                        show='headings')
        self.products_tree.heading('Produit', text='Produit')
        self.products_tree.heading('Quantité', text='Quantité')
        self.products_tree.heading('Prix', text='Prix')
        self.products_tree.heading('Total', text='Total')
        self.products_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Total
        total_frame = ttk.Frame(self.top)
        total_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(total_frame, text="Total:").pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="0.00 €")
        ttk.Label(total_frame, textvariable=self.total_var).pack(side=tk.LEFT)

        # Buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.RIGHT, padx=5)

    def load_customers(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM customers')
        customers = [row[0] for row in cursor.fetchall()]
        self.customer_combo['values'] = customers

    def load_products(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM products')
        products = [row[0] for row in cursor.fetchall()]
        self.product_combo['values'] = products

    def add_product(self):
        try:
            product = self.product_var.get()
            quantity = float(self.quantity_var.get())
            
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT price FROM products WHERE name = ?', (product,))
            price = cursor.fetchone()[0]
            
            total = price * quantity
            
            self.products_tree.insert('', 'end', values=(product, quantity, price, total))
            
            # Update total
            current_total = float(self.total_var.get().replace('€', '').strip())
            self.total_var.set(f"{current_total + total:.2f} €")
            
            # Clear inputs
            self.product_var.set('')
            self.quantity_var.set('')
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une quantité valide")

    def save(self):
        try:
            customer = self.customer_var.get()
            cursor = self.db.conn.cursor()
            
            # Get customer id
            cursor.execute('SELECT id FROM customers WHERE name = ?', (customer,))
            customer_id = cursor.fetchone()[0]
            
            # Create sale
            total = float(self.total_var.get().replace('€', '').strip())
            cursor.execute('''
                INSERT INTO sales (date, customer_id, total)
                VALUES (?, ?, ?)
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer_id, total))
            
            sale_id = cursor.lastrowid
            
            # Add sale items
            for item in self.products_tree.get_children():
                values = self.products_tree.item(item)['values']
                product_name = values[0]
                quantity = values[1]
                price = values[2]
                
                cursor.execute('SELECT id FROM products WHERE name = ?', (product_name,))
                product_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, product_id, quantity, price))
                
                # Update stock
                cursor.execute('''
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE id = ?
                ''', (quantity, product_id))
            
            self.db.conn.commit()
            self.top.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.db.conn.rollback()

class SaleDetailsDialog:
    def __init__(self, parent, db, sale_id):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.sale_id = sale_id
        self.setup_ui()

    def setup_ui(self):
        self.top.title(f"Détails de la vente #{self.sale_id}")
        self.top.geometry("500x400")

        # Load sale details
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.date, c.name, s.total 
            FROM sales s 
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        ''', (self.sale_id,))
        sale = cursor.fetchone()

        # Display sale info
        info_frame = ttk.Frame(self.top)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(info_frame, text=f"Date: {sale[0]}").pack()
        ttk.Label(info_frame, text=f"Client: {sale[1]}").pack()
        ttk.Label(info_frame, text=f"Total: {sale[2]} €").pack()

        # Display items
        self.tree = ttk.Treeview(self.top, 
                                columns=('Produit', 'Quantité', 'Prix', 'Total'),
                                show='headings')
        self.tree.heading('Produit', text='Produit')
        self.tree.heading('Quantité', text='Quantité')
        self.tree.heading('Prix', text='Prix')
        self.tree.heading('Total', text='Total')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Load items
        cursor.execute('''
            SELECT p.name, si.quantity, si.price, (si.quantity * si.price) as total
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        ''', (self.sale_id,))

        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

        ttk.Button(self.top, text="Fermer", command=self.top.destroy).pack(pady=5)
