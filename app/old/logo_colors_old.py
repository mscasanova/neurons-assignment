import os
from ultralytics import YOLO
from PIL import Image
import fitz  # PyMuPDF for PDF image extraction
from typing import List, Tuple
import easyocr
import shutil  # For deleting temporary directories
import cv2



def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image using EasyOCR.

    Args:
        image_path: Path to the image file.

    Returns:
        Extracted text as a string.
    """
    #try:
    color_img = cv2.imread(image_path)
    if color_img is None:
        raise ValueError(f"Failed to load image at {image_path}")
    
    gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
    # Initialize EasyOCR with English language
    reader = easyocr.Reader(['en'])
    # Extract text with bounding boxes and confidence scores
    # Pass the grayscale image directly instead of the file path
    results = reader.readtext(gray_img, detail=1)

    # Extract only the text part
    extracted_text = " ".join([res[1] for res in results if isinstance(res, (list, tuple)) and len(res) >= 2])
    return extracted_text.lower()  # Convert to lowercase for easier matching
    '''except Exception as e:
        print(f"Error extracting text from image {image_path}: {e}")
        return ""'''

def detect_logo(image_path: str, model, company_name, confidence_threshold: float = 0.5) -> List[Tuple[str, Image.Image]]:
    """
    Detects logos in an image using the YOLO model and filters by company names.

    Args:
        image_path: Path to the image file.
        model: Ultralytics YOLO model.
        confidence_threshold: Confidence threshold for detection.
        company_name: Company name to filter detections.

    Returns:
        A list of tuples containing the label and cropped logo images.
    """
    results = model(image_path)
    detections = results[0].boxes
    print("results: ", results)
    print('detections: ', detections)

    cropped_images = []
    image = Image.open(image_path)
    for detection in detections:
        print("conf: ", detection.conf)
        if detection.conf >= confidence_threshold:
            x1, y1, x2, y2 = map(int, detection.xyxy[0])  # Bounding box coordinates
            cropped_image = image.crop((x1, y1, x2, y2))
            label = detection.cls  # Assuming label is meaningful (e.g., company name)

            # Filter by company names if provided
            if company_name and company_name.lower() in label.lower():
                cropped_images.append((label, cropped_image))
            elif not company_name:
                cropped_images.append((label, cropped_image))
    """    if not cropped_images:
        print(f"No relevant logos detected in the image: {image_path}")
    """    
    return cropped_images

def extract_logo_colors(image: Image.Image, top_n: int = 5) -> List[Tuple[int, int, int]]:
    """
    Extracts the dominant colors from an image.

    Args:
        image: PIL Image to process.
        top_n: Number of dominant colors to extract.

    Returns:
        A list of RGB tuples representing the most common colors.
    """
    image = image.resize((200, 200))  # Resize for faster processing
    pixels = list(image.getdata())
    color_counts = {}
    for color in pixels:
        if color in color_counts:
            color_counts[color] += 1
        else:
            color_counts[color] = 1
    sorted_colors = sorted(color_counts.items(), key=lambda item: item[1], reverse=True)
    return [color[0] for color in sorted_colors[:top_n]]

def compare_colors(colors1: List[Tuple[int, int, int]], colors2: List[Tuple[int, int, int]]) -> Tuple[int, str]:
    """
    Compares two sets of colors and determines if they are the same.

    Args:
        colors1: List of RGB tuples for the first logo.
        colors2: List of RGB tuples for the second logo.

    Returns:
        A tuple containing a similarity score (1 for similar, 0 for different)
        and an explanation string.
    """
    if not colors1 and not colors2:
        return 0, "Both logo color sets are empty. Ensure the logos are properly detected and analyzed."
    elif not colors1:
        return 0, "The logo color set extracted from the first image is empty."
    elif not colors2:
        return 0, "The logo color set extracted from the second image is empty."

    # Calculate color similarity using Euclidean distance
    avg_distance = sum([sum([(c1 - c2) ** 2 for c1, c2 in zip(color1, color2)]) ** 0.5 for color1, color2 in zip(colors1, colors2)]) / len(colors1)

    if avg_distance < 50:  # Arbitrary threshold for similarity
        return 1, f"The logos use similar colors with an average distance of {avg_distance:.2f}."
    else:
        return 0, f"The logos use different colors with an average distance of {avg_distance:.2f}."

def check_logo_colors(pdf_path, image_path, model, company_name):
    """
    Assess the color similarity of logos in a PDF and an image.

    Args:
        pdf_path: Path to the PDF file.
        image_path: Path to the image file.
        model: YOLO model.
        company_name: Company name to filter detections.

    Returns:
        A tuple of similarity score and explanation, or an error message.
    """
    # Create a temporary directory for saving PDF images
    temp_dir = "temp_pdf_images"
    os.makedirs(temp_dir, exist_ok=True)

    pdf_images = []
    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc[page_number]
        pix = page.get_pixmap()  # Render page as an image
        pdf_image_path = os.path.join(temp_dir, f"page_{page_number + 1}.jpg")
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(pdf_image_path)
        text = extract_text_from_image(pdf_image_path)
        if "logo" in text:  # Check if the word "logo" is in the text
            pdf_images.append(pdf_image_path)

    if not pdf_images:
        return 0, "No logos detected in the PDF."

    pdf_cropped_images = []
    for pdf_image_path in pdf_images:
        pdf_cropped_images += detect_logo(pdf_image_path, model, company_name)

    if not pdf_cropped_images:
        return 0, "No logos detected in the PDF."

    # Step 3: Detect logos in the slide image
    slide_cropped_images = detect_logo(image_path, model, company_name)
    if not slide_cropped_images:
        return 0, "No logos detected in the slide image."

    # Step 4: Extract colors and compare (same as before)
    try:
        pdf_colors = extract_logo_colors(pdf_cropped_images[0][1])
        slide_colors = extract_logo_colors(slide_cropped_images[0][1])
    except Exception as e:
        return 0, f"Error extracting colors from logos: {e}"
    
    # Cleanup: Remove the temporary directory after use
    shutil.rmtree(temp_dir, ignore_errors=True)

    return compare_colors(pdf_colors, slide_colors)



def assess_logo_colors(pdf_path, image_path, company_name):
    model = YOLO("yolov5s.pt")  # Use the small YOLOv5 model (fine-tune if needed)
    score, explanation = check_logo_colors(pdf_path, image_path, model, company_name)
    return score, explanation