# AI Brand Compliance Checker

Welcome to the **AI Brand Compliance Checker**, a multimodal assessment tool that uses cutting-edge deep learning and large language models (LLMs) to evaluate whether marketing materials adhere to a brand's visual identity guidelines.

---

## 🚀 What Does It Do?

This tool assesses the **brand compliance** of uploaded creative materials (like slides or banners) against an official **brand kit (PDF)**. It performs the following checks:

- ✅ **Font Matching** – Ensures font usage aligns with your brand.
- ✅ **Logo Position & Size** – Checks placement and sizing against guidelines.
- ✅ **Logo Colors** – Validates logo colors against the brand palette.
- ✅ **Overall Color Palette** – Compares slide colors with those defined in the brand kit.

The result is a **score out of 4** with detailed reasoning.

---

## 📁 Project Structure
```
.
├── app/
│   ├── models/
│   │   └── complex_llms.py
│   ├── utils/
│   │   ├── colors.py
│   │   ├── fonts.py
│   │   ├── logo_colors.py
│   │   └── logo_position.py
│   └── frontend/
│       └── frontend.py
├── main.py
├── tests.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧰 Requirements

### Local Setup
- Python 3.10+
- Docker (for containerized deployment)
- Basic OS packages (Linux):
  - `libgl1-mesa-glx`
  - `libglib2.0-0`

---

## 📦 Installation Instructions

### ✅ Option 1: Docker (Recommended)

```bash
docker-compose up --build
```

- FastAPI API: http://localhost:8000/docs
- Gradio UI: http://localhost:8501

### ✅ Option 2: Manual Local Setup

```bash
# Clone the repository
git clone https://github.com/your-org/brand-compliance-checker.git
cd brand-compliance-checker

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload

# Run the frontend
python app/frontend/frontend.py
```

---

## 🧪 Running Tests

This repository includes a set of unit tests to verify the core logic.

```bash
# Make sure you are in the project root directory
pytest tests.py
```

The tests use mocking to simulate:
- Font verification
- Color palette compliance
- Logo position and color extraction
- End-to-end scoring pipeline

Ensure all test dependencies (e.g., `pytest`, `unittest`, `mock`) are installed and accessible in your Python environment.

---

## 🖼️ Sample Usage (API)
```bash
curl -X POST "http://localhost:8000/upload/" \
  -F image=@slide.png \
  -F pdf=@brandkit.pdf \
  -F company_name="Acme Corp"
```

---

## 🔐 Notes
- Some models use EasyOCR and pretrained ViT or BLIP2 models from HuggingFace
- Be patient: LLMs may take up to 1-2 minutes depending on input size

---

## 🧠 Authors
- Developed by [Your Name / Team / Org]