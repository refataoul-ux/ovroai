import streamlit as st
import os
import random

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
# ২. সেশন স্টেট কন্ট্রোল (লগইন এবং প্রিমিয়াম প্যাকেজ ব্যাকএন্ড)
# =========================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "Basic"
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

# =========================================================================
# ৩. আপনার লোগোর হুবহু কালার ও স্লো-মোশন ব্লিংকিং স্প্ল্যাশ স্ক্রিন (কোনো ল্যাগ নেই)
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700&family=Inter:wght@400;700&display=swap');
    
    /* ব্যাকগ্রাউন্ড সম্পূর্ণ ডার্ক */
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
        /* স্টাইলিশ ভাবে উপরে সরে যাওয়ার জন্য ট্র্যানজিশন */
        transition: transform 1.5s cubic-bezier(0.85, 0, 0.15, 1), opacity 1.2s ease-in-out;
    }
    
    .intro-box {
        text-align: center;
        /* ৪.৫ সেকেন্ড ব্যাপী একদম স্লো-মোশন ব্লিংকিং বা পালস ইফেক্ট */
        animation: slowMotionBlink 4.5s ease-in-out infinite;
    }
    
    /* আপনার দেওয়া লোগোর মতো বেগুনী গ্লো */
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
    
    /* CREATED BY অংশটি থাকবে সম্পূর্ণ সাদা */
    .sub-text {
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        color: #ffffff; 
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-top: 15px;
        font-weight: 400;
    }
    
    /* REFAT AOUL অংশটি থাকবে উজ্জ্বল নীল গ্লো */
    .designer-name {
        color: #6366f1; 
        font-weight: 700;
        text-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
    }

    /* মসৃণ স্লো-মোশন ব্লিংকিং অ্যানিমেশন */
    @keyframes slowMotionBlink {
        0%, 100% { opacity: 0.5; transform: scale(0.98); }
        50% { opacity: 1; transform: scale(1.01); filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.3)); }
    }

    /* মূল ড্যাশবোর্ড ও চ্যাট পেজের কাস্টম লাক্সারি লুক */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
    }
    [data-testid="stSidebar"] {
        background-color: #05070c !important;
        border-right: 1px solid rgba(168, 85, 247, 0.15) !important;
    }
    
    /* সাইডবারের স্থায়ী প্রিমিয়াম আপগ্রেড কার্ড */
    .premium-sidebar-card {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(99, 102, 241, 0.05));
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    </style>

    <div id="intro-overlay">
        <div class="intro-box">
            <div class="logo-title">🤖 OvroAI</div>
            <div class="sub-text">CREATED BY <span class="designer-name">REFAT AOUL</span></div>
        </div>
    </div>

    <script>
    // ঠিক ৪.৫ সেকেন্ড স্লো-মোশন অ্যানিমেশন দেখানোর পর স্টাইলিশ ভাবে উপরে স্লাইড হয়ে উঠে যাবে
    setTimeout(function() {
        var overlay = window.parent.document.getElementById('intro-overlay');
        if (overlay) {
            overlay.style.transform = 'translateY(-100vh)'; // স্টাইলিশ উপরের দিকে সরে যাওয়া
            overlay.style.opacity = '0';
            setTimeout(function() { overlay.style.display = 'none'; }, 1500);
        }
    }, 4500);
    </script>
    """, unsafe_allow_html=True)

# =========================================================================
# ৪. গিটহাব রিমুভাল ও ইন্টারফেস ক্লিনিং সিএসএস
# =========================================================================
st.markdown("""
    <style>
    div[data-testid="stHeader"] > div:first-child { display: none !important; }
    div.stDeployButton, footer, #MainMenu, [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stChatInput"] { border-radius: 16px !important; border: 1px solid rgba(168, 85, 247, 0.3) !important; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# ৫. স্থায়ী সাইডবার এবং প্রিমিয়াম মেম্বারশিপ অপশন প্যানেল
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #a855f7; font-weight: 700; margin-bottom: 0;'>🤖 OvroAI Core</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 12px; margin-top:0;'>Next-Gen AI Workspace</p>", unsafe_allow_html=True)
    st.markdown("---")

    # লগইন প্যানেল (অপশনাল অ্যাক্সেস)
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

    # 💎 আপনার কাঙ্ক্ষিত প্রিমিয়াম মেম্বারশিপ বক্স ($9 অপশন সহ)
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
        
    if st.session_state.is_logged_in:
        if st.button("Logout", use_container_width=True, key="logout_sidebar"):
            st.session_state.is_logged_in = False
            st.session_state.user_tier = "Basic"
            st.rerun()

# =========================================================================
# 👑 ৬. মূল চ্যাট উইন্ডো ইন্টারফেস
# =========================================================================
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 0;'>🤖 OvroAI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-top: 5px;'>2026 Intelligence Engine • Created by Refat Aoul</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# চ্যাট হিস্ট্রি রেন্ডারিং
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# চ্যাট প্রসেসিং কোড
if prompt := st.chat_input("OvroAI-কে কিছু জিজ্ঞেস করুন..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        # আপনার এপিআই কি রোটেশন ব্যাকএন্ড থেকে ডাইনামিক রেসপন্স জেনারেট করবে
        st.markdown("রেসপন্স প্রসেস হচ্ছে...")
