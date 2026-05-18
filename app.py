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
# ৩. সিএসএস ডিজাইন (সাইডবার ফিরিয়ে আনার বাটন এবং ইউজার ইন্টারফেস ফিক্স)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314 !important;
    }
    
    /* সাইডবার মেনু বাটন বা কোলাপ্সড আইকন যাতে স্ক্রিন থেকে চিরতরে হারিয়ে না যায় */
    [data-testid="stSidebarNav"] { display: block !important; }
    
    /* সাইডবার ভেতরে চলে গেলে তাকে স্ক্রিনে ফিরিয়ে আনার গোল সুন্দর বাটন ফিক্স */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        background-color: #1e1f20 !important;
        border: 1px solid #11caa0 !important;
        border-radius: 50% !important;
        color: #11caa0 !important;
        z-index: 999999 !important;
    }
    
    /* স্ট্রিমলিটের অপ্রয়োজনীয় ডেকরেশন ও গিটহাব লোগো হাইড করা */
    div.stDeployButton, [data-testid="stDecoration"], footer {
        visibility: hidden !important;
        display: none !important;
    }

    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
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
# ७. সাইডবার ডিজাইন ও কন্ট্রোল
# =========================================================================
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 24px;'>OvroAI 2026</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; font-size: 12px;'>Global Assistant Platform</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.markdown("🔒 **লগইন প্যানেল (অপショナル)**")
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
        st.info("✅ লগইন সেশন সক্রিয়।")
        if st.button("Logout", use_container_width=True):
            st.session_state.is_logged_in = False
            st.query_params.clear()
            st.rerun()

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৮. মূল চ্যাট উইন্ডো ইন্টারফেস
# =========================================================================
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500;'>🤖 OvroAI - Global Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Powered by 5x Deep Failover Key Routing</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

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
        
        # রিফাত ভাইয়ের চাহিদামতো নিখুঁত লুপ মেকানিজম
        for current_key in shuffled_keys:
            try:
                # এই কী দিয়ে চেষ্টা করা হচ্ছে, ব্যস্ত থাকলে কোনো এরর স্ক্রিনে না দেখিয়ে সরাসরি পরেরটায় চলে যাবে
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
                break  # যেকোনো একটা কী কাজ করে ফেললে লুপ সাথে সাথে বন্ধ হয়ে যাবে
                
            except Exception as e:
                # ব্যস্ততার এরর (429/RESOURCE_EXHAUSTED) হলে কোডটি স্ক্রিনে কিচ্ছু দেখাবে না, সাইলেন্টলি পরের কী ট্রাই করবে
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    last_error_message = "RESOURCE_EXHAUSTED"
                    continue
                else:
                    # অন্য কোনো টেকনিক্যাল এরর হলে সেটা ট্র্যাক করার জন্য সেভ করবে
                    last_error_message = str(e)
                    continue
        
        # যদি ৫টি লাইনের একটি লাইনও সফল হতে না পারে (সবগুলোই যদি একসাথে ব্লক থাকে)
        if not response_success:
            if last_error_message == "RESOURCE_EXHAUSTED":
                st.info("⏱️ ওভ্রোআই-এর ৫টি ফ্রি ব্যাকএন্ড লাইনের সবগুলোই এই মুহূর্তে অত্যন্ত ব্যস্ত। অনুগ্রহ করে ৩০ সেকেন্ড পর আবার চেষ্টা করুন।")
            else:
                st.error(f"Error: {last_error_message}")
        else:
            st.rerun()
