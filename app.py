import streamlit as st
import numpy as np
from PIL import Image
from watermark_utils import WatermarkEmbedder, WatermarkDecoder
import cv2
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="AuthPixel - Invisible Watermarking",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Cyberpunk/Dark Mode ---
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #0e0e0e;
        color: #00ff41;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00ff41 !important;
        text-shadow: 0 0 5px #00ff41;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #000000;
        color: #00ff41;
        border: 1px solid #00ff41;
        border-radius: 0px;
        box-shadow: 0 0 5px #00ff41;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000000;
        box-shadow: 0 0 15px #00ff41;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: #00ff41;
        border: 1px solid #00ff41;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        color: #888;
        border-radius: 0px;
        border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #000000 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
        box-shadow: 0 0 5px #00ff41;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(0, 255, 65, 0.1);
        color: #00ff41;
        border: 1px solid #00ff41;
    }
    .stError {
        background-color: rgba(255, 0, 0, 0.1);
        color: #ff0000;
        border: 1px solid #ff0000;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def embed_watermark(image, text):
    """Embeds invisible watermark into the image."""
    try:
        # Convert PIL Image to Numpy array (RGB)
        img_np = np.array(image)
        
        embedder = WatermarkEmbedder()
        
        # Embed watermark
        img_encoded_np = embedder.embed(img_np, text)
        
        return Image.fromarray(img_encoded_np), None
    except Exception as e:
        return None, str(e)

def decode_watermark(image):
    """Decodes invisible watermark from the image."""
    try:
        # Convert PIL Image to Numpy array (RGB)
        img_np = np.array(image)
        
        decoder = WatermarkDecoder()
        watermark = decoder.decode(img_np)
        
        if watermark:
            # Filter out non-printable characters just in case
            clean_watermark = "".join([c for c in watermark if c.isprintable()])
            if clean_watermark:
                return clean_watermark, None
            else:
                return None, "Decoded data contains no printable text."
        else:
            return None, "No watermark detected."
    except Exception as e:
        return None, str(e)

# --- Main App Layout ---
st.title("AuthPixel 🔒")
st.markdown("### Invisible Watermarking System (Lightweight)")

tab1, tab2 = st.tabs(["🛡️ PROTECT", "🔍 VERIFY"])

# --- Tab 1: Protect ---
with tab1:
    st.header("Embed Invisible Watermark")
    
    uploaded_file = st.file_uploader("Upload Image to Protect", type=['png', 'jpg', 'jpeg', 'bmp'], key="protect_upload")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_column_width=True)
        
        watermark_text = st.text_input("Enter Watermark Text (Max 20 chars)", max_chars=20)
        
        if st.button("🔒 Embed Watermark"):
            if not watermark_text:
                st.warning("Please enter watermark text.")
            else:
                with st.spinner("Embedding watermark..."):
                    watermarked_img, error = embed_watermark(image, watermark_text)
                    
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.success("Watermark embedded successfully!")
                    st.image(watermarked_img, caption="Protected Image", use_column_width=True)
                    
                    # Convert to bytes for download
                    buf = io.BytesIO()
                    watermarked_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="⬇️ Download Protected Image",
                        data=byte_im,
                        file_name="protected_image.png",
                        mime="image/png"
                    )

# --- Tab 2: Verify ---
with tab2:
    st.header("Verify & Decode Watermark")
    
    verify_file = st.file_uploader("Upload Image to Verify", type=['png', 'jpg', 'jpeg', 'bmp'], key="verify_upload")
    
    if verify_file:
        verify_image = Image.open(verify_file)
        st.image(verify_image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("🔍 Decode Watermark"):
            with st.spinner("Decoding..."):
                decoded_text, error = decode_watermark(verify_image)
            
            if decoded_text:
                st.success("Watermark Detected!")
                st.markdown(f"## 🕵️ Hidden Message: `{decoded_text}`")
            elif error and "No watermark detected" not in error:
                 st.error(f"Error: {error}")
            else:
                st.error("No watermark detected or decoding failed.")

st.markdown("---")
st.markdown("© 2024 AuthPixel | Secure Your Assets")
