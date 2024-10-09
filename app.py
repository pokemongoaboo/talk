import streamlit as st
import os
from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS
import io
import base64

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 使用最新可用的模型
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
    st.set_page_config(page_title="AI 語音聊天", page_icon="🎤")
    st.title("用語音與你的 AI 朋友互動聊天")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 使用 speech_recognition 進行語音識別
    r = sr.Recognizer()
    if st.button("開始說話"):
        with sr.Microphone() as source:
            st.write("請說話...")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="zh-TW")
                st.write(f"您說的是：{text}")
                
                # 處理用戶輸入
                st.session_state.messages.append({"role": "user", "content": text})
                with st.chat_message("user"):
                    st.markdown(text)

                # 獲取 AI 回應
                ai_response = get_ai_response(text)
                if ai_response:
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                    
                    # 將 AI 回應轉換為語音
                    audio_bytes = text_to_speech(ai_response)
                    audio_base64 = base64.b64encode(audio_bytes).decode()
                    audio_tag = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}">'
                    st.markdown(audio_tag, unsafe_allow_html=True)

            except sr.UnknownValueError:
                st.write("無法識別您的語音")
            except sr.RequestError as e:
                st.write(f"無法從Google Speech Recognition服務獲取結果; {e}")

if __name__ == "__main__":
    main()
