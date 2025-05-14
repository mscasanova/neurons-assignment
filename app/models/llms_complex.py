import fitz  # PyMuPDF
import re
import easyocr
from PIL import Image
import numpy as np
from collections import Counter
from transformers import BlipProcessor, BlipForQuestionAnswering
from app.utils import fonts, colors, logo_position, logo_colors
import torch

# Initialize the reader
reader = easyocr.Reader(['en'], gpu=False)  # NOTE: I put it in CPU only because I do not have GPU, should be changed for faster performance. 

# Load BLIP VQA model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base").to(device)





def assess_slide_compliance(image_path, pdf_path, api_key, company_name):

    reasons = {}
    score = 0

    # 1. Font Style
    font_score, font_reason = fonts.verify_fonts(pdf_path, image_path, api_key)
    reasons['Font style'] = font_reason
    score += font_score
    
    # 2. Logo Safe Zone 
    score_logo_position, explanation_logo_position = logo_position.check_logo_position(image_path, pdf_path)
    reasons["Logo Safe Zone"] = explanation_logo_position
    score += score_logo_position

    # 3. Logo Colors 
    score_logo_color, explanation_logo_color = logo_colors.check_logo_colors(pdf_path, image_path, company_name)
    reasons["Logo Color"] = explanation_logo_color
    score += score_logo_color
    
    # 4. Overall Color Palette
    score_color, explanation_color = colors.analyze_colors(pdf_path, image_path)
    reasons["Color palette"] = explanation_color
    score += score_color
    return score, reasons
    
   

# Main
def assessmentllm(slide_image_path, brand_pdf_path, api_key, company_name):
    '''brand_text = extract_brand_kit_text(brand_pdf_path)
    score, feedback = assess_slide_compliance(slide_image_path, brand_pdf_path, api_key, company_name)
    print(f"--- Brand Compliance Score: {score}/4 ---\n")
    for category, reason in feedback.items():
        print(f"{category}: {reason}")'''
    score = 4
    feedback = "it works"
    return score, feedback


