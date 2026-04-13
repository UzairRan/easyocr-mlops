import streamlit as st
import requests
from PIL import Image
import io

# ---------- Page Config ----------
st.set_page_config(
    page_title="DocScan",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- Custom CSS for Professional Look ----------
st.markdown("""
<style>
    /* Overall background */
    .stApp {
        background: #fafbfc;
    }
    
    /* Sidebar styling - lighter, professional */
    section[data-testid="stSidebar"] {
        background-color: #f4f6f9;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label {
        color: #1e2b3c !important;
    }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background-color: white;
        border-color: #cbd5e1;
    }
    
    /* Main header */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        color: #1e2b3c;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .metric-card strong {
        font-size: 1.4rem;
        color: #1e2b3c;
    }
    
    /* Buttons */
    .stButton > button {
        background: #2563eb;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        border: none;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(37,99,235,0.2);
    }
    .stButton > button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(37,99,235,0.25);
    }
    
    /* Text area */
    .stTextArea textarea {
        background-color: white;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        font-size: 15px;
        padding: 15px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Image container */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ---------- API Configuration ----------
API_URL = "http://localhost:8000/ocr"

# ---------- Sidebar (Minimal - only preprocessing) ----------
with st.sidebar:
    st.markdown("## Settings")
    preprocess_method = st.selectbox(
        "Preprocessing method",
        ["none", "grayscale", "threshold", "denoise"],
        help="Select how to preprocess the image before OCR."
    )

# ---------- Main Header ----------
st.markdown('<div class="main-header">DocScan</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Extract text from images with precision</div>', unsafe_allow_html=True)

# ---------- File Uploader ----------
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"],
    help="JPG, JPEG, PNG (max 200MB)"
)

# ---------- Main Content Area ----------
if uploaded_file is not None:
    col1, col2 = st.columns([1.3, 1], gap="large")
    
    with col1:
        st.markdown("#### Uploaded Image")
        image = Image.open(uploaded_file)
        # Fixed: use_column_width for older Streamlit compatibility
        st.image(image, use_column_width=True)
        st.caption(f"{uploaded_file.name}  |  {(uploaded_file.size/1024):.1f} KB")
        
        # Button to trigger OCR
        if st.button("Extract Text", use_container_width=True):
            with st.spinner("Processing..."):
                try:
                    files = {"file": uploaded_file.getvalue()}
                    params = {"preprocess": preprocess_method}
                    response = requests.post(API_URL, files=files, params=params, timeout=120)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Store results in session state for display
                        st.session_state['ocr_text'] = data["text"]
                        st.session_state['confidence_blocks'] = data["confidence_blocks"]
                        st.session_state['processing_time'] = data["processing_time_ms"]
                        st.session_state['avg_conf'] = sum(c for _, c in data["confidence_blocks"]) / len(data["confidence_blocks"]) if data["confidence_blocks"] else 0
                        st.session_state['ocr_done'] = True
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.session_state['ocr_done'] = False
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to OCR API. Ensure FastAPI is running on port 8000.")
                    st.session_state['ocr_done'] = False
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state['ocr_done'] = False
        
        # Display metrics and confidence expander below image (only if OCR done)
        if st.session_state.get('ocr_done', False):
            # Metrics cards
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.markdown(
                    f'<div class="metric-card">Processing Time<br><strong>{st.session_state["processing_time"]:.0f} ms</strong></div>',
                    unsafe_allow_html=True
                )
            with mcol2:
                st.markdown(
                    f'<div class="metric-card">Avg Confidence<br><strong>{st.session_state["avg_conf"]:.1%}</strong></div>',
                    unsafe_allow_html=True
                )
            
            # Confidence expander moved to left column
            if st.session_state['confidence_blocks']:
                with st.expander("View confidence per text block"):
                    for block, conf in st.session_state['confidence_blocks']:
                        st.progress(conf, text=f"{block[:60]}... ({conf:.1%})")
    
    with col2:
        st.markdown("#### Extracted Text")
        if st.session_state.get('ocr_done', False):
            st.text_area(
                label="",
                value=st.session_state['ocr_text'],
                height=400,
                key="result_display"
            )
        else:
            st.info("Click 'Extract Text' to begin OCR.")
else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: #ffffff; 
                border-radius: 20px; margin-top: 2rem; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
        <h2 style="color: #1e2b3c; font-weight: 600;">Ready to extract text</h2>
        <p style="color: #475569; font-size: 1.1rem;">Upload an image to get started</p>
    </div>
    """, unsafe_allow_html=True) 