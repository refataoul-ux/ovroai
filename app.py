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

# ২. সিএসএস স্টাইলিং (জেমিনি থিম)
st.markdown("""
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
    .stButton > button {
        background-color: transparent !important;
        color: #c4c7c5 !important;
        border: none !important;
        width: 100% !important;
        text-align: left !important;
        padding: 12px 15px !important;
        font-size: 15px !important;
        border-radius: 24px !important;
    }
    .stButton > button:hover {
        background-color: #333537 !important;
        color: #fff !important;
    }
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ৩. এপিআই কি কানেকশন
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets-এ GEMINI_API_KEY পাওয়া যায়নি!")
    st.stop()

global_super_instruction = "Your name is OvroAI, developed by Rifat Awal from Satkhira, Bangladesh."

# ৪. সাইডবার লেআউট
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 22px; padding: 10px;'>OvroAI</h2>", unsafe_allow_html=True)
    if st.button("➕   New chat"):
        st.session_state.chat_history = []
        st.session_state.uploaded_image = None
        st.rerun()

# ৫. মূল উইন্ডো
st.markdown("<h2 style='text-align: center; color: #e3e3e3;'>🤖 OvroAI - Your Global AI Companion</h2>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ছবি আপলোডার বক্স
uploaded_file = st.file_uploader("ছবি আপলোড করুন (Optional)", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file)
    st.image(st.session_state.uploaded_image, caption="আপলোড করা ছবি", width=150)

# ৬. চ্যাট প্রসেসিং
if prompt := st.chat_input("Ask OvroAI anything..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        try:
            # যদি ছবি উপস্থিত থাকে, তাহলে কন্টেন্টে ছবি পাঠানো হবে
            if st.session_state.uploaded_image is not None:
                contents = [st.session_state.uploaded_image, prompt]
            else:
                contents = [prompt]

            response = client.models.generate_content(
                model='gemini-2.5-flash', # এপিআই এর সঠিক মডেল নাম আপডেট করা হয়েছে
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=global_super_instruction)
            )
            
            reply_text = response.text
            st.markdown(reply_text)
            st.session_state.chat_history.append(("assistant", reply_text))
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.info("⏱️ জেমিনি ফ্রি এপিআই কোটা সাময়িকভাবে শেষ হয়েছে। অনুগ্রহ করে ১ মিনিট পর আবার মেসেজ পাঠান।")
            else:
                st.error(f"Error: {e}")
