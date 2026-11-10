import os
import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq




from database import (
    create_tables,
    save_conversation,
    save_message,
    load_conversations,
    update_conversation_title,
    delete_conversation
)

create_tables()  

# Step 1: Load the API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Step 2: Configure Streamlit
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

st.markdown(
    """
<style>
.stApp { background-color: #0E1117; }
.block-container { max-width: 950px; padding-top: 1.5rem; padding-bottom: 5rem; }
[data-testid="stSidebar"] { background-color: #171B26; border-right: 1px solid #252B3B; }
[data-testid="stChatMessage"] {
    background-color: #1A2030;
    border: 1px solid #293247;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: #29213F;
    border-color: #49366D;
}
[data-testid="stChatInput"] { border-radius: 18px; }
div.stButton > button {
    background-color: #1A2030;
    color: #F8FAFC;
    border: 1px solid #30384B;
    border-radius: 12px;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    background-color: #29213F;
    border-color: #A78BFA;
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)

# Step 3: Check the API key before building the chatbot
if not groq_api_key:
    st.error("API key is missing. Set GROQ_API_KEY in your .env file.")
    st.code("GROQ_API_KEY=your_api_key_here", language="text")
    st.stop()

# Step 4: Available models
model_options = {
    "GPT-OSS 20B": "openai/gpt-oss-20b",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
}

# Step 5: Initialize conversation state before accessing it
# Step 5: Initialize conversation state

# Load existing conversations from SQLite
if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()

# Initialize the current chat ID
if "current_chat_id" not in st.session_state:

    if st.session_state.conversations:
        st.session_state.current_chat_id = next(
            reversed(st.session_state.conversations)
        )
    else:
        st.session_state.current_chat_id = str(uuid.uuid4())

# Create a new conversation if it doesn't exist
if st.session_state.current_chat_id not in st.session_state.conversations:

    chat_id = st.session_state.current_chat_id

    st.session_state.conversations[chat_id] = {
        "title": "New Conversation",
        "messages": []
    }

    # Save the new conversation to SQLite
    save_conversation(chat_id, "New Conversation")

# Get the currently selected conversation
current_chat = st.session_state.conversations[
    st.session_state.current_chat_id
]

messages = current_chat["messages"]


# Step 6: Sidebar
with st.sidebar:
    st.markdown("## ✦ AI Assistant")
    st.caption("Your intelligent conversation partner")
    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.conversations[new_chat_id] = {
            "title": "New Conversation",
            "messages": [],
        }
        # Save the conversation in SQLite
        save_conversation(new_chat_id, "New Conversation")
        st.session_state.current_chat_id = new_chat_id
        st.rerun()

    st.subheader("Recent Conversations")

    for chat_id, chat_data in reversed(list(st.session_state.conversations.items())):
        chat_col, delete_col = st.columns([5, 1])

        with chat_col:
            if st.button(
                chat_data["title"],
                key=f"chat_{chat_id}",
                use_container_width=True,
                type="primary" if chat_id == st.session_state.current_chat_id else "secondary",
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        with delete_col:
            if st.button("✕", key=f"delete_{chat_id}", help="Delete conversation"):
                del st.session_state.conversations[chat_id]

                delete_conversation(chat_id)

                if st.session_state.current_chat_id == chat_id:
                    if st.session_state.conversations:
                        st.session_state.current_chat_id = next(
                            reversed(st.session_state.conversations)
                        )
                    else:
                        replacement_id = str(uuid.uuid4())
                        st.session_state.conversations[replacement_id] = {
                            "title": "New Conversation",
                            "messages": [],
                        }
                        st.session_state.current_chat_id = replacement_id

                st.rerun()

    st.divider()
    with st.expander("⚙️ Settings", expanded=False):
        selected_model_name = st.selectbox("AI Model", options=list(model_options))
        model_id = model_options[selected_model_name]
        temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.slider(
            "Maximum Response Tokens", min_value=100, max_value=2000, value=500, step=100
        )

    st.divider()
    st.caption("Built with Streamlit, LangChain & Groq")
    st.caption("Chats are saved only for this Streamlit session.")

# Step 7: Initialize the model
llm = ChatGroq(
    model=model_id,
    api_key=groq_api_key,
    temperature=temperature,
    max_tokens=max_tokens,
)

# Step 8: Main header
header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown("### ✦ AI Assistant")
with header_right:
    st.caption("● Ready")
st.divider()

# Step 9: Welcome screen (only when the current conversation is empty)
starter_prompt = None
if not messages:
    st.markdown(
        """
<div style="text-align:center; padding:65px 0 35px 0;">
<h1 style="font-size:42px; font-weight:700; margin-bottom:12px;">How can I help you today?</h1>
<p style="color:#94A3B8; font-size:17px;">Ask anything, explore ideas, or learn something new.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if st.button("🧠 Explain a concept", use_container_width=True):
            starter_prompt = "Explain machine learning in simple terms."
        if st.button("💻 Help me with Python", use_container_width=True):
            starter_prompt = "Explain Python functions with examples."
    with col2:
        if st.button("✍️ Improve my writing", use_container_width=True):
            starter_prompt = "Help me improve my writing."
        if st.button("💡 Explore AI", use_container_width=True):
            starter_prompt = "What are large language models?"

# Step 10: Display the selected conversation's history
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Step 11: User input
# Keep this in the main body for Streamlit's bottom-pinned input.
typed_prompt = st.chat_input("Ask anything...")
user_prompt = starter_prompt or typed_prompt

if user_prompt:
    messages.append({"role": "user", "content": user_prompt})

        # Step 2: Save the user's message in SQLite
    save_message(
        st.session_state.current_chat_id,
        "user",
        user_prompt
    )

    # Set the conversation title from the first user question.
    if current_chat["title"] == "New Conversation":
        current_chat["title"] = user_prompt[:35] + ("..." if len(user_prompt) > 35 else "")
        update_conversation_title(
        st.session_state.current_chat_id,
        current_chat["title"]
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Step 12: Build the conversation context for LangChain
    langchain_messages = [
        SystemMessage(
            content=(
                "You are a helpful AI assistant. Explain things accurately and clearly. "
                "Use simple examples when helpful. If unsure, say so instead of inventing facts."
            )
        )
    ]
    for message in messages:
        if message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        else:
            langchain_messages.append(AIMessage(content=message["content"]))

    # Step 13: Stream the response and save it to the current conversation
    with st.chat_message("assistant"):
        try:
            def generate_response():
                for chunk in llm.stream(langchain_messages):
                    if isinstance(chunk.content, str) and chunk.content:
                        yield chunk.content

            answer = st.write_stream(generate_response())
        except Exception as error:
            st.error("Something went wrong while generating the response.")
            st.exception(error)
            answer = ""

    if answer:

        messages.append({
        "role": "assistant",
        "content": answer
        })

        save_message(
        st.session_state.current_chat_id,
        "assistant",
        answer
        )

        st.rerun()
