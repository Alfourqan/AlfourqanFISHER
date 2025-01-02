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
        # Title
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
        self.tree = ttk.Treeview(self.parent, columns=('ID', 'Date', 'Client', 'Total'),
                                show='headings')
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
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        sale_id = self.tree.item(item)['values'][0]
        dialog = SaleDetailsDialog(self.parent, self.db, sale_id)
        self.parent.wait_window(dialog.top)

class SaleDialog:
    def __init__(self, parent, db):
        self.parent = parent  # Store the parent window
        self.db = db
        self.top = tk.Toplevel(parent)
        self.setup_ui()

    def setup_ui(self):
        self.top.title("Nouvelle Vente")
        self.top.transient(self.parent)  # Make dialog modal
        self.top.grab_set()  # Make dialog modal

        # Window size and position
        window_width = 800
        window_height = 600

        # Get parent window position
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Calculate position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2

        # Set geometry
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Main container
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Customer selection
        customer_frame = ttk.LabelFrame(main_frame, text="Client")
        customer_frame.pack(fill=tk.X, pady=(0, 10))

        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=40)
        self.load_customers()
        self.customer_combo.pack(padx=10, pady=10)

        # Products frame
        products_frame = ttk.LabelFrame(main_frame, text="Ajouter un produit")
        products_frame.pack(fill=tk.X, pady=10)

        # Product selection - using grid for better control
        input_frame = ttk.Frame(products_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Product combobox
        ttk.Label(input_frame, text="Produit:").grid(row=0, column=0, padx=5, pady=5)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(input_frame, textvariable=self.product_var, width=40)
        self.load_products()
        self.product_combo.grid(row=0, column=1, padx=5, pady=5)

        # Quantity entry
        ttk.Label(input_frame, text="Quantité (kg):").grid(row=0, column=2, padx=5, pady=5)
        self.quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        # Add button
        ttk.Button(input_frame, text="Ajouter", command=self.add_product).grid(row=0, column=4, padx=5, pady=5)

        # Products list frame
        list_frame = ttk.LabelFrame(main_frame, text="Produits sélectionnés")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Products list
        self.products_tree = ttk.Treeview(list_frame, 
                                        columns=('Produit', 'Quantité', 'Prix', 'Total'),
                                        show='headings')
        self.products_tree.heading('Produit', text='Produit')
        self.products_tree.heading('Quantité', text='Quantité')
        self.products_tree.heading('Prix', text='Prix')
        self.products_tree.heading('Total', text='Total')

        # Configure column widths
        self.products_tree.column('Produit', width=300)
        self.products_tree.column('Quantité', width=100)
        self.products_tree.column('Prix', width=100)
        self.products_tree.column('Total', width=100)

        self.products_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Total frame
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X, pady=10)
        ttk.Label(total_frame, text="Total:", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="0.00 €")
        ttk.Label(total_frame, textvariable=self.total_var, font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, padx=5)

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.RIGHT)

    def load_customers(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM customers ORDER BY name')
        customers = [row[0] for row in cursor.fetchall()]
        self.customer_combo['values'] = customers

    def load_products(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT name FROM products WHERE stock > 0 ORDER BY name')
        products = [row[0] for row in cursor.fetchall()]
        self.product_combo['values'] = products

    def add_product(self):
        try:
            product = self.product_var.get()
            if not product:
                raise ValueError("Veuillez sélectionner un produit")

            quantity = float(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("La quantité doit être positive")

            cursor = self.db.conn.cursor()
            cursor.execute('SELECT price, stock FROM products WHERE name = ?', (product,))
            result = cursor.fetchone()

            if not result:
                raise ValueError("Produit non trouvé")

            price, stock = result

            if quantity > stock:
                raise ValueError(f"Stock insuffisant (disponible: {stock} kg)")

            total = price * quantity

            self.products_tree.insert('', 'end', values=(product, f"{quantity:.2f}", f"{price:.2f}", f"{total:.2f}"))

            # Update total
            current_total = float(self.total_var.get().replace('€', '').strip())
            self.total_var.set(f"{current_total + total:.2f} €")

            # Clear inputs
            self.product_var.set('')
            self.quantity_var.set('')

        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")

    def save(self):
        try:
            customer = self.customer_var.get()
            if not customer:
                raise ValueError("Veuillez sélectionner un client")

            if not self.products_tree.get_children():
                raise ValueError("Veuillez ajouter des produits à la vente")

            cursor = self.db.conn.cursor()

            # Get customer id
            cursor.execute('SELECT id FROM customers WHERE name = ?', (customer,))
            customer_id = cursor.fetchone()
            if not customer_id:
                raise ValueError("Client non trouvé")

            customer_id = customer_id[0]
            total = float(self.total_var.get().replace('€', '').strip())

            # Create sale
            cursor.execute('''
                INSERT INTO sales (date, customer_id, total)
                VALUES (?, ?, ?)
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer_id, total))

            sale_id = cursor.lastrowid

            # Add sale items
            for item in self.products_tree.get_children():
                values = self.products_tree.item(item)['values']
                product_name = values[0]
                quantity = float(values[1])
                price = float(values[2])

                cursor.execute('SELECT id FROM products WHERE name = ?', (product_name,))
                product_id = cursor.fetchone()[0]

                # Insert sale item
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
            messagebox.showinfo("Succès", "La vente a été enregistrée avec succès")
            self.top.destroy()

        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")

class SaleDetailsDialog:
    def __init__(self, parent, db, sale_id):
        self.parent = parent
        self.db = db
        self.sale_id = sale_id
        self.top = tk.Toplevel(parent)
        self.setup_ui()

    def setup_ui(self):
        self.top.title(f"Détails de la vente #{self.sale_id}")
        self.top.transient(self.parent)
        self.top.grab_set()

        # Center the dialog
        window_width = 500
        window_height = 400
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - window_width) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")

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
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(info_frame, text=f"Date: {sale[0]}", font=('Helvetica', 10)).pack()
        ttk.Label(info_frame, text=f"Client: {sale[1]}", font=('Helvetica', 10)).pack()
        ttk.Label(info_frame, text=f"Total: {sale[2]} €", font=('Helvetica', 10, 'bold')).pack()

        # Display items
        self.tree = ttk.Treeview(self.top, 
                                columns=('Produit', 'Quantité', 'Prix', 'Total'),
                                show='headings')
        self.tree.heading('Produit', text='Produit')
        self.tree.heading('Quantité', text='Quantité')
        self.tree.heading('Prix', text='Prix')
        self.tree.heading('Total', text='Total')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load items
        cursor.execute('''
            SELECT p.name, si.quantity, si.price, (si.quantity * si.price) as total
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        ''', (self.sale_id,))

        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=(
                row[0],
                f"{row[1]:.2f}",
                f"{row[2]:.2f} €",
                f"{row[3]:.2f} €"
            ))

        ttk.Button(self.top, text="Fermer", command=self.top.destroy).pack(pady=10)