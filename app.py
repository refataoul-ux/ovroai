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
# ৩. ৩ সেকেন্ডের আল্ট্রা-স্টাইলিশ ইন্ট্রো স্ক্রিন এবং প্রিমিয়াম UI/UX সিএসএস
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* গ্লোবাল থিম */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
        color: #f1f5f9 !important;
    }

    /* ⏳ ম্যাজিক স্প্ল্যাশ স্ক্রিন (ইন্ট্রো অ্যানিমেশন) */
    #intro-overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #020408;
        z-index: 9999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: opacity 1s ease, visibility 1s;
    }
    
    .intro-logo {
        font-size: 60px;
        font-weight: 700;
        background: linear-gradient(45deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 2s infinite alternate;
        margin-bottom: 10px;
    }
    
    .intro-credits {
        font-size: 18px;
        color: #94a3b8;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 500;
        opacity: 0;
        animation: fadeInUp 1.5s forwards 0.5s;
    }
    
    .creator-name {
        color: #6366f1;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
    }

    @keyframes pulseGlow {
        0% { transform: scale(0.98); filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.3)); }
        100% { transform: scale(1.02); filter: drop-shadow(0 0 30px rgba(168, 85, 247, 0.7)); }
    }
    @keyframes fadeInUp {
        to { opacity: 1; transform: translateY(-5px); }
    }

    /* 🎯 সাইডবার স্লাইড ট্রানজিশন ও স্টাইল */
    [data-testid="stSidebar"] {
        background-color: #05070c !important;
        border-right: 1px solid rgba(99, 102, 241, 0.1) !important;
        transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }
    
    [data-testid="stSidebarNav"] { display: block !important; }
    
    /* 🎯 স্লাইড বাটন ফিরিয়ে আনার জন্য আল্টিমেট ফিক্স (সব সময় দৃশ্যমান থাকবে) */
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
        z-index: 999998 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.7) !important;
        transform: scale(1.08);
    }
    
    /* 🔴 ডান কোণার গিটহাব আইকন ও থ্রি-ডট মেনু রিমুভাল (সাইডবার বাটন না ভেঙে) */
    [data-testid="stHeader"] {
        background: transparent !important;
        z-index: 999;
    }
    /* হেডার এলিমেন্টের ভেতরের গিটহাব এবং অতিরিক্ত মেনু বাটন শুধু হাইড করা */
    [data-testid="stHeader"] > div:first-child {
        display: none !important;
    }
    div.stDeployButton, [data-testid="stDecoration"], footer, #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }

    /* চ্যাট ইনপুট বক্স ও বাটন */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        background-color: #090d16 !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #0f111a, #18132b) !important;
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-2px);
    }
    </style>

    <div id="intro-overlay">
        <div class="intro-logo">🤖 OvroAI</div>
        <div class="intro-credits">Created by <span class="creator-name">Rifat Awal</span></div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================================
# ৪. 🔮 জাভাস্ক্রিপ্ট ইন্জেকশন (৩ সেকেন্ড পর ইন্ট্রো হাইড করার কন্ট্রোল)
# =========================================================================
st.components.v1.html("""
<script>
    const runIntroAndFixes = () => {
        const parentDoc = window.parent.document;
        
        // ৩ সেকেন্ড (৩০০০ মিলিমেকেন্ড) পর স্টাইলিশ উপায়ে ইন্ট্রো স্ক্রিন হাইড করা
        const intro = parentDoc.getElementById('intro-overlay');
        if (intro) {
            setTimeout(() => {
                intro.style.opacity = '0';
                setTimeout(() => { intro.style.display = 'none'; }, 1000);
            }, 3000);
        }
    };
    runIntroAndFixes();
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
# ৬. স্থায়ী লগইন সিস্টেম
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
