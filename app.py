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
# ৩. আল্ট্রা-স্টাইলিশ স্প্ল্যাশ ইন্ট্রো ও প্রিমিয়াম UI/UX সিএসএস
# =========================================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* গ্লোবাল ডার্ক থিম */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: radial-gradient(circle at top right, #090d16, #020408) !important;
        color: #f1f5f9 !important;
    }}

    /* ⏳ ৩ সেকেন্ডের স্প্ল্যাশ ইন্ট্রো স্ক্রিন */
    #intro-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #020408;
        z-index: 9999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: opacity 1s ease-in-out, visibility 1s;
    }}
    
    .intro-logo {{
        font-size: 70px;
        font-weight: 700;
        background: linear-gradient(45deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 2s infinite alternate;
        margin-bottom: 10px;
    }}
    
    .intro-credits {{
        font-size: 20px;
        color: #94a3b8;
        letter-spacing: 3px;
        text-transform: uppercase;
        opacity: 0;
        animation: fadeInUp 1.5s forwards 0.5s;
    }}
    
    .creator-name {{
        color: #6366f1;
        font-weight: 700;
        text-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
    }}

    @keyframes pulseGlow {{
        0% {{ transform: scale(0.97); filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.4)); }}
        100% {{ transform: scale(1.03); filter: drop-shadow(0 0 35px rgba(168, 85, 247, 0.7)); }}
    }}
    @keyframes fadeInUp {{
        to {{ opacity: 1; transform: translateY(-5px); }}
    }}

    /* 🎯 সাইডবার ও স্লাইড আইকন ফিক্স */
    [data-testid="stSidebar"] {{
        background-color: #05070c !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
        transition: transform 0.5s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }}
    
    /* সাইডবার ফিরিয়ে আনার বাটন পিন করা */
    [data-testid="stSidebarCollapseButton"] {{
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
    }}

    /* 🔴 গিটহাব ও বাড়তি অপশন রিমুভাল */
    div[data-testid="stHeader"] > div:first-child {{
        display: none !important;
    }}
    div.stDeployButton, [data-testid="stDecoration"], footer, #MainMenu {{
        visibility: hidden !important;
        display: none !important;
    }}

    /* প্রিমিয়াম টায়ার কার্ড ডিজাইন */
    .tier-box {{
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid
