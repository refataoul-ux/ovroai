import streamlit as st
import os
import random
import time
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
# ৩. সেশন স্টেট ইনিশিয়ালাইজেশন (স্মার্ট কন্ট্রোল)
# =========================================================================
if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False

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
# ৪. ৪-৫ সেকেন্ডের প্রিমিয়াম স্প্ল্যাশ স্ক্রিন অ্যানিমেশন (ফাস্ট লোড ও অটো-ভ্যানিশ)
# =========================================================================
if not st.session_state.intro_shown:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700&display=swap');
            
            .intro-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: #020408;
                z-index: 999999;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                font-family: 'Plus Jakarta Sans', sans-serif;
            }
            
            .intro-box {
                text-align: center;
                animation: fadeInOut 4.5s ease-in-out infinite;
            }
            
            .intro-title {
                font-size: 65px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 10px;
                letter-spacing: -1px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                text-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
            }
            
            .intro-sub {
                font-size: 16px;
                color: #6366f1;
                letter-spacing: 3px;
                text-transform: uppercase;
                font-weight: 700;
                margin-top: 15px;
                text-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
            }

            @keyframes fadeInOut {
                0% { opacity: 0; transform: scale(0.95); }
                15% { opacity: 1; transform: scale(1); }
                85% { opacity: 1; transform: scale(1); }
                100% { opacity: 0; transform: scale(1.02); }
            }
            </style>
            <div class="intro-bg">
                <div class="intro-box">
                    <div class="intro-title">🤖 OvroAI</div>
                    <div class="intro-sub">CREATED BY REFAT AOUL</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(4.5)  # আপনার চাহিদা মতো ঠিক ৪.৫ সেকেন্ড গ্লোয়িং অ্যানিমেশন চলবে
    placeholder.empty()  # মেমোরি থেকে স্প্ল্যাশ স্ক্রিন মুছে মূল পেজ ওপেন হবে
    st.session_state.intro_shown = True
    st.rerun()

# =========================================================================
# ৫. মূল অ্যাপ্লিকেশনের গ্লোবাল সিএসএস (UI/UX ও বাংলা ফন্ট ফিক্স)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Hind+Siliguri:wght@400;600;700&display=swap');
    
    /* সাইডবার ও মূল চ্যাটের বাংলা যুক্তাক্ষর ফিক্স */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', 'Hind Siliguri', sans-serif !important;
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
        color: #f1f5f9 !important;
    }

    /* সাইডবার কাস্টমাইজেশন */
    [data-testid="stSidebar"] {
        background-color: #05070c !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }
    
    /* সাইডবার বাটন স্টাইল */
    [data-testid="stSidebarCollapseButton"] {
        background: rgba(10, 15, 30, 0.9) !important;
        border: 1px solid #6366f1 !important;
        color: #6366f1 !important;
        border-radius: 10px !important;
    }

    /* গিটহাব আইকন ও মেনু হাইড */
    div[data-testid="stHeader"] > div:first-child {
        display: none !important;
    }
    div.stDeployButton, [data-testid="stDecoration"], footer, #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }

    /* প্রিমিয়াম মেম্বারশিপ ইনফো বক্স */
    .premium-card {
        background: rgba(99, 102, 241, 0.08) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# ৬. স্মার্ট এপিআই কী রোটেশন ইঞ্জিন
# =========================================================================
def get_ai_client():
    valid_keys = []
    for secret_key in st.secrets.keys():
        if "GEMINI_API_KEY" in secret_key:
            valid_keys.append(st.secrets[secret_key])
            
    if not valid_keys:
        st.error("Secrets-এ কোনো GEMINI_API_KEY পাওয়া যায়নি!")
        st.stop()
        
    return genai.Client(api_key=random.choice(valid_keys))

# =========================================================================
# ৭. সাইডবার লেআউট (লগইন, সাইনআপ এবং $9 প্রিমিয়াম প্যাকেজ)
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #6366f1; font-weight: 700; margin-bottom:0;'>OvroAI 2026</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 13px;'>Next-Gen Intelligent Core</p>", unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.is_logged_in:
        st.markdown("<b style='color: #94a3b8; font-size: 15px;'>🔒 লগইন প্যানেল (ঐচ্ছিক)</b>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Username", key="user_field")
        pwd = st.text_input("Password", type="password", placeholder="Password", key="pass_field")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, key="login_action"):
                if user == "rifat" and pwd == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Pro"
                    st.query_params["login"] = "true"
                    st.query_params["tier"] = "Pro"
                    st.rerun()
                else:
                    st.error("ভুল তথ্য!")
        with col2:
            st.button("Sign Up", use_container_width=True, key="signup_action")
    else:
        # প্রিমিয়াম মেম্বারশিপ টায়ার ($9 প্রাইসিং ফিক্স)
        st.markdown(f"""
            <div class='premium-card'>
                <p style='margin:0; font-size:12px; color:#94a3b8;'>Subscription Plan</p>
                <h3 style='margin:0; color:#fbbf24;'>💎 {st.session_state.user_tier} Member</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<b style='color: #94a3b8; font-size: 14px;'>🏆 একটিভ ফিচারসমূহ:</b>", unsafe_allow_html=True)
        st.markdown("- আনলিমিটেড আল্ট্রা-ফাস্ট এপিআই কল\n- ২০২৬ রিয়েল-টাইম গ্লোবাল ডেটা")
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.user_tier == "Basic":
            if st.button("Upgrade to Pro ($9/mo)", use_container_width=True, key="upgrade_to_pro_btn"):
                st.balloons()
                st.session_state.user_tier = "Pro"
                st.query_params["tier"] = "Pro"
                st.rerun()
        elif st.session_state.user_tier == "Pro":
            if st.button("Upgrade to Elite ($49/mo)", use_container_width=True, key="elite_btn"):
                st.balloons()
                st.session_state.user_tier = "Elite"
                st.query_params["tier"] = "Elite"
                st.rerun()
        else:
            st.success("👑 Elite Active (Maximum Access)")
            
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True, key="logout_action"):
            st.session_state.is_logged_in = False
            st.query_params.clear()
            st.rerun()

    st.markdown("---")
    if st.button("➕ New Conversation", use_container_width=True, key="new_chat_action"):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৮. মূল চ্যাট ইন্টারফেস
# =========================================================================
st.markdown("<h1 style='text-align: center; color: #ffffff; margin-bottom:0;'>🤖 OvroAI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>2026 Core Engine • Powered by Refat Aoul</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# চ্যাট হিস্ট্রি ডিসপ্লে
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# চ্যাট ইনপুট প্রসেসিং
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
                st.warning("⏱️ বর্তমান লাইনটি ব্যস্ত! ব্যাকএন্ড অন্য লাইনে ট্রাই করছে, দয়া করে আবার সেন্ড করুন।")
            else:
                st.error(f"Error: {e}")
