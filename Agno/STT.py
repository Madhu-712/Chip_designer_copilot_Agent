
import streamlit as st
import streamlit.components.v1 as components
import os
from PIL import Image
from io import BytesIO
from tempfile import NamedTemporaryFile
from gtts import gTTS
import base64


MAX_IMAGE_WIDTH = 300

# --- SPEECH-TO-TEXT FUNCTION (Client-Side) ---
def stt_button(text, key=None):
    """A button that, when clicked, turns into a speech-to-text recorder."""
    speech_script = f"""
        <script>
        let recognition;
        let buttonKey = '{key}'; // Capture the buttonKey

        function startSpeechRecognition(buttonKey) {{
            if ('webkitSpeechRecognition' in window) {{
                recognition = new webkitSpeechRecognition();
            }} else if ('SpeechRecognition' in window) {{
                recognition = new SpeechRecognition();
            }} else {{
                alert('Speech recognition not supported in this browser.');
                return;
            }}

            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = function() {{
                document.getElementById('stt_button_' + buttonKey).innerHTML = 'Recording...';
            }}

            recognition.onresult = function(event) {{
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript += event.results[i][0].transcript;
                    }}
                }}
                document.getElementById('stt_button_' + buttonKey).innerHTML = finalTranscript || 'Click to Speak';

                // Send the final transcript back to Streamlit
                Streamlit.setComponentValue(finalTranscript);

            }};

            recognition.onerror = function(event) {{
                console.error('Speech recognition error:', event.error);
                document.getElementById('stt_button_' + buttonKey).innerHTML = 'Error - Click to Speak';
            }}

            recognition.onend = function() {{
                document.getElementById('stt_button_' + buttonKey).innerHTML = 'Click to Speak';
            }}

            recognition.start();
        }}

        document.getElementById('stt_button_' + buttonKey).addEventListener('click', function() {{
            startSpeechRecognition(buttonKey);
        }});
        </script>
        """

    return components.html(
        f"""
        <button id="stt_button_{key}" style="width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer;">
            {text}
        </button>
        {speech_script}
        """,
        height=50,
    )

def resize_image_for_display(image_file):
    """Resize image for display only, returns bytes"""
    try:
        if isinstance(image_file, str):
            img = Image.open(image_file)
        else:
            img = Image.open(image_file)
        img.seek(0)

        aspect_ratio = img.height / img.width
        new_height = int(MAX_IMAGE_WIDTH * aspect_ratio)
        img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None


def save_uploaded_file(uploaded_file):
    try:
        with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
            f.write(uploaded_file.getbuffer())
            return f.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None

def text_to_speech(text):
    """Converts the given text to speech and returns a playable audio widget."""
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        data_url = "data:audio/mp3;base64," + base64.b64encode(mp3_fp.read()).decode()
        return f"""
        <audio controls autoplay volume="0.5">
            <source src="{data_url}" type="audio/mp3">
        </audio>
        """
    except gTTS.tts.gTTSError as e:
        st.error(f"gTTS Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error during TTS: {type(e).__name__} - {e}") # Print the type of the exception and its message
        return None


def main():
    st.title("🤖🖥 Design Copilot Agent")

    # Add Speech-to-Text input
    speech_result = stt_button("Click to Speak", key="stt_1") # Add stt button.
    if speech_result: # If there's a result.
        st.write(f"You said: {speech_result}") # Write it out.
        # Now you can use speech_result as input to your application
        # For example, you could use it to search for something,
        # generate an image based on the text, etc.

    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = None
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False

    tab_examples, tab_upload, tab_camera = st.tabs([
        "📚 Example Products",
        "📤 Upload Image",
        "📸 Take Photo"
    ])

    with tab_examples:
        example_images = {
            "Chip 1": "images/Chip 1.jpg",
            "Chip 2": "images/Chip 2.jpg",
            "Code 1": "images/Code 1.jpg",
            "Code 2": "images/Code 2.jpg"
        }

        cols = st.columns(4)
        for idx, (name, path) in enumerate(example_images.items()):
            with cols[idx]:
                if st.button(name, use_container_width=True):
                    st.session_state.selected_example = path
                    st.session_state.analyze_clicked = False

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload product image",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of IC chip or verilog or VHDL code"
        )
        if uploaded_file:
            try:
                resized_image = resize_image_for_display(uploaded_file)
                if resized_image:
                    st.image(resized_image, caption="Uploaded Image", use_container_width=False, width=MAX_IMAGE_WIDTH)
            except Exception as e:
                st.error(f"Error displaying uploaded image: {e}")

    with tab_camera:
        camera_photo = st.camera_input("Take a picture of the IC chip or verilog or VHDL code")
        if camera_photo:
            try:
                resized_image = resize_image_for_display(camera_photo)
                if resized_image:
                    st.image(resized_image, caption="Captured Photo", use_container_width=False, width=MAX_IMAGE_WIDTH)
            except Exception as e:
                st.error(f"Error displaying captured photo: {e}")


    if st.session_state.selected_example:
        st.divider()
        st.subheader("Selected image")
        try:
            resized_image = resize_image_for_display(st.session_state.selected_example)
            if resized_image:
                st.image(resized_image, caption="Selected Example", use_container_width=False, width=MAX_IMAGE_WIDTH)
        except Exception as e:
            st.error(f"Error displaying selected example image: {e}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Design copilot/assistant Agent",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()
