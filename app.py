import base64
import urllib.parse
import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
from streamlit_mic_recorder import speech_to_text

# 1. Setup Page Configuration
st.set_page_config(page_title="Omni-Tutor AI", page_icon="🎓")
st.title("🎓 Omni-Tutor AI")

# 2. Retrieve OpenAI API Key
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.warning("Please configure your OPENAI_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I am your AI Omni Tutor. Upload your homework, speak to me, or ask me to search the web or draw an image!",
        }
    ]

# 3. Sidebar Features
with st.sidebar:
    st.header("🛠️ Input Options")

    # File / Image Upload
    uploaded_file = st.file_uploader(
        "Upload Homework Image", type=["png", "jpg", "jpeg"]
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

# Determine Input Source
user_prompt = st.chat_input("Ask a question or type 'draw [something]'...")
if spoken_text:
    user_prompt = spoken_text

if user_prompt:
    # Display user message
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
        # Contextual Web Search
        context = ""
        if use_web_search:
            with st.spinner("Searching the live web..."):
                try:
                    results = DDGS().text(user_prompt, max_results=3)
                    context = "\n\nLive Search Results:\n" + "\n".join(
                        [r["body"] for r in results if "body" in r]
                    )
                except Exception as e:
                    st.warning(f"Could not fetch search results: {e}")

        # Construct Prompt Content
        full_prompt = f"""You are a friendly, encouraging homework tutor. Explain concepts simply and step-by-step.

{context}

Student Question: {user_prompt}"""

        # Build message payload for OpenAI
        user_content = [{"type": "text", "text": full_prompt}]

        # Convert image to base64 if uploaded
        if uploaded_file:
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{uploaded_file.type};base64,{base64_image}"
                    },
                }
            )

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a helpful tutor."},
                            {"role": "user", "content": user_content},
                        ],
                    )

                    reply_text = response.choices[0].message.content
                    st.write(reply_text)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply_text}
                    )
                except Exception as e:
                    st.error(f"Error calling OpenAI API: {e}")
