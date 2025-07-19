"""TreeLine AI Customer Support Agent - Streamlit UI

A clean, minimal interface for interacting with the TreeLine AI agent.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TIMEOUT = 30.0

# Page configuration
st.set_page_config(
    page_title="TreeLine AI Support",
    page_icon="🌲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E7D32;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
        background-color: #F8F9FA;
    }
    
    .user-message {
        background-color: #E3F2FD;
        border-left-color: #1976D2;
        margin-left: 2rem;
    }
    
    .ai-message {
        background-color: #F1F8E9;
        border-left-color: #388E3C;
        margin-right: 2rem;
    }
    
    .timestamp {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .status-info {
        background-color: #FFF3E0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.9rem;
        color: #E65100;
        margin: 0.5rem 0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "backend_status" not in st.session_state:
        st.session_state.backend_status = None


async def check_backend_status() -> Dict[str, Any]:
    """Check if the backend is available."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def send_message(message: str, session_id: str) -> Dict[str, Any]:
    """Send a message to the backend API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/chat",
                json={
                    "message": message,
                    "session_id": session_id
                },
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
    except httpx.TimeoutException:
        return {"status": "error", "error": "Request timed out. Please try again."}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "error": f"Server error: {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": f"Connection error: {str(e)}"}


def display_message(message: Dict[str, Any], is_user: bool = False):
    """Display a chat message."""
    css_class = "user-message" if is_user else "ai-message"
    sender = "You" if is_user else "TreeLine AI"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{sender}:</strong><br>
        {message['content']}
        <div class="timestamp">{message['timestamp']}</div>
    </div>
    """, unsafe_allow_html=True)


def display_status_info(info: str):
    """Display status information."""
    st.markdown(f'<div class="status-info">{info}</div>', unsafe_allow_html=True)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🌲 TreeLine AI Support</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">Your AI-powered customer support assistant</p>', unsafe_allow_html=True)
    
    # Check backend status
    if st.session_state.backend_status is None:
        with st.spinner("Connecting to TreeLine AI..."):
            import asyncio
            status = asyncio.run(check_backend_status())
            st.session_state.backend_status = status
    
    # Display connection status
    if st.session_state.backend_status["status"] != "healthy":
        st.error("⚠️ Unable to connect to TreeLine AI backend. Please check if the service is running.")
        st.info("To start the backend, run: `./dev.sh start`")
        
        if st.button("🔄 Retry Connection"):
            st.session_state.backend_status = None
            st.rerun()
        return
    
    # Display chat messages
    if st.session_state.messages:
        st.markdown("### Conversation")
        for message in st.session_state.messages:
            display_message(message, message.get("is_user", False))
    else:
        st.markdown("### Welcome!")
        st.info("👋 Hi! I'm TreeLine AI, your customer support assistant. How can I help you today?")
    
    # Chat input
    st.markdown("### Send a Message")
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message here...",
            placeholder="Ask me anything about our products or services!",
            height=100,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("Send Message", use_container_width=True)
    
    # Process message submission
    if submit_button and user_input.strip():
        # Add user message to chat
        user_message = {
            "content": user_input.strip(),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "is_user": True
        }
        st.session_state.messages.append(user_message)
        
        # Show loading spinner
        with st.spinner("TreeLine AI is thinking..."):
            import asyncio
            response = asyncio.run(send_message(user_input.strip(), st.session_state.session_id))
        
        if response["status"] == "success":
            # Add AI response to chat
            ai_data = response["data"]
            ai_message = {
                "content": ai_data["ai_response"],
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "is_user": False,
                "response_time": ai_data.get("response_time_ms"),
                "sources_used": ai_data.get("sources_used", 0)
            }
            st.session_state.messages.append(ai_message)
            
            # Show response info
            if ai_data.get("response_time_ms"):
                display_status_info(f"Response time: {ai_data['response_time_ms']}ms")
        
        else:
            # Show error message
            st.error(f"❌ Error: {response['error']}")
            st.info("Please try again or contact support if the problem persists.")
        
        # Rerun to update the display
        st.rerun()
    
    elif submit_button and not user_input.strip():
        st.warning("Please enter a message before sending.")
    
    # Sidebar with session info and controls
    with st.sidebar:
        st.markdown("### Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")
        st.text(f"Messages: {len(st.session_state.messages)}")
        
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🔄 New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### About TreeLine AI")
        st.markdown("""
        TreeLine AI is powered by:
        - **OpenAI GPT-4 Turbo** for natural language understanding
        - **ChromaDB** for knowledge retrieval
        - **FastAPI** backend for reliable service
        - **Streamlit** for this clean interface
        """)
        
        # Backend status indicator
        if st.session_state.backend_status["status"] == "healthy":
            st.success("🟢 Backend Connected")
        else:
            st.error("🔴 Backend Disconnected")


if __name__ == "__main__":
    main()
