import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database
from utils.pdf_generator import PDFGenerator
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class ReportsView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.pdf_gen = PDFGenerator()
        self.setup_ui()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Rapports", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)

        # Report types
        reports_frame = ttk.LabelFrame(self.parent, text="Types de rapports", padding=10)
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Daily sales report
        daily_frame = ttk.Frame(reports_frame)
        daily_frame.pack(fill=tk.X, pady=5)
        ttk.Label(daily_frame, text="Rapport journalier:").pack(side=tk.LEFT)
        self.daily_date = ttk.Entry(daily_frame, width=10)
        self.daily_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.daily_date.pack(side=tk.LEFT, padx=5)
        ttk.Button(daily_frame, text="Générer", command=self.generate_daily_report).pack(side=tk.LEFT)

        # Monthly sales report
        monthly_frame = ttk.Frame(reports_frame)
        monthly_frame.pack(fill=tk.X, pady=5)
        ttk.Label(monthly_frame, text="Rapport mensuel:").pack(side=tk.LEFT)
        self.month_var = tk.StringVar()
        months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        month_combo = ttk.Combobox(monthly_frame, textvariable=self.month_var, values=months)
        month_combo.set(months[datetime.now().month - 1])
        month_combo.pack(side=tk.LEFT, padx=5)
        
        self.year_var = tk.StringVar()
        year_combo = ttk.Combobox(monthly_frame, textvariable=self.year_var, 
                                 values=[str(y) for y in range(2020, datetime.now().year + 1)])
        year_combo.set(str(datetime.now().year))
        year_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(monthly_frame, text="Générer", command=self.generate_monthly_report).pack(side=tk.LEFT)

        # Stock report
        stock_frame = ttk.Frame(reports_frame)
        stock_frame.pack(fill=tk.X, pady=5)
        ttk.Label(stock_frame, text="Rapport de stock:").pack(side=tk.LEFT)
        ttk.Button(stock_frame, text="Générer", command=self.generate_stock_report).pack(side=tk.LEFT, padx=5)

        # Preview frame
        preview_frame = ttk.LabelFrame(self.parent, text="Aperçu", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_tree = ttk.Treeview(preview_frame, show='headings')
        self.preview_tree.pack(fill=tk.BOTH, expand=True)

    def generate_daily_report(self):
        try:
            date_str = self.daily_date.get()
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            cursor = self.db.conn.cursor()
            
            # Get sales data
            cursor.execute('''
                SELECT p.name, SUM(si.quantity) as quantity, SUM(si.quantity * si.price) as revenue
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.date) = ?
                GROUP BY p.id, p.name
                ORDER BY revenue DESC
            ''', (date_str,))
            
            sales_data = cursor.fetchall()
            
            # Get total sales and transaction count
            cursor.execute('''
                SELECT COUNT(*) as transaction_count, SUM(total) as total_sales
                FROM sales
                WHERE DATE(date) = ?
            ''', (date_str,))
            
            summary = cursor.fetchone()
            transaction_count = summary[0]
            total_sales = summary[1] or 0
            average_basket = total_sales / transaction_count if transaction_count > 0 else 0
            
            report_data = {
                'sales_summary': [
                    {
                        'product_name': row[0],
                        'quantity': row[1],
                        'revenue': row[2]
                    } for row in sales_data
                ],
                'transaction_count': transaction_count,
                'total_sales': total_sales,
                'average_basket': average_basket
            }
            
            # Generate PDF
            filename = f"rapport_journalier_{date_str}.pdf"
            self.pdf_gen.generate_daily_report(report_data, filename)
            
            # Update preview
            self.preview_tree['columns'] = ('Produit', 'Quantité', 'CA')
            for col in self.preview_tree['columns']:
                self.preview_tree.heading(col, text=col)
            
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
                
            for row in sales_data:
                self.preview_tree.insert('', 'end', values=(row[0], f"{row[1]} kg", f"{row[2]} €"))
            
            messagebox.showinfo("Succès", f"Rapport généré: {filename}")
            
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide (YYYY-MM-DD)")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def generate_monthly_report(self):
        try:
            months = {
                'Janvier': 1, 'Février': 2, 'Mars': 3, 'Avril': 4,
                'Mai': 5, 'Juin': 6, 'Juillet': 7, 'Août': 8,
                'Septembre': 9, 'Octobre': 10, 'Novembre': 11, 'Décembre': 12
            }
            
            month = months[self.month_var.get()]
            year = int(self.year_var.get())
            
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(s.date) as sale_date,
                    COUNT(*) as transactions,
                    SUM(s.total) as daily_total
                FROM sales s
                WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
                GROUP BY DATE(s.date)
                ORDER BY sale_date
            ''', (f"{month:02d}", str(year)))
            
            data = cursor.fetchall()
            
            # Update preview
            self.preview_tree['columns'] = ('Date', 'Transactions', 'Total')
            for col in self.preview_tree['columns']:
                self.preview_tree.heading(col, text=col)
            
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
                
            for row in data:
                self.preview_tree.insert('', 'end', values=(row[0], row[1], f"{row[2]} €"))
            
            # Generate PDF report...
            filename = f"rapport_mensuel_{year}_{month:02d}.pdf"
            messagebox.showinfo("Succès", f"Rapport généré: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def generate_stock_report(self):
        try:
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
                SELECT p.name, p.stock, c.name as category, p.price
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY c.name, p.name
            ''')
            
            data = cursor.fetchall()
            
            # Update preview
            self.preview_tree['columns'] = ('Produit', 'Stock', 'Catégorie', 'Prix')
            for col in self.preview_tree['columns']:
                self.preview_tree.heading(col, text=col)
            
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
                
            for row in data:
                self.preview_tree.insert('', 'end', values=(row[0], f"{row[1]} kg", row[2], f"{row[3]} €"))
            
            # Generate PDF report...
            filename = f"rapport_stock_{datetime.now().strftime('%Y%m%d')}.pdf"
            messagebox.showinfo("Succès", f"Rapport généré: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
