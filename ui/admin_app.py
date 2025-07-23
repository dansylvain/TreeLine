"""TreeLine AI Admin Interface

A Streamlit-based admin interface for managing the TreeLine knowledge base.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
KNOWLEDGE_BASE_PATH = Path("ai_agent/data/knowledge_base")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Page configuration
st.set_page_config(
    page_title="TreeLine Admin",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for admin styling
st.markdown("""
<style>
    .main-header {
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
    
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    .delete-button > button {
        background-color: #D32F2F;
        color: white;
        border: none;
    }
    
    .delete-button > button:hover {
        background-color: #B71C1C;
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
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "embedding_model" not in st.session_state:
        st.session_state.embedding_model = "text-embedding-ada-002"
    
    if "message" not in st.session_state:
        st.session_state.message = None
    
    if "message_type" not in st.session_state:
        st.session_state.message_type = None


def authenticate(username: str, password: str) -> bool:
    """Authenticate admin user."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


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


def show_login_form():
    """Display the login form."""
    st.markdown('<h1 class="main-header">🔧 TreeLine Admin Login</h1>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("### Please enter your credentials")
        
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter admin password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            login_button = st.form_submit_button("Login", use_container_width=True)
        
        if login_button:
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.message = "Successfully logged in!"
                st.session_state.message_type = "success"
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
    
    # Show default credentials info for demo
    st.info("💡 **Demo Credentials:**\n- Username: `admin`\n- Password: `admin123`")


def show_admin_interface():
    """Display the main admin interface."""
    st.markdown('<h1 class="main-header">🔧 TreeLine Admin Interface</h1>', unsafe_allow_html=True)
    
    # Show messages
    if st.session_state.message:
        if st.session_state.message_type == "success":
            st.markdown(f'<div class="success-message">✅ {st.session_state.message}</div>', unsafe_allow_html=True)
        elif st.session_state.message_type == "error":
            st.markdown(f'<div class="error-message">❌ {st.session_state.message}</div>', unsafe_allow_html=True)
        elif st.session_state.message_type == "warning":
            st.markdown(f'<div class="warning-message">⚠️ {st.session_state.message}</div>', unsafe_allow_html=True)
        
        # Clear message after displaying
        st.session_state.message = None
        st.session_state.message_type = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Admin Controls")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.message = None
            st.session_state.message_type = None
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
            st.session_state.message = f"Embedding model set to: {selected_model}"
            st.session_state.message_type = "success"
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
                                st.session_state.message = f"Successfully deleted {file_info['name']}"
                                st.session_state.message_type = "success"
                                st.rerun()
                            else:
                                st.session_state.message = f"Failed to delete {file_info['name']}"
                                st.session_state.message_type = "error"
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
                    st.session_state.message = f"Successfully uploaded {success_count} file(s)"
                    st.session_state.message_type = "success"
                
                if failed_files:
                    st.session_state.message += f"\nFailed to upload: {', '.join(failed_files)}"
                    st.session_state.message_type = "warning" if success_count > 0 else "error"
                
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


def main():
    """Main application function."""
    initialize_session_state()
    
    if not st.session_state.logged_in:
        show_login_form()
    else:
        show_admin_interface()


if __name__ == "__main__":
    main()
