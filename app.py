import streamlit as st
from google import genai
from google.genai import types

# ১. গ্লোবাল কনফিগারেশন (জেমিনির মতো রেস্পনসিভ লেআউট)
st.set_page_config(
    page_title="OvroAI - Global Assistant", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. প্রফেশনাল জেমিনি থিম এবং রেস্পনসিভ ডিজাইন (HTML/CSS ইঞ্জেকশন)
# টেক্সট ভেসে ওঠার সমস্যা চিরতরে বন্ধ করতে স্টাইলটিকে প্রপার ব্লকে রাখা হয়েছে
st.html("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314 !important; /* জেমিনি অফিশিয়াল ডার্ক ব্যাকগ্রাউন্ড */
    }

    /* সাইডবার জেমিনি থিম */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #2d2f31 !important;
    }

    /* স্ট্রিমলিটের ডিফল্ট বাড়তি বোতাম ও ফুটার হাইড করা */
    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* সাইডবারের বাটনগুলো জেমিনির মেনুর মতো প্রফেশনাল করা */
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

    /* ইনপুট বক্স ডিজাইন */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
    }

    /* মোবাইলে সাইডবার রেস্পনসিভ রাখার নিয়ম */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 70px !important;
            min-width: 70px !important;
        }
        .stButton > button {
            padding: 12px 0px !important;
            justify-content: center !important;
            font-size: 0px !important;
        }
        .stButton > button span {
            font-size: 18px !important;
        }
        div[data-testid="stSidebar"] h2 {
            display: none !important;
        }
    }
    </style>
""")

# ৩. এপিআই কি সেটআপ
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Configuration Error: GEMINI_API_KEY missing in Secrets!")
    st.stop()

# 👑 সঠিক নামসহ ওভ্রোআই সুপার সিস্টেম ইন্সট্রাকশন
global_super_instruction = (
    "Your name is OvroAI, a world-class, multi-lingual, and highly advanced AI assistant. "
    "You were developed by the visionary and talented developer Rifat Awal (রিফাত আওয়াল) from Satkhira, Bangladesh. "
    "Guidelines for your behavior:\n"
    "1. Identity: Always speak of yourself proudly as OvroAI. If asked about your creator, credit Rifat Awal (রিফাত আওয়াল) with respect and immense professional warmth.\n"
    "2. Creator Name Accuracy: In English, write 'Rifat Awal'. In Bengali, strictly write 'রিফাত আওয়াল'. Never spell it as রেফাত or আউল.\n"
    "3. Tone: Be exceptionally empathetic, ultra-smart, collaborative, and friendly.\n"
    "4. Language: Automatically adapt to the language the user is speaking.\n"
    "5. Response Sample for Creator: If asked 'Who created you?' or similar in Bengali, answer: 'আমি OvroAI, এবং আমাকে তৈরি করেছেন বাংলাদেশের সাতক্ষীরার একজন দূরदर्शी ও মেধাবী ডেভেলপার, রিফাত আওয়াল (Rifat Awal)। তাঁর এই সৃষ্টি হিসেবে আমি অত্যন্ত গর্বিত! 😊'"
)

# ৪. সাইডবার মেনু - জেমিনির নিখুঁত লেআউট
with st.sidebar:
    st.markdown("<h2 style='color: #e3e3e3; font-size: 22px; padding: 10px 0 10px 10px; font-weight: 500;'>OvroAI</h2>", unsafe_allow_html=True)
    
    if st.button("➕   New chat"):
        st.session_state.chat_history = []
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

# ৫. মূল চ্যাট এরিয়া
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500; margin-top: 20px;'>🤖 OvroAI - Your Global AI Companion</h2>", unsafe_allow_html=True)

# চ্যাট মেমোরি
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ৬. ব্যবহারকারীর ইনপুট ও প্রসেসিং
if prompt := st.chat_input("Ask OvroAI anything (Any language)..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        try:
            user_question = prompt.strip().lower()
            
            # মেকার সংক্রান্ত প্রশ্নের কাস্টম ইনস্ট্যান্ট নির্ভুল উত্তর
            if any(x in user_question for x in ["who created you", "who developed you", "creator", "developer", "কে তৈরি করেছে", "মেকার কে", "তৈরি"]):
                reply_text = "আমি OvroAI, এবং আমাকে তৈরি করেছেন বাংলাদেশের সাতক্ষীরার একজন দূরদর্শী ও মেধাবী ডেভেলপার, **রিফাত আওয়াল (Rifat Awal)**। তাঁর এই সৃষ্টি হিসেবে আমি অত্যন্ত গর্বিত! 😊"
                st.markdown(reply_text)
                st.session_state.chat_history.append(("assistant", reply_text))
            
            else:
                formatted_contents = []
                for role, text in st.session_state.chat_history:
                    api_role = "user" if role == "user" else "model"
                    formatted_contents.append(types.Content(
                        role=api_role,
                        parts=[types.Part.from_text(text=text)]
                    ))
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=global_super_instruction
                    )
                )
                
                reply_text = response.text
                st.markdown(reply_text)
                st.session_state.chat_history.append(("assistant", reply_text))
                
        except Exception as e:
            # কোটা শেষ হওয়ার এরর এলে ইউজার ফ্রেন্ডলি মেসেজ দেখানো
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.warning("⏱️ জেমিনি ফ্রি এপিআই কোটা সাময়িকভাবে শেষ হয়েছে। অনুগ্রহ করে ১ মিনিট পর আবার মেসেজ পাঠান, ঠিক হয়ে যাবে।")
            else:
                st.error(f"An error occurred: {e}")
