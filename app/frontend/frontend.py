import gradio as gr
import requests

API_URL = "http://127.0.0.1:8000/upload/"
COMPANY_LOGO = "company_logo.png"
PRIMARY_COLORS = ["#85A0FE", "#FE839C", "#FFD14C", "#AA82FF", "#380F57"]  # Blue, Pink, Yellow, Purple, Dark

def assess_brand_compliance(image, pdf):
    files = {
        "image": (image.name, image, "image/png"),
        "pdf": (pdf.name, pdf, "application/pdf"),
    }

    try:
        response = requests.post(API_URL, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Server returned {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def create_interface():
    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Lexend:wght@500;700&display=swap');

    body {{
        background-color: {PRIMARY_COLORS[0]};
        font-family: 'Inter', sans-serif;
        color: {PRIMARY_COLORS[4]};
        margin: 0;
        padding: 0;
    }}

    h1, h2, h3, .gr-button {{
        font-family: 'Lexend', sans-serif !important;
    }}

    .gradio-container {{
        border-radius: 16px;
        padding: 30px;
        max-width: 900px;
        margin: 30px auto;
        background-color: white;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }}

    h1 {{
        color: {PRIMARY_COLORS[4]};
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    h1 img {{
        vertical-align: middle;
        height: 40px;
    }}

    .gr-button-primary {{
        background-color: {PRIMARY_COLORS[1]};
        color: white;
        border: none;
        font-weight: 600;
    }}

    .gr-button-primary:hover {{
        background-color: {PRIMARY_COLORS[3]};
    }}
    """

    with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
        with gr.Row():
            gr.HTML(f"<h1><img src='{COMPANY_LOGO}' alt='Logo' /> Brand Compliance Assessment Tool</h1>")
        gr.Markdown(f"<span style='color: {PRIMARY_COLORS[3]}; font-size: 1.1em;'>Upload your creative and brand kit for compliance scoring.</span>")

        with gr.Row():
            image_input = gr.File(label="Slide Image", file_types=[".jpg", ".jpeg", ".png"])
            pdf_input = gr.File(label="Brand Kit PDF", file_types=[".pdf"])

        output = gr.JSON(label="Assessment Results")
        submit = gr.Button("Assess Brand Compliance", variant="primary")

        submit.click(fn=assess_brand_compliance, inputs=[image_input, pdf_input], outputs=output)

    return demo

if __name__ == '__main__':
    create_interface().launch(share=True)
