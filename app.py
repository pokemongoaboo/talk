import streamlit as st
import openai
import os
from gtts import gTTS
import speech_recognition as sr
import tempfile
import base64

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def text_to_speech(text, lang='zh-TW'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def get_ai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
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

def main():
    st.title("用語音與你的 AI 朋友互動聊天")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.button("開始說話"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("正在聆聽...")
            audio = recognizer.listen(source)
            st.write("處理中...")

        try:
            user_input = recognizer.recognize_google(audio, language="zh-TW")
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            ai_response = get_ai_response(user_input)
            if ai_response:
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                
                # Convert AI response to speech
                speech_file = text_to_speech(ai_response)
                autoplay_audio(speech_file)
                os.unlink(speech_file)

        except sr.UnknownValueError:
            st.error("無法識別語音")
        except sr.RequestError as e:
            st.error(f"無法連接到 Google 語音識別服務; {e}")

if __name__ == "__main__":
    main()
