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
Today's date is Tuesday, May 19, 2026. 
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
            
            .sub-text {
                font-family: 'Inter', sans-serif;
                font-size: 15px;
                color: #ffffff; 
                letter-spacing: 5px;
                text-transform: uppercase;
                margin-top: 15px;
                font-weight: 400;
            }
            
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
        time.sleep(2.5)
    
    placeholder.empty()
    st.session_state.intro_done = True 
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
# ৬. সকল উপলব্ধ এপিআই কী লোড করার ফাংশন (ক্রমানুসারে সাজানো)
# =========================================================================
def load_all_keys():
    keys = []
    # ১ম কী-টি প্রথমে লিস্টে ঢুকবে
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
        keys.append(st.secrets["GEMINI_API_KEY"].strip())
    # ২য় কী-টি ব্যাকআপ হিসেবে লিস্টের পরে থাকবে
    if "GEMINI_API_KEY_2" in st.secrets and st.secrets["GEMINI_API_KEY_2"]:
        keys.append(st.secrets["GEMINI_API_KEY_2"].strip())
    return keys

# =========================================================================
# ৭. সাইডবার এবং প্রিমিয়াম মেম্বারশিপ অপশন প্যানেল
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #a855f7; font-weight: 700; margin-bottom: 0;'>🤖 OvroAI Core</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 12px; margin-top:0;'>Next-Gen AI Workspace</p>", unsafe_allow_html=True)
    st.markdown("---")

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
# ৮. মূল চ্যাট উইন্ডো ও স্মার্ট ফেল-ওভার জেনারেশন ইঞ্জিন
# =========================================================================
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 0;'>🤖 OvroAI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-top: 5px;'>2026 Core Engine • Created by Refat Aoul</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# আগের চ্যাট হিস্ট্রি রেন্ডার করা
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

if prompt := st.chat_input("OvroAI-কে কিছু জিজ্ঞেস করুন..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        available_keys = load_all_keys()
        
        if not available_keys:
            st.error("🔑 Secrets (secrets.toml) ফাইলে কোনো সঠিক এপিআই কী খুঁজে পাওয়া যায়নি।")
            st.stop()
            
        response_received = False
        last_error = ""

        # চ্যাট হিস্ট্রি প্রিপারেশন (নতুন google-genai SDK স্ট্রাকচার অনুযায়ী)
        recent_history = st.session_state.chat_history[-6:] # সর্বশেষ ৩ জোড়া মেসেজ পাঠানো হচ্ছে
        formatted_contents = [types.Content(role=role, parts=[types.Part.from_text(text=text)]) for role, text in recent_history]
        formatted_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

        # স্মার্ট কী রোটেশন ইঞ্জিন (১ম কী ফেইল করলে ২য় কী কাজ করবে)
        for index, current_key in enumerate(available_keys):
            try:
                client = genai.Client(api_key=current_key)
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(system_instruction=current_date_info)
                )
                
                reply = response.text
                st.markdown(reply)
                
                # সেশন স্টেটে নতুন চ্যাট সেভ করা
                st.session_state.chat_history.append(("user", prompt))
                st.session_state.chat_history.append(("assistant", reply))
                response_received = True
                break # সফল হলে লুপ থেকে বের হয়ে যাবে
                
            except Exception as e:
                last_error = str(e)
                # যদি ১ম কী নষ্ট বা কোটা শেষ হয়, তবে নোটিফিকেশন ছাড়াই ২য় কি ট্রাই করবে।
                continue 

        if not response_received:
            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                st.error("⏱️ গুগলের ফ্রি কোটা (সবগুলো Key-এর জন্য) সাময়িকভাবে সম্পূর্ণ শেষ। দয়া করে ১ মিনিট পর আবার চেষ্টা করুন।")
            else:
                st.error(f"API Error: {last_error}")
