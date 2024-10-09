import streamlit as st
import openai
import os

# Set up OpenAI API key
#openai.api_key = os.getenv("OPENAI_API_KEY")
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

def main():
    st.set_page_config(page_title="AI 語音聊天", page_icon="🎤")
    st.title("用語音與你的 AI 朋友互動聊天")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 使用 HTML 和 JavaScript 來處理語音輸入和輸出
    st.components.v1.html("""
    <script>
    let recognition;
    function startSpeechRecognition() {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'zh-TW';
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('speech-input').value = transcript;
            document.getElementById('submit-button').click();
        };
        recognition.start();
    }

    function speakResponse(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-TW';
        speechSynthesis.speak(utterance);
    }
    </script>
    <button onclick="startSpeechRecognition()">開始說話</button>
    <input type="hidden" id="speech-input">
    """, height=100)

    user_input = st.empty()
    speech_input = st.text_input("語音輸入結果", key="speech_input", label_visibility="hidden")

    if st.button("發送", key="submit-button"):
        if speech_input:
            st.session_state.messages.append({"role": "user", "content": speech_input})
            with st.chat_message("user"):
                st.markdown(speech_input)

            ai_response = get_ai_response(speech_input)
            if ai_response:
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                
                # 使用 JavaScript 來播放 AI 回應
                st.components.v1.html(f"""
                <script>
                speakResponse("{ai_response.replace('"', '\\"')}");
                </script>
                """)

            # 清空輸入
            user_input.text_input("語音輸入結果", value="", key="clear_input")

if __name__ == "__main__":
    main()
