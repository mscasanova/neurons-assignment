import streamlit as st
import requests


# Set the FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000/upload/"

# Streamlit App
def main():
    st.title("Brand Assessment API")
    st.write("Upload an image and a brand kit PDF to assess brand alignment.")

    # File inputs
    image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if not image_file:
        st.error("Please upload an image file.")
        return


    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    # Text inputs for API key and company name
    company_name = st.text_input("Company Name")

    # Submit button
    if st.button("Submit"):
        # Input validation
        if not image_file:
            st.error("Please upload an image file.")
            return
        if not pdf_file:
            st.error("Please upload a PDF file.")
            return
        
        if not company_name:
            st.error("Please provide the company name.")
            return

        # Notify the user that the process might take time
        with st.spinner("Processing your request. This may take a few minutes..."):
            # Prepare files and data for the request
            files = {
                "image": (image_file.name, image_file, image_file.type),
                "pdf": (pdf_file.name, pdf_file, pdf_file.type),
            }
            data = {
                "company_name": company_name,
            }

            # Send the request to the FastAPI backend
            try:
                response = requests.post(BACKEND_URL, files=files, data=data)
                response_data = response.json()

                if response.status_code == 200:
                    st.success("Request processed successfully!")
                    st.write("### Result:")
                    st.json(response_data)
                else:
                    st.error("Error occurred:")
                    st.json(response_data)
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()