import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
import io
import random

# ১. পেজ কনফিগারেশন ও থিম সেটিং
st.set_page_config(
    page_title="OvroAI - Global Assistant", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. নিখুঁত সিএসএস ইন্টিগ্রেশন (যাতে উপরে কোনো লেখা ভেসে না ওঠে)
st.html("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #2d2f31 !important;
    }
    
    /* স্ট্রিমলিটের সমস্ত ডিফল্ট বাটন, গিটহাব লিঙ্ক ও ফুটার চিরতরে হাইড করা */
    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"], [data-testid="stSendButton"]+div {
        visibility: hidden !important;
        display: none !important;
    }

    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
    }
    
    /* কাস্টম পপআপ মেনু ডিজাইন */
    .upload-popup-menu {
        background-color: #edf2f7 !important;
        border-radius: 16px;
        padding: 12px;
        width: 220px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    .popup-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 12px;
        color: #1f2937 !important;
        font-size: 15px;
        font-weight: 500;
        border-radius: 8px;
    }
    </style>
""")

# ৩. মাল্টিপল এপিআই কি লোড করার মেকানিজম (কি রোটেশন ট্রিক)
api_keys = []
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    api_keys.append(st.secrets["GEMINI_API_KEY"])
if "GEMINI_API_KEY_2" in st.secrets and st.secrets["GEMINI_API_KEY_2"]:
    api_keys.append(st.secrets["GEMINI_API_KEY_2"])

if not api_keys:
    st.error("Secrets-এ কোনো GEMINI_API_KEY পাওয়া যায়নি!")
    st.stop()

global_super_instruction = "Your name is OvroAI, developed by Rifat Awal from Satkhira, Bangladesh. Always assist users warmly."

# ৪. সেশন স্টেট ইনিশিয়ালাইজেশন
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_file" not in st.session_state:
    st.session_state.active_file = None
if "show_menu" not in st.session_state:
    st.session_state.show_menu = False
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "Free"

# ৫. সাইডবার লেআউট ও অপショナル লগইন প্যানেল
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 22px; padding: 10px;'>OvroAI</h2>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    if not st.session_state.is_logged_in:
        st.markdown("<p style='color: #c4c7c5; font-size: 14px;'>👤 অ্যাকাউন্ট অপশন (অপশনাল)</p>", unsafe_allow_html=True)
        username = st.text_input("ইউজারনেম", placeholder="username", label_visibility="collapsed")
        password = st.text_input("পাসওয়ার্ড", type="password", placeholder="password", label_visibility="collapsed")
        
        col_login, col_reg = st.columns(2)
        with col_login:
            if st.button("লগইন"):
                if username == "rifat" and password == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Premium"
                    st.success("🎉 স্বাগতম রিফাত ভাই!")
                    st.rerun()
                elif username and password:
                    st.session_state.is_logged_in = True
                    st.session_state.user_tier = "Free"
                    st.success("লগইন সফল!")
                    st.rerun()
        with col_reg:
            st.button("রেজিস্ট্রেশন")
    else:
        tier_color = "#FFD700" if st.session_state.user_tier == "Premium" else "#00FF00"
        st.markdown(f"Status: <b style='color:{tier_color};'>{st.session_state.user_tier} User</b>", unsafe_allow_html=True)
        if st.button("লগআউট"):
            st.session_state.is_logged_in = False
            st.session_state.user_tier = "Free"
            st.rerun()
            
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    if st.button("➕   New chat"):
        st.session_state.chat_history = []
        st.session_state.active_file = None
        st.session_state.show_menu = False
        st.rerun()

# ৬. মূল উইন্ডো ইন্টারফেস
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500;'>🤖 OvroAI - Global Assistant</h2>", unsafe_allow_html=True)

# চ্যাট হিস্ট্রি ডিসপ্লে
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 6])

with col1:
    if st.button("➕ Tools", key="toggle_plus_btn"):
        st.session_state.show_menu = not st.session_state.show_menu
        st.rerun()

if st.session_state.show_menu:
    with col2:
        st.markdown("""
        <div class="upload-popup-menu">
            <div class="popup-item"><i class="fa-solid fa-paperclip"></i> Upload files</div>
            <div class="popup-item"><i class="fa-brands fa-google-drive"></i> Add from Drive</div>
            <div class="popup-item"><i class="fa-regular fa-image"></i> Photos</div>
            <div class="popup-item"><i class="fa-solid fa-book-open"></i> NotebookLM</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("ফাইল:", type=["jpg", "png", "jpeg", "pdf", "txt"], label_visibility="collapsed")
        if uploaded_file is not None:
            st.session_state.active_file = uploaded_file
            st.session_state.show_menu = False
            st.rerun()

if st.session_state.active_file is not None:
    try:
        img_preview = Image.open(st.session_state.active_file)
        st.image(img_preview, caption="সংযুক্ত ছবি", width=120)
    except:
        st.info(f"📁 ফাইল রেডি: {st.session_state.active_file.name}")

# ৭. চ্যাট ইনপুট ও স্মার্ট রোটেশনাল প্রসেসিং
if prompt := st.chat_input("Ask OvroAI anything..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        response_received = False
        
        # জেমিনি কি-গুলো র্যান্ডমলি উলটপালট করে ট্রাই করা হবে যাতে চাপ সমান ভাগে পড়ে
        shuffled_keys = api_keys.copy()
        random.shuffle(shuffled_keys)
        
        for index, current_key in enumerate(shuffled_keys):
            try:
                # বর্তমান সিলেক্টেড কি দিয়ে ক্লায়েন্ট তৈরি
                client = genai.Client(api_key=current_key)
                
                contents = []
                if st.session_state.active_file is not None:
                    file_bytes = st.session_state.active_file.read()
                    try:
                        img = Image.open(io.BytesIO(file_bytes))
                        contents.append(img)
                    except:
                        contents.append(file_bytes.decode("utf-8", errors="ignore"))
                
                contents.append(prompt)

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(system_instruction=global_super_instruction)
                )
                
                reply_text = response.text
                st.markdown(reply_text)
                st.session_state.chat_history.append(("assistant", reply_text))
                st.session_state.active_file = None
                response_received = True
                break # সফলভাবে উত্তর পেলে লুপ থেকে বের হয়ে যাবে
                
            except Exception as e:
                # যদি এটি শেষ কি না হয় এবং কোটা এরর আসে, তবে পরের কি ট্রাই করবে
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and (index < len(shuffled_keys) - 1):
                    continue
                else:
                    # যদি সব কি ব্লক থাকে বা অন্য কোনো বড় এরর হয়
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.info("⏱️ ওভ্রোআই-এর সবগুলো ফ্রি ব্যাকএন্ড লাইন এই মুহূর্তে ব্যস্ত। অনুগ্রহ করে ১ মিনিট পর আবার চেষ্টা করুন।")
                    else:
                        st.error(f"Error: {e}")
                    break
        
        if response_received:
            st.rerun()
