import tkinter as tk
from tkinter import ttk, messagebox
from models.database import Database

class CategoriesView:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Gestion des Catégories", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="+ Nouvelle Catégorie", command=self.add_category).pack(side=tk.RIGHT)

        # Categories list
        self.tree = ttk.Treeview(self.parent, columns=('ID', 'Nom'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nom', text='Nom')
        
        self.tree.column('ID', width=50)
        self.tree.column('Nom', width=300)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind double click for editing
        self.tree.bind('<Double-1>', self.edit_category)

    def load_categories(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM categories')
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def add_category(self):
        dialog = CategoryDialog(self.parent, self.db)
        self.parent.wait_window(dialog.top)
        self.load_categories()

    def edit_category(self, event):
        item = self.tree.selection()[0]
        category_id = self.tree.item(item)['values'][0]
        dialog = CategoryDialog(self.parent, self.db, category_id)
        self.parent.wait_window(dialog.top)
        self.load_categories()

class CategoryDialog:
    def __init__(self, parent, db, category_id=None):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.category_id = category_id
        self.setup_ui()
        if category_id:
            self.load_category()

    def setup_ui(self):
        self.top.title("Nouvelle Catégorie" if not self.category_id else "Modifier Catégorie")
        
        # Name
        ttk.Label(self.top, text="Nom:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.top.destroy).pack(side=tk.LEFT, padx=5)
        if self.category_id:
            ttk.Button(btn_frame, text="Supprimer", command=self.delete).pack(side=tk.LEFT, padx=5)

    def load_category(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE id = ?', (self.category_id,))
        category = cursor.fetchone()
        self.name_var.set(category[1])

    def save(self):
        try:
            name = self.name_var.get()

            cursor = self.db.conn.cursor()
            if self.category_id:
                cursor.execute('''
                    UPDATE categories 
                    SET name = ?
                    WHERE id = ?
                ''', (name, self.category_id))
            else:
                cursor.execute('''
                    INSERT INTO categories (name)
                    VALUES (?)
                ''', (name,))
            
            self.db.conn.commit()
            self.top.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def delete(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette catégorie ?"):
            try:
                cursor = self.db.conn.cursor()
                cursor.execute('DELETE FROM categories WHERE id = ?', (self.category_id,))
                self.db.conn.commit()
                self.top.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
