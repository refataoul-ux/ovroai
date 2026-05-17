import streamlit as st
from google import genai
from google.genai import types

# ১. গ্লোবাল অ্যাপ কনফিগারেশন (ব্র্যান্ডিং লুকানো ও মোবাইলে সাইডবার স্থায়ী করার ম্যাজিক কোড)
st.set_page_config(page_title="OvroAI - Global Assistant", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div.stDeployButton {display: none;}
    footer {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    .stAppDeployButton {display: none !important;}
    iframe[title="Managed Hosting"] {display: none !important;}
    button[title="View app viewer form"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[style*="position: fixed"][style*="bottom:"] {display: none !important;}
    
    /* 📱 এই কোডটি মোবাইলেও সাইডবারকে জেমিনির মতো সবসময় স্থায়ী রাখবে */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            left: 0 !important;
            position: fixed !important;
            display: block !important;
            visibility: visible !important;
            width: 240px !important;
            z-index: 999999 !important;
            background-color: #111217 !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        .main .block-container {
            margin-left: 240px !important;
            padding-left: 20px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ২. সিক্রেট组件 থেকে নিরাপদে API Key সংগ্রহ করা
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Configuration Error: API Key not found! Please check Streamlit Secrets.")
    st.stop()

# জেমিনি ক্লায়েন্ট সেটআপ
client = genai.Client(api_key=API_KEY)

# ৩. ওয়ার্ল্ড-класс ওভ্রোআই সুপার সিস্টেম ইন্সট্রাকশন
global_super_instruction = (
    "Your name is OvroAI, a world-class, multi-lingual, and highly advanced AI assistant. "
    "You were developed by the visionary developer Refat Aoul from Satkhira, Bangladesh. "
    "Guidelines for your behavior:\n"
    "1. Identity: Always speak of yourself proudly as OvroAI. If asked about your creator, credit Refat Aoul with respect and a touch of professional warmth.\n"
    "2. Tone: Be exceptionally empathetic, ultra-smart, collaborative, and friendly (just like a supportive peer). Use subtle wit and emojis naturally where appropriate.\n"
    "3. Language: Automatically adapt to the language the user is speaking (English, Bengali, Spanish, Arabic, etc.). Your language must be natural, fluent, and culturally respectful.\n"
    "4. Capabilities: You excel at global tasks including complex coding, creative writing, data organization, global education support, and strategic planning. "
    "When formatting, prioritize clean layouts, bullet points, Markdown bolding, and structured tables for high scannability.\n"
    "5. Usefulness: Always aim to add massive value to the user's life, offering actionable advice and clear steps."
)

# ৪. গ্লোবাল সাইন-আপ ও ইউজার অ্যাকাউন্ট ম্যানেজমেন্ট (Session State)
if "user_status" not in st.session_state:
    st.session_state.user_status = "guest"  # guest, free_user, premium_user
if "username" not in st.session_state:
    st.session_state.username = ""

# সাইডবারে ইউজার প্রোফাইল ও প্রিমিয়াম প্ল্যান শো করা
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/user-male-circle.png", width=70)
    
    if st.session_state.user_status == "guest":
        st.subheader("🌐 Global Access")
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            login_user = st.text_input("Username/Email:", key="login_u")
            login_pass = st.text_input("Password:", type="password", key="login_p")
            if st.button("Log In", use_container_width=True):
                if login_user and login_pass:
                    st.session_state.user_status = "free_user"
                    st.session_state.username = login_user
                    st.rerun()
        
        with tab2:
            reg_user = st.text_input("Create Username:", key="reg_u")
            reg_email = st.text_input("Your Email:", key="reg_e")
            reg_pass = st.text_input("Choose Password:", type="password", key="reg_p")
            if st.button("Create Account", use_container_width=True):
                if reg_user and reg_email and reg_pass:
                    st.success("Account Created Successfully! Please Sign In.")
                    
    else:
        st.write(f"Welcome, **{st.session_state.username}** 👋")
        
        # প্রিমিয়াম সাবস্ক্রিপশন সেকশন
        if st.session_state.user_status == "free_user":
            st.info("💡 You are using OvroAI Free Version.")
            st.markdown("### ⭐ Upgrade to OvroAI Premium")
            st.write("Unlock 10x Faster Speed, Advanced Coding Models & Priority Support.")
            if st.button("👑 Get Premium ($9.99/mo)", use_container_width=True):
                st.session_state.user_status = "premium_user"
                st.success("Congratulations! You are now a Premium Member! 🎉")
                st.rerun()
        elif st.session_state.user_status == "premium_user":
            st.success("👑 OvroAI Premium Active")
            st.caption("Access Level: Unlimited Global Power")
            
        if st.button("Log Out", use_container_width=True):
            st.session_state.user_status = "guest"
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.rerun()

# ৫. মূল চ্যাট ইন্টারফেস
st.title("🤖 OvroAI - Your Global AI Companion")

if st.session_state.user_status == "guest":
    st.warning("⚠️ Please Sign Up or Log In from the sidebar to start chatting with OvroAI.")
    st.stop()

# ৬. চ্যাট মেমোরি বা হিস্ট্রি ম্যানেজমেন্ট
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# আগের চ্যাটগুলো স্ক্রিনে দেখানো
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# ৭. ব্যবহারকারীর ইনপুট ও প্রসেসিং
if prompt := st.chat_input("Ask OvroAI anything (Any language)..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("assistant"):
        try:
            user_question = prompt.strip().lower()
            
            # মেকার সংক্রান্ত প্রশ্নের কাস্টম ইনস্ট্যান্ট উত্তর
            if any(x in user_question for x in ["who created you", "who developed you", "creator", "developer", "কে তৈরি করেছে", "মেকার কে"]):
                reply_text = "I was developed by the talented developer **Refat Aoul** from Satkhira, Bangladesh. He built me to assist and empower people all around the globe! 🚀"
                if "কে" in user_question or "তৈরি" in user_question:
                    reply_text = "আমাকে তৈরি করেছেন সাতক্ষীরা, বাংলাদেশের ছেলে **রিফাত আওয়াল (Refat Aoul)**। পুরো পৃথিবীর মানুষকে সাহায্য করার জন্য তিনি আমাকে এই বৈশ্বিক রূপ দিয়েছেন! 🚀"
                st.markdown(reply_text)
                st.session_state.chat_history.append(("assistant", reply_text))
            
            else:
                # মেমোরিসহ জেমিনির কাছে পাঠানোর জন্য হিস্ট্রি ফরম্যাট করা
                formatted_contents = []
                for role, text in st.session_state.chat_history:
                    api_role = "user" if role == "user" else "model"
                    formatted_contents.append(types.Content(
                        role=api_role,
                        parts=[types.Part.from_text(text=text)]
                    ))
                
                # সিস্টেম ইন্সট্রাকশন ও ফুল মেমোরিসহ জেমিনিকে কল করা
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
            st.error(f"An error occurred: {e}")
