"""
Payroll PDF Generator
Generate individual payslips and compile them into a ZIP file
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from datetime import datetime
from decimal import Decimal
from typing import List
import io
import zipfile
import os
from pathlib import Path

from modules.payroll.models import Payroll, PayrollEntry


class PayrollPDFGenerator:
    """Generate payroll PDFs for individual employees"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.logo_path = Path(__file__).parent.parent.parent / "static" / "inara-logo-pdf.png"
        
    def generate_payslip(self, payroll: Payroll, entry: PayrollEntry) -> bytes:
        """Generate a single payslip PDF for an employee"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Add logo if exists
        if self.logo_path.exists():
            logo = Image(str(self.logo_path), width=1.5*inch, height=1.5*inch)
            logo._restrictSize(1.5*inch, 1.5*inch)
            story.append(logo)
            story.append(Spacer(1, 0.3*inch))
        
        # Title
        story.append(Paragraph("INARA - International Network for Aid, Relief and Assistance", title_style))
        story.append(Paragraph("PAYSLIP", self.styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        # Payroll Period
        period_text = f"<b>Period:</b> {payroll.year}-{payroll.month:02d} | <b>Payment Date:</b> {payroll.payment_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(period_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Employee Information
        emp_data = [
            ['Employee Information', ''],
            ['Employee Number:', entry.employee_number],
            ['Name:', f"{entry.first_name} {entry.last_name}"],
            ['Position:', entry.position or 'N/A'],
            ['Department:', entry.department or 'N/A'],
        ]
        
        emp_table = Table(emp_data, colWidths=[2.5*inch, 4*inch])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Salary Breakdown
        salary_data = [
            ['Description', 'Amount'],
            ['Basic Salary', f"{entry.currency} {entry.basic_salary:,.2f}"],
            ['Allowances', f"{entry.currency} {entry.allowances:,.2f}"],
            ['Gross Salary', f"{entry.currency} {entry.gross_salary:,.2f}"],
            ['Deductions', f"{entry.currency} {entry.deductions:,.2f}"],
            ['NET SALARY', f"{entry.currency} {entry.net_salary:,.2f}"],
        ]
        
        salary_table = Table(salary_data, colWidths=[4*inch, 2.5*inch])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 4), colors.lightgrey),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#dcfce7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 5), (-1, 5), 14),
        ]))
        story.append(salary_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = """
        <para align=center>
        <font size=8>
        This is a computer-generated document. No signature is required.<br/>
        For any queries, please contact HR Department.<br/>
        <b>INARA - International Network for Aid, Relief and Assistance</b><br/>
        Generated on {date}
        </font>
        </para>
        """.format(date=datetime.utcnow().strftime('%B %d, %Y %I:%M %p'))
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_payroll_zip(self, payroll: Payroll, entries: List[PayrollEntry]) -> bytes:
        """Generate a ZIP file containing all payslips"""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for entry in entries:
                # Generate payslip PDF
                pdf_bytes = self.generate_payslip(payroll, entry)
                
                # Create filename
                filename = f"{entry.employee_number}_{entry.first_name}_{entry.last_name}_payslip_{payroll.year}_{payroll.month:02d}.pdf"
                filename = filename.replace(" ", "_")
                
                # Add to ZIP
                zip_file.writestr(filename, pdf_bytes)
            
            # Add summary file
            summary_pdf = self.generate_payroll_summary(payroll, entries)
            zip_file.writestr(f"PAYROLL_SUMMARY_{payroll.year}_{payroll.month:02d}.pdf", summary_pdf)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def generate_payroll_summary(self, payroll: Payroll, entries: List[PayrollEntry]) -> bytes:
        """Generate a summary PDF for the entire payroll batch"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Title
        if self.logo_path.exists():
            logo = Image(str(self.logo_path), width=1.5*inch, height=1.5*inch)
            logo._restrictSize(1.5*inch, 1.5*inch)
            story.append(logo)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("PAYROLL SUMMARY", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Period
        period_text = f"<b>Period:</b> {payroll.year}-{payroll.month:02d} | <b>Payment Date:</b> {payroll.payment_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(period_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary table
        summary_data = [
            ['Total Employees', str(len(entries))],
            ['Total Basic Salary', f"{entries[0].currency if entries else 'USD'} {payroll.total_basic_salary:,.2f}"],
            ['Total Allowances', f"{entries[0].currency if entries else 'USD'} {payroll.total_allowances:,.2f}"],
            ['Total Gross Salary', f"{entries[0].currency if entries else 'USD'} {payroll.total_gross_salary:,.2f}"],
            ['Total Deductions', f"{entries[0].currency if entries else 'USD'} {payroll.total_deductions:,.2f}"],
            ['TOTAL NET PAYABLE', f"{entries[0].currency if entries else 'USD'} {payroll.total_net_salary:,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#dcfce7')),
            ('FONTSIZE', (0, 5), (-1, 5), 14),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Employee list
        story.append(Paragraph("<b>Employee Breakdown:</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        employee_data = [['#', 'Emp No.', 'Name', 'Position', 'Net Salary']]
        for idx, entry in enumerate(entries, 1):
            employee_data.append([
                str(idx),
                entry.employee_number,
                f"{entry.first_name} {entry.last_name}",
                entry.position or 'N/A',
                f"{entry.currency} {entry.net_salary:,.2f}"
            ])
        
        employee_table = Table(employee_data, colWidths=[0.4*inch, 0.8*inch, 2*inch, 1.8*inch, 1.2*inch])
        employee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(employee_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
pdf_generator = PayrollPDFGenerator()
