import fitz  # PyMuPDF
from PIL import Image
from torchvision import transforms
import torch
import torchvision.models as models
import easyocr
import requests
import matplotlib.font_manager as fm
from os.path import basename, splitext
import numpy as np



def fetch_google_fonts(api_key):
    """
    Fetch font family names from Google Fonts API.
    Returns a list of font names.
    """
    try: 
        response = requests.get(f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}")
        if response.status_code == 200:
            fonts_data = response.json()
            return [font["family"] for font in fonts_data["items"]]
    except Exception as e:
        print(f"Error fetching google fonts: {e}")
        return []
    
def get_system_fonts():
    """
    Retrieve a list of system-installed font names by parsing font file paths.
    """
    try:
        # Extract font names from file paths
        font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        font_names = [splitext(basename(font_path))[0] for font_path in font_paths]
        return font_names
    except Exception as e:
        print(f"Error fetching system fonts: {e}")
        return []
    
def build_known_fonts(api_key):
    """
    Combine fonts from Google Fonts API and system-installed fonts.
    """
    google_fonts = fetch_google_fonts(api_key)
    system_fonts = get_system_fonts()
    # Add any other known fonts manually (e.g., from Adobe Fonts)
    manual_fonts = ["Lexend", "Inter", "Arial", "Helvetica", "Times New Roman"]
    
    # Merge all fonts into a single set
    known_fonts = set(google_fonts + system_fonts + manual_fonts)
    return known_fonts





def analyze_slide_fonts(slide_path, model, api_key):
    """
    Analyze fonts used in the slide image using a vision transformer (ViT) model.
    Returns a set of predicted font names.
    """
    try:
        image = Image.open(slide_path).convert("RGB")
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        input_tensor = preprocess(image).unsqueeze(0)
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        known_fonts = build_known_fonts(api_key)
        font_mapping = {i: font for i, font in enumerate(known_fonts)}
        # Fallback for unmapped predictions
        font_name = font_mapping.get(predicted.item(), f"Unknown Font (Class {predicted.item()})")
        return {font_name}
    except FileNotFoundError:
        return {"Error: Slide image not found"}
    except RuntimeError as runtime_err:
        return {f"Runtime error: {runtime_err}"}
    except Exception as e:
        return {f"Unexpected font analysis error: {e}"}
    


    

def extract_written_fonts_from_image(image, api_key):
    """
    Extract font names written explicitly in a slide image using EasyOCR.
    Returns a set of font names if detected.
    """
    try: 
        reader = easyocr.Reader(['en'])
        # Convert PIL image to NumPy array
        image_np = np.array(image)

        # Extract text using EasyOCR
        ocr_results = reader.readtext(image_np)

        # Known font names or keywords to look for
        known_fonts = build_known_fonts(api_key)
        detected_fonts = set()
        for _, text, _ in ocr_results:  # EasyOCR returns [bbox, text, confidence]
            for font in known_fonts:
                if font.lower() in text.lower():
                    detected_fonts.add(font)

        return detected_fonts
    except Exception as e:
        return {f"Unexpected error when extracting font names written explicitly in a slide image using EasyOCR.: {e}"}
    

def analyze_pdf_fonts(pdf_path, model, api_key):
    """
    Analyze fonts used in a PDF file by converting each page to an image
    and using the `analyze_slide_fonts` function for font detection.
    Returns a set of all fonts detected across the PDF.
    """
    try:
        detected_fonts = set()
        doc = fitz.open(pdf_path)

        for page_number in range(len(doc)):
            page = doc[page_number]
            pix = page.get_pixmap()  # Render page as an image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            written_fonts = extract_written_fonts_from_image(img, api_key)
            detected_fonts.update(written_fonts)

            if not written_fonts:
                # Save the image temporarily in memory (or use a temporary file)
                slide_path = f"temp_page_{page_number}.png"
                img.save(slide_path)

                # Use the `analyze_slide_fonts` function to detect fonts in the image
                fonts_in_slide = analyze_slide_fonts(slide_path, model, api_key)
                detected_fonts.update(fonts_in_slide)
        return detected_fonts
    
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except RuntimeError as rt:
        print(f"Rendering or OCR issue while analyzing PDF: {rt}")
    except Exception as e:
        print(f"Unexpected error during PDF font analysis: {e}")
    

def compare_fonts(pdf_fonts, slide_fonts):
    """
    Compare fonts from the PDF and slide image.
    Returns (1, explanation) if fonts match, otherwise (0, explanation).
    """
    if slide_fonts.issubset(pdf_fonts):
        return 1, "All fonts used in the slide are present in the brandkit PDF."

    else:
        missing_fonts = slide_fonts - pdf_fonts
        print("pdf_fonts",pdf_fonts)
        print("slide_fonts", slide_fonts)
        return 0, f"Incorrect fonts detected: {', '.join(missing_fonts)}."


def verify_fonts(pdf_path, slide_path, api_key):
    # Load a pre-trained vision-based model
    model = models.resnet18(pretrained=True)
    model.eval()

    pdf_fonts = analyze_pdf_fonts(pdf_path, model, api_key)
    slide_fonts = analyze_slide_fonts(slide_path, model, api_key)

    result, explanation = compare_fonts(pdf_fonts, slide_fonts)
    return result, explanation
