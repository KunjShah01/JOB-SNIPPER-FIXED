"""
Exporter utility for PDF generation and email sending
Handles missing dependencies gracefully
"""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import PDF libraries
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        REPORTLAB_AVAILABLE = True
        FPDF_AVAILABLE = False
    except ImportError:
        FPDF_AVAILABLE = False
        REPORTLAB_AVAILABLE = False
        logger.warning("No PDF library available. Install fpdf2 or reportlab: pip install fpdf2 reportlab")

def export_to_pdf(data, filename="resume_analysis.pdf", title="Resume Analysis Report"):
    """
    Export analysis data to PDF
    
    Args:
        data: Analysis data dictionary
        filename: Output filename
        title: Report title
    
    Returns:
        str: Path to generated PDF or None if failed
    """
    try:
        if FPDF_AVAILABLE:
            return _export_with_fpdf(data, filename, title)
        elif REPORTLAB_AVAILABLE:
            return _export_with_reportlab(data, filename, title)
        else:
            logger.error("No PDF library available")
            return None
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")
        return None

def _export_with_fpdf(data, filename, title):
    """Export using FPDF library"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(10)
        
        # Content
        pdf.set_font("Arial", size=12)
        
        # Add timestamp
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(5)
        
        # Add data sections
        if isinstance(data, dict):
            for key, value in data.items():
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, f"{key.replace('_', ' ').title()}:", ln=True)
                
                pdf.set_font("Arial", size=10)
                if isinstance(value, (list, tuple)):
                    for item in value:
                        pdf.cell(0, 8, f"• {str(item)}", ln=True)
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        pdf.cell(0, 8, f"  {sub_key}: {str(sub_value)}", ln=True)
                else:
                    # Handle long text
                    text = str(value)
                    if len(text) > 80:
                        words = text.split()
                        line = ""
                        for word in words:
                            if len(line + word) > 80:
                                pdf.cell(0, 8, line, ln=True)
                                line = word + " "
                            else:
                                line += word + " "
                        if line:
                            pdf.cell(0, 8, line, ln=True)
                    else:
                        pdf.cell(0, 8, text, ln=True)
                
                pdf.ln(3)
        
        # Save to temporary file
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        pdf.output(temp_path)
        
        logger.info(f"PDF exported successfully: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Error with FPDF export: {e}")
        return None

def _export_with_reportlab(data, filename, title):
    """Export using ReportLab library"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        c = canvas.Canvas(temp_path, pagesize=letter)
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, title)
        
        # Timestamp
        c.setFont("Helvetica", 10)
        c.drawString(100, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Content
        y_position = 700
        c.setFont("Helvetica", 12)
        
        if isinstance(data, dict):
            for key, value in data.items():
                if y_position < 100:  # Start new page
                    c.showPage()
                    y_position = 750
                
                # Section header
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, y_position, f"{key.replace('_', ' ').title()}:")
                y_position -= 20
                
                # Section content
                c.setFont("Helvetica", 10)
                if isinstance(value, (list, tuple)):
                    for item in value:
                        if y_position < 100:
                            c.showPage()
                            y_position = 750
                        c.drawString(120, y_position, f"• {str(item)}")
                        y_position -= 15
                else:
                    text = str(value)
                    if len(text) > 80:
                        words = text.split()
                        line = ""
                        for word in words:
                            if len(line + word) > 80:
                                if y_position < 100:
                                    c.showPage()
                                    y_position = 750
                                c.drawString(120, y_position, line)
                                y_position -= 15
                                line = word + " "
                            else:
                                line += word + " "
                        if line:
                            if y_position < 100:
                                c.showPage()
                                y_position = 750
                            c.drawString(120, y_position, line)
                            y_position -= 15
                    else:
                        if y_position < 100:
                            c.showPage()
                            y_position = 750
                        c.drawString(120, y_position, text)
                        y_position -= 15
                
                y_position -= 10
        
        c.save()
        logger.info(f"PDF exported successfully with ReportLab: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Error with ReportLab export: {e}")
        return None

def send_email(to_email, subject, body, attachment_path=None, smtp_config=None):
    """
    Send email with optional attachment
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        attachment_path: Path to attachment file (optional)
        smtp_config: SMTP configuration dict (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Get SMTP configuration
        if smtp_config is None:
            try:
                from utils.config import load_config
                config = load_config()
                smtp_config = {
                    'smtp_server': config.get('smtp_server', 'smtp.gmail.com'),
                    'smtp_port': config.get('smtp_port', 587),
                    'sender_email': config.get('sender_email', ''),
                    'sender_password': config.get('sender_password', '')
                }
            except ImportError:
                logger.error("Could not load email configuration")
                return False
        
        if not smtp_config.get('sender_email') or not smtp_config.get('sender_password'):
            logger.error("Email configuration incomplete")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['sender_email']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}'
            )
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
        server.starttls()
        server.login(smtp_config['sender_email'], smtp_config['sender_password'])
        
        text = msg.as_string()
        server.sendmail(smtp_config['sender_email'], to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_email_fallback(to_email, subject, body, attachment_path=None):
    """
    Fallback email function with basic error handling
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        attachment_path: Path to attachment file (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        return send_email(to_email, subject, body, attachment_path)
    except Exception as e:
        logger.error(f"Email fallback failed: {e}")
        return False

def create_text_report(data, title="Analysis Report"):
    """
    Create a text-based report as fallback when PDF is not available
    
    Args:
        data: Analysis data dictionary
        title: Report title
    
    Returns:
        str: Formatted text report
    """
    try:
        report = []
        report.append("=" * 60)
        report.append(f"{title}")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if isinstance(data, dict):
            for key, value in data.items():
                report.append(f"{key.replace('_', ' ').title()}:")
                report.append("-" * 40)
                
                if isinstance(value, (list, tuple)):
                    for item in value:
                        report.append(f"• {str(item)}")
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        report.append(f"  {sub_key}: {str(sub_value)}")
                else:
                    report.append(str(value))
                
                report.append("")
        
        return "\n".join(report)
        
    except Exception as e:
        logger.error(f"Error creating text report: {e}")
        return f"Error generating report: {e}"

# Compatibility functions for existing code
def export_analysis_to_pdf(analysis_data, filename="analysis.pdf"):
    """Compatibility function for existing code"""
    return export_to_pdf(analysis_data, filename, "Resume Analysis Report")

def send_analysis_email(to_email, analysis_data, include_pdf=True):
    """Send analysis results via email"""
    try:
        subject = "Resume Analysis Results"
        body = create_text_report(analysis_data, "Resume Analysis Results")
        
        attachment_path = None
        if include_pdf:
            attachment_path = export_to_pdf(analysis_data, "resume_analysis.pdf")
        
        success = send_email(to_email, subject, body, attachment_path)
        
        # Cleanup temporary file
        if attachment_path and os.path.exists(attachment_path):
            try:
                os.unlink(attachment_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending analysis email: {e}")
        return False