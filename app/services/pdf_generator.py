import os
from flask import render_template, current_app
from weasyprint import HTML
import json
from app.services.score_calculator import ScoreCalculator

class PDFGenerator:
    def generate_report(self, analysis):
        """
        Generates a professional PDF report for a given analysis.
        """
        result_data = json.loads(analysis.result)
        grade = ScoreCalculator.get_grade(analysis.score)
        
        # Prepare data for the template
        template_vars = {
            'analysis': analysis,
            'data': result_data,
            'grade': grade,
            'report_url': f"https://rankmind.app/report/{analysis.uuid}"
        }
        
        # Render HTML
        html_out = render_template('dashboard/pdf_template.html', **template_vars)
        
        # Generate PDF
        # Note: In some environments, we might need to specify base_url for assets
        pdf = HTML(string=html_out).write_pdf()
        
        return pdf
