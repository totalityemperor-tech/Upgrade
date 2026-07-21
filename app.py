import urllib.parse
import PIL.Image
import streamlit as st
from duckduckgo_search import DDGS
from google import genai
from streamlit_mic_recorder import speech_to_text

# 1. Setup Page Configuration
st.set_page_config(page_title="Omni-Tutor AI", page_icon="🎓")
st.title("🎓 Omni-Tutor AI")

# 2. Retrieve Gemini API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("Please configure your GEMINI_API_KEY in .streamlit/secrets.toml")
    st.stop()

# Initialize modern Gemini Client
client = genai.Client(api_key=api_key)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I am your AI Omni Tutor. Upload your homework, speak to me, or ask me to search the web or draw an image!",
        }
    ]

# 3. Sidebar Features (File Upload & Audio Input)
with st.sidebar:
    st.header("🛠️ Input Options")

    # File / Image Upload
    uploaded_file = st.file_uploader(
        "Upload Homework Image/Document", type=["png", "jpg", "jpeg", "pdf"]
    )

    # Speech-to-Text
    st.subheader("🎤 Voice Input")
    spoken_text = speech_to_text(
        language="en",
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="speech",
    )

    # Web Search Toggle
    use_web_search = st.checkbox("🔍 Enable Live Web Search")

# Display previous conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Determine Input Source (Text box or Voice)
user_prompt = st.chat_input("Ask a question or type 'draw [something]'...")
if spoken_text:
    user_prompt = spoken_text

if user_prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # IMAGE GENERATION FEATURE
    if user_prompt.lower().startswith(
        "draw "
    ) or user_prompt.lower().startswith("generate image of "):
        image_prompt = (
            user_prompt.lower()
            .replace("draw ", "")
            .replace("generate image of ", "")
        )
        encoded_prompt = urllib.parse.quote(image_prompt)
        image_url = f"https://pollinations.ai/p/{encoded_prompt}"

        with st.chat_message("assistant"):
            st.image(image_url, caption=f"Generated Image: {image_prompt}")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"![{image_prompt}]({image_url})",
                }
            )

    # AI CHAT / TUTORING FEATURE
    else:
        # Contextual Web Search Integration
        context = ""
        if use_web_search:
            with st.spinner("Searching the live web..."):
                try:
                    results = DDGS().text(user_prompt, max_results=3)
                    context = "\n\nLive Search Results:\n" + "\n".join(
                        [r["body"] for r in results if "body" in r]
                    )
                except Exception as e:
                    st.warning(f"Could not fetch web search results: {e}")

        prompt_with_context = f"""
        You are a friendly, encouraging homework tutor and social companion for a student. 
        Explain concepts simply and step-by-step.
        
        {context}
        
        Student Question: {user_prompt}
        """

        # Build contents list for Gemini call
        contents = [prompt_with_context]

        # Handle Image File Uploads if provided
        if uploaded_file and uploaded_file.type.startswith("image/"):
            img = PIL.Image.open(uploaded_file)
            contents.append(img)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=contents
                    )

                    st.write(response.text)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.text}
                    )
                except Exception as e:
                    st.error(f"Error generating response: {e}")
