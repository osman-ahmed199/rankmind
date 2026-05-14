import io
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from app.services.score_calculator import ScoreCalculator

class PDFGenerator:
    def __init__(self):
        # Sample style sheet
        self.styles = getSampleStyleSheet()
        
    def _format_ar(self, text):
        """Reshapes and fixes bidirectional text for Arabic support in ReportLab."""
        if not text:
            return ""
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text

    def generate_report(self, analysis):
        """
        Generates a professional PDF report using ReportLab (Railway compatible).
        """
        result_data = json.loads(analysis.result)
        grade = ScoreCalculator.get_grade(analysis.score)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        # Custom Styles
        ar_style = ParagraphStyle(
            'ArabicStyle',
            fontName='Helvetica', # Fallback, best to register a real font if available
            fontSize=12,
            leading=18,
            alignment=2, # Right alignment
            wordWrap='RTL'
        )
        
        title_style = ParagraphStyle(
            'TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=30,
            alignment=1, # Center
            textColor=colors.indigo
        )

        # 1. Cover Content
        elements.append(Spacer(1, 100))
        elements.append(Paragraph(self._format_ar("RankMind"), title_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(self._format_ar("تقرير تحسين ظهور الموقع في محركات الذكاء الاصطناعي"), ar_style))
        elements.append(Spacer(1, 50))
        elements.append(Paragraph(self._format_ar(f"رابط الموقع: {analysis.site.url}"), ar_style))
        elements.append(Paragraph(self._format_ar(f"تاريخ التقرير: {analysis.completed_at.strftime('%Y-%m-%d')}"), ar_style))
        elements.append(Spacer(1, 200))
        
        # 2. Score Section
        elements.append(Paragraph(self._format_ar("ملخص الدرجة النهائية"), ar_style))
        elements.append(Spacer(1, 10))
        score_data = [[self._format_ar(f"الدرجة: {analysis.score}"), self._format_ar(f"التقييم: {grade}")]]
        score_table = Table(score_data, colWidths=[200, 200])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.indigo),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 30))

        # 3. AI Summary
        elements.append(Paragraph(self._format_ar("رؤية المحلل الذكي:"), ar_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(self._format_ar(result_data.get('ai_summary', '')), ar_style))
        elements.append(Spacer(1, 30))

        # 4. Breakdown Table
        elements.append(Paragraph(self._format_ar("تحليل المعايير:"), ar_style))
        elements.append(Spacer(1, 10))
        
        breakdown_rows = []
        for key, item in result_data.get('breakdown', {}).items():
            breakdown_rows.append([self._format_ar(f"{item.get('score', 0)}%"), self._format_ar(item.get('label', key))])
        
        if breakdown_rows:
            table = Table(breakdown_rows, colWidths=[100, 300])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (1, -1), colors.ghostwhite),
            ]))
            elements.append(table)

        # Build PDF
        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()
        return pdf_content
