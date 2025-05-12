from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from abc import ABC, abstractmethod
import os
from django.conf import settings



class IPDFGenerator(ABC):
    @abstractmethod
    def generate_order_pdf(self,order, order_items):
        pass


class ReportLabPDFGenerator(IPDFGenerator):
    def generate_order_pdf(self,order,order_items):
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # PDF configuration
        # Header
        pdf.setTitle(f"Orden de Compra #{order.id}")
        
        # Title
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100,750, "AgroMerc - Orden de Compra")
        
        # Order information
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 700, f"ID de Orden: {order.id}")
        pdf.drawString(100,710,f"Fecha: {order.created_at.strftime('%d/%m/%Y %H:%M')}" )
        pdf.drawString(100, 690, f"Cliente: {order.user.fullname + ' '+ order.user.fullLastName}")
        pdf.drawString(100,670,f"Cédula: {order.user.idNumber}")
        
        # Order Details
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 630, "Detalles de la Orden")
        
        # Products table
        data = [
            ["Producto", "Cantidad", "Precio Unitario", "Precio Total"]
        ]
        for item in order_items:
            data.append([
                f"{item.product.productName} ({item.product.specificName})",
                str(item.quantity),
                f"${item.price:.2f}",
                f"${item.price * item.quantity:.2f}"
            ])
        
        table = Table(data,colWidths=[250, 80, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3A5A78")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#EEEEEE")),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        table.wrapOn(pdf, 50, 50)
        table.drawOn(pdf, 50, 500)
        
        # total and status
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(350, 450, f"Total: ${order.totalPrice:.2f}")
        
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 430, f"Estado: {'Pagado' if order.idPaid else 'Pendiente'}")
        
        
        # Footer
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawString(100, 30, "¡Gracias por su compra en AgroMerc!")
        
        pdf.showPage()
        pdf.save()
        
        buffer.seek(0)
        return buffer