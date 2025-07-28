from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os
from datetime import datetime
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)

class InvoiceGenerator:
    def __init__(self, business_info):
        self.business_info = business_info
        self.invoice_dir = 'invoices'
        os.makedirs(self.invoice_dir, exist_ok=True)
    
    def create_invoice(self, job_data, parts_used=None, labor_hours=2):
        """Generate a PDF invoice for a given job."""
        if parts_used is None:
            parts_used = []
            
        invoice_number = f"INV-{job_data['id']}-{datetime.now().strftime('%Y%m%d')}"
        filename = os.path.join(self.invoice_dir, f"{invoice_number}.pdf")
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph(f"<b>{self.business_info['name']}</b>", styles['Title']))
        story.append(Spacer(1, 12))
        
        business_info_text = f"""
        {self.business_info['address']}<br/>
        Phone: {self.business_info['phone']}<br/>
        Email: {self.business_info['email']}
        """
        story.append(Paragraph(business_info_text, styles['Normal']))
        story.append(Spacer(1, 24))
        
        invoice_info = f"""
        <b>Invoice #{invoice_number}</b><br/>
        Date: {datetime.now().strftime('%m/%d/%Y')}<br/>
        Service Date: {job_data['scheduled_date']}<br/>
        """
        story.append(Paragraph(invoice_info, styles['Normal']))
        story.append(Spacer(1, 12))
        
        customer_info = f"""
        <b>Bill To:</b><br/>
        {job_data['customer_name']}<br/>
        {job_data.get('customer_address', 'N/A')}<br/>
        {job_data.get('customer_phone', 'N/A')}
        """
        story.append(Paragraph(customer_info, styles['Normal']))
        story.append(Spacer(1, 24))
        
        data = [['Description', 'Quantity', 'Rate', 'Amount']]
        total = 0
        
        labor_cost = labor_hours * self.business_info['hourly_rate']
        data.append([
            f"Labor - {job_data['job_type'].title()}",
            f"{labor_hours} hrs",
            f"${self.business_info['hourly_rate']:.2f}",
            f"${labor_cost:.2f}"
        ])
        total += labor_cost
        
        for part in parts_used:
            part_total = part['quantity'] * part['unit_cost']
            data.append([
                part['name'],
                str(part['quantity']),
                f"${part['unit_cost']:.2f}",
                f"${part_total:.2f}"
            ])
            total += part_total
        
        data.append(['', '', 'Total:', f"<b>${total:.2f}</b>"])
        
        table = Table(data, colWidths=[3*72, 1*72, 1*72, 1*72])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0,1), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,1), (0,-1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 24))
        
        story.append(Paragraph("Payment due within 30 days. Thank you for your business!", styles['Normal']))
        
        doc.build(story)
        return filename, total
    
    def send_invoice(self, recipient_email, filename, job_data):
        """Send an invoice via email using SendGrid."""
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            print("SENDGRID_API_KEY not set. Cannot send email.")
            return False

        message = Mail(
            from_email=self.business_info['email'],
            to_emails=recipient_email,
            subject=f"Invoice #{os.path.basename(filename).replace('.pdf', '')} from {self.business_info['name']}",
            html_content=f"""
            <p>Dear {job_data['customer_name']},</p>
            <p>Please find attached your invoice for the recent HVAC service.</p>
            <p>Service Date: {job_data['scheduled_date']}</p>
            <p>Thank you for your business!</p>
            <p>
                <strong>{self.business_info['name']}</strong><br/>
                {self.business_info['phone']}<br/>
                {self.business_info['email']}
            </p>
            """
        )
        
        with open(filename, 'rb') as f:
            data = f.read()
            encoded_file = base64.b64encode(data).decode()
        
        attachment = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(filename)),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        message.attachment = attachment
        
        try:
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
