"""
PDF Generation Utilities
Helper functions for generating PDF documents
"""

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Logo and Header - preserve aspect ratio
    import os
    from PIL import Image as PILImage
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo-pdf.png')
    
    if os.path.exists(logo_path):
        # Load image to get original dimensions and preserve aspect ratio
        pil_img = PILImage.open(logo_path)
        original_width, original_height = pil_img.size
        aspect_ratio = original_width / original_height
        
        # Set width and calculate height to preserve aspect ratio
        logo_width = 0.8*inch
        logo_height = logo_width / aspect_ratio
        
        img = Image(logo_path, width=logo_width, height=logo_height)
        header_data = [[img, Paragraph("<b>INARA</b><br/>International Network for Aid, Relief and Assistance", 
                                       ParagraphStyle('OrgName', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT))]]
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
    
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_timesheet_pdf(timesheet: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for timesheet with compact grid layout matching the review dialog
    
    Args:
        timesheet: Timesheet dictionary with entries
        
    Returns:
        BytesIO buffer containing PDF
    """
    from datetime import datetime as dt
    from calendar import monthrange
    
    buffer = BytesIO()
    # Use landscape orientation to fit the grid, reduced margins
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.2*inch, bottomMargin=0.2*inch, leftMargin=0.2*inch, rightMargin=0.2*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Logo and Header - preserve aspect ratio
    import os
    from PIL import Image as PILImage
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo-pdf.png')
    
    if os.path.exists(logo_path):
        # Load image to get original dimensions and preserve aspect ratio
        pil_img = PILImage.open(logo_path)
        original_width, original_height = pil_img.size
        aspect_ratio = original_width / original_height
        
        # Set width and calculate height to preserve aspect ratio
        logo_width = 1.0*inch
        logo_height = logo_width / aspect_ratio
        
        img = Image(logo_path, width=logo_width, height=logo_height)
        
        # Create header table with logo and title
        header_data = [[img, Paragraph("<b>Monthly Timesheet - Review</b>", 
                                       ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, 
                                                      textColor=colors.HexColor('#D91C5C'), 
                                                      fontName='Helvetica-Bold', alignment=TA_LEFT))]]
        header_table = Table(header_data, colWidths=[1.2*inch, 6.3*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.05*inch))
    else:
        # Fallback if logo not found
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#D91C5C'),
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("Monthly Timesheet - Review", title_style))
        elements.append(Spacer(1, 0.05*inch))
    
    # Status and Submission Info
    status = timesheet.get('status', 'pending').upper()
    status_color = colors.green if status == 'APPROVED' else colors.orange if status == 'PENDING' else colors.red
    
    status_data = [
        [Paragraph(f"Status: <b><font color='{status_color.hexval()}'>{status}</font></b>", 
                  ParagraphStyle('Status', parent=styles['Normal'], fontSize=8)),
         Paragraph(f"Submitted: {timesheet.get('submitted_date', timesheet.get('submitted_at', 'N/A'))[:10]}", 
                  ParagraphStyle('Status', parent=styles['Normal'], fontSize=8))]
    ]
    
    status_table = Table(status_data, colWidths=[3*inch, 4.5*inch])
    status_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.08*inch))
    
    # Section 1: Employee Information - header aligned with table
    employee_name = f"{timesheet.get('employee', {}).get('first_name', '')} {timesheet.get('employee', {}).get('last_name', '')}"
    employee_data_split = [
        ['1. EMPLOYEE INFORMATION', ''],  # Header spanning both columns
        ['Employee Name:', employee_name],
        ['Timesheet ID:', str(timesheet.get('id', 'N/A'))[:8]],
    ]
    
    employee_table = Table(employee_data_split, colWidths=[1.3*inch, 6.2*inch])
    employee_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),  # Span header across both columns
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 8),
        ('TOPPADDING', (0, 0), (0, 0), 4),
        ('BOTTOMPADDING', (0, 0), (0, 0), 2),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, -1), 7),
        ('TOPPADDING', (0, 1), (0, -1), 3),
        ('BOTTOMPADDING', (0, 1), (0, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(employee_table)
    elements.append(Spacer(1, 0.08*inch))
    
    # Section 2: Reporting Period
    start_date = timesheet.get('start_date', timesheet.get('period_start', 'N/A'))
    end_date = timesheet.get('end_date', timesheet.get('period_end', 'N/A'))
    total_hours = timesheet.get('total_hours', 0)
    submitted_date = timesheet.get('submitted_date', timesheet.get('submitted_at', 'N/A'))
    if submitted_date and len(str(submitted_date)) > 10:
        submitted_date = str(submitted_date)[:10]
    
    period_data = [
        ['2. REPORTING PERIOD', ''],  # Header spanning both columns
        ['Period Start:', str(start_date)],
        ['Period End:', str(end_date)],
        ['Total Hours Logged:', f"<b>{total_hours} hours</b>"],
        ['Submitted On:', str(submitted_date)],
    ]
    
    period_table = Table(period_data, colWidths=[1.3*inch, 6.2*inch])
    period_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),  # Span header across both columns
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 8),
        ('TOPPADDING', (0, 0), (0, 0), 4),
        ('BOTTOMPADDING', (0, 0), (0, 0), 2),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, -1), 7),
        ('TOPPADDING', (0, 1), (0, -1), 3),
        ('BOTTOMPADDING', (0, 1), (0, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(period_table)
    elements.append(Spacer(1, 0.08*inch))
    
    # Section 3: Approval Status
    approval_data = [
        ['3. APPROVAL STATUS', ''],  # Header spanning both columns
        ['Current Status:', Paragraph(f"<b><font color='{status_color.hexval()}'>{status}</font></b>", 
                                     ParagraphStyle('Status', parent=styles['Normal'], fontSize=7))],
    ]
    
    if timesheet.get('approved_by'):
        approver_name = f"{timesheet.get('approved_by', {}).get('first_name', '')} {timesheet.get('approved_by', {}).get('last_name', '')}"
        approval_data.append(['Approved By:', approver_name])
        if timesheet.get('approved_at'):
            approved_at = timesheet.get('approved_at', 'N/A')
            if len(str(approved_at)) > 10:
                approved_at = str(approved_at)[:10]
            approval_data.append(['Approved On:', str(approved_at)])
    
    approval_table = Table(approval_data, colWidths=[1.3*inch, 6.2*inch])
    approval_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),  # Span header across both columns
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 8),
        ('TOPPADDING', (0, 0), (0, 0), 4),
        ('BOTTOMPADDING', (0, 0), (0, 0), 2),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, -1), 7),
        ('TOPPADDING', (0, 1), (0, -1), 3),
        ('BOTTOMPADDING', (0, 1), (0, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(approval_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Build grid data from entries
    period_start = timesheet.get('period_start', timesheet.get('start_date'))
    period_end = timesheet.get('period_end', timesheet.get('end_date'))
    
    if period_start and period_end:
        try:
            start_dt = dt.strptime(str(period_start), '%Y-%m-%d') if isinstance(period_start, str) else period_start
            end_dt = dt.strptime(str(period_end), '%Y-%m-%d') if isinstance(period_end, str) else period_end
            
            year = start_dt.year
            month = start_dt.month
            days_in_month = monthrange(year, month)[1]
            
            # Build project map
            project_map = {}
            project_names = {}
            
            for entry in timesheet.get('entries', []):
                entry_date_str = entry.get('date')
                if not entry_date_str:
                    continue
                    
                try:
                    entry_date = dt.strptime(str(entry_date_str), '%Y-%m-%d') if isinstance(entry_date_str, str) else entry_date_str
                    
                    # Verify date is in the correct month
                    if entry_date.year != year or entry_date.month != month:
                        continue
                    
                    day = entry_date.day
                    project_id = entry.get('project_id', 'Unknown')
                    project_name = entry.get('project_name') or project_id
                    hours = float(entry.get('hours', 0))
                    
                    if project_id not in project_map:
                        project_map[project_id] = {}
                        project_names[project_id] = project_name
                    
                    project_map[project_id][day] = project_map[project_id].get(day, 0) + hours
                except (ValueError, TypeError):
                    continue
            
            # Build grid table
            projects = list(project_map.keys())
            
            # Calculate column widths - maximize size to use available space
            # Landscape letter is 11 x 8.5 inches, minus margins (0.2*2) = 10.6 x 8.1 inches usable
            available_width = 10.6*inch
            project_col_width = 1.5*inch
            totals_col_width = 0.6*inch
            percent_col_width = 0.6*inch
            # Calculate day column width to fill remaining space
            remaining_width = available_width - project_col_width - totals_col_width - percent_col_width
            day_col_width = remaining_width / days_in_month
            
            # Header row
            header_row = ['Project \\ Grant Name']
            
            # Helper to check if weekend
            def is_weekend(day):
                date = dt(year, month, day)
                return date.weekday() >= 5  # Saturday = 5, Sunday = 6
            
            # Helper to get day name
            def get_day_name(day):
                date = dt(year, month, day)
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                return day_names[date.weekday()]
            
            for day in range(1, days_in_month + 1):
                # Use smaller format for day headers
                header_row.append(Paragraph(f"{get_day_name(day)}<br/>{day}", 
                                           ParagraphStyle('DayHeader', parent=styles['Normal'], fontSize=4, alignment=TA_CENTER, leading=4.5)))
            
            header_row.extend(['TOTALS', '% of Time'])
            
            # Calculate column widths list
            col_widths = [project_col_width] + [day_col_width] * days_in_month + [totals_col_width, percent_col_width]
            
            grid_data = [header_row]
            
            # Calculate totals
            grand_total = 0
            for project_id in projects:
                project_total = sum(project_map[project_id].values())
                grand_total += project_total
            
            # Project rows
            for project_id in projects:
                project_total = sum(project_map[project_id].values())
                percentage = (project_total / grand_total * 100) if grand_total > 0 else 0
                
                row = [project_names[project_id]]
                
                for day in range(1, days_in_month + 1):
                    hours = project_map[project_id].get(day, 0)
                    row.append(f"{hours:.2f}" if hours > 0 else "")
                
                row.append(f"{project_total:.2f}")
                row.append(f"{percentage:.1f}%")
                grid_data.append(row)
            
            # Grand total row
            total_row = ['TOTAL HOURS:']
            for day in range(1, days_in_month + 1):
                day_total = sum(project_map.get(proj, {}).get(day, 0) for proj in projects)
                total_row.append(f"{day_total:.2f}" if day_total > 0 else "")
            
            total_row.append(Paragraph(f"<b>{grand_total:.2f}</b>", ParagraphStyle('Total', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
            total_row.append("100.0%")
            grid_data.append(total_row)
            
            # Create grid table
            grid_table = Table(grid_data, colWidths=col_widths, repeatRows=1)
            
            # Style the grid
            grid_style = [
                # Header row - very small font for day headers
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#BFDBFE')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 4),  # Reduced to 4pt
                ('TOPPADDING', (0, 0), (-1, 0), 2),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
                ('LEADING', (0, 0), (-1, 0), 4.5),  # Tighter line spacing
                
                # Weekend columns in header
                ('BACKGROUND', (days_in_month + 1, 0), (days_in_month + 2, 0), colors.HexColor('#93C5FD')),  # TOTALS and % columns
                
                # All borders - thinner
                ('GRID', (0, 0), (-1, -1), 0.2, colors.grey),
                
                # Project name column
                ('ALIGN', (0, 1), (0, -2), 'LEFT'),
                ('FONTNAME', (0, 1), (0, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (0, -2), 5),  # Reduced to 5pt
                ('TOPPADDING', (0, 1), (0, -2), 1),
                ('BOTTOMPADDING', (0, 1), (0, -2), 1),
                ('BACKGROUND', (0, 1), (0, -2), colors.HexColor('#F9FAFB')),
                
                # Day columns - smallest font for numbers
                ('ALIGN', (1, 1), (days_in_month, -2), 'CENTER'),
                ('FONTSIZE', (1, 1), (days_in_month, -2), 4),  # Reduced to 4pt for day numbers
                ('TOPPADDING', (1, 1), (days_in_month, -2), 1),
                ('BOTTOMPADDING', (1, 1), (days_in_month, -2), 1),
                
                # Totals columns
                ('ALIGN', (days_in_month + 1, 1), (days_in_month + 1, -2), 'CENTER'),
                ('FONTNAME', (days_in_month + 1, 1), (days_in_month + 1, -2), 'Helvetica-Bold'),
                ('FONTSIZE', (days_in_month + 1, 1), (days_in_month + 1, -2), 5),  # Reduced to 5pt
                ('BACKGROUND', (days_in_month + 1, 1), (days_in_month + 2, -2), colors.HexColor('#F3F4F6')),
                
                # Percentage column
                ('ALIGN', (days_in_month + 2, 1), (days_in_month + 2, -2), 'CENTER'),
                ('FONTSIZE', (days_in_month + 2, 1), (days_in_month + 2, -2), 5),  # Reduced to 5pt
                
                # Grand total row
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 6),  # Reduced to 6pt
                ('TOPPADDING', (0, -1), (-1, -1), 2),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 2),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DBEAFE')),
                ('ALIGN', (1, -1), (days_in_month, -1), 'CENTER'),
                ('FONTSIZE', (1, -1), (days_in_month, -1), 4),  # Day totals also 4pt
                ('ALIGN', (days_in_month + 1, -1), (days_in_month + 1, -1), 'CENTER'),
                ('TEXTCOLOR', (days_in_month + 1, -1), (days_in_month + 1, -1), colors.HexColor('#2563EB')),
            ]
            
            # Highlight weekend columns
            for day in range(1, days_in_month + 1):
                if is_weekend(day):
                    col_idx = day  # +1 because first column is project name
                    grid_style.append(('BACKGROUND', (col_idx, 0), (col_idx, -1), colors.HexColor('#E5E7EB')))
            
            grid_table.setStyle(TableStyle(grid_style))
            
            # Add grid title
            grid_title = Paragraph("<b>Timesheet Grid</b>", ParagraphStyle('GridTitle', parent=styles['Heading3'], fontSize=9, spaceAfter=4))
            elements.append(grid_title)
            elements.append(grid_table)
            
        except (ValueError, TypeError) as e:
            # Fallback if date parsing fails
            elements.append(Paragraph(f"<i>Error generating grid: Invalid date format</i>", styles['Normal']))
    else:
        elements.append(Paragraph("<i>No period dates available</i>", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.1*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=6, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    elements.append(Paragraph("INARA - International Network for Aid, Relief and Assistance", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_travel_request_pdf(travel_request: Dict[str, Any]) -> BytesIO:
    """
    Generate PDF for travel request with INARA logo and detailed form
    
    Args:
        travel_request: Travel request dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Logo and Header - preserve aspect ratio
    import os
    from PIL import Image as PILImage
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo-pdf.png')
    
    if os.path.exists(logo_path):
        # Load image to get original dimensions and preserve aspect ratio
        pil_img = PILImage.open(logo_path)
        original_width, original_height = pil_img.size
        aspect_ratio = original_width / original_height
        
        # Set width and calculate height to preserve aspect ratio
        logo_width = 1*inch
        logo_height = logo_width / aspect_ratio
        
        img = Image(logo_path, width=logo_width, height=logo_height)
        
        # Create header table with logo and organization name
        header_data = [[img, Paragraph("<b>INARA</b><br/>International Network for Aid, Relief and Assistance", 
                                       ParagraphStyle('OrgName', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT))]]
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#D91C5C'),
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("TRAVEL REQUEST FORM", title_style))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph("Official Travel Authorization Document", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Section 1: Employee Information
    section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=12, 
                                    textColor=colors.HexColor('#D91C5C'), fontName='Helvetica-Bold', spaceAfter=5)
    elements.append(Paragraph("1. EMPLOYEE INFORMATION", section_style))
    elements.append(Spacer(1, 0.1*inch))
    
    employee_data = [
        ['Employee Name:', f"{travel_request.get('employee', {}).get('first_name', '')} {travel_request.get('employee', {}).get('last_name', '')}"],
        ['Request ID:', travel_request.get('id', 'N/A')[:8]],
        ['Submission Date:', travel_request.get('created_at', 'N/A')[:10] if travel_request.get('created_at') else 'N/A'],
    ]
    
    employee_table = Table(employee_data, colWidths=[2*inch, 4.5*inch])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(employee_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Section 2: Travel Details
    elements.append(Paragraph("2. TRAVEL DETAILS", section_style))
    elements.append(Spacer(1, 0.1*inch))
    
    travel_data = [
        ['Destination:', travel_request.get('destination', 'N/A')],
        ['Purpose of Travel:', travel_request.get('purpose', 'N/A')],
        ['Departure Date:', travel_request.get('departure_date', 'N/A')],
        ['Return Date:', travel_request.get('return_date', 'N/A')],
        ['Duration:', f"{travel_request.get('duration_days', 'N/A')} days"],
        ['Mode of Transport:', travel_request.get('transport_mode', 'N/A').replace('_', ' ').title()],
    ]
    
    travel_table = Table(travel_data, colWidths=[2*inch, 4.5*inch])
    travel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(travel_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Section 3: Financial Details
    elements.append(Paragraph("3. ESTIMATED COSTS", section_style))
    elements.append(Spacer(1, 0.1*inch))
    
    cost_data = [
        ['Estimated Total Cost:', f"${travel_request.get('estimated_cost', 0):.2f}"],
    ]
    
    cost_table = Table(cost_data, colWidths=[2*inch, 4.5*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Section 4: Description/Notes
    if travel_request.get('description'):
        elements.append(Paragraph("4. ADDITIONAL NOTES", section_style))
        elements.append(Spacer(1, 0.1*inch))
        desc_style = ParagraphStyle('Description', parent=styles['Normal'], fontSize=10)
        elements.append(Paragraph(travel_request.get('description', ''), desc_style))
        elements.append(Spacer(1, 0.2*inch))
    
    # Section 5: Approval Status
    elements.append(Paragraph("5. APPROVAL STATUS", section_style))
    elements.append(Spacer(1, 0.1*inch))
    
    status = travel_request.get('status', 'pending').upper()
    status_color = colors.green if status == 'APPROVED' else colors.orange if status == 'PENDING' else colors.red
    
    approval_data = [
        ['Current Status:', Paragraph(f"<b><font color='{status_color.hexval()}'>{status}</font></b>", styles['Normal'])],
    ]
    
    if travel_request.get('approved_by'):
        approval_data.append(['Approved By:', f"{travel_request.get('approved_by', {}).get('first_name', '')} {travel_request.get('approved_by', {}).get('last_name', '')}"])
    
    approval_table = Table(approval_data, colWidths=[2*inch, 4.5*inch])
    approval_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(approval_table)
    
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Logo and Header - preserve aspect ratio
    import os
    from PIL import Image as PILImage
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo-pdf.png')
    
    if os.path.exists(logo_path):
        # Load image to get original dimensions and preserve aspect ratio
        pil_img = PILImage.open(logo_path)
        original_width, original_height = pil_img.size
        aspect_ratio = original_width / original_height
        
        # Set width and calculate height to preserve aspect ratio
        logo_width = 0.8*inch
        logo_height = logo_width / aspect_ratio
        
        img = Image(logo_path, width=logo_width, height=logo_height)
        header_data = [[img, Paragraph("<b>INARA</b><br/>International Network for Aid, Relief and Assistance", 
                                       ParagraphStyle('OrgName', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT))]]
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
    
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
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
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Logo and Header - preserve aspect ratio
    import os
    from PIL import Image as PILImage
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo-pdf.png')
    
    if os.path.exists(logo_path):
        # Load image to get original dimensions and preserve aspect ratio
        pil_img = PILImage.open(logo_path)
        original_width, original_height = pil_img.size
        aspect_ratio = original_width / original_height
        
        # Set width and calculate height to preserve aspect ratio
        logo_width = 0.8*inch
        logo_height = logo_width / aspect_ratio
        
        img = Image(logo_path, width=logo_width, height=logo_height)
        header_data = [[img, Paragraph("<b>INARA</b><br/>International Network for Aid, Relief and Assistance", 
                                       ParagraphStyle('OrgName', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT))]]
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
    
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_employment_contract_pdf(contract: dict, employee: dict) -> BytesIO:
    """Generate an employment contract PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    
    # Logo and Header - preserve aspect ratio
    import os
    from PIL import Image as PILImage
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'inara-logo-pdf.png')
    
    elements = []
    if os.path.exists(logo_path):
        # Load image to get original dimensions and preserve aspect ratio
        pil_img = PILImage.open(logo_path)
        original_width, original_height = pil_img.size
        aspect_ratio = original_width / original_height
        
        # Set width and calculate height to preserve aspect ratio
        logo_width = 0.8*inch
        logo_height = logo_width / aspect_ratio
        
        img = Image(logo_path, width=logo_width, height=logo_height)
        header_data = [[img, Paragraph("<b>INARA</b><br/>International Network for Aid, Relief and Assistance", 
                                       ParagraphStyle('OrgName', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT))]]
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#1F2937'), spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1F2937'), spaceAfter=10, spaceBefore=15)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_LEFT)
    
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
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


def create_user_manual_pdf() -> BytesIO:
    """Generate PDF version of the User Manual"""
    buffer = BytesIO()
    
    # Read the markdown manual
    import os
    # Calculate path to USER_MANUAL.md at project root
    # __file__ is at: apps/api/core/pdf_generator.py
    # Need to go up 3 levels to get to project root
    current_dir = os.path.dirname(__file__)  # apps/api/core
    api_dir = os.path.dirname(current_dir)  # apps/api
    apps_dir = os.path.dirname(api_dir)  # apps
    project_root = os.path.dirname(apps_dir)  # project root
    manual_path = os.path.join(project_root, "USER_MANUAL.md")
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
    except FileNotFoundError:
        # If manual file not found, create a basic version
        manual_content = "# INARA HR Management System - User Manual\n\nVersion 1.0\n\nThis is the user manual for the INARA HR Management System."
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading styles
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # List style
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add logo if available
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "inara-logo.png")
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            logo_width = 2 * inch
            logo_height = logo_width / aspect_ratio
            
            logo = Image(logo_path, width=logo_width, height=logo_height)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        except:
            pass
    
    # Title
    elements.append(Paragraph("INARA HR Management System", title_style))
    elements.append(Paragraph("User Manual", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Version 1.0 | Last Updated: January 2026", body_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Parse markdown content and convert to PDF elements
    lines = manual_content.split('\n')
    i = 0
    in_list = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            if not in_list:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            if i > 0:  # Don't add page break for first heading
                elements.append(PageBreak())
            elements.append(Paragraph(line[2:], h1_style))
            in_list = False
        elif line.startswith('## '):
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line[3:], h2_style))
            in_list = False
        elif line.startswith('### '):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(line[4:], h3_style))
            in_list = False
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(f"• {line[2:]}", list_style))
        # Handle numbered lists
        elif line and line[0].isdigit() and '. ' in line[:5]:
            if not in_list:
                elements.append(Spacer(1, 0.05*inch))
            in_list = True
            elements.append(Paragraph(line, list_style))
        # Handle bold text (simple)
        elif line.startswith('**') and line.endswith('**'):
            bold_text = line[2:-2]
            bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
            elements.append(Paragraph(bold_text, bold_style))
            in_list = False
        # Handle code blocks (skip for PDF)
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue
        # Regular paragraph
        else:
            # Clean up markdown formatting
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line:
                elements.append(Paragraph(clean_line, body_style))
                in_list = False
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
