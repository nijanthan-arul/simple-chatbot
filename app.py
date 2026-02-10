import streamlit as st
import requests

# Configure Streamlit page
st.set_page_config(page_title="OpenRouter Chatbot", layout="wide")
st.title("💬 OpenRouter Chatbot")

# --- Sidebar: customization controls ---
st.sidebar.header("Settings")

# Initialize API key from secrets
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

if not api_key:
    st.sidebar.warning("Please set OPENROUTER_API_KEY in Streamlit secrets")
    st.sidebar.info("Create `.streamlit/secrets.toml` and add OPENROUTER_API_KEY = 'your-key'")
    st.stop()

# OpenRouter API configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model selector and generation params
MODEL = st.sidebar.selectbox("Model", [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
], index=0)

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max tokens", 100, 2000, 1000, step=50)

# Optional system prompt to control assistant's behavior
system_prompt = st.sidebar.text_area("System prompt (optional)", value="You are a helpful assistant.")

if st.sidebar.button("Clear chat"):
    st.session_state.messages = []

# File upload to include document content in the conversation
uploaded_file = st.sidebar.file_uploader("Attach a text file (optional)", type=["txt", "md"]) 

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if uploaded_file is not None:
    try:
        raw = uploaded_file.read()
        text = raw.decode("utf-8", errors="ignore")
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
        # Append file content as system message for context
        st.session_state.messages.append({"role": "system", "content": f"File {uploaded_file.name}:\n{text}"})
    except Exception:
        st.sidebar.error("Failed to read file")

# Ensure system prompt exists in messages (keeps history tidy)
if system_prompt:
    # place as first system message if not already present
    if not any(m["role"] == "system" for m in st.session_state.messages):
        st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display bot response
    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Prepare request to OpenRouter
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Streamlit Chatbot",
            }
            
            payload = {
                "model": MODEL,
                "messages": st.session_state.messages,
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
            }
            
            response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            bot_response = response.json()["choices"][0]["message"]["content"]
            message_placeholder.markdown(bot_response)
            
            # Add bot response to history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# --- Examples / snippets for customization ---
with st.expander("Customization examples"):
    st.markdown("**Change model and temperature from the sidebar to experiment.**")
    st.markdown("**Add a system prompt to change assistant style.**")
    st.code('''# Example: change system prompt\nsystem_prompt = "You are a concise, professional assistant."\n# Or set in sidebar''')
