import streamlit as st
import os
from openai import OpenAI
from gtts import gTTS
import io
import base64

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你熱愛吐槽，對我說的話總是能雞蛋裡挑骨頭，找出許多負面的東西，但同時你又是我非常好的朋友，請帶著毒舌卻帶有一絲溫暖的對話。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in getting AI response: {str(e)}")
        return None

def text_to_speech(text):
    tts = gTTS(text=text, lang='zh-tw')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def main():
    st.set_page_config(page_title="AI 文字聊天", page_icon="💬")
    st.title("與你的 AI 朋友互動聊天")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 文字輸入
    user_input = st.text_input("輸入你的訊息", key="user_input")

    if st.button("發送"):
        if user_input:
            # 處理用戶輸入
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # 獲取 AI 回應
            ai_response = get_ai_response(user_input)
            if ai_response:
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                
                # 將 AI 回應轉換為語音
                audio_bytes = text_to_speech(ai_response)
                audio_base64 = base64.b64encode(audio_bytes).decode()
                st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}">', unsafe_allow_html=True)

    # 清除對話按鈕
    if st.button("清除對話"):
        st.session_state.messages = []
        st.experimental_rerun()

if __name__ == "__main__":
    main()
