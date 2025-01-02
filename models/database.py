import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_file = "poissonnerie.db"
        self.conn = None
        self.init_db()

    def init_db(self):
        create_tables = True
        if os.path.exists(self.db_file):
            create_tables = False
            
        self.conn = sqlite3.connect(self.db_file)
        if create_tables:
            self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Produits
        cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock REAL NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')

        # Catégories
        cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')

        # Clients
        cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        ''')

        # Fournisseurs
        cursor.execute('''
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        ''')

        # Ventes
        cursor.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            customer_id INTEGER,
            total REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
        ''')

        # Détails des ventes
        cursor.execute('''
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY,
            sale_id INTEGER,
            product_id INTEGER,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')

        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
