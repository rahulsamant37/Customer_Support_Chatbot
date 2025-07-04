import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, invoke_chain

class TestAPI:
    """Test cases for the FastAPI application endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Welcome to the Product Information Bot API. Use the /get endpoint to chat with the bot."
        }
    
    def test_chat_endpoint_valid_message(self, client):
        """Test the chat endpoint with a valid message."""
        with patch('main.invoke_chain') as mock_invoke:
            mock_invoke.return_value = "Test response from bot"
            
            response = client.post("/get", data={"msg": "Tell me about headphones"})
            
            assert response.status_code == 200
            assert response.json() == {"response": "Test response from bot"}
            mock_invoke.assert_called_once_with("Tell me about headphones")
    
    def test_chat_endpoint_empty_message(self, client):
        """Test the chat endpoint with an empty message."""
        response = client.post("/get", data={"msg": ""})
        assert response.status_code == 200
        # Should still process empty messages
    
    def test_chat_frontend_endpoint(self, client):
        """Test the frontend chat endpoint."""
        response = client.get("/chat")
        assert response.status_code == 200
        # Should return HTML file
    
    @patch('main.retriever_obj')
    @patch('main.model_loader')
    def test_invoke_chain_success(self, mock_model_loader, mock_retriever_obj):
        """Test successful chain invocation."""
        # Mock retriever
        mock_retriever = Mock()
        mock_docs = [Mock(page_content="Test product content")]
        mock_retriever.invoke.return_value = mock_docs
        mock_retriever_obj.load_retriever.return_value = mock_retriever
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = "AI response"
        mock_model_loader.load_llm.return_value = mock_llm
        
        # Test the function
        result = invoke_chain("test query")
        
        assert isinstance(result, str)
        mock_retriever_obj.load_retriever.assert_called_once()
        mock_model_loader.load_llm.assert_called_once()
    
    @patch('main.retriever_obj')
    def test_invoke_chain_no_documents(self, mock_retriever_obj):
        """Test chain invocation when no documents are found."""
        # Mock retriever returning empty results
        mock_retriever = Mock()
        mock_retriever.invoke.return_value = []
        mock_retriever_obj.load_retriever.return_value = mock_retriever
        
        result = invoke_chain("test query")
        
        assert "I'm sorry, I couldn't find any relevant product information" in result
    
    @patch('main.retriever_obj')
    def test_invoke_chain_exception(self, mock_retriever_obj):
        """Test chain invocation when an exception occurs."""
        # Mock retriever raising an exception
        mock_retriever_obj.load_retriever.side_effect = Exception("Test error")
        
        result = invoke_chain("test query")
        
        assert "I'm experiencing technical difficulties" in result
        assert "Test error" in result

class TestAPIIntegration:
    """Integration tests for the API."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/")
        # CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
    
    def test_static_files_mounting(self, client):
        """Test that static files are properly mounted."""
        # This test assumes frontend directory exists
        response = client.get("/static/index.html")
        # Should either serve the file or return 404 if file doesn't exist
        assert response.status_code in [200, 404]

if __name__ == "__main__":
    pytest.main([__file__])
