import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database

class CustomersView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Gestion des Clients", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="+ Nouveau Client", command=self.add_customer).pack(side=tk.RIGHT)

        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_customers)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        # Customers table
        self.tree = ttk.Treeview(self.parent, columns=('ID', 'Nom', 'Téléphone', 'Adresse'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nom', text='Nom')
        self.tree.heading('Téléphone', text='Téléphone')
        self.tree.heading('Adresse', text='Adresse')

        self.tree.column('ID', width=50)
        self.tree.column('Nom', width=200)
        self.tree.column('Téléphone', width=150)
        self.tree.column('Adresse', width=300)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bind double click for editing
        self.tree.bind('<Double-1>', self.edit_customer)

    def load_customers(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers')

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in cursor.fetchall():
            row_data = dict(row)
            self.tree.insert('', 'end', values=(
                row_data['id'],
                row_data['name'],
                row_data['phone'],
                row_data['address']
            ))

    def filter_customers(self, *args):
        search_term = self.search_var.get().lower()
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE LOWER(name) LIKE ?', (f'%{search_term}%',))

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in cursor.fetchall():
            row_data = dict(row)
            self.tree.insert('', 'end', values=(
                row_data['id'],
                row_data['name'],
                row_data['phone'],
                row_data['address']
            ))

    def add_customer(self):
        dialog = CustomerDialog(self.parent, self.db)
        self.parent.wait_window(dialog.top)
        self.load_customers()

    def edit_customer(self, event):
        item = self.tree.selection()[0]
        customer_id = self.tree.item(item)['values'][0]
        dialog = CustomerDialog(self.parent, self.db, customer_id)
        self.parent.wait_window(dialog.top)
        self.load_customers()

class CustomerDialog:
    def __init__(self, parent, db, customer_id=None):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.customer_id = customer_id
        self.setup_ui()
        if customer_id:
            self.load_customer()

    def setup_ui(self):
        self.top.title("Nouveau Client" if not self.customer_id else "Modifier Client")

        # Name
        ttk.Label(self.top, text="Nom:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        # Phone
        ttk.Label(self.top, text="Téléphone:").grid(row=1, column=0, padx=5, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.phone_var).grid(row=1, column=1, padx=5, pady=5)

        # Address
        ttk.Label(self.top, text="Adresse:").grid(row=2, column=0, padx=5, pady=5)
        self.address_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.address_var).grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.LEFT, padx=5)
        if self.customer_id:
            ttk.Button(btn_frame, text="Supprimer", command=self.delete).pack(side=tk.LEFT, padx=5)

    def load_customer(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (self.customer_id,))
        customer = cursor.fetchone()
        customer_data = dict(customer)

        self.name_var.set(customer_data['name'])
        self.phone_var.set(customer_data['phone'])
        self.address_var.set(customer_data['address'])

    def save(self):
        try:
            name = self.name_var.get()
            phone = self.phone_var.get()
            address = self.address_var.get()

            cursor = self.db.conn.cursor()
            if self.customer_id:
                cursor.execute('''
                    UPDATE customers 
                    SET name = ?, phone = ?, address = ?
                    WHERE id = ?
                ''', (name, phone, address, self.customer_id))
            else:
                cursor.execute('''
                    INSERT INTO customers (name, phone, address)
                    VALUES (?, ?, ?)
                ''', (name, phone, address))

            self.db.conn.commit()
            self.top.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce client ?"):
            try:
                cursor = self.db.conn.cursor()
                cursor.execute('DELETE FROM customers WHERE id = ?', (self.customer_id,))
                self.db.conn.commit()
                self.top.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))