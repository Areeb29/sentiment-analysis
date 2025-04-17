import os
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from io import BytesIO

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Invoice Analyzer",
    layout="wide"
)

# ----------------- CUSTOM CSS -----------------
# ----------------- CUSTOM CSS -----------------
# ----------------- CUSTOM CSS -----------------
st.markdown("""
    <style>
    /* Entire background including body */
    body {
        background-color: #f0f4f8 !important;
        color: #333333 !important;
    }

    /* Main container */
    .main {
        background-color: #f0f4f8 !important;
    }

    /* Block container that wraps Streamlit components */
    .main .block-container {
        background-color: #f0f4f8 !important;
        padding-top: 2rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #e0e4e8 !important;
        color: #000000 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p {
        color: #000000 !important;
    }

    /* Optional: content centering helper */
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONTENT -----------------
with st.sidebar:
    st.header("📄 Project Info")
    st.markdown("""
    This tool leverages **Azure Document Intelligence** to analyze invoice PDFs.

    **Features:**
    - Extract fields and line items using `prebuilt-invoice` model  
    - Confidence scoring on every field  
    - Download results as plain text  

    **Tech Stack:**
    - Python  
    - Streamlit  
    - Azure AI Document Intelligence  

    💡 Developed for automating invoice data extraction.
    """)

# ----------------- MAIN CONTENT -----------------
st.markdown("<div class='centered'>", unsafe_allow_html=True)
st.markdown("<h2 style='color: #0A84FF;'>Invoice Analyzer using Azure Model</h2>", unsafe_allow_html=True)
st.markdown("<p>Upload your Invoice PDFs below 👇</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- ANALYZE FUNCTION -----------------
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

# ----------------- FILE UPLOADER -----------------
uploaded_files = st.file_uploader(
    "Drag and drop files here",
    type=["pdf"],
    accept_multiple_files=True
)

# ----------------- RUN ANALYSIS BUTTON -----------------
if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded:")
    for f in uploaded_files:
        st.write(f.name)

    # Add "Run Analysis" button
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
