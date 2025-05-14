import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from skimage.metrics import structural_similarity as ssim


def extract_slide_images(pdf_path, max_pages=5, scale=2.0):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(min(len(doc), max_pages)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append((page_num, np.array(img)))
    return images


def find_logo_in_slide(slide_img, logo_img, threshold=0.8):
    result = cv2.matchTemplate(slide_img, logo_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        top_left = max_loc
        h, w, _ = logo_img.shape
        logo_region = slide_img[top_left[1]:top_left[1]+h, top_left[0]:top_left[0]+w]
        return True, logo_region
    return False, None


def get_dominant_color(image, k=3):
    # Reshape and convert to float
    img_data = image.reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(img_data)
    colors = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(kmeans.labels_)
    dominant_color = colors[np.argmax(counts)]
    return dominant_color


def compare_colors(color1, color2):
    # Compute Euclidean distance between RGB values
    dist = np.linalg.norm(np.array(color1) - np.array(color2))
    score = max(0, 100 - dist)  # 100 if identical, lower otherwise
    return round(score, 2), f"Color distance: {dist:.2f}, similarity score: {score:.2f}/100"


def verify_logo_and_colors(pdf_path, logo_path):
    # Load logo image
    logo_img = cv2.imread(logo_path)
    logo_img_rgb = cv2.cvtColor(logo_img, cv2.COLOR_BGR2RGB)

    # Extract slides
    slides = extract_slide_images(pdf_path)

    for page_num, slide_img in slides:
        found, matched_region = find_logo_in_slide(slide_img, logo_img_rgb)
        if found:
            # Get dominant colors
            logo_color = get_dominant_color(logo_img_rgb)
            slide_logo_color = get_dominant_color(matched_region)

            score, explanation = compare_colors(logo_color, slide_logo_color)
            return score, explanation

    return 0, "Logo not found in first few slides."
