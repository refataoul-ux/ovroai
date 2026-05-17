import streamlit as st
from google import genai

# এখানে আপনার নতুন জেনারেট করা API Key টি বসান
API_KEY = "AIzaSyAJRjN0fEuEkidYfr8dWCFtKyapqcfG6K0"

# জেমিনি ক্লায়েন্ট সেটআপ
client = genai.Client(api_key=API_KEY)

# অ্যাপের টাইটেল ও ডিজাইন
st.set_page_config(page_title="OvroAI", page_icon="🤖")
st.title("🤖 OvroAI - আপনার নিজস্ব এআই")
st.write("আমি OvroAI, আজ আপনাকে কীভাবে সাহায্য করতে পারি?")

# চ্যাট হিস্ট্রি বা মেসেজ জমা রাখার জায়গা তৈরি
if "messages" not in st.session_state:
    st.session_state.messages = []

# আগের মেসেজগুলো স্ক্রিনে দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ব্যবহারকারীর কাছ থেকে ইনপুট নেওয়া
if prompt := st.chat_input("OvroAI কে কিছু জিজ্ঞেস করুন..."):
    # ইউজারের মেসেজ স্ক্রিনে দেখানো ও সেভ করা
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # এআই এর কাছ থেকে উত্তর আনা
    with st.chat_message("assistant"):
        try:
            # প্রশ্নটি ছোট হাতের অক্ষরে রূপান্তর করে চেক করা (যাতে ইংরেজি বা বাংলা যেভাবে লিখুক কাজ করে)
            user_question = prompt.strip()
            
            # তৈরি করার প্রশ্নের জন্য কাস্টম উত্তর সেট করা
            if "কে তৈরি করেছে" in user_question or "তৈরি করেছে কে" in user_question or "maker" in user_question.lower() or "developer" in user_question.lower() or "তৈরি কর্তা" in user_question:
                custom_reply = "আমাকে তৈরি করেছেন সাতক্ষীরা, বাংলাদেশের ছেলে **রিফাত আওয়াল (Refat Aoul)**। 😎"
                st.markdown(custom_reply)
                st.session_state.messages.append({"role": "assistant", "content": custom_reply})
            
            else:
                # অন্য সব সাধারণ প্রশ্নের জন্য জেমিনি থেকে উত্তর আনা
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
        except Exception as e:
            st.error(f"দুঃখিত, একটি সমস্যা হয়েছে: {e}")
