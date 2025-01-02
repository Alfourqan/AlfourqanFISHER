import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database
from datetime import datetime

class CashierView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.setup_ui()
        self.cart = []
        self.total = 0.0

    def setup_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Products
        left_panel = ttk.Frame(self.main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Product search
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher produit:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        # Products list
        self.products_tree = ttk.Treeview(left_panel, 
                                        columns=('ID', 'Nom', 'Prix', 'Stock'),
                                        show='headings')
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Nom', text='Nom')
        self.products_tree.heading('Prix', text='Prix')
        self.products_tree.heading('Stock', text='Stock')
        
        self.products_tree.column('ID', width=50)
        self.products_tree.column('Nom', width=200)
        self.products_tree.column('Prix', width=100)
        self.products_tree.column('Stock', width=100)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        self.products_tree.bind('<Double-1>', self.add_to_cart)

        # Right panel - Cart
        right_panel = ttk.Frame(self.main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        # Client selection
        client_frame = ttk.Frame(right_panel)
        client_frame.pack(fill=tk.X, pady=5)
        ttk.Label(client_frame, text="Client:").pack(side=tk.LEFT)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(client_frame, textvariable=self.client_var)
        self.load_clients()
        self.client_combo.pack(side=tk.LEFT, padx=5)

        # Cart
        cart_frame = ttk.LabelFrame(right_panel, text="Panier", padding=5)
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cart_tree = ttk.Treeview(cart_frame, 
                                     columns=('Produit', 'Qté', 'Prix', 'Total'),
                                     show='headings')
        self.cart_tree.heading('Produit', text='Produit')
        self.cart_tree.heading('Qté', text='Qté')
        self.cart_tree.heading('Prix', text='Prix')
        self.cart_tree.heading('Total', text='Total')
        
        self.cart_tree.column('Produit', width=150)
        self.cart_tree.column('Qté', width=70)
        self.cart_tree.column('Prix', width=70)
        self.cart_tree.column('Total', width=70)
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        self.cart_tree.bind('<Double-1>', self.remove_from_cart)

        # Total
        total_frame = ttk.Frame(right_panel)
        total_frame.pack(fill=tk.X, pady=5)
        ttk.Label(total_frame, text="Total:", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="0.00 €", font=('Helvetica', 12, 'bold'))
        self.total_label.pack(side=tk.RIGHT)

        # Buttons
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Valider la vente", command=self.process_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.clear_cart).pack(side=tk.LEFT)

        # Load initial products
        self.load_products()

    def load_products(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, name, price, stock FROM products WHERE stock > 0')
        
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        for row in cursor.fetchall():
            self.products_tree.insert('', 'end', values=row)

    def load_clients(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM customers')
        clients = [row[0] for row in cursor.fetchall()]
        self.client_combo['values'] = clients

    def filter_products(self, *args):
        search_term = self.search_var.get().lower()
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, name, price, stock 
            FROM products 
            WHERE LOWER(name) LIKE ? AND stock > 0
        ''', (f'%{search_term}%',))
        
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        for row in cursor.fetchall():
            self.products_tree.insert('', 'end', values=row)

    def add_to_cart(self, event):
        selection = self.products_tree.selection()
        if not selection:
            return

        # Get product info
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        price = item['values'][2]
        available_stock = item['values'][3]

        # Ask for quantity
        dialog = QuantityDialog(self.parent, available_stock)
        self.parent.wait_window(dialog.top)
        
        if dialog.quantity is not None:
            quantity = dialog.quantity
            total = price * quantity
            
            # Add to cart
            self.cart_tree.insert('', 'end', values=(product_name, quantity, price, total))
            self.cart.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            })
            
            # Update total
            self.total += total
            self.total_label.config(text=f"{self.total:.2f} €")

    def remove_from_cart(self, event):
        selection = self.cart_tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Confirmation", "Voulez-vous retirer cet article du panier ?"):
            item = self.cart_tree.item(selection[0])
            total_item = item['values'][3]
            
            self.total -= total_item
            self.total_label.config(text=f"{self.total:.2f} €")
            
            self.cart_tree.delete(selection[0])
            # Remove from cart list - approximate match based on position
            if self.cart:
                self.cart.pop(self.cart_tree.index(selection[0]))

    def process_sale(self):
        if not self.cart:
            messagebox.showwarning("Attention", "Le panier est vide")
            return

        if not self.client_var.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un client")
            return

        try:
            cursor = self.db.conn.cursor()
            
            # Get client ID
            cursor.execute('SELECT id FROM customers WHERE name = ?', (self.client_var.get(),))
            customer_id = cursor.fetchone()[0]
            
            # Create sale
            cursor.execute('''
                INSERT INTO sales (date, customer_id, total)
                VALUES (?, ?, ?)
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer_id, self.total))
            
            sale_id = cursor.lastrowid
            
            # Add sale items and update stock
            for item in self.cart:
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, item['product_id'], item['quantity'], item['price']))
                
                cursor.execute('''
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE id = ?
                ''', (item['quantity'], item['product_id']))
            
            self.db.conn.commit()
            messagebox.showinfo("Succès", "Vente enregistrée avec succès")
            
            # Clear cart
            self.clear_cart()
            # Reload products
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.db.conn.rollback()

    def clear_cart(self):
        self.cart = []
        self.total = 0.0
        self.total_label.config(text="0.00 €")
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        self.client_var.set('')

class QuantityDialog:
    def __init__(self, parent, max_quantity):
        self.top = tk.Toplevel(parent)
        self.max_quantity = float(max_quantity)  # Convert to float when initializing
        self.quantity = None
        self.setup_ui()

    def setup_ui(self):
        self.top.title("Quantité")

        ttk.Label(self.top, text="Quantité (kg):").grid(row=0, column=0, padx=5, pady=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.quantity_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="OK", command=self.validate).grid(row=1, column=0, columnspan=2, pady=10)

    def validate(self):
        try:
            quantity = float(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("La quantité doit être positive")
            if quantity > self.max_quantity:
                raise ValueError(f"Stock disponible: {self.max_quantity} kg")

            self.quantity = quantity
            self.top.destroy()

        except ValueError as e:
            messagebox.showerror("Erreur", str(e))