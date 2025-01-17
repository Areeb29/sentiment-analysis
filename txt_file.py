import os
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from io import BytesIO

# Add custom styles
def add_custom_styles():
    st.markdown(f"""
        <style>
        /* Background styling */
        .stApp {{
            background-color: #D9DFF0;
            color: #333333;
            font-family: 'Arial', sans-serif;
            padding: 10px;
        }}

        /* Centered and styled logo */
        .logo-container {{
            text-align: center;
            margin: 10px auto;
        }}
        .logo-container img {{
            width: 200px; /* Adjust width for compact display */
            margin-bottom: 10px; /* Reduce bottom margin */
        }}

        /* Header styling */
        h1 {{
            color: #4B0082;
            text-align: center;
            font-size: 28px; /* Smaller font size */
            margin-bottom: 15px; /* Reduce margin below header */
        }}

        /* Buttons */
        .stButton > button {{
            background-color: #606BA6;
            color: white;
            font-size: 14px; /* Smaller button font */
            padding: 8px 16px; /* Reduce padding for compact buttons */
            border-radius: 5px; /* Slightly rounded corners */
            border: none;
            margin: 10px auto; /* Center and compact margin */
        }}
        .stButton > button:hover {{
            background-color: #6A5ACD;
        }}

        /* File uploader styling */
        .stFileUploader {{
            margin: 5px 0; /* Compact file uploader margin */
        }}
        </style>
    """, unsafe_allow_html=True)


# Function to analyze the uploaded PDFs
def analyze_invoices(files):
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")

    if not endpoint or not key:
        st.error("Please set the AZURE_ENDPOINT and AZURE_KEY environment variables.")
        return None

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    results = ""

    for uploaded_file in files:
        try:
            file_content = uploaded_file.read()
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-invoice", file_content, locale="en-US", content_type="application/octet-stream"
            )
            invoices: AnalyzeResult = poller.result()

            results += f"Processing file: {uploaded_file.name}\n"
            if invoices.documents:
                for idx, invoice in enumerate(invoices.documents):
                    results += f"--------Analyzing invoice #{idx + 1}--------\n"
                    if invoice.fields:
                        for field_name, field_value in invoice.fields.items():
                            results += f"{field_name}: {field_value.get('content')} (Confidence: {field_value.get('confidence')})\n"

                    results += "Invoice items:\n"
                    items = invoice.fields.get("Items")
                    if items:
                        for idx, item in enumerate(items.get("valueArray", [])):
                            results += f"...Item #{idx + 1}\n"
                            for key, value in item.get("valueObject", {}).items():
                                results += f"......{key}: {value.get('content')} (Confidence: {value.get('confidence')})\n"

        except Exception as e:
            results += f"Error processing file {uploaded_file.name}: {e}\n"

        results += "\n"  # Add a blank line between results for each file

    return results

# Streamlit App UI
add_custom_styles()

# Logo Section
# Logo Section
col1, col2, col3 = st.columns([2, 5, 1])

# Place the image in the center column
with col2:
    st.image("YoutubeLogo.png", width=300)


# App Title
st.title("Invoice Processing with Mango Analytics")

# File uploader
st.markdown("### Upload your File below 👇")
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Run Analysis 🚀"):
        # Run analysis and display a progress indicator
        with st.spinner("Analyzing PDFs... please wait ⏳"):
            output = analyze_invoices(uploaded_files)

        if output:
            st.success("🎉 Analysis complete! Download your results below.")
            
            # Save output to a downloadable text file
            output_file = BytesIO()
            output_file.write(output.encode("utf-8"))
            output_file.seek(0)

            # Display the download button
            st.download_button(
                label="📥 Download Results",
                data=output_file,
                file_name="invoice_analysis_results.txt",
                mime="text/plain"
            )
