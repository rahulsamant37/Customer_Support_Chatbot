import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retriever.retrieval import Retriever

class TestRetriever:
    """Test cases for the Retriever class."""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing."""
        env_vars = {
            "GOOGLE_API_KEY": "test_google_api_key",
            "ASTRA_DB_API_ENDPOINT": "https://test-endpoint.apps.astra.datastax.com",
            "ASTRA_DB_APPLICATION_TOKEN": "test_token",
            "ASTRA_DB_KEYSPACE": "test_keyspace"
        }
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    @patch('retriever.retrieval.load_config')
    @patch('retriever.retrieval.ModelLoader')
    def test_retriever_initialization_success(self, mock_model_loader, mock_load_config, mock_env_vars):
        """Test successful initialization of Retriever."""
        mock_load_config.return_value = {
            "astra_db": {"collection_name": "test_collection"},
            "retriever": {"top_k": 5}
        }
        
        retriever = Retriever()
        
        assert retriever.google_api_key == "test_google_api_key"
        assert retriever.db_api_endpoint == "https://test-endpoint.apps.astra.datastax.com"
        assert retriever.db_application_token == "test_token"
        assert retriever.db_keyspace == "test_keyspace"
        assert retriever.vstore is None
        assert retriever.retriever is None
    
    @patch('retriever.retrieval.ModelLoader')
    def test_retriever_missing_env_vars(self, mock_model_loader):
        """Test Retriever initialization with missing environment variables."""
        # Mock ModelLoader to avoid its own environment validation
        mock_model_loader.return_value = Mock()
        
        # Mock load_dotenv to do nothing (don't load .env file)
        with patch('retriever.retrieval.load_dotenv'):
            # Clear all environment variables
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(EnvironmentError) as exc_info:
                    Retriever()
                
                assert "Missing environment variables" in str(exc_info.value)
    
    @patch('retriever.retrieval.AstraDBVectorStore')
    @patch('retriever.retrieval.load_config')
    @patch('retriever.retrieval.ModelLoader')
    def test_load_retriever_first_time(self, mock_model_loader, mock_load_config, mock_astra_db, mock_env_vars):
        """Test loading retriever for the first time."""
        # Mock configuration
        mock_load_config.return_value = {
            "astra_db": {"collection_name": "test_collection"},
            "retriever": {"top_k": 5}
        }
        
        # Mock model loader
        mock_embeddings = Mock()
        mock_model_loader_instance = Mock()
        mock_model_loader_instance.load_embeddings.return_value = mock_embeddings
        mock_model_loader.return_value = mock_model_loader_instance
        
        # Mock AstraDB vector store
        mock_vstore_instance = Mock()
        mock_retriever_instance = Mock()
        mock_vstore_instance.as_retriever.return_value = mock_retriever_instance
        mock_astra_db.return_value = mock_vstore_instance
        
        retriever = Retriever()
        result = retriever.load_retriever()
        
        # Verify AstraDB was initialized with correct parameters
        mock_astra_db.assert_called_once_with(
            embedding=mock_embeddings,
            collection_name="test_collection",
            api_endpoint="https://test-endpoint.apps.astra.datastax.com",
            token="test_token",
            namespace="test_keyspace"
        )
        
        # Verify retriever was configured
        mock_vstore_instance.as_retriever.assert_called_once_with(search_kwargs={"k": 5})
        assert result == mock_retriever_instance
        assert retriever.vstore == mock_vstore_instance
        assert retriever.retriever == mock_retriever_instance
    
    @patch('retriever.retrieval.AstraDBVectorStore')
    @patch('retriever.retrieval.load_config')
    @patch('retriever.retrieval.ModelLoader')
    def test_load_retriever_cached(self, mock_model_loader, mock_load_config, mock_astra_db, mock_env_vars):
        """Test loading retriever when already cached."""
        mock_load_config.return_value = {
            "astra_db": {"collection_name": "test_collection"},
            "retriever": {"top_k": 5}
        }
        
        retriever = Retriever()
        
        # Set up cached vstore and retriever to simulate already loaded state
        mock_vstore = Mock()
        mock_cached_retriever = Mock()
        retriever.vstore = mock_vstore
        retriever.retriever = mock_cached_retriever
        
        result = retriever.load_retriever()
        
        # Should return cached retriever without creating new one
        assert result == mock_cached_retriever
        # AstraDBVectorStore might have been called during initialization, but not again
        # during load_retriever call since vstore is already set
    
    @patch('retriever.retrieval.load_config')
    @patch('retriever.retrieval.ModelLoader')
    def test_load_retriever_default_top_k(self, mock_model_loader, mock_load_config, mock_env_vars):
        """Test loading retriever with default top_k when not specified in config."""
        # Config without retriever section
        mock_load_config.return_value = {
            "astra_db": {"collection_name": "test_collection"}
        }
        
        with patch('retriever.retrieval.AstraDBVectorStore') as mock_astra_db:
            mock_vstore_instance = Mock()
            mock_retriever_instance = Mock()
            mock_vstore_instance.as_retriever.return_value = mock_retriever_instance
            mock_astra_db.return_value = mock_vstore_instance
            
            retriever = Retriever()
            retriever.load_retriever()
            
            # Should use default top_k of 3
            mock_vstore_instance.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
    
    @patch('retriever.retrieval.load_config')
    @patch('retriever.retrieval.ModelLoader')
    def test_call_retriever(self, mock_model_loader, mock_load_config, mock_env_vars):
        """Test the call_retriever method."""
        mock_load_config.return_value = {
            "astra_db": {"collection_name": "test_collection"},
            "retriever": {"top_k": 5}
        }
        
        retriever = Retriever()
        
        # Mock the load_retriever method
        mock_retriever_instance = Mock()
        mock_documents = [Mock(), Mock()]
        mock_retriever_instance.invoke.return_value = mock_documents
        
        with patch.object(retriever, 'load_retriever', return_value=mock_retriever_instance):
            result = retriever.call_retriever("test query")
            
            mock_retriever_instance.invoke.assert_called_once_with("test query")
            assert result == mock_documents

class TestRetrieverIntegration:
    """Integration tests for the Retriever class."""
    
    @patch('retriever.retrieval.load_config')
    @patch('retriever.retrieval.ModelLoader')
    @patch('retriever.retrieval.AstraDBVectorStore')
    def test_retriever_full_workflow(self, mock_astra_db, mock_model_loader, mock_load_config):
        """Test the complete retriever workflow."""
        # Setup mocks
        mock_load_config.return_value = {
            "astra_db": {"collection_name": "test_collection"},
            "retriever": {"top_k": 5}
        }
        
        mock_embeddings = Mock()
        mock_model_loader_instance = Mock()
        mock_model_loader_instance.load_embeddings.return_value = mock_embeddings
        mock_model_loader.return_value = mock_model_loader_instance
        
        mock_vstore_instance = Mock()
        mock_retriever_instance = Mock()
        mock_documents = [Mock(page_content="Test content", metadata={"id": "1"})]
        mock_retriever_instance.invoke.return_value = mock_documents
        mock_vstore_instance.as_retriever.return_value = mock_retriever_instance
        mock_astra_db.return_value = mock_vstore_instance
        
        # Set environment variables
        env_vars = {
            "GOOGLE_API_KEY": "test_key",
            "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com",
            "ASTRA_DB_APPLICATION_TOKEN": "test_token",
            "ASTRA_DB_KEYSPACE": "test_keyspace"
        }
        
        with patch.dict(os.environ, env_vars):
            retriever = Retriever()
            results = retriever.call_retriever("test query")
            
            assert results == mock_documents
            assert len(results) == 1
            assert results[0].page_content == "Test content"

if __name__ == "__main__":
    pytest.main([__file__])
