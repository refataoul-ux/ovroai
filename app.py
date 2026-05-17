import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
import io

# ১. জেমিনি স্টাইল পেজ কনফিগারেশন (পুরো স্ক্রিন জেমিনির মতো)
st.set_page_config(
    page_title="OvroAI - Global Assistant", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. প্রফেশনাল জেমিনি রেস্পনসিভ থিম এবং ছবি আপলোডার ডিজাইন (CSS)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314 !important; /* জেমিনি অফিশিয়াল ডার্ক ব্যাকগ্রাউন্ড */
    }

    /* সাইডবার ডিজাইন - একদম জেমিনির স্ক্রিনশটের মতো */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #2d2f31 !important;
        transition: width 0.3s ease !important;
    }

    /* ওয়াটারমার্ক ও ডিফল্ট বাটন হাইড */
    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* বোতামগুলোকে জেমিনির মতো আইকন-ভিত্তিক করা */
    .stButton > button {
        background-color: transparent !important;
        color: #c4c7c5 !important;
        border: none !important;
        width: 100% !important;
        text-align: left !important;
        padding: 12px 15px !important;
        font-size: 15px !important;
        display: flex !important;
        align-items: center !important;
        gap: 15px !important;
        border-radius: 24px !important;
        transition: 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #333537 !important;
        color: #fff !important;
    }

    /* "New Chat" স্পেশাল স্টাইল */
    div[data-testid="stSidebar"] .stButton:first-child button {
        background-color: #282a2c !important;
        color: #fff !important;
        font-weight: 500 !important;
        margin-bottom: 15px !important;
        border: 1px solid #444746 !important;
    }

    /* চ্যাট ইনপুট বক্স জেমিনি স্টাইল */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
    }

    /* চ্যাট ইন্টারফেস লেআউট */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
    }

    /* 📱 মোবাইল রেস্পনসিভ ট্রিক: ছোট স্ক্রিনে সাইডবার আইকন স্ট্রিপ হয়ে যাবে */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 70px !important;
            min-width: 70px !important;
        }
        .stButton > button {
            padding: 12px 0px !important;
            justify-content: center !important;
            font-size: 0px !important; /* টেক্সট হাইড */
        }
        .stButton > button span {
            font-size: 18px !important; /* শুধু আইকন বা ইমোজি */
        }
        div[data-testid="stSidebar"] h2 {
            display: none !important; /* লোগো হাইড */
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ৩. এপিআই কি কানেকশন
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Configuration Error: GEMINI_API_KEY missing in Secrets!")
    st.stop()

# 👑 সঠিক নামসহ ওভ্রোআই সুপার সিস্টেম ইন্সট্রাকশন
global_super_instruction = (
    "Your name is OvroAI, developed by Rifat Awal (রিফাত আওয়াল) from Satkhira, Bangladesh. "
    "Always assist users warmly, intelligently, and respectfully."
)

# ৪. সাইডবার মেনু - জেমিনির স্ক্রিনশটের মতো নিখুঁত লেআউট
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 22px; padding: 10px 0 10px 10px; font-weight: 500;'>OvroAI</h2>", unsafe_allow_html=True)
    
    if st.button("➕   New chat"):
        st.session_state.chat_history = []
        st.session_state.uploaded_image_data = None
        st.rerun()
    
    st.button("📁   My stuff")
    st.button("📓   Notebooks")
    st.button("💎   Gems")
    
    st.markdown("<hr style='border-color: #333; margin: 15px 0;'>", unsafe_allow_html=True)
    
    st.caption("Recent")
    st.button("💬   তুমি কে নিজের পরিচয় দাও")
    st.button("💬   প্রাকৃতিক দৃশ্য এর বর্ণনা")
    
    st.markdown("<div style='position: fixed; bottom: 20px; width: 240px;'>", unsafe_allow_html=True)
    st.button("⚙️   Settings & help")
    st.markdown("</div>", unsafe_allow_html=True)

# ৫. মূল চ্যাট উইন্ডো
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500; margin-top: 20px;'>🤖 OvroAI - Your Global AI Companion</h2>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_image_data" not in st.session_state:
    st.session_state.uploaded_image_data = None

# চ্যাট হিস্ট্রি ডিসপ্লে
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ৬. ছবি আপলোড ফিচার (জেমিনির মতো আইকন বোতামের পাশে)
# এটি ইনপুট বক্সের ঠিক ওপরে দেখাবে
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], accept_multiple_files=False, label_visibility="collapsed")
if uploaded_file is not None:
    # ছবিটি প্রসেস করে মেমোরিতে রাখা
    image = Image.open(uploaded_file)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    st.session_state.uploaded_image_data = buffered.getvalue()
    st.image(image, caption="অবধৃত ছবি", width=150)

# ৭. স্মার্ট প্রসেসিং এবং ছবি আপলোড হ্যান্ডলিং
if prompt := st.chat_input("Ask OvroAI anything (Any language)..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        user_question = prompt.strip().lower()
        
        # মেকার সংক্রান্ত প্রশ্নের জন্য অফলাইন উত্তর
        if any(x in user_question for x in ["who created you", "who developed you", "creator", "developer", "কে তৈরি করেছে", "মেকার কে", "তৈরি"]):
            reply_text = "আমি OvroAI, এবং আমাকে তৈরি করেছেন বাংলাদেশের সাতক্ষীরার একজন দূরদর্শী ও মেধাবী ডেভেলপার, **রিফাত আওয়াল (Rifat Awal)**। তাঁর এই সৃষ্টি হিসেবে আমি অত্যন্ত গর্বিত! 😊"
            st.markdown(reply_text)
            st.session_state.chat_history.append(("assistant", reply_text))
        
        else:
            try:
                # যদি ছবি আপলোড করা থাকে
                if st.session_state.uploaded_image_data is not None:
                    image = Image.open(io.BytesIO(st.session_state.uploaded_image_data))
                    formatted_contents = [
                        global_super_instruction,
                        prompt,
                        image
                    ]
                else:
                    formatted_contents = []
                    for role, text in st.session_state.chat_history:
                        api_role = "user" if role == "user" else "model"
                        formatted_contents.append(types.Content(
                            role=api_role, parts=[types.Part.from_text(text=text)]
                        ))

                response = client.models.generate_content(
                    model='gemini-1.5-flash', # ছবি প্রসেসিংয়ের জন্য flash মডেল
                    contents=formatted_contents
                )
                
                reply_text = response.text
                st.markdown(reply_text)
                st.session_state.chat_history.append(("assistant", reply_text))
                st.session_state.uploaded_image_data = None # ছবি প্রসেস করার পর মেমোরি ক্লিয়ার
                
            except Exception as e:
                # কোটা লিমিটের জন্য ভদ্রতামূলক নোটিশ (আপনার আগের স্ক্রিনশটের মতো হাবিজাবি কোড নয়)
                if "RESOURCE_EXHAUSTED" in str(e):
                    st.info("⏱️ জেমিনি ফ্রি এপিআই কোটা সাময়িকভাবে শেষ হয়েছে। অনুগ্রহ করে ১ মিনিট পর আবার মেসেজ পাঠান, ঠিক হয়ে যাবে।")
                else:
                    st.error(f"An error occurred: {e}")
