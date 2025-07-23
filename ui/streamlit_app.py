"""TreeLine AI Customer Support Agent - Streamlit UI

A clean, minimal interface for interacting with the TreeLine AI agent with integrated admin interface.
"""

import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

import streamlit as st
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TIMEOUT = 30.0
KNOWLEDGE_BASE_PATH = Path("ai_agent/data/knowledge_base")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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
    
    .admin-header {
        text-align: center;
        color: #1976D2;
        margin-bottom: 2rem;
    }
    
    .section-header {
        color: #1976D2;
        border-bottom: 2px solid #1976D2;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
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
    
    .file-item {
        background-color: #F8F9FA;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #1976D2;
    }
    
    .file-name {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .file-info {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .success-message {
        background-color: #E8F5E8;
        color: #2E7D32;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F44336;
        margin: 1rem 0;
    }
    
    .warning-message {
        background-color: #FFF3E0;
        color: #E65100;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    
    .upload-section {
        background-color: #F5F5F5;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    
    .stats-container {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
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
    
    .delete-button > button {
        background-color: #D32F2F;
        color: white;
        border: none;
    }
    
    .delete-button > button:hover {
        background-color: #B71C1C;
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
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if "embedding_model" not in st.session_state:
        st.session_state.embedding_model = "text-embedding-ada-002"
    
    if "admin_message" not in st.session_state:
        st.session_state.admin_message = None
    
    if "admin_message_type" not in st.session_state:
        st.session_state.admin_message_type = None


def authenticate_admin(username: str, password: str) -> bool:
    """Authenticate admin user."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


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


def get_knowledge_base_files() -> List[dict]:
    """Get list of files in the knowledge base directory."""
    files = []
    
    if not KNOWLEDGE_BASE_PATH.exists():
        return files
    
    for file_path in KNOWLEDGE_BASE_PATH.iterdir():
        if file_path.is_file() and file_path.name != '.gitkeep':
            file_info = {
                'name': file_path.name,
                'path': file_path,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            }
            files.append(file_info)
    
    # Sort by name
    files.sort(key=lambda x: x['name'].lower())
    return files


def delete_file(file_path: Path) -> bool:
    """Delete a file from the knowledge base."""
    try:
        file_path.unlink()
        return True
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return False


def save_uploaded_file(uploaded_file) -> bool:
    """Save an uploaded file to the knowledge base directory."""
    try:
        # Ensure the knowledge base directory exists
        KNOWLEDGE_BASE_PATH.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file_path = KNOWLEDGE_BASE_PATH / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def show_admin_login():
    """Display the admin login form."""
    st.markdown('<h1 class="admin-header">🔧 TreeLine Admin Login</h1>', unsafe_allow_html=True)
    
    with st.form("admin_login_form"):
        st.markdown("### Please enter your credentials")
        
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter admin password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            login_button = st.form_submit_button("Login", use_container_width=True)
        
        if login_button:
            if authenticate_admin(username, password):
                st.session_state.admin_logged_in = True
                st.session_state.admin_message = "Successfully logged in!"
                st.session_state.admin_message_type = "success"
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
    
    # Show default credentials info for demo
    st.info("💡 **Demo Credentials:**\n- Username: `admin`\n- Password: `admin123`")


def show_admin_interface():
    """Display the main admin interface."""
    st.markdown('<h1 class="admin-header">🔧 TreeLine Admin Interface</h1>', unsafe_allow_html=True)
    
    # Show messages
    if st.session_state.admin_message:
        if st.session_state.admin_message_type == "success":
            st.markdown(f'<div class="success-message">✅ {st.session_state.admin_message}</div>', unsafe_allow_html=True)
        elif st.session_state.admin_message_type == "error":
            st.markdown(f'<div class="error-message">❌ {st.session_state.admin_message}</div>', unsafe_allow_html=True)
        elif st.session_state.admin_message_type == "warning":
            st.markdown(f'<div class="warning-message">⚠️ {st.session_state.admin_message}</div>', unsafe_allow_html=True)
        
        # Clear message after displaying
        st.session_state.admin_message = None
        st.session_state.admin_message_type = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Admin Controls")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.admin_message = None
            st.session_state.admin_message_type = None
            st.rerun()
        
        st.markdown("---")
        
        # Embedding Model Selector
        st.markdown("### 🧠 Embedding Model")
        embedding_models = [
            "text-embedding-ada-002",
            "text-embedding-3-small",
            "text-embedding-3-large",
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
            "sentence-transformers/all-MiniLM-L6-v2"
        ]
        
        selected_model = st.selectbox(
            "Select Embedding Model",
            embedding_models,
            index=embedding_models.index(st.session_state.embedding_model) if st.session_state.embedding_model in embedding_models else 0,
            key="embedding_model_selector"
        )
        
        if selected_model != st.session_state.embedding_model:
            st.session_state.embedding_model = selected_model
            st.session_state.admin_message = f"Embedding model set to: {selected_model}"
            st.session_state.admin_message_type = "success"
            st.rerun()
        
        st.info(f"**Current Model:**\n{st.session_state.embedding_model}")
        
        st.markdown("---")
        
        # Statistics
        files = get_knowledge_base_files()
        total_size = sum(f['size'] for f in files)
        
        st.markdown("### 📊 Statistics")
        st.metric("Total Files", len(files))
        st.metric("Total Size", format_file_size(total_size))
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Document Management Section
        st.markdown('<h2 class="section-header">📄 Document Management</h2>', unsafe_allow_html=True)
        
        files = get_knowledge_base_files()
        
        if not files:
            st.info("📁 No documents found in the knowledge base.")
        else:
            st.markdown(f"**Found {len(files)} documents:**")
            
            for file_info in files:
                with st.container():
                    st.markdown(f'<div class="file-item">', unsafe_allow_html=True)
                    
                    file_col1, file_col2 = st.columns([3, 1])
                    
                    with file_col1:
                        st.markdown(f'<div class="file-name">📄 {file_info["name"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="file-info">Size: {format_file_size(file_info["size"])}</div>', unsafe_allow_html=True)
                    
                    with file_col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{file_info['name']}", help=f"Delete {file_info['name']}"):
                            if delete_file(file_info['path']):
                                st.session_state.admin_message = f"Successfully deleted {file_info['name']}"
                                st.session_state.admin_message_type = "success"
                                st.rerun()
                            else:
                                st.session_state.admin_message = f"Failed to delete {file_info['name']}"
                                st.session_state.admin_message_type = "error"
                                st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # File Upload Section
        st.markdown('<h2 class="section-header">⬆️ Upload Documents</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['md', 'txt', 'pdf', 'docx', 'doc'],
            help="Supported formats: Markdown (.md), Text (.txt), PDF (.pdf), Word (.docx, .doc)"
        )
        
        if uploaded_files:
            st.markdown("**Files to upload:**")
            for uploaded_file in uploaded_files:
                st.write(f"📄 {uploaded_file.name} ({format_file_size(uploaded_file.size)})")
            
            if st.button("📤 Upload Files", use_container_width=True):
                success_count = 0
                failed_files = []
                
                for uploaded_file in uploaded_files:
                    if save_uploaded_file(uploaded_file):
                        success_count += 1
                    else:
                        failed_files.append(uploaded_file.name)
                
                if success_count > 0:
                    st.session_state.admin_message = f"Successfully uploaded {success_count} file(s)"
                    st.session_state.admin_message_type = "success"
                
                if failed_files:
                    st.session_state.admin_message += f"\nFailed to upload: {', '.join(failed_files)}"
                    st.session_state.admin_message_type = "warning" if success_count > 0 else "error"
                
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Information Section
        st.markdown('<h2 class="section-header">ℹ️ Information</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        **Knowledge Base Path:**
        ```
        ai_agent/data/knowledge_base/
        ```
        
        **Supported File Types:**
        - Markdown (.md)
        - Text (.txt)
        - PDF (.pdf)
        - Word (.docx, .doc)
        
        **Note:** After uploading or deleting files, the vector store will need to be updated separately by the AI agent.
        """)


def show_chat_interface():
    """Display the main chat interface."""
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


def main():
    """Main application function."""
    initialize_session_state()
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    
    # Page selection
    if st.sidebar.button("💬 Chat Interface", use_container_width=True):
        st.session_state.current_page = "chat"
        st.rerun()
    
    if st.sidebar.button("🔧 Admin Panel", use_container_width=True):
        st.session_state.current_page = "admin"
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Show appropriate interface based on current page
    if st.session_state.current_page == "admin":
        if not st.session_state.admin_logged_in:
            show_admin_login()
        else:
            show_admin_interface()
    else:
        show_chat_interface()


if __name__ == "__main__":
    main()
