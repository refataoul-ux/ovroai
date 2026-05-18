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
# ২. ২০২৬ সালের তথ্যের জন্য সুপার ইনস্ট্রাকশন ফিক্স
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
# ৩. সিএসএস ডিজাইন (সাইডবার বাটন ফিক্স, গিটহাব লোগো হাইড, ইউজার ইন্টারফেস)
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
    .st-emotion-cache-hp898u, .st-emotion-cache-1m4vsg4 { color: #11caa0 !important; } 
    
    /* স্ট্রিমলিটের ডিফল্ট ফুটার, গিটহাব বাটন এবং উপরের সাজসজ্জা চিরতরে হাইড করা */
    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"] {
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
# ৪. ৫টি এপিআই কী-র লিস্ট রোটেশন লজিক (সবচেয়ে নিরাপদ মেথড)
# =========================================================================
def get_random_client():
    valid_keys = []
    
    # সিক্রেটস থেকে GEMINI_API_KEYS লিস্টটি রিড করার চেষ্টা
    if "GEMINI_API_KEYS" in st.secrets:
        try:
            valid_keys = list(st.secrets["GEMINI_API_KEYS"])
        except Exception:
            pass

    # যদি কোনো কারণে লিস্ট খালি থাকে বা না পায়
    if not valid_keys:
        st.error("Secrets-এ কোনো GEMINI_API_KEYS লিস্ট পাওয়া যায়নি বা ফরম্যাটে ভুল আছে! দয়া করে Streamlit Secrets চেক করুন।")
        st.stop()
        
    # লিস্টে থাকা ৫টি কী থেকে যেকোনো একটি কী প্রতি মেসেজে রেন্ডমলি বেছে নেবে
    selected_key = random.choice(valid_keys)
    return genai.Client(api_key=selected_key)

# =========================================================================
# ৫. স্থায়ী লগইন সিস্টেম (পেইজ রিলোড বা রিফ্রেশ দিলেও লগআউট হবে না)
# =========================================================================
if "is_logged_in" not in st.session_state:
    # পেইজ রিফ্রেশ হলে ব্রাউজারের ইউআরএল প্যারামিটার থেকে সেশন পুনরুদ্ধার করবে
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
    st.markdown("<h2 style='color: #e3e3e3; font-size: 24px;'>OvroAI 2026</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; font-size: 12px;'>Global Assistant Platform</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.markdown("🔒 **লগইন প্যানেল (অপশনাল)**")
        user = st.text_input("Username", placeholder="username", label_visibility="collapsed")
        pwd = st.text_input("Password", type="password", placeholder="password", label_visibility="collapsed")
        
        col_login, col_reg = st.columns(2)
        with col_login:
            if st.button("Login", use_container_width=True):
                if user == "rifat" and pwd == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Premium"
                    # ইউআরএল প্যারামিটারে স্টেট লক করা যাতে রিফ্রেশে লগআউট না হয়
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
        st.info("✅ আপনার লগইন সেশন সক্রিয় আছে। রিলোড দিলেও লগআউট হবে না।")
        if st.button("Logout", use_container_width=True):
            st.session_state.is_logged_in = False
            st.query_params.clear() # লগআউট করলে ইউআরএল ক্লিন হবে
            st.rerun()

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৮. মূল চ্যাট উইন্ডো ইন্টারফেস
# =========================================================================
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500;'>🤖 OvroAI - Global Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Powered by 5x Dynamic API Key Rotation</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# পুরোনো চ্যাট স্ক্রিনে দেখানো
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# =========================================================================
# ৯. চ্যাট ইনপুট ও প্রসেসিং
# =========================================================================
if prompt := st.chat_input("Ask OvroAI anything..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        try:
            # ডায়নামিক ৫টি কী-র লিস্ট থেকে ক্লায়েন্ট তৈরি
            client = get_random_client()
            
            # লেটেস্ট ২০২৬ রেডি প্রফেশনাল মডেল
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=current_date_info)
            )
            
            reply = response.text
            st.markdown(reply)
            st.session_state.chat_history.append(("assistant", reply))
            st.rerun()
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.info("⏱️ সবগুলো ফ্রি ব্যাকএন্ড লাইন এই মুহূর্তে অত্যন্ত ব্যস্ত। অনুগ্রহ করে ১০ সেকেন্ড পর আবার মেসেজ দিন।")
            else:
                st.error(f"Error: {e}")
