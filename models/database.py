import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    @property
    def conn(self):
        return self.connect()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        ''')

        # Insert default admin user if not exists
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash)
        VALUES (?, ?)
        ''', ('admin', generate_password_hash('admin123')))

        # Commit the changes
        self.conn.commit()

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

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            return {'id': user[0], 'username': user[1]}
        return None

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None