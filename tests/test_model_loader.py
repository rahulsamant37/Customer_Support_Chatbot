import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.model_loader import ModelLoader

class TestModelLoader:
    """Test cases for the ModelLoader class."""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing."""
        env_vars = {
            "GOOGLE_API_KEY": "test_google_api_key"
        }
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    @patch('utils.model_loader.load_config')
    def test_model_loader_initialization_success(self, mock_load_config, mock_env_vars):
        """Test successful initialization of ModelLoader."""
        mock_config = {
            "embedding_model": {"model_name": "models/text-embedding-004"},
            "llm": {"model_name": "gemini-2.0-flash"}
        }
        mock_load_config.return_value = mock_config
        
        model_loader = ModelLoader()
        
        assert model_loader.config == mock_config
        mock_load_config.assert_called_once()
    
    def test_model_loader_missing_api_key(self):
        """Test ModelLoader initialization with missing Google API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('utils.model_loader.load_config') as mock_load_config:
                mock_load_config.return_value = {}
                
                with patch('utils.model_loader.load_dotenv'):
                    with pytest.raises(EnvironmentError) as exc_info:
                        ModelLoader()
                    
                    assert "Missing environment variables: ['GOOGLE_API_KEY']" in str(exc_info.value)
    
    @patch('utils.model_loader.GoogleGenerativeAIEmbeddings')
    @patch('utils.model_loader.load_config')
    def test_load_embeddings(self, mock_load_config, mock_embeddings_class, mock_env_vars):
        """Test loading embeddings model."""
        mock_config = {
            "embedding_model": {"model_name": "models/text-embedding-004"}
        }
        mock_load_config.return_value = mock_config
        
        mock_embeddings_instance = Mock()
        mock_embeddings_class.return_value = mock_embeddings_instance
        
        model_loader = ModelLoader()
        result = model_loader.load_embeddings()
        
        mock_embeddings_class.assert_called_once_with(model="models/text-embedding-004")
        assert result == mock_embeddings_instance
    
    @patch('utils.model_loader.ChatGoogleGenerativeAI')
    @patch('utils.model_loader.load_config')
    def test_load_llm(self, mock_load_config, mock_chat_class, mock_env_vars):
        """Test loading LLM model."""
        mock_config = {
            "llm": {"model_name": "gemini-2.0-flash"}
        }
        mock_load_config.return_value = mock_config
        
        mock_llm_instance = Mock()
        mock_chat_class.return_value = mock_llm_instance
        
        model_loader = ModelLoader()
        result = model_loader.load_llm()
        
        mock_chat_class.assert_called_once_with(model="gemini-2.0-flash")
        assert result == mock_llm_instance
    
    @patch('utils.model_loader.GoogleGenerativeAIEmbeddings')
    @patch('utils.model_loader.load_config')
    def test_load_embeddings_with_different_model(self, mock_load_config, mock_embeddings_class, mock_env_vars):
        """Test loading embeddings with a different model name."""
        mock_config = {
            "embedding_model": {"model_name": "models/custom-embedding-model"}
        }
        mock_load_config.return_value = mock_config
        
        model_loader = ModelLoader()
        model_loader.load_embeddings()
        
        mock_embeddings_class.assert_called_once_with(model="models/custom-embedding-model")
    
    @patch('utils.model_loader.ChatGoogleGenerativeAI')
    @patch('utils.model_loader.load_config')
    def test_load_llm_with_different_model(self, mock_load_config, mock_chat_class, mock_env_vars):
        """Test loading LLM with a different model name."""
        mock_config = {
            "llm": {"model_name": "gemini-1.5-pro"}
        }
        mock_load_config.return_value = mock_config
        
        model_loader = ModelLoader()
        model_loader.load_llm()
        
        mock_chat_class.assert_called_once_with(model="gemini-1.5-pro")

class TestModelLoaderEdgeCases:
    """Test edge cases and error conditions for ModelLoader."""
    
    @patch('utils.model_loader.load_config')
    def test_model_loader_missing_config_sections(self, mock_load_config):
        """Test ModelLoader with missing configuration sections."""
        # Missing embedding_model and llm sections
        mock_load_config.return_value = {}
        
        env_vars = {"GOOGLE_API_KEY": "test_key"}
        with patch.dict(os.environ, env_vars):
            model_loader = ModelLoader()
            
            # Should handle missing config gracefully or raise appropriate errors
            with pytest.raises(KeyError):
                model_loader.load_embeddings()
            
            with pytest.raises(KeyError):
                model_loader.load_llm()
    
    @patch('utils.model_loader.GoogleGenerativeAIEmbeddings')
    @patch('utils.model_loader.load_config')
    def test_load_embeddings_api_error(self, mock_load_config, mock_embeddings_class):
        """Test handling of API errors when loading embeddings."""
        mock_config = {
            "embedding_model": {"model_name": "models/text-embedding-004"}
        }
        mock_load_config.return_value = mock_config
        
        # Simulate API error
        mock_embeddings_class.side_effect = Exception("API Error")
        
        env_vars = {"GOOGLE_API_KEY": "invalid_key"}
        with patch.dict(os.environ, env_vars):
            model_loader = ModelLoader()
            
            with pytest.raises(Exception) as exc_info:
                model_loader.load_embeddings()
            
            assert "API Error" in str(exc_info.value)
    
    @patch('utils.model_loader.ChatGoogleGenerativeAI')
    @patch('utils.model_loader.load_config')
    def test_load_llm_api_error(self, mock_load_config, mock_chat_class):
        """Test handling of API errors when loading LLM."""
        mock_config = {
            "llm": {"model_name": "gemini-2.0-flash"}
        }
        mock_load_config.return_value = mock_config
        
        # Simulate API error
        mock_chat_class.side_effect = Exception("LLM API Error")
        
        env_vars = {"GOOGLE_API_KEY": "invalid_key"}
        with patch.dict(os.environ, env_vars):
            model_loader = ModelLoader()
            
            with pytest.raises(Exception) as exc_info:
                model_loader.load_llm()
            
            assert "LLM API Error" in str(exc_info.value)

class TestModelLoaderIntegration:
    """Integration tests for ModelLoader."""
    
    @patch('utils.model_loader.ChatGoogleGenerativeAI')
    @patch('utils.model_loader.GoogleGenerativeAIEmbeddings')
    @patch('utils.model_loader.load_config')
    def test_model_loader_full_workflow(self, mock_load_config, mock_embeddings_class, mock_chat_class):
        """Test the complete model loading workflow."""
        mock_config = {
            "embedding_model": {"model_name": "models/text-embedding-004"},
            "llm": {"model_name": "gemini-2.0-flash"}
        }
        mock_load_config.return_value = mock_config
        
        mock_embeddings_instance = Mock()
        mock_llm_instance = Mock()
        mock_embeddings_class.return_value = mock_embeddings_instance
        mock_chat_class.return_value = mock_llm_instance
        
        env_vars = {"GOOGLE_API_KEY": "test_key"}
        with patch.dict(os.environ, env_vars):
            model_loader = ModelLoader()
            
            # Test loading embeddings
            embeddings = model_loader.load_embeddings()
            assert embeddings == mock_embeddings_instance
            
            # Test loading LLM
            llm = model_loader.load_llm()
            assert llm == mock_llm_instance
            
            # Verify both models use the same config
            mock_embeddings_class.assert_called_once_with(model="models/text-embedding-004")
            mock_chat_class.assert_called_once_with(model="gemini-2.0-flash")

if __name__ == "__main__":
    pytest.main([__file__])
