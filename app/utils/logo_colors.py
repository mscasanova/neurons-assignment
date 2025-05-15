from PIL import Image
import numpy as np
import fitz  # PyMuPDF
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import re
import matplotlib
import os

try:
  # Load model and processor
  processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
  model = Blip2ForConditionalGeneration.from_pretrained(
      "Salesforce/blip2-flan-t5-xl",
      torch_dtype=torch.float16,
  )
  device = "cuda" if torch.cuda.is_available() else "cpu"
  model.to(device)

except Exception as e:
    print(f"Error initializing the Vision-to-Text model: {e}")




def extract_logo_colors_from_pdf(pdf_path):
    """
    Extracts hex color codes from the text of a brand kit PDF.

    pdf_path: Path to the pdf file.

    Returns: list of detected colors in hex format.
    """
    try:
      doc = fitz.open(pdf_path)
      extracted_colors = set()
      hex_color_pattern = r'#(?:[0-9a-fA-F]{3}){1,2}\b'

      for page_number in range(len(doc)):
          page = doc[page_number]
          page_text = page.get_text()
          if "primary colors" in page_text.lower():
            # Find all hex color codes in the page text
            found_colors = re.findall(hex_color_pattern, page_text)
            for color in found_colors:
                extracted_colors.add(color.upper())  # Normalize to uppercase for consistency

      return list(extracted_colors)
    except FileNotFoundError:
        return {"Error: PDF file not found"}
    except fitz.FileDataError as e:
        print(f"Error: Could not open or read PDF file '{pdf_path}'. Reason: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while processing '{pdf_path}' for logo colors: {e}")
        return []




def check_logo_colors(image_path, pdf_path):
    """
    Determines if the logo uses the correct colors.
    
    pdf_path: Path to the pdf file.
    image_path: Path to the slide image to be assessed.

    Returns: 1 if it uses the proper colors, 0 if not. And a text explaining. 
    """
    if not os.path.exists(image_path):
      error_message = f"Error: Logo image file not found at '{image_path}'"
      print(error_message)
      return []

    if not os.path.exists(pdf_path):
      error_message = f"Error: Brand kit PDF file not found at '{pdf_path}'"
      print(error_message)
      return []
    try:
      # Load image
      image = Image.open(image_path).convert("RGB")
      
      # Extract instruction text from PDF
      brandkit_colors = extract_logo_colors_from_pdf(pdf_path)
      # Compose prompt
      prompt = "What colors are used in the company logo?"
      
      # Process and generate
      inputs = processor(images=image, text=prompt, return_tensors="pt").to(device, torch.float16)
      output = model.generate(**inputs, max_new_tokens=100)
      result = processor.tokenizer.decode(output[0], skip_special_tokens=True)
      
      # Get all named colors in matplotlib
      color_name_to_hex = matplotlib.colors.CSS4_COLORS
      colors_llm = []
      mentioned_names = set(word.lower() for word in re.findall(r"\b[a-zA-Z]+\b", result))
      for color in mentioned_names:
        try:
          hex_value = color_name_to_hex.get(color.lower(), "Color not found")
          colors_llm.append(hex_value)
        except:
          continue

      logo_colors = []
      for color in colors_llm:
        if color != "Color not found" and color != "#FFFFFF" and color != "#000000":
          logo_colors.append(color)

      logo_colors_set = set(logo_colors)
      if logo_colors_set.issubset(brandkit_colors):
        return 1, "The logo uses only the brand colors."
      else:
        return 0, "The logo includes colors not in the brand kit."
      
    except FileNotFoundError as e:
        return {f"Error: Could not open file: {e.filename}"}
    except Exception as e:
        return {f"An unexpected error occurred during logo color check: {e}"}






