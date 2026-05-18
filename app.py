import streamlit as st
import os
import random
from google import genai
from google.genai import types

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
# ২. ২০২৬ সালের তথ্যের জন্য সুপার ইনস্ট্রাকশন ফিক্স (Refat Aoul Branding)
# =========================================================================
current_date_info = """
Today's date is Monday, May 18, 2026. 
Current Global Context for you:
- You are OvroAI, a highly advanced AI developed by Refat Aoul from Satkhira, Bangladesh.
- World is preparing for the 2026 FIFA World Cup.
- Always provide information based on this 2026 timeline.
"""

# =========================================================================
# ৩. ১০০% সুরক্ষিত আল্ট্রা-স্টাইলিশ স্প্ল্যাশ ইন্ট্রো ও UI/UX সিএসএস (কোন f-string বাগ নেই)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Hind+Siliguri:wght@400;500;600;700&display=swap');
    
    /* গ্লোবাল ডার্ক থিম ও বাংলা ফন্ট ফিক্স */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Plus Jakarta Sans', 'Hind Siliguri', sans-serif !important;
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
        color: #f1f5f9 !important;
    }

    /* ⏳ ৩ সেকেন্ডের স্প্ল্যাশ ইন্ট্রো স্ক্রিন */
    #intro-overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #020408;
        z-index: 9999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: opacity 1s ease-in-out, visibility 1s;
    }
    
    .intro-logo {
        font-size: 70px;
        font-weight: 700;
        background: linear-gradient(45deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 2s infinite alternate;
        margin-bottom: 10px;
    }
    
    .intro-credits {
        font-size: 20px;
        color: #94a3b8;
        letter-spacing: 3px;
        text-transform: uppercase;
        opacity: 0;
        animation: fadeInUp 1.5s forwards 0.5s;
    }
    
    .creator-name {
        color: #6366f1;
        font-weight: 700;
        text-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
    }

    @keyframes pulseGlow {
        0% { transform: scale(0.97); filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.4)); }
        100% { transform: scale(1.03); filter: drop-shadow(0 0 35px rgba(168, 85, 247, 0.7)); }
    }
    @keyframes fadeInUp {
        to { opacity: 1; transform: translateY(-5px); }
    }

    /* 🎯 সাইডবার ও স্লাইড বাটন পুনরুদ্ধার */
    [data-testid="stSidebar"] {
        background-color: #05070c !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }
    
    /* সাইডবার ফিরিয়ে আনার নেভিগেশন বাটন পিনড */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        left: 20px !important;
        top: 20px !important;
        background: rgba(10, 15, 30, 0.9) !important;
        border: 1px solid #6366f1 !important;
        border-radius: 12px !important;
        color: #6366f1 !important;
        z-index: 999998 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4) !important;
    }

    /* 🔴 ডান কোণার গিটহাব আইকন ক্লিনিং */
    div[data-testid="stHeader"] > div:first-child {
        display: none !important;
    }
    div.stDeployButton, [data-testid="stDecoration"], footer, #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }

    /* প্রিমিয়াম টায়ার ডিজাইন */
    .tier-box {
        background: rgba(99, 102, 241, 0.08) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
    }

    /* চ্যাট ইনপুট */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        background-color: #090d16 !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
    }
    </style>

    <div id="intro-overlay">
        <div class="intro-logo">🤖 OvroAI</div>
        <div class="intro-credits">Created by <span class="creator-name">Refat Aoul</span></div>
    </div>

    <script>
        // ৩ সেকেন্ড পর স্প্ল্যাশ স্ক্রিন হাইড করার জাভাস্ক্রিপ্ট
        setTimeout(function() {
            var intro = window.parent.document.getElementById('intro-overlay');
            if (intro) {
                intro.style.opacity = '0';
                setTimeout(function() { intro.style.display = 'none'; }, 1000);
            }
        }, 3000);
    </script>
    """, unsafe_allow_html=True)

# =========================================================================
# ৪. স্মার্ট এপিআই কী ডিটেকশন ও রোটেশন (আপনার সিক্রেটস ফরম্যাট অনুযায়ী)
# =========================================================================
def get_ai_client():
    valid_keys = []
    # আপনার স্ক্রিনশট অনুযায়ী আলাদা আলাদা নামের কী-গুলো স্বয়ংক্রিয়ভাবে খুঁজে নেবে
    for secret_key in st.secrets.keys():
        if "GEMINI_API_KEY" in secret_key:
            valid_keys.append(st.secrets[secret_key])
            
    if not valid_keys:
        st.error("Secrets-এ কোনো GEMINI_API_KEY পাওয়া যায়নি! দয়া করে App Settings চেক করুন।")
        st.stop()
        
    # র্যান্ডমলি একটি কী সিলেক্ট করে রিটার্ন করবে (Failover Automation)
    return genai.Client(api_key=random.choice(valid_keys))

# =========================================================================
# ৫. স্থায়ী লগইন ও সাবস্ক্রিপশন স্টেট ম্যানেজমেন্ট
# =========================================================================
if "is_logged_in" not in st.session_state:
    params = st.query_params
    if params.get("login") == "true":
        st.session_state.is_logged_in = True
        st.session_state.user_tier = params.get("tier", "Pro")
    else:
        st.session_state.is_logged_in = False
        st.session_state.user_tier = "Basic"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================================================================
# ৬. সাইডবার ইন্টারফেস (লগইন, সাইনআপ এবং প্রিমিয়াম মেম্বারশিপ টায়ার)
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #6366f1; font-weight: 700; margin-bottom:0;'>OvroAI 2026</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 13px;'>Next-Gen Intelligent Core</p>", unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.is_logged_in:
        st.markdown("<b style='color: #94a3b8; font-size: 15px;'>🔒 লগইন প্যানেল (ঐচ্ছিক)</b>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="rifat", key="username_field")
        pwd = st.text_input("Password", type="password", placeholder="1234", key="password_field")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, key="login_btn"):
                if user == "rifat" and pwd == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Pro"
                    st.query_params["login"] = "true"
                    st.query_params["tier"] = "Pro"
                    st.rerun()
                else:
                    st.error("ভুল ইউজার বা পাসওয়ার্ড!")
        with col2:
            st.button("Sign Up", use_container_width=True, key="signup_btn")
    else:
        # প্রিমিয়াম সাবস্ক্রিপশন ভিজ্যুয়াল অপশন বক্স
        st.markdown(f"""
            <div class='tier-box'>
                <p style='margin:0; font-size:12px; color:#94a3b8;'>Your Subscription Status</p>
                <h3 style='margin:0; color:#fbbf24;'>💎 {st.session_state.user_tier} Member</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<b style='color: #94a3b8; font-size: 14px;'>🏆 প্রিমিয়াম ফিচারসমূহ সচল:</b>", unsafe_allow_html=True)
        st.markdown("- আনলিমিটেড স্মার্ট এপিআই কল\n- ২০২৬ রিয়েল-টাইম নলেজ বেস\n- রোটেশনাল ব্যাকএন্ড ফেইলওভার")
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.user_tier == "Pro":
            if st.button("Upgrade to Elite ($49/mo)", use_container_width=True, key="elite_upgrade_btn"):
                st.balloons()
                st.session_state.user_tier = "Elite"
                st.query_params["tier"] = "Elite"
                st.rerun()
        else:
            st.success("👑 You are on the highest Elite tier!")
            
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.is_logged_in = False
            st.query_params.clear()
            st.rerun()

    st.markdown("---")
    if st.button("➕ New Conversation", use_container_width=True, key="new_chat_btn"):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৭. মূল চ্যাট ইন্টারফেস
# =========================================================================
st.markdown("<h1 style='text-align: center; color: #ffffff; margin-bottom:0;'>🤖 OvroAI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>2026 Core Engine • Created by Refat Aoul</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# চ্যাট হিস্ট্রি রেন্ডার
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# চ্যাট ইনপুট ও প্রসেসিং
if prompt := st.chat_input("OvroAI-কে কিছু জিজ্ঞেস করুন..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        try:
            client = get_ai_client()
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=current_date_info)
            )
            
            reply = response.text
            st.markdown(reply)
            st.session_state.chat_history.append(("assistant", reply))
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.warning("⏱️ এই লাইনের কোটা শেষ! ব্যাকএন্ড অন্য একটি কী ট্রাই করছে, দয়া করে আবার মেসেজ পাঠান।")
            else:
                st.error(f"Error: {e}")
