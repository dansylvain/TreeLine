"""Chat interface components for Streamlit UI."""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List


def render_message_bubble(message: Dict[str, Any], is_user: bool = False) -> None:
    """Render a single message bubble."""
    if is_user:
        # User message (right-aligned, blue theme)
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            margin: 1rem 0;
        ">
            <div style="
                background-color: #1976D2;
                color: white;
                padding: 0.75rem 1rem;
                border-radius: 1rem 1rem 0.25rem 1rem;
                max-width: 70%;
                word-wrap: break-word;
            ">
                {message['content']}
                <div style="
                    font-size: 0.75rem;
                    opacity: 0.8;
                    margin-top: 0.25rem;
                ">
                    {message.get('timestamp', '')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # AI message (left-aligned, green theme)
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: flex-start;
            margin: 1rem 0;
        ">
            <div style="
                background-color: #2E7D32;
                color: white;
                padding: 0.75rem 1rem;
                border-radius: 1rem 1rem 1rem 0.25rem;
                max-width: 70%;
                word-wrap: break-word;
            ">
                <div style="
                    font-weight: 500;
                    margin-bottom: 0.5rem;
                    font-size: 0.9rem;
                ">
                    🌲 TreeLine AI
                </div>
                {message['content']}
                <div style="
                    font-size: 0.75rem;
                    opacity: 0.8;
                    margin-top: 0.25rem;
                    display: flex;
                    justify-content: space-between;
                ">
                    <span>{message.get('timestamp', '')}</span>
                    {f"<span>{message.get('response_time', '')}ms</span>" if message.get('response_time') else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    """Render the complete chat history."""
    if not messages:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem;
            color: #666;
            font-style: italic;
        ">
            👋 Welcome! Start a conversation with TreeLine AI by typing a message below.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Create a container for messages with custom scrolling
    with st.container():
        for message in messages:
            render_message_bubble(message, message.get('is_user', False))


def render_typing_indicator() -> None:
    """Render a typing indicator for when AI is processing."""
    st.markdown("""
    <div style="
        display: flex;
        justify-content: flex-start;
        margin: 1rem 0;
    ">
        <div style="
            background-color: #E8F5E8;
            color: #2E7D32;
            padding: 0.75rem 1rem;
            border-radius: 1rem 1rem 1rem 0.25rem;
            border: 1px solid #C8E6C9;
        ">
            <div style="font-weight: 500; margin-bottom: 0.25rem;">🌲 TreeLine AI</div>
            <div style="display: flex; align-items: center;">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span style="margin-left: 0.5rem; font-style: italic;">is typing...</span>
            </div>
        </div>
    </div>
    
    <style>
    .typing-dots {
        display: inline-flex;
        align-items: center;
    }
    
    .typing-dots span {
        height: 6px;
        width: 6px;
        background-color: #2E7D32;
        border-radius: 50%;
        display: inline-block;
        margin: 0 1px;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) {
        animation-delay: -0.32s;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: -0.16s;
    }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_message_input() -> str:
    """Render the message input form and return the submitted message."""
    with st.form("message_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            message = st.text_input(
                "Message",
                placeholder="Type your message here...",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True)
    
    return message.strip() if submitted and message.strip() else ""


def render_quick_actions() -> str:
    """Render quick action buttons and return selected action."""
    st.markdown("**Quick Actions:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("❓ Get Help", use_container_width=True):
            return "I need help with my account"
    
    with col2:
        if st.button("📞 Contact Info", use_container_width=True):
            return "How can I contact customer support?"
    
    with col3:
        if st.button("🔧 Technical Issue", use_container_width=True):
            return "I'm experiencing a technical problem"
    
    return ""


def render_session_controls(session_id: str, message_count: int) -> Dict[str, bool]:
    """Render session control buttons and return actions."""
    actions = {"clear": False, "new_session": False}
    
    st.markdown("### Session Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            actions["clear"] = True
    
    with col2:
        if st.button("🔄 New Session", use_container_width=True):
            actions["new_session"] = True
    
    # Session info
    st.markdown("---")
    st.markdown("### Session Info")
    st.text(f"ID: {session_id[:8]}...")
    st.text(f"Messages: {message_count}")
    
    return actions


def render_connection_status(is_connected: bool, backend_url: str) -> None:
    """Render connection status indicator."""
    if is_connected:
        st.success("🟢 Connected to TreeLine AI")
    else:
        st.error("🔴 Connection Failed")
        st.info(f"Backend URL: {backend_url}")
        st.info("Make sure the backend service is running with `./dev.sh start`")


def render_error_message(error: str, show_retry: bool = True) -> bool:
    """Render error message with optional retry button."""
    st.error(f"❌ {error}")
    
    if show_retry:
        return st.button("🔄 Retry", key="error_retry")
    
    return False


def render_response_metadata(response_data: Dict[str, Any]) -> None:
    """Render metadata about the AI response."""
    if not response_data:
        return
    
    metadata_items = []
    
    if response_data.get("response_time_ms"):
        metadata_items.append(f"⏱️ {response_data['response_time_ms']}ms")
    
    if response_data.get("sources_used", 0) > 0:
        metadata_items.append(f"📚 {response_data['sources_used']} sources")
    
    if response_data.get("fallback_used"):
        metadata_items.append("🔄 Fallback mode")
    
    if metadata_items:
        st.markdown(
            f"<small style='color: #666;'>{' • '.join(metadata_items)}</small>",
            unsafe_allow_html=True
        )
