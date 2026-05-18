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
# ৩. সেশন স্টেট কন্ট্রোল (স্প্ল্যাশ স্ক্রিন যেন লাইফে শুধু প্রথমবার আসে)
# =========================================================================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "Basic"
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

# =========================================================================
# ৪. ২.৫ সেকেন্ডের জন্য স্প্ল্যাশ স্ক্রিন (অটো-ভ্যানিশ লজিক সহ)
# =========================================================================
if not st.session_state.intro_done:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700&family=Inter:wght@400;700&display=swap');
            
            #intro-overlay {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: #020408;
                z-index: 9999999;
                display: flex;
                justify-content: center;
                align-items: center;
                opacity: 1;
                transform: translateY(0);
                transition: transform 0.8s cubic-bezier(0.85, 0, 0.15, 1), opacity 0.6s ease-in-out;
            }
            
            .intro-box {
                text-align: center;
                animation: smoothPulse 1.2s ease-in-out infinite;
            }
            
            /* বেগুনী গ্লোয়িং লোগো */
            .logo-title {
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 70px;
                font-weight: 700;
                color: #a855f7; 
                text-shadow: 0 0 25px rgba(168, 85, 247, 0.7), 0 0 50px rgba(168, 85, 247, 0.4);
                margin-bottom: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }
            
            /* CREATED BY সাদা */
            .sub-text {
                font-family: 'Inter', sans-serif;
                font-size: 15px;
                color: #ffffff; 
                letter-spacing: 5px;
                text-transform: uppercase;
                margin-top: 15px;
                font-weight: 400;
            }
            
            /* REFAT AOUL নীল গ্লো */
            .designer-name {
                color: #6366f1; 
                font-weight: 700;
                text-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
            }

            @keyframes smoothPulse {
                0%, 100% { opacity: 0.7; transform: scale(0.99); }
                50% { opacity: 1; transform: scale(1.01); }
            }
            </style>

            <div id="intro-overlay">
                <div class="intro-box">
                    <div class="logo-title">🤖 OvroAI</div>
                    <div class="sub-text">CREATED BY <span class="designer-name">REFAT AOUL</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(2.5)  # লোগোটি ২.৫ সেকেন্ড থাকবে
    
    placeholder.empty()  # মেমোরি থেকে চিরতরে মুছে গেল
    st.session_state.intro_done = True  # লক হয়ে গেল, আর কখনো Rerun-এ আসবে না
    st.rerun()

# =========================================================================
# ৫. মূল অ্যাপ্লিকেশনের গ্লোবাল স্টাইল (UI/UX ও বাংলা ফন্ট ফিক্স)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Hind+Siliguri:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', 'Hind Siliguri', sans-serif !important;
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
        color: #f1f5f9 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #05070c !important;
        border-right: 1px solid rgba(168, 85, 247, 0.15) !important;
    }

    div[data-testid="stHeader"] > div:first-child { display: none !important; }
    div.stDeployButton, footer, #MainMenu, [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stChatInput"] { border-radius: 16px !important; border: 1px solid rgba(168, 85, 247, 0.3) !important; }
    
    .premium-sidebar-card {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(99, 102, 241, 0.05));
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# ৬. স্মার্ট এপিআই কী রোটেশন ব্যাকএন্ড ইঞ্জিন (লিস্ট বাগ ফিক্সড)
# =========================================================================
def get_ai_client():
    valid_keys = []
    
    # প্রথমে সরাসরি একক কী চেক করা হচ্ছে
    if "GEMINI_API_KEY" in st.secrets:
        key_val = st.secrets["GEMINI_API_KEY"]
        if isinstance(key_val, str) and key_val.strip():
            valid_keys.append(key_val.strip())
        elif isinstance(key_val, list):
            for k in key_val:
                if isinstance(k, str) and k.strip():
                    valid_keys.append(k.strip())
                    
    # মাল্টিপল কী রোটেশনের জন্য অন্যান্য কী-গুলো স্ক্যান করা হচ্ছে
    for secret_key in st.secrets.keys():
        if "GEMINI_API_KEY" in secret_key and secret_key != "GEMINI_API_KEY":
            key_val = st.secrets[secret_key]
            if isinstance(key_val, str) and key_val.strip():
                valid_keys.append(key_val.strip())
            elif isinstance(key_val, list):
                for k in key_val:
                    if isinstance(k, str) and k.strip():
                        valid_keys.append(k.strip())
                        
    # ডুপ্লিকেট কী থাকলে তা ফিল্টার করে বাদ দেওয়া হচ্ছে
    valid_keys = list(set(valid_keys))
            
    if not valid_keys:
        st.error("Secrets-এ কোনো বৈধ GEMINI_API_KEY (String) পাওয়া যায়নি! দয়া করে .streamlit/secrets.toml ফাইলটি চেক করুন।")
        st.stop()
        
    return genai.Client(api_key=random.choice(valid_keys))

# =========================================================================
# ৭. সাইডবার এবং প্রিমিয়াম মেম্বারশিপ অপশন প্যানেল
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #a855f7; font-weight: 700; margin-bottom: 0;'>🤖 OvroAI Core</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 12px; margin-top:0;'>Next-Gen AI Workspace</p>", unsafe_allow_html=True)
    st.markdown("---")

    # লগইন প্যানেল
    if not st.session_state.is_logged_in:
        st.markdown("<b style='color: #94a3b8; font-size: 14px;'>🔒 সিস্টেম লগইন</b>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="rifat", label_visibility="collapsed", key="sidebar_user")
        pwd = st.text_input("Password", type="password", placeholder="1234", label_visibility="collapsed", key="sidebar_pass")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, key="sidebar_login_btn"):
                if user == "rifat" and pwd == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Pro"
                    st.rerun()
                else:
                    st.error("ভুল তথ্য!")
        with col2:
            st.button("Sign Up", use_container_width=True, key="sidebar_signup_btn")
            
    st.markdown("---")

    # 💎 প্রিমিয়াম মেম্বারশিপ বক্স ($9 অপশন)
    st.markdown("<div class='premium-sidebar-card'>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #94a3b8; margin:0; font-size:12px;'>CURRENT PLAN</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #fbbf24; margin-top:5px; margin-bottom:15px;'>👑 {st.session_state.user_tier} Tier</h3>", unsafe_allow_html=True)
    
    if st.session_state.user_tier == "Basic":
        if st.button("Upgrade to Pro ($9/mo)", use_container_width=True, key="upgrade_pro_9"):
            st.session_state.user_tier = "Pro"
            st.balloons()
            st.rerun()
    elif st.session_state.user_tier == "Pro":
        st.markdown("<p style='color: #22c55e; font-size:14px; font-weight:600;'>✅ $9 Pro Plan Active</p>", unsafe_allow_html=True)
        if st.button("Upgrade to Elite ($49/mo)", use_container_width=True, key="upgrade_elite_49"):
            st.session_state.user_tier = "Elite"
            st.snow()
            st.rerun()
    else:
        st.markdown("<p style='color: #a855f7; font-size:14px; font-weight:600;'>👑 Elite Maximum Active</p>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("➕ New Conversation", use_container_width=True, key="new_chat_sidebar"):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================================
# ৮. মূল চ্যাট উইন্ডো ইন্টারফেস (১০০% রিয়েল এপিআই কানেকশন)
# =========================================================================
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 0;'>🤖 OvroAI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-top: 5px;'>2026 Core Engine • Created by Refat Aoul</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# চ্যাট হিস্ট্রি রেন্ডারিং
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# চ্যাট ইনপুট ও প্রসেসিং ইঞ্জিন
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
