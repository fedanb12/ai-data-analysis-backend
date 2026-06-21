import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime

def generate_report(
    file_name: str,
    stats: dict,
    insights: str,
    history: list,
    df: pd.DataFrame
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#111827'),
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4,
        leading=16
    )
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=4
    )

    elements = []

    # Title
    elements.append(Paragraph('AI Data Analysis Report', title_style))
    elements.append(Paragraph(f'File: {file_name}', meta_style))
    elements.append(Paragraph(f'Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}', meta_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    elements.append(Spacer(1, 12))

    # Dataset Overview
    elements.append(Paragraph('Dataset Overview', heading_style))
    overview_data = [
        ['Metric', 'Value'],
        ['Total Rows', str(stats.get('rowCount', 'N/A'))],
        ['Total Columns', str(stats.get('columnCount', 'N/A'))],
        ['Missing Values', str(sum(c.get('missing', 0) for c in stats.get('columns', {}).values()))],
        ['Numeric Columns', str(sum(1 for c in stats.get('columns', {}).values() if c.get('type') == 'numeric'))],
        ['Categorical Columns', str(sum(1 for c in stats.get('columns', {}).values() if c.get('type') == 'categorical'))],
        ['Date Columns', str(sum(1 for c in stats.get('columns', {}).values() if c.get('type') == 'date'))],
    ]
    overview_table = Table(overview_data, colWidths=[3 * inch, 3 * inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 16))

    # Column Summary
    elements.append(Paragraph('Column Summary', heading_style))
    col_data = [['Column', 'Type', 'Missing', 'Unique', 'Min', 'Max', 'Average']]
    for col_name, col_stats in stats.get('columns', {}).items():
        col_data.append([
            col_name,
            col_stats.get('type', ''),
            str(col_stats.get('missing', '')),
            str(col_stats.get('unique', '')),
            str(col_stats.get('min', '-')),
            str(col_stats.get('max', '-')),
            str(col_stats.get('average', '-')),
        ])
    col_table = Table(col_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    col_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(col_table)
    elements.append(Spacer(1, 16))

    # AI Insights
    if insights:
        elements.append(Paragraph('AI Insights', heading_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
        elements.append(Spacer(1, 8))
        for line in insights.split('\n'):
            if line.strip():
                elements.append(Paragraph(line.strip(), body_style))
        elements.append(Spacer(1, 16))

    # Analysis History
    if history:
        elements.append(Paragraph('Analysis History', heading_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))
        elements.append(Spacer(1, 8))
        for i, item in enumerate(history):
            q_style = ParagraphStyle(
                'Question',
                parent=body_style,
                textColor=colors.HexColor('#4f46e5'),
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph(f"Q{i+1}: {item.get('question', '')}", q_style))
            elements.append(Paragraph(item.get('answer', ''), body_style))
            elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()