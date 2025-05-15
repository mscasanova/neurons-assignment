import gradio as gr
import requests

# Define the URL for the backend API endpoint that will process the uploaded files.
API_URL = "http://127.0.0.1:8000/upload/"

# Define the URL for the company logo image to be displayed in the interface.
COMPANY_LOGO_URL = "https://github.com/mscasanova/neurons-assignment/blob/main/app/frontend/company_logo.png?raw=true"

# Define a list of primary brand colors to be used for styling the interface.
PRIMARY_COLORS = ["#85A0FE", "#FE839C", "#FFD14C", "#AA82FF", "#380F57"]

def assess_brand_compliance(image, pdf):
    """
    Sends the uploaded image and PDF files to the backend API for brand compliance assessment.

    image: An uploaded image file object from Gradio. (image to be assessed uploaded by user)
    pdf: An uploaded PDF file object from Gradio.  (brand kit pdf uploaded by user)

    Returns: dictionary containing the JSON response from the API.
    """
    # Prepare a dictionary of files to be sent in the POST request.
    files = {
        "image": (image.name, image, "image/png"),
        "pdf": (pdf.name, pdf, "application/pdf"),
    }

    try:
        # Send a POST request to the API_URL with the uploaded files.
        response = requests.post(API_URL, files=files)
        # Check if the request was successful (status code 200).
        if response.status_code == 200:
            # If successful, parse the JSON response from the API and return it.
            return response.json()
        else:
            # If the request failed, return an error dictionary containing the status code and error text.
            return {"error": f"Server returned {response.status_code}: {response.text}"}
    except Exception as e:
        # If any exception occurs during the API request, return an error dictionary with the exception message.
        return {"error": str(e)}

def create_interface():
    """
    Creates the Gradio user interface for the brand compliance assessment tool.

    Returns: Gradio Blocks object representing the interface.
    """
    # Define custom CSS to style the Gradio interface.
    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Lexend:wght@500;700&display=swap');

    body {{
        background-color: {PRIMARY_COLORS[0]}; /* Set the background color of the body */
        font-family: 'Inter', sans-serif; /* Use the Inter font for the body text */
        color: {PRIMARY_COLORS[4]}; /* Set the default text color */
        margin: 0;
        padding: 0;
    }}

    h1, h2, h3, .gr-button {{
        font-family: 'Lexend', sans-serif !important; /* Use the Lexend font for headings and buttons */
    }}

    .gradio-container {{
        border-radius: 16px; /* Add rounded corners to the main container */
        padding: 30px; /* Add padding around the content */
        max-width: 900px; /* Set a maximum width for the container */
        margin: 30px auto; /* Center the container horizontally with top and bottom margin */
        background-color: white; /* Set the background color of the container to white */
        box-shadow: 0 8px 24px rgba(0,0,0,0.1); /* Add a subtle box shadow */
    }}

    h1 {{
        color: {PRIMARY_COLORS[4]}; /* Set the color of the main heading */
        display: flex; /* Use flexbox to align items horizontally */
        align-items: center; /* Vertically align items in the flex container */
        gap: 10px; /* Add some space between the logo and the heading text */
    }}

    h1 img {{
        vertical-align: middle; /* Vertically align the image within the heading */
        height: 30px; /* Reduced the height of the logo */
    }}

    .gr-button-primary {{
        background-color: {PRIMARY_COLORS[1]}; /* Set the background color for primary buttons */
        color: white; /* Set the text color for primary buttons */
        border: none; /* Remove the button border */
        font-weight: 600; /* Make the button text bold */
    }}

    .gr-button-primary:hover {{
        background-color: {PRIMARY_COLORS[3]}; /* Change the background color on hover */
    }}
    """

    # Create a Gradio Blocks interface with the defined CSS and a soft theme.
    with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
        # Create a column to group elements at the top (header).
        with gr.Column(elem_id="header"):
            # Display the company logo image.
            gr.Image(value=COMPANY_LOGO_URL, show_label=False, interactive=False, height=30)
            # Display the main heading of the tool.
            gr.HTML("<h1>Brand Compliance Assessment Tool</h1>")
        # Add a markdown component to provide a brief description.
        gr.Markdown(f"<span style='color: {PRIMARY_COLORS[3]}; font-size: 1.1em;'>Upload your creative and brand kit for compliance scoring.</span>")

        # Create a row to arrange the input file components side by side.
        with gr.Row():
            # File upload component for the slide image, accepting JPG, JPEG, and PNG files.
            image_input = gr.File(label="Slide Image", file_types=[".jpg", ".jpeg", ".png"])
            # File upload component for the brand kit PDF, accepting PDF files.
            pdf_input = gr.File(label="Brand Kit PDF", file_types=[".pdf"])

        # JSON output component to display the assessment results from the API.
        output = gr.JSON(label="Assessment Results")

        # Primary button to trigger the brand compliance assessment.
        submit = gr.Button("Assess Brand Compliance", variant="primary")

        # Define the event listener for the submit button.
        submit.click(fn=assess_brand_compliance, inputs=[image_input, pdf_input], outputs=output)

    return demo

# This block ensures the create_interface function is called and the Gradio app is launched
if __name__ == '__main__':
    create_interface().launch(share=True) # share=True --> makes it shareable online.