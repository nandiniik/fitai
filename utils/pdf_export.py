# utils/pdf_export.py
# ReportLab is the industry standard for PDF generation in Python.
# WHY PDF EXPORT: Makes the app feel like a real product.
# Users can download, print, and share their plan.

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                  Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime
from models.user_profile import UserProfile
from utils.health_calc import get_health_summary


# Brand colors — match the app theme
GREEN = HexColor("#00C896")
DARK_BG = HexColor("#1a1d27")
DARK_CARD = HexColor("#252836")
LIGHT_TEXT = HexColor("#FAFAFA")
GRAY_TEXT = HexColor("#aaaaaa")
ORANGE = HexColor("#FF6B35")


def generate_pdf_report(profile: UserProfile,
                         diet_plan: dict,
                         workout_plan: dict) -> bytes:
    """
    Generates a complete PDF health report.
    Returns bytes — Streamlit can offer this as a download button.
    
    WHY RETURN BYTES: We don't save to disk (no file management needed).
    Bytes go directly to the browser download.
    """
    buffer = io.BytesIO()  # in-memory file — no disk I/O needed
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story = []  # list of PDF elements to render in order

    # --- CUSTOM STYLES ---
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=26,
        textColor=GREEN,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=GRAY_TEXT,
        alignment=TA_CENTER,
        spaceAfter=2
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=GREEN,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=LIGHT_TEXT,
        spaceAfter=4,
        leading=16
    )
    meal_name_style = ParagraphStyle(
        'MealName',
        parent=styles['Normal'],
        fontSize=11,
        textColor=GREEN,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=2
    )
    item_style = ParagraphStyle(
        'Item',
        parent=styles['Normal'],
        fontSize=9,
        textColor=LIGHT_TEXT,
        leftIndent=12,
        spaceAfter=2
    )

    summary = get_health_summary(profile)

    # ============================================================
    # HEADER
    # ============================================================
    story.append(Paragraph("💪 FitAI Health Report", title_style))
    story.append(Paragraph("AI-Powered Personalized Health Platform", subtitle_style))
    story.append(Paragraph(
        f"Generated for {profile.name} | {datetime.now().strftime('%d %B %Y')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=12))

    # ============================================================
    # HEALTH METRICS TABLE
    # ============================================================
    story.append(Paragraph("Your Health Metrics", section_style))

    metrics_data = [
        ["Metric", "Value", "Details"],
        ["BMI", str(summary["bmi"]), summary["bmi_category"]],
        ["Daily Calorie Target", f"{summary['calorie_target']} kcal",
         f"Goal: {profile.fitness_goal.value.replace('_', ' ').title()}"],
        ["TDEE (calories burned)", f"{summary['tdee']} kcal", "Total Daily Energy Expenditure"],
        ["Protein Target", f"{summary['protein_target_g']}g", "Per day"],
        ["Carbs Target", f"{summary['carbs_g']}g", "Per day"],
        ["Fat Target", f"{summary['fat_g']}g", "Per day"],
        ["Water Intake", f"{summary['water_liters']}L", "Per day"],
    ]

    metrics_table = Table(metrics_data, colWidths=[5.5*cm, 4*cm, 8*cm])
    metrics_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 8),
        # Data rows alternate colors
        ('BACKGROUND', (0, 1), (-1, -1), DARK_CARD),
        ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT_TEXT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [DARK_BG, DARK_CARD]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#333344")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [DARK_BG, DARK_CARD]),
    ]))
    story.append(metrics_table)

    # ============================================================
    # DIET PLAN
    # ============================================================
    story.append(Paragraph("🥗 Your Personalized Diet Plan", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=8))

    if "meals" in diet_plan:
        meal_icons = {
            "early_morning": "🌅 Early Morning",
            "breakfast": "🍳 Breakfast",
            "mid_morning": "🍎 Mid Morning",
            "lunch": "🍱 Lunch",
            "evening_snack": "☕ Evening Snack",
            "dinner": "🌙 Dinner"
        }
        for meal_key, meal_data in diet_plan["meals"].items():
            meal_label = meal_icons.get(meal_key, meal_key.replace("_", " ").title())
            time_str = meal_data.get("time", "")
            story.append(Paragraph(f"{meal_label} — {time_str}", meal_name_style))

            # Items table for this meal
            items = meal_data.get("items", [])
            if items:
                item_data = [["Food Item", "Quantity", "Calories", "Protein"]]
                for item in items:
                    item_data.append([
                        item.get("name", ""),
                        item.get("quantity", ""),
                        f"{item.get('calories', 0)} kcal",
                        f"{item.get('protein_g', 0)}g"
                    ])
                item_table = Table(item_data, colWidths=[6*cm, 4*cm, 3.5*cm, 3.5*cm])
                item_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1a3a2e")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), GREEN),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), DARK_BG),
                    ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT_TEXT),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#333344")),
                ]))
                story.append(item_table)

        # Daily totals
        totals = diet_plan.get("daily_totals", {})
        if totals:
            story.append(Spacer(1, 8))
            totals_text = (f"<b>Daily Totals:</b> "
                          f"🔥 {totals.get('calories', 0)} kcal | "
                          f"💪 {totals.get('protein_g', 0)}g protein | "
                          f"🌾 {totals.get('carbs_g', 0)}g carbs | "
                          f"🥑 {totals.get('fat_g', 0)}g fat")
            story.append(Paragraph(totals_text, body_style))

        # Nutrition tips
        tips = diet_plan.get("key_nutrition_tips", [])
        if tips:
            story.append(Paragraph("Nutrition Tips:", meal_name_style))
            for tip in tips:
                story.append(Paragraph(f"• {tip}", item_style))

    # ============================================================
    # WORKOUT PLAN
    # ============================================================
    story.append(Paragraph("💪 Your Weekly Workout Plan", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE, spaceAfter=8))

    if "weekly_plan" in workout_plan:
        day_order = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        for day in day_order:
            if day not in workout_plan["weekly_plan"]:
                continue
            data = workout_plan["weekly_plan"][day]
            focus = data.get("focus", "Rest")
            duration = data.get("duration_mins", 0)

            day_style = ParagraphStyle(
                'DayTitle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=ORANGE,
                fontName='Helvetica-Bold',
                spaceBefore=10,
                spaceAfter=4
            )
            story.append(Paragraph(
                f"{day.title()} — {focus} ({duration} mins)", day_style
            ))

            exercises = data.get("exercises", [])
            if exercises and focus not in ["Complete Rest", "Rest/Active Recovery"]:
                ex_data = [["Exercise", "Sets", "Reps", "Rest"]]
                for ex in exercises:
                    ex_data.append([
                        ex.get("name", ""),
                        str(ex.get("sets", "")),
                        str(ex.get("reps", "")),
                        f"{ex.get('rest_seconds', 0)}s"
                    ])
                ex_table = Table(ex_data, colWidths=[7*cm, 2.5*cm, 3*cm, 2.5*cm])
                ex_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor("#3a1a0a")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), ORANGE),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), DARK_BG),
                    ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT_TEXT),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.3, HexColor("#333344")),
                ]))
                story.append(ex_table)

        # Pro tips
        pro_tips = workout_plan.get("pro_tips", [])
        if pro_tips:
            story.append(Paragraph("Pro Tips:", meal_name_style))
            for tip in pro_tips:
                story.append(Paragraph(f"• {tip}", item_style))

    # ============================================================
    # FOOTER
    # ============================================================
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN))
    story.append(Spacer(1, 6))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=GRAY_TEXT,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "Generated by FitAI | Powered by Llama 3.3-70B via Groq + LangChain | "
        "For informational purposes only. Consult a healthcare professional before starting any diet or exercise program.",
        footer_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()  # returns raw bytes