from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from app.models import llms_complex
import shutil
import os

app = FastAPI(title="Brand Compliance Checker")

# Define a function to return a description of the app
def get_app_description():
    return (
        "Welcome to the Brand Assessment API!"
        "This API allows you to assess brand alignment by analyzing an image and a brand kit PDF."
        "Use the '/upload/' endpoint with a POST request to upload an image file, a PDF file, along with your company name."
        "Example usage: POST to '/upload/' with form data including 'image', 'pdf', and 'company_name'."
    )


# Define the root endpoint to return the app description
@app.get("/") # to define a path use : @app.get("/") so when someone visits that path then the functions below are called
async def root():
	return {"message": get_app_description()}

@app.post("/upload/")
async def upload_files(
    image: UploadFile = File(...),
    pdf: UploadFile = File(...)
):
    try:
        # Notify the user that the process may take a few minutes
        processing_message = "Processing your request. This may take a few minutes..."
        if not os.path.exists("temp"):
              os.makedirs("temp")

        # Save the uploaded image
        image_path = f"temp/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Save the uploaded PDF
        pdf_path = f"temp/{pdf.filename}"
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(pdf.file, buffer)
        print(processing_message)

        # Call the assessllm function
        value, reasoning = llms_complex.assessmentllm(image_path, pdf_path, API_KEY, company_name)
        
        # Clean up temporary files
        os.remove(image_path)
        os.remove(pdf_path)
        
        # Return the response
        return JSONResponse(content={"value": value, "reasoning": reasoning})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)







'''brandkit_pdf_path = "Neurons_brand_kit.pdf"
# Load query image
image_path = "neurons_1.png"
company_name = "Neurons"
llms_complex.assessmentllm(image_path, brandkit_pdf_path, API_KEY, company_name)
'''