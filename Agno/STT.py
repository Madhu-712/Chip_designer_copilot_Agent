
import streamlit as st
import streamlit.components.v1 as components

def stt_button(text, key=None):
    """A simple speech-to-text button."""
    speech_script = f"""
        <script>
        let recognition;
        let buttonKey = '{key}';

        function startSpeechRecognition(buttonKey) {{
            console.log('startSpeechRecognition called for key:', buttonKey); // DEBUG
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                recognition = new (webkitSpeechRecognition || SpeechRecognition)();
                recognition.continuous = false;
                recognition.interimResults = false;  // Simplify: no interim results
                recognition.lang = 'en-US';

                recognition.onresult = function(event) {{
                    const transcript = event.results[0][0].transcript;
                    console.log('Transcript:', transcript); // DEBUG
                    Streamlit.setComponentValue(transcript);
                }}

                recognition.onerror = function(event) {{
                    console.error('Speech recognition error:', event.error);
                }}

                recognition.onend = function() {{
                    console.log('Speech recognition ended.'); // DEBUG
                }}

                recognition.start();
            }} else {{
                alert('Speech recognition not supported.');
            }}
        }}

        document.getElementById('stt_button_' + buttonKey).addEventListener('click', function() {{
            console.log('Button clicked for key:', buttonKey); // DEBUG
            startSpeechRecognition(buttonKey);
        }});
        </script>
        """

    return components.html(
        f"""
        <button id="stt_button_{key}" style="width: 100%; padding: 10px;">{text}</button>
        {speech_script}
        """,
        height=50,
    )


def main():
    st.title("Simple STT Test")
    speech_result = stt_button("Speak", key="stt_1")  # Important: Provide a key!
    if speech_result:
        st.write(f"You said: {speech_result}")


if __name__ == "__main__":
    main()
