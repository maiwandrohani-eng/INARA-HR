"""
PDF Generation Utilities
Helper functions for generating PDF documents
"""

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any


class OrgChartBox(Flowable):
    """Custom flowable for drawing organization chart boxes"""
    
    def __init__(self, employees_data, width, height):
        Flowable.__init__(self)
        self.employees = employees_data
        self.width = width
        self.height = height
        
    def draw(self):
        """Draw the organization chart with boxes and lines"""
        # Build hierarchy
        employee_dict = {emp['id']: emp for emp in self.employees}
        roots = [emp for emp in self.employees if not emp.get('manager_id')]
        
        # Chart dimensions
        box_width = 140
        box_height = 50
        h_spacing = 20
        v_spacing = 40
        start_y = self.height - 50
        
        # Calculate positions for each level
        levels = []
        
        def get_level(emp, level=0):
            if level >= len(levels):
                levels.append([])
            levels[level].append(emp)
            
            # Get direct reports
            reports = [e for e in self.employees if e.get('manager_id') == emp['id']]
            for report in reports:
                get_level(report, level + 1)
        
        # Build levels starting from roots
        for root in roots:
            get_level(root)
        
        # Draw each level
        positions = {}  # Store box positions for drawing lines
        
        for level_idx, level_employees in enumerate(levels):
            y = start_y - (level_idx * (box_height + v_spacing))
            num_boxes = len(level_employees)
            total_width = (num_boxes * box_width) + ((num_boxes - 1) * h_spacing)
            start_x = (self.width - total_width) / 2
            
            for emp_idx, emp in enumerate(level_employees):
                x = start_x + (emp_idx * (box_width + h_spacing))
                positions[emp['id']] = (x + box_width/2, y)
                
                # Draw box
                self.canv.setFillColor(colors.HexColor('#FFF5F7'))
                self.canv.setStrokeColor(colors.HexColor('#D91C5C'))
                self.canv.setLineWidth(1.5)
                self.canv.rect(x, y - box_height, box_width, box_height, fill=1)
                
                # Draw text
                self.canv.setFillColor(colors.black)
                self.canv.setFont("Helvetica-Bold", 9)
                name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}"
                # Center text
                text_width = self.canv.stringWidth(name, "Helvetica-Bold", 9)
                self.canv.drawString(x + (box_width - text_width)/2, y - 15, name)
                
                self.canv.setFont("Helvetica", 7)
                position = emp.get('position', {}).get('title', 'N/A') if isinstance(emp.get('position'), dict) else 'N/A'
                text_width = self.canv.stringWidth(position, "Helvetica", 7)
                self.canv.drawString(x + (box_width - text_width)/2, y - 27, position)
                
                dept = emp.get('department', {}).get('name', '') if isinstance(emp.get('department'), dict) else ''
                if dept:
                    text_width = self.canv.stringWidth(dept, "Helvetica", 7)
                    self.canv.drawString(x + (box_width - text_width)/2, y - 38, dept)
        
        # Draw connecting lines
        self.canv.setStrokeColor(colors.HexColor('#D91C5C'))
        self.canv.setLineWidth(1)
        
        for emp in self.employees:
            if emp['id'] in positions and emp.get('manager_id') and emp['manager_id'] in positions:
                # Draw line from manager to employee
                manager_pos = positions[emp['manager_id']]
                emp_pos = positions[emp['id']]
                
                # Vertical line from manager
                self.canv.line(manager_pos[0], manager_pos[1] - box_height, 
                             manager_pos[0], manager_pos[1] - box_height - v_spacing/2)
                
                # Horizontal line
                self.canv.line(manager_pos[0], manager_pos[1] - box_height - v_spacing/2,
                             emp_pos[0], manager_pos[1] - box_height - v_spacing/2)
                
                # Vertical line to employee
                self.canv.line(emp_pos[0], manager_pos[1] - box_height - v_spacing/2,
                             emp_pos[0], emp_pos[1])


def create_organization_chart_pdf(employees: List[Dict[str, Any]]) -> BytesIO:
    """
    Generate PDF for organization chart with visual org chart style
    
    Args:
        employees: List of employee dictionaries with hierarchy
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    elements.append(Paragraph("International Network for Aid, Relief and Assistance", title_style))
    elements.append(Paragraph("Organizational Structure", ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=20
    )))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Add the org chart
    page_width = landscape(A4)[0] - 60  # minus margins
    page_height = landscape(A4)[1] - 150  # minus margins and title
    
    org_chart = OrgChartBox(employees, page_width, page_height)
    elements.append(org_chart)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_leave_request_pdf(leave_request: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for leave request
    
    Args:
        leave_request: Leave request dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    elements.append(Paragraph("Leave Request", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Request details
    data = [
        ['Request ID:', leave_request.get('id', 'N/A')],
        ['Employee:', f"{leave_request.get('employee', {}).get('first_name', '')} {leave_request.get('employee', {}).get('last_name', '')}"],
        ['Leave Type:', leave_request.get('leave_type', 'N/A').replace('_', ' ').title()],
        ['Start Date:', leave_request.get('start_date', 'N/A')],
        ['End Date:', leave_request.get('end_date', 'N/A')],
        ['Total Days:', str(leave_request.get('total_days', 'N/A'))],
        ['Status:', leave_request.get('status', 'N/A').upper()],
        ['Applied On:', leave_request.get('created_at', 'N/A')[:10] if leave_request.get('created_at') else 'N/A'],
    ]
    
    if leave_request.get('approved_by'):
        data.append(['Approved By:', f"{leave_request.get('approved_by', {}).get('first_name', '')} {leave_request.get('approved_by', {}).get('last_name', '')}"])
    
    if leave_request.get('approved_at'):
        data.append(['Approved On:', leave_request.get('approved_at', 'N/A')[:10]])
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(table)
    
    # Reason
    if leave_request.get('reason'):
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Reason:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(leave_request.get('reason', ''), styles['Normal']))
    
    # Notes
    if leave_request.get('notes'):
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Notes:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(leave_request.get('notes', ''), styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_timesheet_pdf(timesheet: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for timesheet
    
    Args:
        timesheet: Timesheet dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    elements.append(Paragraph("Timesheet", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Employee details
    data = [
        ['Employee:', f"{timesheet.get('employee', {}).get('first_name', '')} {timesheet.get('employee', {}).get('last_name', '')}"],
        ['Period:', f"{timesheet.get('start_date', 'N/A')} to {timesheet.get('end_date', 'N/A')}"],
        ['Total Hours:', str(timesheet.get('total_hours', 'N/A'))],
        ['Status:', timesheet.get('status', 'N/A').upper()],
        ['Submitted On:', timesheet.get('submitted_at', 'N/A')[:10] if timesheet.get('submitted_at') else 'N/A'],
    ]
    
    if timesheet.get('approved_by'):
        data.append(['Approved By:', f"{timesheet.get('approved_by', {}).get('first_name', '')} {timesheet.get('approved_by', {}).get('last_name', '')}"])
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Daily entries
    if timesheet.get('entries'):
        elements.append(Paragraph("<b>Daily Entries:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        entries_data = [['Date', 'Hours', 'Description']]
        for entry in timesheet.get('entries', []):
            entries_data.append([
                entry.get('date', 'N/A'),
                str(entry.get('hours', 'N/A')),
                entry.get('description', 'N/A')
            ])
        
        entries_table = Table(entries_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
        entries_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D91C5C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        elements.append(entries_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_travel_request_pdf(travel_request: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for travel request
    
    Args:
        travel_request: Travel request dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    elements.append(Paragraph("Travel Request", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    data = [
        ['Request ID:', travel_request.get('id', 'N/A')],
        ['Employee:', f"{travel_request.get('employee', {}).get('first_name', '')} {travel_request.get('employee', {}).get('last_name', '')}"],
        ['Destination:', travel_request.get('destination', 'N/A')],
        ['Purpose:', travel_request.get('purpose', 'N/A')],
        ['Departure Date:', travel_request.get('departure_date', 'N/A')],
        ['Return Date:', travel_request.get('return_date', 'N/A')],
        ['Duration:', f"{travel_request.get('duration_days', 'N/A')} days"],
        ['Transport Mode:', travel_request.get('transport_mode', 'N/A').replace('_', ' ').title()],
        ['Estimated Cost:', f"${travel_request.get('estimated_cost', 'N/A')}"],
        ['Status:', travel_request.get('status', 'N/A').upper()],
        ['Requested On:', travel_request.get('created_at', 'N/A')[:10] if travel_request.get('created_at') else 'N/A'],
    ]
    
    if travel_request.get('approved_by'):
        data.append(['Approved By:', f"{travel_request.get('approved_by', {}).get('first_name', '')} {travel_request.get('approved_by', {}).get('last_name', '')}"])
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(table)
    
    if travel_request.get('description'):
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Description:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(travel_request.get('description', ''), styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_performance_appraisal_pdf(appraisal: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for performance appraisal
    
    Args:
        appraisal: Performance appraisal dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    elements.append(Paragraph("Performance Appraisal", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Basic info
    data = [
        ['Employee:', f"{appraisal.get('employee', {}).get('first_name', '')} {appraisal.get('employee', {}).get('last_name', '')}"],
        ['Position:', appraisal.get('employee', {}).get('position', {}).get('title', 'N/A')],
        ['Review Period:', f"{appraisal.get('period_start', 'N/A')} to {appraisal.get('period_end', 'N/A')}"],
        ['Reviewer:', f"{appraisal.get('reviewer', {}).get('first_name', '')} {appraisal.get('reviewer', {}).get('last_name', '')}"],
        ['Overall Rating:', f"{appraisal.get('overall_rating', 'N/A')}/5"],
        ['Status:', appraisal.get('status', 'N/A').upper()],
        ['Date:', appraisal.get('appraisal_date', 'N/A')],
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Rating categories
    if appraisal.get('ratings'):
        elements.append(Paragraph("<b>Performance Ratings:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        ratings_data = [['Category', 'Rating', 'Comments']]
        for rating in appraisal.get('ratings', []):
            ratings_data.append([
                rating.get('category', 'N/A'),
                f"{rating.get('score', 'N/A')}/5",
                rating.get('comments', 'N/A')[:50] + '...' if len(rating.get('comments', '')) > 50 else rating.get('comments', 'N/A')
            ])
        
        ratings_table = Table(ratings_data, colWidths=[2*inch, 1*inch, 3*inch])
        ratings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D91C5C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(ratings_table)
    
    # Overall comments
    if appraisal.get('comments'):
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Overall Comments:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(appraisal.get('comments', ''), styles['Normal']))
    
    # Development goals
    if appraisal.get('development_goals'):
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Development Goals:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(appraisal.get('development_goals', ''), styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_grievance_report_pdf(grievance: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for grievance/safeguarding report
    
    Args:
        grievance: Grievance report dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    elements.append(Paragraph("Grievance Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Confidentiality notice
    notice_style = ParagraphStyle(
        'Notice',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.red,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    elements.append(Paragraph("CONFIDENTIAL - Handle with Care", notice_style))
    elements.append(Spacer(1, 0.2*inch))
    
    data = [
        ['Report ID:', grievance.get('id', 'N/A')],
        ['Reported By:', f"{grievance.get('reporter', {}).get('first_name', '')} {grievance.get('reporter', {}).get('last_name', '')}"],
        ['Category:', grievance.get('category', 'N/A').replace('_', ' ').title()],
        ['Severity:', grievance.get('severity', 'N/A').upper()],
        ['Date Reported:', grievance.get('created_at', 'N/A')[:10] if grievance.get('created_at') else 'N/A'],
        ['Status:', grievance.get('status', 'N/A').upper()],
    ]
    
    if grievance.get('assigned_to'):
        data.append(['Assigned To:', f"{grievance.get('assigned_to', {}).get('first_name', '')} {grievance.get('assigned_to', {}).get('last_name', '')}"])
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(table)
    
    if grievance.get('description'):
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Description:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(grievance.get('description', ''), styles['Normal']))
    
    if grievance.get('resolution'):
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Resolution:</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(grievance.get('resolution', ''), styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_employment_contract_pdf(contract: dict, employee: dict) -> BytesIO:
    """Generate an employment contract PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#1F2937'), spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1F2937'), spaceAfter=10, spaceBefore=15)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_LEFT)
    
    elements = []
    elements.append(Paragraph("Employment Agreement", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Contract Info Table
    data = [
        ['Name:', employee.get('full_name', f"{employee.get('first_name', '')} {employee.get('last_name', '')}")],
        ['Position:', contract.get('position_title', '')],
        ['Location:', contract.get('location', '')],
        ['Type of Contract:', contract.get('contract_type', '')],
        ['Employee #:', employee.get('employee_number', '')]
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Agreement content
    intro_text = f"""This Employment Agreement was made on <b>{contract.get('start_date', '')}</b> between <b>INARA</b> and <b>{employee.get('full_name', '')}</b>."""
    elements.append(Paragraph(intro_text, body_style))
    
    elements.append(Paragraph("1. POSITION AND DUTIES:", heading_style))
    elements.append(Paragraph(f"Position: <b>{contract.get('position_title', '')}</b>", body_style))
    
    elements.append(Paragraph("2. EMPLOYMENT TERM:", heading_style))
    elements.append(Paragraph(f"From <b>{contract.get('start_date', '')}</b> to <b>{contract.get('end_date', '')}</b>", body_style))
    
    elements.append(Paragraph("3. COMPENSATION:", heading_style))
    monthly_salary = float(contract.get('monthly_salary', 0))
    currency = contract.get('currency', 'USD')
    elements.append(Paragraph(f"Salary: <b>{currency} {monthly_salary:,.2f}/month</b>", body_style))
    
    # Signatures
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("_________________________ | _________________________", body_style))
    elements.append(Paragraph("INARA (Employer) | Employee", body_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_resignation_letter_pdf(resignation: dict, employee: dict) -> BytesIO:
    """Generate a resignation letter PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=11, leading=16)
    
    elements = []
    
    # Header
    elements.append(Paragraph(employee.get('full_name', ''), body_style))
    elements.append(Paragraph(employee.get('work_email', ''), body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(resignation.get('resignation_date', ''), body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Recipient
    elements.append(Paragraph("Human Resources<br/>INARA", body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Subject
    elements.append(Paragraph("<b>Subject: Resignation Notice</b>", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Body
    elements.append(Paragraph("Dear Sir/Madam,", body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    body_text = f"""I am writing to notify you of my resignation, effective <b>{resignation.get('intended_last_working_day', '')}</b>. I am providing <b>{resignation.get('notice_period_days', 30)} days</b> notice as per my contract.
    <br/><br/>
    <b>Reason:</b> {resignation.get('reason', '')}
    <br/><br/>
    I am committed to ensuring a smooth transition and will assist in handover activities.
    <br/><br/>
    Thank you for the opportunities provided during my tenure at INARA.
    """
    elements.append(Paragraph(body_text, body_style))
    
    elements.append(Spacer(1, 0.4*inch))
    elements.append(Paragraph("Sincerely,", body_style))
    elements.append(Spacer(1, 0.6*inch))
    elements.append(Paragraph("_________________________", body_style))
    elements.append(Paragraph(employee.get('full_name', ''), body_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
