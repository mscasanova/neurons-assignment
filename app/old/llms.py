import torch
from transformers.utils.import_utils import is_flash_attn_2_available

from colpali_engine.models import ColQwen2, ColQwen2Processor

from PIL import Image
import fitz  # PyMuPDF
import io
import time

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=100)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")  # Ensure correct format
        images.append(image)
    return images
def llm_eval(image_path, brandkit_pdf_path):
    model_name = "vidore/colqwen2-v0.1"

    # Set device to CPU
    device = torch.device("cpu")
    start_time = time.time()
    print("Starting model loading...")
    # Initialize model and processor on CPU
    model = ColQwen2.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,  # Or you can use torch.float32 if bfloat16 is not supported on your CPU
        device_map="cpu",  # No need for GPU or CUDA configuration
        attn_implementation=None  # Temporarily disable flash attention
        #attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
    ).to(device).eval()
    model = ColQwen2.from_pretrained(model_name, torch_dtype=torch.float32, device_map="cpu").eval()
    print(f"Model loaded in {time.time() - start_time:.2f} seconds.")


    processor = ColQwen2Processor.from_pretrained(model_name)



    # Convert the brand kit PDF to images (one for each slide)
    brandkit_images = pdf_to_images(brandkit_pdf_path)
    resized_brandkit_images = [img.resize((128, 128)) for img in brandkit_images]  # or 384x384


    # Load the image to be evaluated
    query_image = Image.open(image_path)
    # Process the inputs (the query image and the brand kit pages as images)
    images = [query_image] + resized_brandkit_images  # The query image and brandkit images
    batch_images = processor.process_images(images).to(model.device)
    #batch_queries = processor.process_queries(queries).to(model.device)

    # Forward pass to get embeddings
    with torch.no_grad():
        image_embeddings = model(**batch_images)
        # Normalize embeddings to unit vectors (optional)
        image_embeddings = image_embeddings / image_embeddings.norm(p=2, dim=-1, keepdim=True)

        #query_embeddings = model(**batch_queries)

    # Define 4 evaluation questions
    criteria = [
        "Is the font style in the image consistent with the brand kit? Answer Yes or No",
        "Is the logo placed within the safe zone according to the brand kit? Answer Yes or No",
        "Are the logo colours consistent with those specified in the brand kit? Answer Yes or No",
        "Does the overall image match the brand's colour palette? Answer Yes or No"
    ]
    # Compute the scores for brand compliance based on similarity
    #scores = processor.score_multi_vector(query_embeddings, image_embeddings)
    score = 0
    threshold = 15.0  # You may need to tune this
    reasoning = {}

    for i, criterion in enumerate(criteria):
        print(f"Evaluating criterion {i + 1}: {criterion}")
        query = f"{criterion}"
        query_embedding = processor.process_queries([query]).to(device)
        query_embedding = query_embedding / query_embedding.norm(p=2, dim=-1, keepdim=True)

        with torch.no_grad():
            query_vector = model(**query_embedding)
            query_vector = query_vector / query_vector.norm(p=2, dim=-1, keepdim=True)


        similarity = processor.score_multi_vector(query_vector, image_embeddings)
        max_similarity = similarity.max().item()

        print(f" → Similarity score: {max_similarity:.2f}")

        # Ask the model to generate reasoning (like GPT does) based on the similarity score
        prompt = f"Given the similarity score of {max_similarity:.2f}, explain why the image {'complies' if max_similarity > threshold else 'does not comply'} with the following criterion: '{criterion}'"

        # Generate reasoning using the model (GPT-like reasoning)
        reasoning_text = model.generate_text(prompt)  # You may need to replace this with actual model call for text generation

        reasoning[criterion] = reasoning_text

        if max_similarity > threshold:
            score += 1

    return score, reasoning