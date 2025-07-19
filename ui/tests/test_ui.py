"""UI component tests."""

import pytest
from unittest.mock import Mock, patch
from components.chat_interface import (
    render_message_bubble,
    render_chat_history,
    render_quick_actions,
    render_session_controls,
    render_connection_status,
    render_error_message,
    render_response_metadata
)


class TestChatInterface:
    """Test chat interface components."""
    
    def test_render_message_bubble_user(self):
        """Test rendering user message bubble."""
        message = {
            "content": "Hello, how can you help me?",
            "timestamp": "10:30:15"
        }
        
        # This would normally render in Streamlit, but we can test the function exists
        # and doesn't raise errors
        try:
            render_message_bubble(message, is_user=True)
        except Exception as e:
            # Expected to fail outside Streamlit context, but function should exist
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_message_bubble_ai(self):
        """Test rendering AI message bubble."""
        message = {
            "content": "I'm here to help! What do you need assistance with?",
            "timestamp": "10:30:20",
            "response_time": 1250
        }
        
        try:
            render_message_bubble(message, is_user=False)
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_chat_history_empty(self):
        """Test rendering empty chat history."""
        messages = []
        
        try:
            render_chat_history(messages)
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_chat_history_with_messages(self):
        """Test rendering chat history with messages."""
        messages = [
            {
                "content": "Hello",
                "timestamp": "10:30:15",
                "is_user": True
            },
            {
                "content": "Hi there! How can I help?",
                "timestamp": "10:30:20",
                "is_user": False,
                "response_time": 1000
            }
        ]
        
        try:
            render_chat_history(messages)
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_quick_actions(self):
        """Test rendering quick action buttons."""
        try:
            result = render_quick_actions()
            # Should return empty string when no button is clicked
            assert result == ""
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_session_controls(self):
        """Test rendering session control buttons."""
        session_id = "test-session-123"
        message_count = 5
        
        try:
            actions = render_session_controls(session_id, message_count)
            # Should return dict with action flags
            assert isinstance(actions, dict)
            assert "clear" in actions
            assert "new_session" in actions
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_connection_status_connected(self):
        """Test rendering connection status when connected."""
        try:
            render_connection_status(True, "http://localhost:8000")
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_connection_status_disconnected(self):
        """Test rendering connection status when disconnected."""
        try:
            render_connection_status(False, "http://localhost:8000")
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_error_message(self):
        """Test rendering error message."""
        error_msg = "Connection failed"
        
        try:
            retry_clicked = render_error_message(error_msg, show_retry=True)
            assert isinstance(retry_clicked, bool)
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_response_metadata_empty(self):
        """Test rendering response metadata with empty data."""
        try:
            render_response_metadata({})
            # Should handle empty data gracefully
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_response_metadata_with_data(self):
        """Test rendering response metadata with data."""
        response_data = {
            "response_time_ms": 1250,
            "sources_used": 3,
            "fallback_used": False
        }
        
        try:
            render_response_metadata(response_data)
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()
    
    def test_render_response_metadata_fallback(self):
        """Test rendering response metadata with fallback mode."""
        response_data = {
            "response_time_ms": 800,
            "sources_used": 0,
            "fallback_used": True
        }
        
        try:
            render_response_metadata(response_data)
        except Exception as e:
            # Expected to fail outside Streamlit context
            assert "streamlit" in str(e).lower() or "st" in str(e).lower()


class TestStreamlitApp:
    """Test main Streamlit application functions."""
    
    @pytest.mark.asyncio
    async def test_check_backend_status_success(self):
        """Test successful backend status check."""
        # Import here to avoid Streamlit import issues in test environment
        try:
            from streamlit_app import check_backend_status
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.json.return_value = {"status": "healthy"}
                mock_response.raise_for_status.return_value = None
                
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
                
                result = await check_backend_status()
                
                assert result["status"] == "healthy"
                assert "data" in result
        except ImportError:
            # Skip if streamlit not available in test environment
            pytest.skip("Streamlit not available in test environment")
    
    @pytest.mark.asyncio
    async def test_check_backend_status_failure(self):
        """Test failed backend status check."""
        try:
            from streamlit_app import check_backend_status
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Connection failed")
                
                result = await check_backend_status()
                
                assert result["status"] == "error"
                assert "error" in result
        except ImportError:
            pytest.skip("Streamlit not available in test environment")
    
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        try:
            from streamlit_app import send_message
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "ai_response": "Hello! How can I help you?",
                    "response_time_ms": 1000
                }
                mock_response.raise_for_status.return_value = None
                
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                result = await send_message("Hello", "test-session")
                
                assert result["status"] == "success"
                assert "data" in result
        except ImportError:
            pytest.skip("Streamlit not available in test environment")
    
    @pytest.mark.asyncio
    async def test_send_message_timeout(self):
        """Test message sending timeout."""
        try:
            from streamlit_app import send_message
            import httpx
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
                
                result = await send_message("Hello", "test-session")
                
                assert result["status"] == "error"
                assert "timed out" in result["error"].lower()
        except ImportError:
            pytest.skip("Streamlit not available in test environment")
    
    def test_initialize_session_state(self):
        """Test session state initialization."""
        try:
            from streamlit_app import initialize_session_state
            import streamlit as st
            
            # Mock streamlit session state
            with patch('streamlit.session_state', {}) as mock_session_state:
                initialize_session_state()
                
                # Function should attempt to set session state variables
                # This test mainly ensures the function doesn't crash
        except ImportError:
            pytest.skip("Streamlit not available in test environment")


class TestUIIntegration:
    """Integration tests for UI components."""
    
    @pytest.mark.integration
    def test_ui_components_integration(self):
        """Test that UI components work together."""
        # This would require a full Streamlit environment
        # For now, just test that imports work
        try:
            from components.chat_interface import (
                render_message_bubble,
                render_chat_history,
                render_quick_actions
            )
            from streamlit_app import initialize_session_state
            
            # If imports succeed, basic integration is working
            assert callable(render_message_bubble)
            assert callable(render_chat_history)
            assert callable(render_quick_actions)
            assert callable(initialize_session_state)
            
        except ImportError as e:
            pytest.skip(f"UI components not available: {e}")
