import streamlit as st
from google import genai

# এখানে আপনার আসল API Key টি বসান
API_KEY = "AIzaSyDKJ5NefPlfFA6-gTnJ-IFEJMxFgjRiV0g"

# জেমিনি ক্লায়েন্ট সেটআপ
client = genai.Client(api_key=API_KEY)

# অ্যাপের টাইটেল ও ডিজাইন
st.set_page_config(page_title="OvroAI", page_icon="🤖")
st.title("🤖 OvroAI - আপনার নিজস্ব এআই")
st.write("আমি OvroAI, আজ আপনাকে কীভাবে সাহায্য করতে পারি?")

# চ্যাট হিস্ট্রি বা মেসেজ জমা রাখার জায়গা তৈরি
if "messages" not in st.session_state:
    st.session_state.messages = []

# আগের মেসেজগুলো স্ক্রিনে দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ব্যবহারকারীর কাছ থেকে ইনপুট নেওয়া
if prompt := st.chat_input("OvroAI কে কিছু জিজ্ঞেস করুন..."):
    # ইউজারের মেসেজ স্ক্রিনে দেখানো ও সেভ করা
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # এআই এর কাছ থেকে উত্তর আনা
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"দুঃখিত, একটি সমস্যা হয়েছে: {e}")