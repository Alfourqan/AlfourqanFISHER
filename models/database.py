import sqlite3
import os
from datetime import datetime

class Database:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_file = "poissonnerie.db"
            cls._instance.init_db()
        return cls._instance

    def init_db(self):
        create_tables = not os.path.exists(self.db_file)
        self.connect()
        if create_tables:
            self.create_tables()

    def connect(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_file, check_same_thread=False)
            # Enable foreign key support
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    @property
    def conn(self):
        return self.connect()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Produits
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
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
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')

        # Clients
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        ''')

        # Fournisseurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        ''')

        # Ventes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            customer_id INTEGER,
            total REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
        ''')

        # Détails des ventes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
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

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None