import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
import io

# ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="OvroAI - Global Assistant", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. সম্পূর্ণ জেমিনি রেস্পনসিভ থিম এবং কাস্টম প্লাস মেনু (HTML/CSS)
# এখানে unsafe_allow_html=True নিশ্চিত করা হয়েছে যাতে টেক্সট ভেসে না ওঠে
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #2d2f31 !important;
    }
    
    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* চ্যাট ইনপুট এবং প্লাস বাটন এরিয়া */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        padding-left: 10px !important;
    }

    /* ফাইল আপলোডার স্টাইলিং */
    .stFileUploader {
        padding: 0px !important;
        margin-top: 5px !important;
    }
    .stFileUploader section {
        background-color: #1e1f20 !important;
        border: 1px dashed #444746 !important;
        border-radius: 15px !important;
        padding: 8px !important;
    }
    
    /* কাস্টম মেনু স্টাইলিং (স্ক্রিনশটের মতো সাদা ব্যাকগ্রাউন্ড বক্স) */
    .upload-popup-menu {
        background-color: #edf2f7 !important;
        border-radius: 16px;
        padding: 12px;
        width: 220px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    .popup-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 12px;
        color: #1f2937 !important;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        border-radius: 8px;
        transition: background 0.2s;
    }
    .popup-item:hover {
        background-color: #e2e8f0;
    }
    .popup-item i {
        font-size: 16px;
        color: #4b5563;
    }
    </style>
    """, unsafe_allow_html=True)

# ৩. এপিআই কি কানেকশন
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets-এ GEMINI_API_KEY পাওয়া যায়নি!")
    st.stop()

global_super_instruction = "Your name is OvroAI, developed by Rifat Awal from Satkhira, Bangladesh. Assist users warmly."

# ৪. সাইডবার লেআউট
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 22px; padding: 10px;'>OvroAI</h2>", unsafe_allow_html=True)
    if st.button("➕   New chat"):
        st.session_state.chat_history = []
        st.session_state.active_file = None
        st.session_state.show_menu = False
        st.rerun()

# ৫. মূল উইন্ডো টাইটেল
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500;'>🤖 OvroAI - Global Assistant</h2>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_file" not in st.session_state:
    st.session_state.active_file = None
if "show_menu" not in st.session_state:
    st.session_state.show_menu = False

# চ্যাট হিস্ট্রি ডিসপ্লে
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ৬. প্লাস মেনু ও ফাইল আপলোডার সেকশন
st.markdown("<hr style='border-color: #2d2f31; margin: 20px 0;'>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 6])

with col1:
    if st.button("➕ Tools", key="toggle_plus_btn"):
        st.session_state.show_menu = not st.session_state.show_menu
        st.rerun()

if st.session_state.show_menu:
    with col2:
        st.markdown("""
        <div class="upload-popup-menu">
            <div class="popup-item"><i class="fa-solid fa-paperclip"></i> Upload files</div>
            <div class="popup-item"><i class="fa-brands fa-google-drive"></i> Add from Drive</div>
            <div class="popup-item"><i class="fa-regular fa-image"></i> Photos</div>
            <div class="popup-item"><i class="fa-solid fa-book-open"></i> NotebookLM</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("সিলেক্ট করুন:", type=["jpg", "png", "jpeg", "pdf", "txt"], label_visibility="collapsed")
        if uploaded_file is not None:
            st.session_state.active_file = uploaded_file
            st.session_state.show_menu = False
            st.rerun()

if st.session_state.active_file is not None:
    try:
        img_preview = Image.open(st.session_state.active_file)
        st.image(img_preview, caption="সংযুক্ত ছবি", width=120)
    except:
        st.info(f"📁 ফাইল রেডি: {st.session_state.active_file.name}")

# ৭. চ্যাট ইনপুট ও প্রসেসিং
if prompt := st.chat_input("Ask OvroAI anything (Any language)..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        try:
            contents = []
            if st.session_state.active_file is not None:
                file_bytes = st.session_state.active_file.read()
                try:
                    img = Image.open(io.BytesIO(file_bytes))
                    contents.append(img)
                except:
                    contents.append(file_bytes.decode("utf-8", errors="ignore"))
            
            contents.append(prompt)

            # জেমিনির অফিশিয়াল ২.৫ ফ্ল্যাশ মডেল ব্যবহার
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=global_super_instruction)
            )
            
            reply_text = response.text
            st.markdown(reply_text)
            st.session_state.chat_history.append(("assistant", reply_text))
            
            st.session_state.active_file = None
            st.rerun()
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.info("⏱️ জেমিনি ফ্রি এপিআই কোটা সাময়িকভাবে শেষ হয়েছে। অনুগ্রহ করে ১ মিনিট পর আবার মেসেজ পাঠান।")
            else:
                st.error(f"Error: {e}")
