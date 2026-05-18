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
# ৩. আল্ট্রা-স্টাইলিশ UI/UX, স্লাইড অ্যানিমেশন এবং গিটহাব আইকন রিমুভাল সিএসএস
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* গ্লোবাল ব্যাকগ্রাউন্ড ও ফন্ট */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
        color: #f1f5f9 !important;
    }
    
    /* 🎯 সাইডবার স্লাইড ট্রানজিশন এবং প্রিমিয়াম অ্যানিমেশন */
    [data-testid="stSidebar"] {
        background-color: #05070c !important;
        border-right: 1px solid rgba(99, 102, 241, 0.1) !important;
        transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1) !important;
        will-change: transform;
    }
    
    /* সাইডবার ভেতরের কন্টেন্ট অ্যানিমেশন */
    [data-testid="stSidebarUserContent"] {
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    [data-testid="stSidebarNav"] { display: block !important; }
    
    /* 🎯 সাইডবার ফিরিয়ে আনার ফ্লোটিং গ্লোয়িং নিয়ন বাটন */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        left: 20px !important;
        top: 20px !important;
        background: rgba(10, 15, 30, 0.85) !important;
        border: 1px solid #6366f1 !important;
        border-radius: 12px !important;
        color: #6366f1 !important;
        backdrop-filter: blur(12px) !important;
        z-index: 999999 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.7) !important;
        transform: scale(1.08);
    }
    
    /* 🔴 ডান কোণার গিটহাব আইকন, থ্রি-ডট মেনু এবং টপ বার সম্পূর্ণ ভ্যানিশ করার মেগা ফিক্স */
    [data-testid="stHeader"], header, footer, div.stDeployButton, [data-testid="stDecoration"], #MainMenu {
        visibility: hidden !important;
        display: none !important;
        opacity: 0 !important;
    }
    
    /* চ্যাট ইনপুট বক্সের মডার্ন গ্লোয়িং লুক */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        background-color: #090d16 !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* সাইডবার বাটনগুলোর প্রিমিয়াম স্টাইল */
    .stButton>button {
        background: linear-gradient(135deg, #0f111a, #18132b) !important;
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-2px);
    }
    
    .stTextInput>div>div>input {
        background-color: rgba(5, 7, 12, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# ৪. 🔮 জাভাস্ক্রিপ্ট ইনজেকশন (মেনু ও অ্যানিমেশন ডিরেক্ট ব্রাউজার ফিক্স)
# =========================================================================
st.components.v1.html("""
<script>
    const applyPremiumEffects = () => {
        const parentDoc = window.parent.document;
        
        // ডান কোণার গিটহাব আইকন সম্বলিত হেডার বার চিরতরে মুছে ফেলার জাভাস্ক্রিপ্ট সিকিউরিটি
        const header = parentDoc.querySelector('[data-testid="stHeader"]');
        if (header) {
            header.style.display = 'none';
            header.style.visibility = 'hidden';
        }
        
        // সাইডবারের ট্রানজিশন আরও স্মুথ ও কাস্টমাইজ করা
        const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.transition = "transform 0.45s cubic-bezier(0.25, 1, 0.5, 1)";
        }
    };
    // অ্যাপ লোড হওয়ার পর এবং প্রতি ১ সেকেন্ড পর পর রান করবে যাতে গিটহাব লোগো ফিরে না আসে
    setInterval(applyPremiumEffects, 1000);
</script>
""", height=0, width=0)

# =========================================================================
# ৫. ৫টি এপিআই কী-র লিস্ট লোড করা
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
# ৬. স্থায়ী লগইন সিস্টেম (পেইজ রিলোড বা রিফ্রেশ দিলেও লগআউট হবে না)
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
# ৭. সেশন স্টেট ইনিশিয়ালাইজেশন
# =========================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================================================================
# ৮. সাইডবার ডিজাইন ও কন্ট্রোল
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #6366f1; font-size: 30px; font-weight: 700; margin-bottom: 0px; letter-spacing: -0.5px;'>OvroAI 2026</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 13px; font-weight: 500;'>Next-Gen Global Platform</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(99, 102, 241, 0.15); margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.markdown("<b style='color: #64748b; font-size: 14px;'>🔒 লগইন প্যানেল (ঐচ্ছিক)</b>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
        pwd = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
        
        st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
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
        tier_color = "#fbbf24" if st.session_state.user_tier == "Premium" else "#34d399"
        st.markdown(f"<div style='background: rgba(99, 102, 241, 0.05); padding: 14px; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.15);'>Status: <b style='color:{tier_color};'>{st.session_state.user_tier} User</b><br><span style='font-size:12px; color:#475569;'>✅ সেশন সুরক্ষিত ও সক্রিয়।</span></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.is_logged_in = False
            st.query_params.clear()
            st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.03); margin-top: 25px; margin-bottom: 25px;'>", unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৯. মূল চ্যাট উইন্ডো ইন্টারফেস (Ultra UI/UX)
# =========================================================================
st.markdown("<div style='padding-top: 25px;'></div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #ffffff; font-weight: 700; font-size: 46px; margin-bottom: 0px; background: linear-gradient(to right, #ffffff, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🤖 OvroAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569; font-size: 15px; font-weight: 500; margin-top: 5px; letter-spacing: 0.5px;'>Intelligence Redefined • 5x Smart Failover Core</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# =========================================================================
# ১০. চ্যাট ইনপুট ও ট্রু-ফেইলওভার লুপ প্রসেসিং (True Fallback Engine)
# =========================================================================
if prompt := st.chat_input("Ask OvroAI anything..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        all_keys = get_all_keys()
        
        shuffled_keys = all_keys.copy()
        random.shuffle(shuffled_keys)
        
        response_success = False
        last_error_message = ""
        
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
        
        if not response_success:
            if last_error_message == "RESOURCE_EXHAUSTED":
                st.info("⏱️ ওভ্রোআই-এর ৫টি ফ্রি ব্যাকএন্ড লাইনের সবগুলোই এই মুহূর্তে অত্যন্ত ব্যস্ত। অনুগ্রহ করে ৩০ সেকেন্ড পর আবার চেষ্টা করুন।")
            else:
                st.error(f"Error: {last_error_message}")
        else:
            st.rerun()
