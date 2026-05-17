import streamlit as st
from google import genai
from google.genai import types

# ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="OvroAI - Global Assistant", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. প্রফেশনাল জেমিনি রেস্পনসিভ থিম (HTML/CSS)
st.html("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #131314 !important;
    }

    /* সাইডবার */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #2d2f31 !important;
    }

    #MainMenu, footer, header, div.stDeployButton, [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }

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

    div[data-testid="stSidebar"] .stButton:first-child button {
        background-color: #282a2c !important;
        color: #fff !important;
        font-weight: 500 !important;
        margin-bottom: 15px !important;
        border: 1px solid #444746 !important;
    }

    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
    }

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

# ৩. এপিআই কি কানেকশন
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Configuration Error: GEMINI_API_KEY missing in Secrets!")
    st.stop()

# 👑 সঠিক নামসহ সুপার সিস্টেম ইন্সট্রাকশন
global_super_instruction = (
    "Your name is OvroAI, developed by Rifat Awal (রিফাত আওয়াল) from Satkhira, Bangladesh. "
    "Always assist users warmly, intelligently, and respectfully."
)

# ৪. জেমিনি স্টাইল সাইডবার লেআউট
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

# ৫. মূল চ্যাট উইন্ডো
st.markdown("<h2 style='text-align: center; color: #e3e3e3; font-weight: 500; margin-top: 20px;'>🤖 OvroAI - Your Global AI Companion</h2>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ৬. স্মার্ট এরর হ্যান্ডলিং প্রসেসিং
if prompt := st.chat_input("Ask OvroAI anything (Any language)..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        user_question = prompt.strip().lower()
        
        # মেকার সংক্রান্ত প্রশ্নের জন্য ডাইরেক্ট অফলাইন ইনস্ট্যান্ট উত্তর (গুগল ব্লক থাকলেও এটি কাজ করবে)
        if any(x in user_question for x in ["who created you", "who developed you", "creator", "developer", "কে তৈরি করেছে", "মেকার কে", "তৈরি"]):
            reply_text = "আমি OvroAI, এবং আমাকে তৈরি করেছেন বাংলাদেশের সাতক্ষীরার একজন দূরদর্শী ও মেধাবী ডেভেলপার, **রিফাত আওয়াল (Rifat Awal)**। তাঁর এই সৃষ্টি হিসেবে আমি অত্যন্ত গর্বিত! 😊"
            st.markdown(reply_text)
            st.session_state.chat_history.append(("assistant", reply_text))
        
        else:
            try:
                formatted_contents = []
                for role, text in st.session_state.chat_history:
                    api_role = "user" if role == "user" else "model"
                    formatted_contents.append(types.Content(
                        role=api_role, parts=[types.Part.from_text(text=text)]
                    ))
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(system_instruction=global_super_instruction)
                )
                
                reply_text = response.text
                st.markdown(reply_text)
                st.session_state.chat_history.append(("assistant", reply_text))
                
            except Exception as e:
                # 🛠️ এটি সেই ব্যাকআপ ট্রিক: গুগল ব্লক দিলে এটি ইউজারকে সুন্দর নোটিশ দেখাবে, ক্র্যাশ করবে না
                st.info("📢 **ওভ্রোআই আপডেট নোটিশ:** গুগলের ফ্রি এপিআই (API) সার্ভার ওভারলোড থাকার কারণে সাময়িকভাবে চ্যাট সিস্টেমটি হোল্ডে আছে। ডেভেলপার রিফাত আওয়াল বর্তমানে এই অ্যাপে সরাসরি **বিকাশ মার্চেন্ট পেমেন্ট গেটওয়ে** যুক্ত করার কাজ করছেন, যার মাধ্যমে খুব শীঘ্রই আপনারা কোনো লিমিটেশন ছাড়াই প্রিমিয়াম স্পিডে ওভ্রোআই ব্যবহার করতে পারবেন! একটু পর আবার চেষ্টা করুন।")
