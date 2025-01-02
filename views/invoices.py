import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database
from utils.pdf_generator import PDFGenerator
import os

class InvoicesView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.pdf_gen = PDFGenerator()
        self.setup_ui()
        self.load_invoices()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Gestion des Factures", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)

        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_invoices)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)

        # Invoices table
        self.tree = ttk.Treeview(self.parent, 
                                columns=('ID', 'Date', 'Client', 'Total', 'Status'),
                                show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Client', text='Client')
        self.tree.heading('Total', text='Total')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('ID', width=50)
        self.tree.column('Date', width=150)
        self.tree.column('Client', width=200)
        self.tree.column('Total', width=100)
        self.tree.column('Status', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Actions frame
        actions_frame = ttk.Frame(self.parent)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(actions_frame, text="Générer PDF", command=self.generate_pdf).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_frame, text="Voir détails", command=self.view_details).pack(side=tk.RIGHT, padx=5)

    def load_invoices(self):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.date, c.name, s.total, 
                   CASE WHEN s.id IN (SELECT sale_id FROM sale_items) THEN 'Complète' ELSE 'En attente' END as status
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            ORDER BY s.date DESC
        ''')
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def filter_invoices(self, *args):
        search_term = self.search_var.get().lower()
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.id, s.date, c.name, s.total,
                   CASE WHEN s.id IN (SELECT sale_id FROM sale_items) THEN 'Complète' ELSE 'En attente' END as status
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE LOWER(c.name) LIKE ?
            ORDER BY s.date DESC
        ''', (f'%{search_term}%',))
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def generate_pdf(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture")
            return

        sale_id = self.tree.item(selection[0])['values'][0]
        
        try:
            # Get sale data
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT s.*, c.name as customer_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                WHERE s.id = ?
            ''', (sale_id,))
            sale = cursor.fetchone()
            
            # Get sale items
            cursor.execute('''
                SELECT p.name as product_name, si.quantity, si.price
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                WHERE si.sale_id = ?
            ''', (sale_id,))
            items = cursor.fetchall()
            
            sale_data = {
                'id': sale[0],
                'date': sale[1],
                'customer_name': sale[4],
                'total': sale[3],
                'items': [
                    {
                        'product_name': item[0],
                        'quantity': item[1],
                        'price': item[2]
                    } for item in items
                ]
            }
            
            # Generate PDF
            filename = f"facture_{sale_id}.pdf"
            self.pdf_gen.generate_invoice(sale_data, filename)
            
            messagebox.showinfo("Succès", f"La facture a été générée: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def view_details(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture")
            return

        sale_id = self.tree.item(selection[0])['values'][0]
        dialog = InvoiceDetailsDialog(self.parent, self.db, sale_id)
        self.parent.wait_window(dialog.top)

class InvoiceDetailsDialog:
    def __init__(self, parent, db, sale_id):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.sale_id = sale_id
        self.setup_ui()

    def setup_ui(self):
        self.top.title(f"Détails de la facture #{self.sale_id}")
        self.top.geometry("500x400")

        # Load invoice details
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT s.date, c.name, s.total 
            FROM sales s 
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        ''', (self.sale_id,))
        sale = cursor.fetchone()

        # Display invoice info
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
