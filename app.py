import os
import streamlit as st
from google import genai
from google.genai import types

class AdvancedMedicalChatbot:
    """An advanced, production-grade AI Medical Chatbot with memory capabilities."""
    
    def __init__(self, api_key: str):
        # Encapsulating the API client configurations
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
        # System instructions enforcing strict medical boundaries and safety rules
        self.system_instruction = (
            "You are an AI Medical Assistant. Analyze user symptoms and offer personalized "
            "recommendations, potential causes, and lifestyle steps based on context. "
            "CRITICAL SAFETY RULE: You must always conclude your response with a highly visible "
            "disclaimer stating that you are an AI, not a healthcare provider, and they must "
            "seek official professional medical advice immediately for real diagnoses."
        )

    def generate_response(self, chat_history: list) -> str:
        """Processes the full conversation history to maintain memory context."""
        try:
            # Transforming our app's memory into the specific format the Gemini API expects
            contents = []
            for message in chat_history:
                role = "user" if message["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message["content"])]
                ))
            
            # Executing the contextual API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.3, # Low temperature ensures highly predictable, factual responses
                )
            )
            return response.text
        except Exception as e:
            return f"System Error: Unable to process request. Details: {str(e)}"

    def save_report(self, chat_history: list):
        """Feature 2: Compiles the full conversation and saves it to a clean local text file."""
        with open("medical_consultation_report.txt", "w", encoding="utf-8") as file:
            file.write("=== PERSONALIZED AI MEDICAL REPORT ===\n\n")
            for msg in chat_history:
                speaker = "Patient" if msg["role"] == "user" else "AI Medical Assistant"
                file.write(f"[{speaker}]:\n{msg['content']}\n")
                file.write("-" * 40 + "\n")
        return "Report successfully exported to 'medical_consultation_report.txt'!"



# STREAMLIT WEB INTERFACE

st.set_page_config(page_title="AI Medical Assistant", page_icon="🏥", layout="centered")

st.title("🏥 AI-Powered Medical Consultation Assistant")
st.caption("Enter your symptoms and medical history below for immediate personalized logic guidance.")

# Hardcoding Mr. James' provided API Key directly into the system engine initialization
MR_JAMES_API_KEY = "AQ.Ab8RN6LBQEl-CHGK4dKX-Nhiy83Ecb2C9pzHc8ci_pTT1WJADw"

# Initializing the chatbot object and keeping it alive across web refreshes using Streamlit session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = AdvancedMedicalChatbot(api_key=MR_JAMES_API_KEY)

# Feature 3: Constructing a persistent conversation memory bank using a Python list
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar options for extra interactive controls during presentation
with st.sidebar:
    st.header("Patient Management Tools")
    st.info("Use this panel to manage data lifecycle operations.")
    
    # Triggering Feature 1: Exporting data to local storage on demand
    if st.button("💾 Export Consultation Report"):
        if st.session_state.messages:
            status_message = st.session_state.chatbot.save_report(st.session_state.messages)
            st.success(status_message)
        else:
            st.warning("No conversation history available to save yet.")
            
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Displaying past chat history on the web interface screen dynamically
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accepting active user input directly via standard web chat interface bars
if user_input := st.chat_input("Describe your current symptoms or type follow-up questions..."):
    
    # Append the user's input message to memory list
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Generate the AI response using contextual memory tracking
    with st.chat_message("assistant"):
        with st.spinner("Analyzing symptoms against medical model databases..."):
            ai_response = st.session_state.chatbot.generate_response(st.session_state.messages)
            st.markdown(ai_response)
            
    # Append the AI's structural response into memory list
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
