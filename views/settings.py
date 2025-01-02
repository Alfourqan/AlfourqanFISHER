import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os

class SettingsView:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "settings.json"
        self.load_settings()
        self.setup_ui()

    def setup_ui(self):
        # Title
        title_frame = ttk.Frame(self.parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(title_frame, text="Paramètres", font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)

        # Settings container
        settings_frame = ttk.LabelFrame(self.parent, text="Configuration", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Company Information
        company_frame = ttk.LabelFrame(settings_frame, text="Information de l'entreprise", padding=5)
        company_frame.pack(fill=tk.X, pady=5)

        ttk.Label(company_frame, text="Nom de l'entreprise:").grid(row=0, column=0, padx=5, pady=5)
        self.company_name_var = tk.StringVar(value=self.settings.get('company_name', ''))
        ttk.Entry(company_frame, textvariable=self.company_name_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(company_frame, text="Adresse:").grid(row=1, column=0, padx=5, pady=5)
        self.address_var = tk.StringVar(value=self.settings.get('address', ''))
        ttk.Entry(company_frame, textvariable=self.address_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(company_frame, text="Téléphone:").grid(row=2, column=0, padx=5, pady=5)
        self.phone_var = tk.StringVar(value=self.settings.get('phone', ''))
        ttk.Entry(company_frame, textvariable=self.phone_var).grid(row=2, column=1, padx=5, pady=5)

        # PDF Settings
        pdf_frame = ttk.LabelFrame(settings_frame, text="Paramètres PDF", padding=5)
        pdf_frame.pack(fill=tk.X, pady=5)

        ttk.Label(pdf_frame, text="Dossier des rapports:").grid(row=0, column=0, padx=5, pady=5)
        self.reports_folder_var = tk.StringVar(value=self.settings.get('reports_folder', 'rapports'))
        ttk.Entry(pdf_frame, textvariable=self.reports_folder_var).grid(row=0, column=1, padx=5, pady=5)

        # Display Settings
        display_frame = ttk.LabelFrame(settings_frame, text="Affichage", padding=5)
        display_frame.pack(fill=tk.X, pady=5)

        ttk.Label(display_frame, text="Thème:").grid(row=0, column=0, padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'Clair'))
        ttk.Combobox(display_frame, textvariable=self.theme_var, 
                     values=['Clair', 'Sombre']).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(display_frame, text="Taille de police:").grid(row=1, column=0, padx=5, pady=5)
        self.font_size_var = tk.StringVar(value=self.settings.get('font_size', '12'))
        ttk.Combobox(display_frame, textvariable=self.font_size_var,
                     values=['10', '11', '12', '13', '14']).grid(row=1, column=1, padx=5, pady=5)

        # Backup Settings
        backup_frame = ttk.LabelFrame(settings_frame, text="Sauvegarde", padding=5)
        backup_frame.pack(fill=tk.X, pady=5)

        ttk.Label(backup_frame, text="Dossier de sauvegarde:").grid(row=0, column=0, padx=5, pady=5)
        self.backup_folder_var = tk.StringVar(value=self.settings.get('backup_folder', 'backup'))
        ttk.Entry(backup_frame, textvariable=self.backup_folder_var).grid(row=0, column=1, padx=5, pady=5)

        self.auto_backup_var = tk.BooleanVar(value=self.settings.get('auto_backup', True))
        ttk.Checkbutton(backup_frame, text="Sauvegarde automatique", 
                        variable=self.auto_backup_var).grid(row=1, column=0, columnspan=2, pady=5)

        # Actions
        actions_frame = ttk.Frame(settings_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        ttk.Button(actions_frame, text="Sauvegarder", 
                   command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_frame, text="Réinitialiser", 
                   command=self.reset_settings).pack(side=tk.RIGHT, padx=5)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.get_default_settings()
        except Exception:
            self.settings = self.get_default_settings()

    def get_default_settings(self):
        return {
            'company_name': 'AL FOURQANE',
            'address': '',
            'phone': '',
            'reports_folder': 'rapports',
            'backup_folder': 'backup',
            'theme': 'Clair',
            'font_size': '12',
            'auto_backup': True
        }

    def save_settings(self):
        try:
            settings = {
                'company_name': self.company_name_var.get(),
                'address': self.address_var.get(),
                'phone': self.phone_var.get(),
                'reports_folder': self.reports_folder_var.get(),
                'backup_folder': self.backup_folder_var.get(),
                'theme': self.theme_var.get(),
                'font_size': self.font_size_var.get(),
                'auto_backup': self.auto_backup_var.get()
            }

            # Create necessary directories
            os.makedirs(settings['reports_folder'], exist_ok=True)
            os.makedirs(settings['backup_folder'], exist_ok=True)

            # Save settings to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)

            self.settings = settings
            messagebox.showinfo("Succès", "Paramètres sauvegardés avec succès")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde des paramètres: {str(e)}")

    def reset_settings(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous réinitialiser tous les paramètres ?"):
            self.settings = self.get_default_settings()
            self.company_name_var.set(self.settings['company_name'])
            self.address_var.set(self.settings['address'])
            self.phone_var.set(self.settings['phone'])
            self.reports_folder_var.set(self.settings['reports_folder'])
            self.backup_folder_var.set(self.settings['backup_folder'])
            self.theme_var.set(self.settings['theme'])
            self.font_size_var.set(self.settings['font_size'])
            self.auto_backup_var.set(self.settings['auto_backup'])
