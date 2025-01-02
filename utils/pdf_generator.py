from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_invoice(self, sale_data, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []

        # Header
        elements.append(Paragraph("AL FOURQANE - Poissonnerie", self.styles['Heading1']))
        elements.append(Paragraph(f"Facture #{sale_data['id']}", self.styles['Heading2']))
        elements.append(Paragraph(f"Date: {sale_data['date']}", self.styles['Normal']))
        elements.append(Paragraph(f"Client: {sale_data['customer_name']}", self.styles['Normal']))

        # Table data
        data = [['Produit', 'Quantité', 'Prix unitaire', 'Total']]
        for item in sale_data['items']:
            data.append([
                item['product_name'],
                f"{item['quantity']} kg",
                f"{item['price']} €",
                f"{item['quantity'] * item['price']} €"
            ])

        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

        # Total
        elements.append(Paragraph(f"Total: {sale_data['total']} €", self.styles['Heading2']))

        # Build PDF
        doc.build(elements)

    def generate_daily_report(self, report_data, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []

        # Header
        elements.append(Paragraph("Rapport Journalier", self.styles['Heading1']))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", self.styles['Normal']))

        # Sales summary
        elements.append(Paragraph("Résumé des ventes", self.styles['Heading2']))
        data = [['Produit', 'Quantité vendue', 'Chiffre d\'affaires']]
        for item in report_data['sales_summary']:
            data.append([
                item['product_name'],
                f"{item['quantity']} kg",
                f"{item['revenue']} €"
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

        # Financial summary
        elements.append(Paragraph("Résumé financier", self.styles['Heading2']))
        financial_data = [
            ['Total des ventes', f"{report_data['total_sales']} €"],
            ['Nombre de transactions', str(report_data['transaction_count'])],
            ['Panier moyen', f"{report_data['average_basket']} €"]
        ]

        financial_table = Table(financial_data)
        financial_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.beige)
        ]))

        elements.append(financial_table)

        # Build PDF
        doc.build(elements)
