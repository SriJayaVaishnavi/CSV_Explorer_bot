import streamlit as st
import pandas as pd
from router import route_query_to_tool
from tools import TOOL_FUNCTIONS

import base64

# Set Streamlit config
st.set_page_config(page_title="CSV Explorer", layout="centered")

# === Add Background & Styling ===
def add_bg_from_local(image_file):
    css = """
    <style>
    .stApp {
        background: radial-gradient(
            circle at top right,
            #4a4a4a 0%,
            #636363 25%,
            #7a7a7a 50%,
            #8f8f8f 75%,
            #a3a3a3 100%
        );
        background-size: 200% 200%;
        background-position: center;
        background-attachment: fixed;
    }
    .stMarkdown {
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    p, label, div {
        color: white !important;
    }
    /* File uploader styling */
    div[data-testid="stFileUploader"] {
        width: 100%;
    }
    div[data-testid="stFileUploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px dashed rgba(255, 255, 255, 0.4) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploadDropzone"] p {
        color: white !important;
    }
    .uploadedFile {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(8px);
    }
    .stTextInput > div > div > input {
        color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.6) !important;
    }
    .stDataFrame {
        background-color: rgba(255,255,255,0.1) !important;
    }
    .stButton > button {
        background-color: rgba(255,255,255,0.15);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .stButton > button:hover {
        background-color: rgba(255,255,255,0.25);
        border: 1px solid rgba(255,255,255,0.3);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# 🐝 Add background (path to saved image)
add_bg_from_local("bg.png")

# === Streamlit App Logic ===
st.title("📊CSV Explorer")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully!")
    st.dataframe(df.head())

    query = st.text_input("Ask a question about the data")

    if query:
        with st.spinner("Analyzing..."):
            tool_name = route_query_to_tool(query)
            st.markdown(f"**Selected Tool:** `{tool_name}`")
            print(f"Debug: Tool name returned by router: '{tool_name}'")

            if tool_name.lower() in TOOL_FUNCTIONS:
                TOOL_FUNCTIONS[tool_name.lower()](df, query)
            else:
                st.error("Tool not recognized.")
