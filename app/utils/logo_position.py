import fitz  # PyMuPDF
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import os

try:
  # Load model and processor
  processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
  model = Blip2ForConditionalGeneration.from_pretrained(
      "Salesforce/blip2-opt-2.7b",
      torch_dtype=torch.float16,
  )
  device = "cuda" if torch.cuda.is_available() else "cpu"
  model.to(device)

except Exception as e:
    print(f"Error initializing the Vision-to-Text model: {e}")

def extract_brand_kit_text(pdf_path):
    """
    Extracts text from a pdf using fitz.
    
    pdf_path: Path to the pdf file.

    Returns: Extracted text as a string.
    """
    # Open pdf document
    doc = fitz.open(pdf_path)
    full_text = ""
    # Extract text from each page and add it to the final string. 
    for page in doc:
      page_text = page.get_text() 
      if "logo" in page_text.lower():
          full_text +=  page_text

    return full_text


def check_logo_position(image_path, pdf_path):
    """
    Determines if the logo is in the right position and if it is properly sized.
    
    pdf_path: Path to the pdf file.
    image_path: Path to the slide image to be assessed.

    Returns: 1 if it is right, 0 if not. And a text explaining. 
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
      instructions = extract_brand_kit_text(pdf_path)
      # Compose prompt
      prompt = f"""
      You are a design reviewer. Given the following slide image, determine if the company logo is positioned correctly and has the proper size according to these instructions:

      {instructions}

      IMPORTANT: Reply with either:
      "1: [Your explanation]" — if the logo is properly positioned and sized.
      "0: [Your explanation]" — if the logo is not correctly positioned or sized.

      Use exactly this format.

      """
      # Process and generate
      inputs = processor(images=image, text=prompt, return_tensors="pt").to(device, torch.float16)
      output = model.generate(**inputs, max_new_tokens=100)
      result = processor.tokenizer.decode(output[0], skip_special_tokens=True)
      result_lower = result.lower()

      if result.startswith("1:") or result_lower.startswith("yes") or "correct" in result_lower:
        if result.startswith("1:"):
          return 1, "Logo is correctly positioned and sized."#result.strip(":")
        elif result_lower.startswith("yes") or "correct" in result_lower:
          return 1, "Logo is correctly positioned and sized." #result_lower
      elif result.startswith("0:") or result_lower.startswith("no") or "incorrect" in result_lower or "not correct" in result_lower:
        if result.startswith("0:"):
            return 0, "Logo is not positioned or sized correctly." #result.strip(":")  # If it starts with "0:", strip it
        else:
            return 0, "Logo is not positioned or sized correctly." #result  # Don't strip if it's just "no", "incorrect", etc.


      else:
          return -1, f"Unclear model output: {result}"

    except FileNotFoundError as e:
        return {f"Error: Could not open file: {e.filename}"}
    except Exception as e:
        return {f"An unexpected error occurred during logo color check: {e}"}


