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
    initial_sidebar_state="expanded"
)

# --- AdSense ---
st.markdown("""
<meta name="google-adsense-account" content="ca-pub-3474389046240414">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3474389046240414"
     crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

# --- Localization ---
if 'language' not in st.session_state:
    st.session_state.language = 'en'

def toggle_language():
    if st.session_state.language == 'en':
        st.session_state.language = 'ko'
    else:
        st.session_state.language = 'en'

translations = {
    "en": {
        "title": "AuthPixel 🔒",
        "subtitle": "Protect your image assets by inserting an invisible watermark.",
        "tab_protect": "🛡️ PROTECT",
        "tab_verify": "🔍 VERIFY",
        "header_protect": "Embed Invisible Watermark",
        "upload_protect": "Upload Image to Protect",
        "privacy_notice": "This service does not store any of your photos or information.",
        "watermark_limitation": "⚠️ AuthPixel watermarks may be damaged by excessive editing.",
        "watermark_text_label": "Enter Watermark Text (Max 20 chars, English letters and numbers.)",
        "embed_button": "🔒 Embed Watermark",
        "warning_no_text": "Please enter watermark text.",
        "embedding_spinner": "Embedding watermark...",
        "success_embed": "Watermark embedded successfully!",
        "download_button": "⬇️ Download Protected Image",
        "header_verify": "Verify & Decode Watermark",
        "upload_verify": "Upload Image to Verify",
        "decode_button": "🔍 Decode Watermark",
        "decoding_spinner": "Decoding...",
        "success_decode": "Watermark Detected!",
        "hidden_message": "## 🕵️ Hidden Message: `{}`",
        "error_no_watermark": "No watermark detected or decoding failed.",
        "search_google": "Search on Google Images",
        "search_instruction": "Click the button to open Google Lens, then drag and drop your image there to search.",
        "footer": "© 2025 AuthPixel | Secure Your Assets",
        "lang_button": "한국어"
    },
    "ko": {
        "title": "AuthPixel 🔒",
        "subtitle": "보이지 않는 워터마크를 삽입해서 이미지 자산을 지켜보세요",
        "tab_protect": "🛡️ 보호하기",
        "tab_verify": "🔍 검증하기",
        "header_protect": "보이지 않는 워터마크 삽입",
        "upload_protect": "보호할 이미지 업로드",
        "privacy_notice": "이 서비스는 고객님의 사진과 정보를 일체 저장하지 않습니다.",
        "watermark_limitation": "⚠️ AuthPixel의 워터마크는 과도한 편집 시에는 훼손될 수 있습니다.",
        "watermark_text_label": "워터마크 텍스트 입력 (최대 20자, 영문+숫자만 입력해주세요)",
        "embed_button": "🔒 워터마크 삽입",
        "warning_no_text": "워터마크 텍스트를 입력해주세요.",
        "embedding_spinner": "워터마크 삽입 중...",
        "success_embed": "워터마크가 성공적으로 삽입되었습니다!",
        "download_button": "⬇️ 보호된 이미지 다운로드",
        "header_verify": "워터마크 검증 및 해독",
        "upload_verify": "검증할 이미지 업로드",
        "decode_button": "🔍 워터마크 해독",
        "decoding_spinner": "해독 중...",
        "success_decode": "워터마크 감지됨!",
        "hidden_message": "## 🕵️ 숨겨진 메시지: `{}`",
        "error_no_watermark": "워터마크가 감지되지 않았거나 해독에 실패했습니다.",
        "search_google": "구글 이미지 검색",
        "search_instruction": "버튼을 클릭하여 구글 렌즈를 열고, 이미지를 드래그 앤 드롭하여 검색하세요.",
        "footer": "© 2025 AuthPixel | 자산 보호",
        "lang_button": "English"
    }
}

t = translations[st.session_state.language]

# --- Custom CSS for Calm Dark Mode ---
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #1A1C23; /* Dark Blue-Grey */
        color: #E0E0E0; /* Off-white */
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Width and Content Containment */
    [data-testid="stSidebar"] {
        width: 350px !important;
        min-width: 350px !important;
        max-width: 350px !important;
        overflow: hidden !important;
    }
    
    [data-testid="stSidebar"] > div {
        width: 350px !important;
        max-width: 350px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        width: 350px !important;
        padding: 1rem !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }
    
    /* Move sidebar completely off-screen when collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: -350px !important;
    }
    
    /* Ensure sidebar content doesn't overflow */
    [data-testid="stSidebar"] img {
        max-width: 100% !important;
        height: auto !important;
    }
    
    [data-testid="stSidebar"] a {
        max-width: 100% !important;
        display: block !important;
    }

    /* Move Sidebar Toggle Button to Left Middle */
    [data-testid="collapsedControl"] {
        position: fixed !important;
        left: 10px !important;
        right: auto !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 999999 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2C2F38;
        color: #FFFFFF;
        border: 1px solid #4A4D55;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #3E424E;
        border-color: #6C707A;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #252830;
        color: #E0E0E0;
        border: 1px solid #4A4D55;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #888;
        border: none;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border-bottom: 2px solid #64B5F6 !important; /* Soft Blue */
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(100, 181, 246, 0.1);
        color: #64B5F6;
        border: 1px solid #64B5F6;
        border-radius: 8px;
    }
    .stError {
        background-color: rgba(239, 83, 80, 0.1);
        color: #EF5350;
        border: 1px solid #EF5350;
        border-radius: 8px;
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
        img_encoded_np, error = embedder.embed(img_np, text)
        
        if error:
            return None, error
        
        return Image.fromarray(img_encoded_np), None
    except Exception as e:
        return None, str(e)

def decode_watermark(image):
    """Decodes invisible watermark from the image."""
    try:
        # Convert PIL Image to Numpy array (RGB)
        img_np = np.array(image)
        
        decoder = WatermarkDecoder()
        watermark, error = decoder.decode(img_np)
        
        if watermark:
            # Filter out non-printable characters just in case
            clean_watermark = "".join([c for c in watermark if c.isprintable()])
            if clean_watermark:
                return clean_watermark, None
            else:
                return None, "Decoded data contains no printable text."
        else:
            return None, error if error else "No watermark detected."
    except Exception as e:
        return None, str(e)

# --- Main App Layout ---
col1, col2 = st.columns([8, 2])
with col1:
    st.title(t["title"])
with col2:
    if st.button(t["lang_button"]):
        toggle_language()
        st.rerun()

sub_col1, sub_col2 = st.columns([3, 10])
with sub_col1:
    st.image("shield_icon.jpg", width=150)
with sub_col2:
    st.markdown(f"### {t['subtitle']}")

tab1, tab2 = st.tabs([t["tab_protect"], t["tab_verify"]])

# --- Tab 1: Protect ---
with tab1:
    st.header(t["header_protect"])
    
    uploaded_file = st.file_uploader(t["upload_protect"], type=['png', 'jpg', 'jpeg', 'bmp'], key="protect_upload")
    st.caption(t["privacy_notice"])
    st.caption(t["watermark_limitation"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_column_width=True)
        
        watermark_text = st.text_input(t["watermark_text_label"], max_chars=20)
        
        if st.button(t["embed_button"]):
            if not watermark_text:
                st.warning(t["warning_no_text"])
            else:
                with st.spinner(t["embedding_spinner"]):
                    watermarked_img, error = embed_watermark(image, watermark_text)
                    
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.success(t["success_embed"])
                    st.image(watermarked_img, caption="Protected Image", use_column_width=True)
                    
                    # Convert to bytes for download
                    buf = io.BytesIO()
                    watermarked_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label=t["download_button"],
                        data=byte_im,
                        file_name="protected_image.png",
                        mime="image/png"
                    )

# --- Tab 2: Verify ---
with tab2:
    st.header(t["header_verify"])
    
    verify_file = st.file_uploader(t["upload_verify"], type=['png', 'jpg', 'jpeg', 'bmp'], key="verify_upload")
    st.caption(t["privacy_notice"])
    st.caption(t["watermark_limitation"])
    
    if verify_file:
        verify_image = Image.open(verify_file)
        st.image(verify_image, caption="Uploaded Image", use_column_width=True)
        
        if st.button(t["decode_button"]):
            with st.spinner(t["decoding_spinner"]):
                decoded_text, error = decode_watermark(verify_image)
            
            if decoded_text:
                st.success(t["success_decode"])
                st.markdown(t["hidden_message"].format(decoded_text))
            elif error and "No watermark detected" not in error:
                 st.error(f"Error: {error}")
            else:
                st.error(t["error_no_watermark"])
        
        st.markdown("---")
        st.markdown(f"### {t['search_google']}")
        st.info(t["search_instruction"])
        st.link_button(t["search_google"], "https://lens.google.com/")

st.markdown("---")
st.markdown(t["footer"])

import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    img_base64 = get_base64_of_bin_file("mywalletqr.png")
    img_src = f"data:image/png;base64,{img_base64}"
except FileNotFoundError:
    img_src = "" # Handle case where file is missing

# Load buymeacoffee button image for toggle button
try:
    coffee_btn_base64 = get_base64_of_bin_file("buymeacoffee_btn.png")
    coffee_btn_src = f"data:image/png;base64,{coffee_btn_base64}"
except FileNotFoundError:
    coffee_btn_src = ""

# Add CSS for coffee button next to toggle
if coffee_btn_src:
    st.markdown(f"""
    <style>
        /* Add Buy Me a Coffee button next to toggle - only when sidebar is collapsed */
        [data-testid="stSidebar"][aria-expanded="false"] ~ div .coffee-btn-overlay {{
            display: block !important;
        }}
        
        .coffee-btn-overlay {{
            display: none;
            position: fixed;
            left: 50px;
            top: 3.5%;
            transform: translateY(-50%);
            width: 90px;
            height: 60px;
            z-index: 999999;
        }}
        
        .coffee-btn-overlay img {{
            width: 100%;
            height: 100%;
            cursor: pointer;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Add clickable link with image
    st.markdown(f"""
    <a href="https://buymeacoffee.com/goohwan" target="_blank" class="coffee-btn-overlay">
        <img src="{coffee_btn_src}" alt="Buy Me a Coffee" />
    </a>
    """, unsafe_allow_html=True)

# --- Sidebar Content (HTML) ---
sidebar_html = f"""
<h3>이 서비스가 도움이 되셨나요?</h3>
<a href="https://www.buymeacoffee.com/goohwan">
<img src="{img_src}" style="width:250px; display:block; margin:15px auto;" title="카메라 앱으로 QR코드를 비춰보세요">
</a><br>
<a href="https://www.buymeacoffee.com/goohwan">
<img src="https://img.buymeacoffee.com/button-api/?text=커피한잔<br>후원하기&emoji=☕&slug=goohwan&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" />
</a>
"""

with st.sidebar:
    st.markdown(sidebar_html, unsafe_allow_html=True)

# --- Mobile Sidebar (Bottom) ---
st.markdown(f"""
<div class="mobile-sidebar">
    <hr>
    {sidebar_html}
</div>
""", unsafe_allow_html=True)

# --- CSS for Mobile Responsiveness ---
st.markdown("""
<style>
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            display: none !important;
        }
        .mobile-sidebar {
            display: block;
            text-align: center;
            padding: 20px;
            background-color: #1A1C23;
            margin-top: 20px;
            border-radius: 10px;
        }
    }
    @media (min-width: 769px) {
        .mobile-sidebar {
            display: none;
        }
    }
</style>
""", unsafe_allow_html=True)
