

import requests
import os
import openai
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph


openai.api_key = ""
# Adzuna API Credentials
ADZUNA_APP_ID = "97cb022e"
ADZUNA_APP_KEY = "b74ceb936268f0f7b8309d6f9f26728a"

# GitHub Token
GITHUB_TOKEN = "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"

# Coursera Credentials
coursera_auth_url = "https://api.coursera.com/oauth2/client_credentials/token"
coursera_payload = {
    'client_id': 'EWMCX9yMt2EolnvVHbmUrOPXgsHo1qlyj9RsACMbF6d4oJBI',
    'client_secret': 'uIPaYe2rlMt9cZ3RLHSTlqMTGu95KCy1PDJapNH6UgiKrmhtiZCESasbeWmNHC2z',
    'grant_type': 'client_credentials'
}
coursera_response = requests.post(coursera_auth_url, data=coursera_payload)
coursera_token = coursera_response.json().get("access_token") if coursera_response.status_code == 200 else ""

def draw_wrapped_text(c, text, x, y, max_width, leading=12):
    """
    Draws wrapped text on the canvas using Paragraph for better text handling.
    """
    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        name='Normal',
        fontName='Times-Roman',
        fontSize=10,
        leading=leading,
        textColor=colors.black
    )
    para = Paragraph(text, style)
    width, height = para.wrap(max_width, y)
    para.drawOn(c, x, y - height)
    return y - height - 5  # Adjust y position for next text

def create_cv_pdf(data, profile_summary):
    buffer = io.BytesIO()
    
    # Handle cases where the name might not have at least two parts
    name_parts = data["name"].split()
    first_name = name_parts[0] if len(name_parts) > 0 else "FirstName"
    last_name = name_parts[-1] if len(name_parts) > 1 else "LastName"
    output_path = f"{first_name}_{last_name}_CV.pdf"

    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Margins
    left_margin = 0.75 * inch
    right_margin = 0.75 * inch
    top_margin = 1 * inch
    bottom_margin = 0.75 * inch
    max_text_width = width - left_margin - right_margin

    # Colors
    header_color = colors.HexColor("#000000")  # Dark Blue for header text
    section_color = colors.HexColor("#000000")  # Black for section titles
    text_color = colors.black

    # Fonts
    # Header: Name and Job Title
    c.setFont("Times-Bold", 20)
    c.setFillColor(header_color)
    c.drawString(left_margin, height - top_margin, data["name"])

    c.setFont("Times-Roman", 14)
    c.setFillColor(text_color)
    c.drawString(left_margin, height - top_margin - 0.3 * inch, data["job_title"])

    # Draw a horizontal line below the header
    c.setStrokeColor(header_color)
    c.setLineWidth(1)
    c.line(left_margin, height - top_margin - 0.5 * inch, width - right_margin, height - top_margin - 0.5 * inch)

    # Contact Information
    contact_y = height - top_margin - 0.6 * inch
    c.setFont("Times-Roman", 10)
    contact_info = f"{data['email']} | {data['phone']} | {data['location']} | DOB: {data['dob']} | Nationality: {data['nationality']}"
    if data.get('linkedin') and data['linkedin'] != "N/A":
        contact_info += f" | LinkedIn: {data['linkedin']}"
    c.setFillColor(text_color)
    c.drawString(left_margin, contact_y, contact_info)

    # Profile Summary
    y_position = contact_y - 0.3 * inch
    c.setFont("Times-Bold", 12)
    c.setFillColor(section_color)
    section_title = "Profile Summary"
    text_width = c.stringWidth(section_title, "Times-Bold", 12)
    c.drawString((width - text_width) / 2, y_position, section_title)

    # Draw a line under the section title
    c.setStrokeColor(section_color)
    c.setLineWidth(0.5)
    c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

    y_position -= 0.2 * inch
    c.setFont("Times-Roman", 10)
    c.setFillColor(text_color)
    y_position = draw_wrapped_text(c, profile_summary, left_margin, y_position, max_text_width)

    # Languages
    if data.get("languages"):
        y_position -= 0.2 * inch
        c.setFont("Times-Bold", 12)
        c.setFillColor(section_color)
        section_title = "Languages"
        text_width = c.stringWidth(section_title, "Times-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, section_title)

        c.setStrokeColor(section_color)
        c.setLineWidth(0.5)
        c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

        y_position -= 0.2 * inch
        c.setFont("Times-Roman", 10)
        for lang in data["languages"]:
            y_position -= 0.15 * inch
            c.drawString(left_margin + 0.2 * inch, y_position, f"• {lang['Language']} - {lang['Level']}")

    # Skills
    if data.get("skills"):
        y_position -= 0.3 * inch
        c.setFont("Times-Bold", 12)
        c.setFillColor(section_color)
        section_title = "Skills"
        text_width = c.stringWidth(section_title, "Times-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, section_title)

        c.setStrokeColor(section_color)
        c.setLineWidth(0.5)
        c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

        y_position -= 0.2 * inch
        c.setFont("Times-Roman", 10)
        for skill in data["skills"]:
            y_position -= 0.15 * inch
            c.drawString(left_margin + 0.2 * inch, y_position, f"• {skill['skill']} - {skill['level']}")

    # Education
    if data.get("education"):
        y_position -= 0.3 * inch
        c.setFont("Times-Bold", 12)
        c.setFillColor(section_color)
        section_title = "Education"
        text_width = c.stringWidth(section_title, "Times-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, section_title)

        c.setStrokeColor(section_color)
        c.setLineWidth(0.5)
        c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

        c.setFillColor(text_color)
        for edu in data["education"]:
            y_position -= 0.25 * inch
            c.setFont("Times-Bold", 11)
            edu_text = f"{edu['Degree']}, {edu['Institution']} ({edu['Years']})"
            y_position = draw_wrapped_text(c, edu_text, left_margin, y_position, max_text_width)
            if edu.get("Details"):
                c.setFont("Times-Roman", 10)
                y_position = draw_wrapped_text(c, edu["Details"], left_margin + 0.2 * inch, y_position, max_text_width - 0.2 * inch)

    # Professional Experience
    if data.get("experience"):
        y_position -= 0.3 * inch
        c.setFont("Times-Bold", 12)
        c.setFillColor(section_color)
        section_title = "Professional Experience"
        text_width = c.stringWidth(section_title, "Times-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, section_title)

        c.setStrokeColor(section_color)
        c.setLineWidth(0.5)
        c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

        c.setFillColor(text_color)
        for exp in data["experience"]:
            y_position -= 0.25 * inch
            c.setFont("Times-Bold", 11)
            exp_text = f"{exp['Title']} at {exp['Company']} ({exp['Years']})"
            y_position = draw_wrapped_text(c, exp_text, left_margin, y_position, max_text_width)
            c.setFont("Times-Roman", 10)
            y_position = draw_wrapped_text(c, exp["Details"], left_margin + 0.2 * inch, y_position, max_text_width - 0.2 * inch)

    # Awards
    if data.get("awards"):
        y_position -= 0.3 * inch
        c.setFont("Times-Bold", 12)
        c.setFillColor(section_color)
        section_title = "Awards"
        text_width = c.stringWidth(section_title, "Times-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, section_title)

        c.setStrokeColor(section_color)
        c.setLineWidth(0.5)
        c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

        c.setFont("Times-Roman", 10)
        for award in data["awards"]:
            y_position -= 0.15 * inch
            c.drawString(left_margin + 0.2 * inch, y_position, f"• {award}")

    # Projects
    if data.get("projects"):
        y_position -= 0.3 * inch
        c.setFont("Times-Bold", 12)
        c.setFillColor(section_color)
        section_title = "Projects"
        text_width = c.stringWidth(section_title, "Times-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, section_title)

        c.setStrokeColor(section_color)
        c.setLineWidth(0.5)
        c.line(left_margin, y_position - 2, width - right_margin, y_position - 2)

        c.setFillColor(text_color)
        for proj in data["projects"]:
            y_position -= 0.25 * inch
            c.setFont("Times-Bold", 11)
            c.drawString(left_margin + 0.2 * inch, y_position, f"• {proj['Title']}")
            y_position -= 0.15 * inch
            c.setFont("Times-Roman", 10)
            y_position = draw_wrapped_text(c, proj["Description"], left_margin + 0.4 * inch, y_position, max_text_width - 0.4 * inch)

    # Footer with page number
    c.setFont("Times-Roman", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2.0, bottom_margin / 2, "Page 1")

    # Save PDF to buffer
    c.save()
    buffer.seek(0)
    return buffer
