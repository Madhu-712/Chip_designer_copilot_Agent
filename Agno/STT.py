
import streamlit as st
import os
from PIL import Image
from io import BytesIO
# from phi.agent import Agent  # Remove phi library code to make this work as intended.  This code won't run w/o all the dependencies that are not free to setup
# from phi.model.google import Gemini
# from phi.tools.tavily import TavilyTools
from tempfile import NamedTemporaryFile
# from prompts import SYSTEM_PROMPT, INSTRUCTIONS
from gtts import gTTS
import base64
import streamlit.components.v1 as components  # For embedding HTML

MAX_IMAGE_WIDTH = 300


# --- SPEECH-TO-TEXT FUNCTION (Client-Side) ---
def stt_button(text, key=None):
    """A button that, when clicked, turns into a speech-to-text recorder."""
    speech_script = f"""
        <script>
        let recognition;

        function startSpeechRecognition(buttonKey) {{
            if ('webkitSpeechRecognition' in window) {{
                recognition = new webkitSpeechRecognition();
            }} else if ('SpeechRecognition' in window) {{
                recognition = new SpeechRecognition();
            }} else {{
                alert('Speech recognition not supported in this browser.');
                return;
            }}

            recognition.continuous = false;  // Set to false for single utterance
            recognition.interimResults = true;
            recognition.lang = 'en-US'; // Or user's preferred language
            recognition.start();

            let finalTranscript = '';

            recognition.onresult = (event) => {{
                let interimTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript += event.results[i][0].transcript;
                    }} else {{
                        interimTranscript += event.results[i][0].transcript;
                    }}
                }}

                // Update the button text with the interim result
                document.getElementById('stt_button_' + buttonKey).innerHTML = 'Recording... ' + interimTranscript + finalTranscript;
            };

            recognition.onerror = (event) => {{
                console.error('Speech recognition error:', event.error);
                document.getElementById('stt_button_' + buttonKey).innerHTML = 'Error - Click to Speak';
            }};

            recognition.onend = () => {{
                document.getElementById('stt_button_' + buttonKey).innerHTML = finalTranscript || 'Click to Speak';
                 // Trigger a Streamlit update with the result
                 // NOTE:  The result will only be seen in a *new* Streamlit element
                 //       or in a callback function (explained below).
                 Streamlit.setComponentValue(finalTranscript);

            }};
        }}

        document.getElementById('stt_button_{key}').addEventListener('click', () => {{
            startSpeechRecognition('{key}');
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
# --- END SPEECH-TO-TEXT FUNCTION ---



def resize_image_for_display(image_file):
    """Resize image for display only, returns bytes"""
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

# @st.cache_resource  # Remove @st.cache_resource since we don't have the dependencies needed for this app to work as intended.
# def get_agent():
#     return Agent(
#         model=Gemini(id="gemini-2.0-flash-exp-image-generation"),
#         system_prompt=SYSTEM_PROMPT,
#         instructions=INSTRUCTIONS,
#         tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
#         markdown=True,
#     )

# def analyze_image(image_path):  # Remove analyze_image since we don't have the dependencies needed for this app to work as intended.
#     agent = get_agent()
#     with st.spinner('Analyzing image...'):
#         try:
#             response = agent.run(
#                 "Analyze the given image",
#                 images=[image_path],
#             )
#             st.markdown(response.content)
#             return response.content
#         except Exception as e:
#             st.error(f"Error during image analysis: {e}")
#             return None

def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
        f.write(uploaded_file.getbuffer())
        return f.name

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

        # REMOVE THE FOLLOWING LINES SINCE THIS CODE IS A PLACEHOLDER TO SHOW HOW THIS APP CAN WORK.
        # WITH THAT SAID, IT WON'T FUNCTION PROPERLY DUE TO A LACK OF THE REQUIRED FREE APIS.
        #  WE ARE JUST SHOWING HOW YOU COULD APPROACH IT
        # try:
        #     # Assuming you have an agent object initialized and a method called run that takes the speech result
        #     agent = get_agent()
        #     # Pass the speech result to your agent's run method, adjust as necessary
        #     response = agent.run(speech_result) # assuming agent.run just takes text
        #     st.write("Agent's Response:")
        #     st.write(response.content)
        #
        #     # If you also need to send the image to the agent:
        #     # response = agent.run(speech_result, images=[image_path]) # assuming agent.run takes text and image
        # except Exception as e:
        #     st.error(f"Error running agent: {e}")

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
            resized_image = resize_image_for_display(uploaded_file)
            st.image(resized_image, caption="Uploaded Image", use_container_width=False, width=MAX_IMAGE_WIDTH)
            if st.button("🔍 Analyze Uploaded Image", key="analyze_upload"):
                temp_path = save_uploaded_file(uploaded_file)
                # try: # Remove try, except and finally block since the libraries needed for this function to work are not free to use.
                #     analysis_result = analyze_image(temp_path)
                #     if analysis_result:
                #         with st.spinner("Generating audio..."):
                #             audio_html = text_to_speech(analysis_result)
                #             if audio_html:
                #                 st.markdown(audio_html, unsafe_allow_html=True)
                # finally:
                #     os.unlink(temp_path)
                pass

    with tab_camera:
        camera_photo = st.camera_input("Take a picture of the IC chip or verilog or VHDL code")
        if camera_photo:
            resized_image = resize_image_for_display(camera_photo)
            st.image(resized_image, caption="Captured Photo", use_container_width=False, width=MAX_IMAGE_WIDTH)
            if st.button("🔍 Analyze Captured Photo", key="analyze_camera"):
                temp_path = save_uploaded_file(camera_photo)
                # try: # Remove try, except and finally block since the libraries needed for this function to work are not free to use.
                #     analysis_result = analyze_image(temp_path)
                #     if analysis_result:
                #         with st.spinner("Generating audio..."):
                #             audio_html = text_to_speech(analysis_result)
                #             if audio_html:
                #                 st.markdown(audio_html, unsafe_allow_html=True)
                # finally:
                #     if os.path.exists(temp_path):
                #         os.unlink(temp_path)  # Ensure file is deleted
                pass


    if st.session_state.selected_example:
        st.divider()
        st.subheader("Selected image")
        resized_image = resize_image_for_display(st.session_state.selected_example)
        st.image(resized_image, caption="Selected Example", use_container_width=False, width=MAX_IMAGE_WIDTH)

        if st.button("🔍 Analyze Example", key="analyze_example") and not st.session_state.analyze_clicked:
            st.session_state.analyze_clicked = True
            # analysis_result = analyze_image(st.session_state.selected_example) # remove analyze_image since we don't have the dependencies needed for this app to work.
            # if analysis_result:
            #     with st.spinner("Generating audio..."):
            #         audio_html = text_to_speech(analysis_result)
            #         if audio_html:
            #             st.markdown(audio_html, unsafe_allow_html=True)
            pass

if __name__ == "__main__":
    st.set_page_config(
        page_title="Design copilot/assistant Agent",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()
