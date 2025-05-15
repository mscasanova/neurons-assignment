# Task a) Replace Streamlit frontend with Gradio + custom styling
import gradio as gr
import requests

API_URL = "http://127.0.0.1:8000/upload/"
COMPANY_LOGO = "company_logo.png"
PRIMARY_COLORS = ["#85A0FE", "#FE839C", "#FFD14C", "#AA82FF", "#380F57"]

def assess_brand_compliance(image, pdf, company_name):
    files = {
        "image": (image.name, image, "image/png"),
        "pdf": (pdf.name, pdf, "application/pdf"),
    }
    data = {"company_name": company_name}

    try:
        response = requests.post(API_URL, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Server returned {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def create_interface():
    css = f"""
    body {{
        background-color: {PRIMARY_COLORS[0]};
        font-family: 'Segoe UI', sans-serif;
        color: {PRIMARY_COLORS[4]};
    }}
    .gradio-container {{
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 0 12px rgba(0,0,0,0.1);
        background-color: white;
    }}
    """
    with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
        gr.Markdown("# <img src='company_logo.png' width='50'/> Brand Compliance Assessment Tool")
        gr.Markdown("Upload your creative and brand kit for compliance scoring.")
        with gr.Row():
            image_input = gr.File(label="Slide Image", file_types=[".jpg", ".jpeg", ".png"])
            pdf_input = gr.File(label="Brand Kit PDF", file_types=[".pdf"])
            company_input = gr.Textbox(label="Company Name")
        output = gr.JSON(label="Results")
        submit = gr.Button("Assess Brand Compliance", variant="primary")
        submit.click(fn=assess_brand_compliance, inputs=[image_input, pdf_input, company_input], outputs=output)
    return demo

if __name__ == '__main__':
    create_interface().launch()
