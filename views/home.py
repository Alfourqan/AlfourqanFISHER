import tkinter as tk
from tkinter import ttk

class HomeView:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Container principal centré
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        # Logo et titre
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=30)
        
        ttk.Label(
            title_frame,
            text="🐟 AL FOURQANE",
            font=('Helvetica', 38, 'bold'),
            foreground='#3b82f6'
        ).pack(anchor=tk.CENTER)
        
        ttk.Label(
            title_frame,
            text="Gestion de Poissonnerie",
            font=('Helvetica', 24),
            foreground='white'
        ).pack(anchor=tk.CENTER)

        # Description
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=30)
        
        description = """
        Bienvenue dans votre application de gestion de poissonnerie.
        
        Cette application vous permet de :
        • Gérer votre inventaire de produits
        • Suivre vos ventes et factures
        • Gérer vos clients et fournisseurs
        • Générer des rapports détaillés
        """
        
        ttk.Label(
            desc_frame,
            text=description,
            font=('Helvetica', 14),
            foreground='white',
            justify=tk.CENTER
        ).pack(anchor=tk.CENTER)

        # Informations de contact
        contact_frame = ttk.Frame(main_frame)
        contact_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(
            contact_frame,
            text="Pour toute assistance, contactez le support technique",
            font=('Helvetica', 12),
            foreground='white'
        ).pack(anchor=tk.CENTER)
