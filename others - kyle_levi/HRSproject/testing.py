from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


def create_pdf_report(table_data, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Create a table from the data
    table = Table(table_data)

    # Define style for the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Apply style to the table
    table.setStyle(style)

    # Add the table to the elements
    elements.append(table)

    # Build the PDF document
    doc.build(elements)

# Example usage:
table_data = [
    ["ID", "Name", "Age"],
    [1, "John Doe", 30],
    [2, "Jane Smith", 25],
    [3, "Bob Johnson", 40]
]

create_pdf_report(table_data, "report.pdf")
