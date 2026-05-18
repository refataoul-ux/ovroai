import streamlit as st
import os
import random
import io
from google import genai
from google.genai import types
from PIL import Image

# =========================================================================
# ১. পেজ কনফিগারেশন ও ব্রাউজার সেটিংস
# =========================================================================
st.set_page_config(
    page_title="OvroAI - Global Assistant 2026", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# ২. ২০২৬ সালের তথ্যের জন্য সুপার ইনস্ট্রাকশন ফিক্স (Timeline Lock)
# =========================================================================
current_date_info = """
Today's date is Monday, May 18, 2026. 
Current Global Context for you:
- World is preparing for the 2026 FIFA World Cup in North America.
- Current News (May 2026): WHO is monitoring a new Ebola strain in DRC.
- You are OvroAI, developed by Rifat Awal from Satkhira, Bangladesh.
Always provide information based on this 2026 timeline and context. Never say your knowledge cutoff is 2024.
"""

# =========================================================================
# ৩. আল্ট্রা-মডার্ন UI/UX ডিজাইন ও সিএসএস (গিটহাব অপশন ও অনাকাঙ্ক্ষিত মেনু হাইড)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    /* ব্যাকগ্রাউন্ড ও গ্লোবাল ফন্ট ফিক্স */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0c10 !important;
        color: #c5c6c7 !important;
    }
    
    /* সাইডবার সুন্দর ডার্ক থিম ও বর্ডার */
    [data-testid="stSidebar"] {
        background-color: #1f2833 !important;
        border-right: 1px solid #1f2833 !important;
    }
    
    [data-testid="stSidebarNav"] { display: block !important; }
    
    /* সাইডবার ফিরিয়ে আনার গোল সুন্দর বাটন ফিক্স */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        background-color: #1f2833 !important;
        border: 1px solid #66fcf1 !important;
        border-radius: 50% !important;
        color: #66fcf1 !important;
        z-index: 999999 !important;
        box-shadow: 0 0 10px rgba(102, 252, 241, 0.3) !important;
    }
    
    /* 🔴 জাহান ভাই, এই কোডটি ডান কোণার গিটহাব আইকন ও সমস্ত ডিফল্ট মেনু চিরতরে হাইড করে দেবে */
    [data-testid="stHeader"], header, footer, div.stDeployButton, [data-testid="stDecoration"], #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }

    /* চ্যাট ইনপুট বক্সের প্রিমিয়াম UI/UX ডিজাইন */
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        background-color: #1f2833 !important;
        border: 1px solid #45f3ff !important;
        box-shadow: 0 0 15px rgba(69, 243, 255, 0.15) !important;
        color: #ffffff !important;
    }
    
    /* বাটনগুলোর আধুনিক ডিজাইন ও হোভার ইফেক্ট */
    .stButton>button {
        background-color: #1f2833 !important;
        color: #66fcf1 !important;
        border: 1px solid #66fcf1 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #66fcf1 !important;
        color: #0b0c10 !important;
        box-shadow: 0 0 10px rgba(102, 252, 241, 0.5) !important;
    }
    
    /* টেক্সট ইনপুট বক্সের স্টাইল */
    .stTextInput>div>div>input {
        background-color: #0b0c10 !important;
        color: #ffffff !important;
        border: 1px solid #45f3ff !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# ৪. ৫টি এপিআই কী-র লিস্ট লোড করা
# =========================================================================
def get_all_keys():
    valid_keys = []
    if "GEMINI_API_KEYS" in st.secrets:
        try:
            valid_keys = list(st.secrets["GEMINI_API_KEYS"])
        except Exception:
            pass
    if not valid_keys:
        st.error("Secrets-এ কোনো GEMINI_API_KEYS লিস্ট পাওয়া যায়নি! দয়া করে Streamlit Secrets চেক করুন।")
        st.stop()
    return valid_keys

# =========================================================================
# ৫. স্থায়ী লগইন সিস্টেম (পেইজ রিলোড বা রিফ্রেশ দিলেও লগআউট হবে না)
# =========================================================================
if "is_logged_in" not in st.session_state:
    params = st.query_params
    if params.get("login") == "true":
        st.session_state.is_logged_in = True
        st.session_state.user_tier = params.get("tier", "Free")
    else:
        st.session_state.is_logged_in = False
        st.session_state.user_tier = "Free"

# =========================================================================
# ৬. সেশন স্টেট ইনিশিয়ালাইজেশন
# =========================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================================================================
# ৭. সাইডবার ডিজাইন ও কন্ট্রোল
# =========================================================================
with st.sidebar:
    st.markdown("<h2 style='color: #66fcf1; font-size: 26px; font-weight: 600; margin-bottom: 0px;'>OvroAI 2026</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a4a7ab; font-size: 13px;'>Global Assistant Platform</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #45f3ff; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        # 🎯 এখানে বাংলা লেখার ফন্ট ফিক্স করে দেওয়া হয়েছে যাতে অনাকাঙ্ক্ষিত কিছু না আসে
        st.markdown("<b style='color: #ffffff;'>🔒 লগইন প্যানেল (ঐচ্ছিক)</b>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="username", label_visibility="collapsed")
        pwd = st.text_input("Password", type="password", placeholder="password", label_visibility="collapsed")
        
        col_login, col_reg = st.columns(2)
        with col_login:
            if st.button("Login", use_container_width=True):
                if user == "rifat" and pwd == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Premium"
                    st.query_params["login"] = "true"
                    st.query_params["tier"] = "Premium"
                    st.rerun()
                else:
                    st.error("ভুল তথ্য!")
        with col_reg:
            st.button("Register", use_container_width=True)
    else:
        tier_color = "#FFD700" if st.session_state.user_tier == "Premium" else "#00FF00"
        st.markdown(f"Status: <b style='color:{tier_color};'>{st.session_state.user_tier} User</b>", unsafe_allow_html=True)
        st.info("✅ লগইন সেশন সক্রিয় আছে।")
        if st.button("Logout", use_container_width=True):
            st.session_state.is_logged_in = False
            st.query_params.clear()
            st.rerun()

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৮. মূল চ্যাট উইন্ডো ইন্টারফেস (UI/UX এনহ্যান্সড)
# =========================================================================
st.markdown("<h1 style='text-align: center; color: #66fcf1; font-weight: 600; letter-spacing: 1px; margin-bottom: 0px;'>🤖 OvroAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a4a7ab; font-size: 14px;'>Global Assistant • Powered by 5x Deep Failover Key Routing</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# পুরোনো চ্যাট হিস্ট্রি স্ক্রিনে রেন্ডার করা
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# =========================================================================
# ৯. চ্যাট ইনপুট ও ট্রু-ফেইলওভার লুপ প্রসেসিং (True Fallback Engine)
# =========================================================================
if prompt := st.chat_input("Ask OvroAI anything..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        all_keys = get_all_keys()
        
        # কী-র লিস্টটি রেন্ডমাইজ করা যাতে সবগুলোর উপর সমান লোড পড়ে
        shuffled_keys = all_keys.copy()
        random.shuffle(shuffled_keys)
        
        response_success = False
        last_error_message = ""
        
        # নিখুঁত লুপ মেকানিজম (ব্যস্ত থাকলে অটো পরের কী ট্রাই করবে)
        for current_key in shuffled_keys:
            try:
                client = genai.Client(api_key=current_key)
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=current_date_info)
                )
                
                reply = response.text
                st.markdown(reply)
                st.session_state.chat_history.append(("assistant", reply))
                response_success = True
                break  
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    last_error_message = "RESOURCE_EXHAUSTED"
                    continue
                else:
                    last_error_message = str(e)
                    continue
        
        # সব কী একই সাথে ব্লকড থাকলে সেফটি নোটিশ
        if not response_success:
            if last_error_message == "RESOURCE_EXHAUSTED":
                st.info("⏱️ ওভ্রোআই-এর ৫টি ফ্রি ব্যাকএন্ড লাইনের সবগুলোই এই মুহূর্তে অত্যন্ত ব্যস্ত। অনুগ্রহ করে ৩০ সেকেন্ড পর আবার চেষ্টা করুন।")
            else:
                st.error(f"Error: {last_error_message}")
        else:
            st.rerun()
