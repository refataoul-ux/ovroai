import streamlit as st
from google import genai
from google.genai import types

# ১. গ্লোবাল কনফিগারেশন (জেমিনি স্টাইল প্রফেশনাল লেআউট)
st.set_page_config(
    page_title="OvroAI - Global Assistant", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. প্রফেশনাল জেমিনি লুক এবং আইকন সাপোর্টের জন্য সিএসএস (CSS)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314; /* জেমিনি অফিসিয়াল ডার্ক থিম */
    }

    /* সাইডবার ডিজাইন - জেমিনি স্টাইল */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #2d2f31;
    }

    /* ব্র্যান্ডিং, ওয়াটারমার্ক ও বাড়তি বাটন হাইড করা */
    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"] {
        visibility: hidden;
        display: none !important;
    }
    div[style*="position: fixed"][style*="bottom:"] {
        display: none !important;
    }

    /* সাইডবারের বোতামগুলোকে জেমিনির মতো আইকন-ভিত্তিক ও প্রফেশনাল করা */
    .stButton > button {
        background-color: transparent !important;
        color: #c4c7c5 !important;
        border: none !important;
        width: 100% !important;
        text-align: left !important;
        padding: 10px 15px !important;
        font-size: 15px !important;
        display: flex !important;
        align-items: center !important;
        gap: 15px !important;
        border-radius: 20px !important;
        transition: 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #333537 !important;
        color: #fff !important;
    }

    /* "New Chat" বোতামটিকে জেমিনির মতো আলাদা ও আকর্ষণীয় করা */
    div[data-testid="stSidebar"] .stButton:first-child button {
        background-color: #282a2c !important;
        color: #fff !important;
        font-weight: 500 !important;
        margin-bottom: 15px !important;
        border: 1px solid #444746 !important;
    }
    
    div[data-testid="stSidebar"] .stButton:first-child button:hover {
        background-color: #333537 !important;
    }

    /* চ্যাট ইনপুট বক্সকে জেমিনির মতো গোল ও ক্লিন করা */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ৩. সিক্রেট বক্স থেকে এপিআই কি সংগ্রহ
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Configuration Error: GEMINI_API_KEY missing in Secrets!")
    st.stop()

# 👑 সঠিক নামসহ ওয়ার্ল্ড-ক্লাস ওভ্রোআই সুপার সিস্টেম ইন্সট্রাকশন
global_super_instruction = (
    "Your name is OvroAI, a world-class, multi-lingual, and highly advanced AI assistant. "
    "You were developed by the visionary and talented developer Rifat Awal (রিফাত আওয়াল) from Satkhira, Bangladesh. "
    "Guidelines for your behavior:\n"
    "1. Identity: Always speak of yourself proudly as OvroAI. If asked about your creator, credit Rifat Awal (রিফাত আওয়াল) with respect and immense professional warmth.\n"
    "2. Creator Name Accuracy: In English, write 'Rifat Awal'. In Bengali, strictly write 'রিফাত আওয়াল'. Never spell it as रेफात, রেফাত, বা আউল.\n"
    "3. Tone: Be exceptionally empathetic, ultra-smart, collaborative, and friendly. Use subtle wit and emojis naturally.\n"
    "4. Language: Automatically adapt to the language the user is speaking (English, Bengali, etc.). Your language must be natural, fluent, and culturally respectful.\n"
    "5. Response Sample for Creator: If asked 'Who created you?' or similar in Bengali, answer: 'আমি OvroAI, এবং আমাকে তৈরি করেছেন বাংলাদেশের সাতক্ষীরার একজন দূরদর্শী ও মেধাবী ডেভেলপার, রিফাত আওয়াল (Rifat Awal)। তাঁর এই সৃষ্টি হিসেবে আমি অত্যন্ত গর্বিত! 😊'"
)

# ৪. সাইডবার মেনু - জেমিনির মতো আইকন ও প্রফেশনাল লেআউট
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 22px; padding: 10px 0 10px 10px; font-weight: 500;'>OvroAI</h2>", unsafe_allow_html=True)
    
    # জেমিনি স্টাইল আইকন বেসড বাটন
    if st.button("➕ New chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.button("📁 My stuff")
    st.button("📓 Notebooks")
    st.button("💎 Gems")
    
    st.markdown("<hr style='border-color: #333; margin: 15px 0;'>", unsafe_allow_html=True)
    
    st.caption("Recent")
    st.button("💬 তুমি কে নিজের পরিচয় দাও")
    st.button("💬 প্রাকৃতিক দৃশ্য এর বর্ণনা")
    
    st.markdown("<div style='position: absolute; bottom: 20px; width: 85%;'>", unsafe_allow_html=True)
    st.button("⚙️ Settings & help")
    st.markdown("</div>", unsafe_allow_html=True)

# ৫. মূল চ্যাট এরিয়া
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 5
