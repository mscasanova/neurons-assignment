from app.utils import fonts, colors, logo_position, logo_colors


def assess_slide_compliance(image_path, pdf_path, api_key):

    reasons = {}
    score = 0

    # 1. Font Style
    try:
        font_score, font_reason = fonts.verify_fonts(pdf_path, image_path, api_key)
    except Exception as e:
        font_score, font_reason = 0, f"Font check failed: {str(e)}"
    reasons['Font style'] = font_reason
    score += font_score

    
    # 2. Logo Safe Zone 
    try:
        score_logo_position, explanation_logo_position = logo_position.check_logo_position(image_path, pdf_path)
    except Exception as e:
        score_logo_position, explanation_logo_position = 0, f"Logo position check failed: {str(e)}"
    reasons["Logo Safe Zone"] = explanation_logo_position
    score += score_logo_position

    # 3. Logo Colors 
    try:
        score_logo_color, explanation_logo_color = logo_colors.check_logo_colors(pdf_path, image_path)
    except Exception as e:
        score_logo_color, explanation_logo_color = 0, f"Logo color check failed: {str(e)}"
    reasons["Logo Color"] = explanation_logo_color
    score += score_logo_color
    
    # 4. Overall Color Palette
    try:
        score_color, explanation_color = colors.analyze_colors(pdf_path, image_path)
    except Exception as e:
        score_color, explanation_color = 0, f"Color palette check failed: {str(e)}"
    reasons["Color palette"] = explanation_color
    score += score_color


    return score, reasons
    
   

# Main
def assessmentllm(slide_image_path, brand_pdf_path, api_key):
    score, feedback = assess_slide_compliance(slide_image_path, brand_pdf_path, api_key)
    print(f"--- Brand Compliance Score: {score}/4 ---\n")
    for category, reason in feedback.items():
        print(f"{category}: {reason}")
    
    return score, feedback


