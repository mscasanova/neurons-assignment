import fitz  # PyMuPDF for PDF processing
from PIL import Image
import numpy as np
from transformers import pipeline, GPT2Tokenizer
import os

def extract_colors_from_pdf(pdf_path):
    """
    Extract primary and secondary colors from the brand kit PDF.
    
    pdf_path: Path to the pdf file.
    
    Returns: list of detected colors in hex format.
    """
    doc = fitz.open(pdf_path)
    extracted_colors = set()
    try: 
        for page_number in range(len(doc)):
            page = doc[page_number]
            pix = page.get_pixmap()  # Convert page to an image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert the image to a NumPy array for pixel analysis
            img_array = np.array(img)
            img_array = img_array.reshape(-1, 3)  # Flatten the image array

            # Extract unique colors and convert to hex
            unique_colors = np.unique(img_array, axis=0)
            for color in unique_colors:
                hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
                extracted_colors.add(hex_color)
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except fitz.FileDataError as e:
        print(f"Error: Could not open or read PDF file '{pdf_path}'. Reason: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while processing '{pdf_path}': {e}")
        return []


    return list(extracted_colors)


def extract_colors_from_slide(slide_path):
    """
    Extract colors used in the slide image.

    slide_path: Path to the slide image to be assessed. 

    Returns: list of detected colors in hex format.
    """
    try:
        img = Image.open(slide_path).convert("RGB")
        img_array = np.array(img)
        img_array = img_array.reshape(-1, 3)  # Flatten the image array

        # Extract unique colors and convert to hex
        unique_colors = np.unique(img_array, axis=0)
        extracted_colors = set()
        for color in unique_colors:
            hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            extracted_colors.add(hex_color)

        return list(extracted_colors)
    except FileNotFoundError:
        print(f"Error: Image file not found at '{slide_path}'")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while processing '{slide_path}': {e}")
        return []


def analyze_colors_with_llm(pdf_colors, slide_colors):
    """
    Use an LLM to analyze and compare colors from the PDF and slide.

    pdf_colors: list of colors from brand kit pdf. 
    slide_colors: list of colors from the image slide to be assessed. 

    Returns: 1 if the colors comply with the brand kit, 0 otherwise. And an explanation.
    """
    try:
        # Initialize an open-source LLM pipeline
        llm = pipeline("text-generation", model="gpt2", device=-1)  # Use CPU (-1)

        # Construct a concise prompt
        prompt = f"""
        Brand colors: {pdf_colors[:10]}... (total {len(pdf_colors)} colors)
        Slide colors: {slide_colors[:10]}... (total {len(slide_colors)} colors)

        Are the colors in the slide from the brand colors? Provide a 1 if compliant and 0 if not, with an explanation.
        """

        # Tokenize and truncate the prompt to avoid exceeding the token limit
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        max_length = 1024  # Maximum sequence length for GPT-2
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_length)

        # Generate a response
        response = llm(prompt, max_new_tokens=50, num_return_sequences=1, pad_token_id=50256)
        output = response[0]["generated_text"]

        # Parse the LLM's response
        if "1" in output.split():
            return 1, output
        else:
            return 0, output
    except Exception as e:
        error_message = f"An error occurred during LLM analysis: {e}"
        print(error_message)
        return None, error_message

def analyze_colors(pdf_path, slide_path):
    """
    Main function to analyze color compliance.

    pdf_path: Path to the pdf file.
    slide_path:  Path to the slide image to be assessed.

    Returns: 1 if the colors comply with the brand kit, 0 otherwise. And an explanation.
    """
    # Extract colors from the brand kit PDF
    pdf_colors = extract_colors_from_pdf(pdf_path)

    # Extract colors used in the slide image
    slide_colors = extract_colors_from_slide(slide_path)

    # Use LLM to analyze color compliance
    score, explanation = analyze_colors_with_llm(pdf_colors, slide_colors)

    return score, explanation


