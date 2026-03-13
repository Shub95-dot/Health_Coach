from fpdf import FPDF
import os
from typing import Dict, Any

class WorkoutPDFGenerator:
    """
    Generates a formatted PDF for a workout plan with tracking fields.
    """
    def __init__(self, output_dir: str = "user_data/pdfs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _clean_text(self, text: str) -> str:
        """Removes non-latin-1 characters and markdown."""
        return text.replace("**", "").replace("~", "About ").strip().encode('latin-1', 'replace').decode('latin-1')

    def generate(self, user_id: str, profile_name: str, stats_text: str, plan_text: str) -> str:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, self._clean_text(f"Health Coach: Workout Plan for {profile_name}"), ln=True, align='C')
        pdf.ln(5)
        
        # Stats Section
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, "Summary & Health Stats", ln=True)
        pdf.set_font("Helvetica", '', 10)
        pdf.multi_cell(0, 5, self._clean_text(stats_text))
        pdf.ln(5)
        
        # Tracking Instructions
        pdf.set_font("Helvetica", 'I', 10)
        pdf.cell(0, 10, "Tracking Guide: Record your sets and weight used in the boxes below.", ln=True)
        pdf.ln(2)
        
        # Plan Section
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, "Your Training Program", ln=True)
        
        lines = plan_text.split("\n")
        pdf.set_font("Helvetica", '', 10)
        
        for line in lines:
            line = self._clean_text(line)
            if not line:
                pdf.ln(2)
                continue
                
            if line.startswith("==="):
                pdf.set_font("Helvetica", 'B', 11)
                pdf.set_text_color(0, 51, 102) 
                pdf.cell(0, 8, line, ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", '', 10)
            elif line.startswith("Day "):
                pdf.set_font("Helvetica", 'B', 10)
                pdf.cell(0, 7, line, ln=True)
                pdf.set_font("Helvetica", '', 10)
            elif line.startswith("- "):
                exercise_part = line[2:]
                # Reduced widths to 130 + 25 + 25 = 180 (well within 190mm available)
                pdf.cell(130, 6, f"  [ ] {exercise_part}", border=0)
                pdf.set_font("Helvetica", '', 8)
                pdf.cell(25, 6, "Sets: ____", border=1)
                pdf.cell(25, 6, " Weight: ____", border=1, ln=True)
                pdf.set_font("Helvetica", '', 10)
            else:
                # Use explicit width (190) instead of 0 to avoid space errors
                pdf.multi_cell(190, 5, line)

        filename = f"{user_id}_workout.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        return filepath
