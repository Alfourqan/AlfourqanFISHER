import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    """
    Gestionnaire de base de données SQLite pour l'application.
    Implémente le pattern Singleton pour garantir une seule instance de connexion.
    """
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_file = "poissonnerie.db"
            cls._instance.init_db()
        return cls._instance

    def init_db(self):
        """Initialise la base de données et crée les tables si elles n'existent pas"""
        create_tables = not os.path.exists(self.db_file)
        self.connect()
        if create_tables:
            self.create_tables()

    def connect(self):
        """Établit une connexion à la base de données SQLite"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_file, check_same_thread=False)
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._connection.execute("PRAGMA synchronous = OFF")
            self._connection.execute("PRAGMA cache_size = -4000")
            self._connection.execute("PRAGMA temp_store = MEMORY")
            self._connection.execute("PRAGMA mmap_size = 30000000000")
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @property
    def conn(self):
        """Retourne la connexion active à la base de données"""
        return self.connect()

    def create_tables(self):
        """Crée toutes les tables nécessaires dans la base de données"""
        cursor = self.conn.cursor()

        # Table des utilisateurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        ''')

        # Insertion de l'utilisateur admin par défaut
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash)
        VALUES (?, ?)
        ''', ('admin', generate_password_hash('admin123')))

        # Valider les changements
        self.conn.commit()

        # Table des produits
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

        # Table des catégories
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')

        # Table des clients
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        ''')

        # Table des fournisseurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
        ''')

        # Table des ventes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            customer_id INTEGER,
            total REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
        ''')

        # Table des détails des ventes
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
        """
        Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe.

        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe en clair

        Returns:
            dict: Informations de l'utilisateur si l'authentification réussit, None sinon
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            return {'id': user[0], 'username': user[1]}
        return None

    def execute(self, query, params=()):
        """
        Exécute une requête SQL avec des paramètres optionnels.

        Args:
            query (str): Requête SQL
            params (tuple): Paramètres de la requête

        Returns:
            sqlite3.Cursor: Curseur pour accéder aux résultats
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def backup_db(self):
        """Effectue une sauvegarde de la base de données"""
        import shutil
        from datetime import datetime
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_file = f"{backup_dir}/poissonnerie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.conn.commit()
        shutil.copy2(self.db_file, backup_file)
        
    def close(self):
        """Ferme la connexion à la base de données"""
        if self._connection:
            self.backup_db()
            self._connection.close()
            self._connection = None