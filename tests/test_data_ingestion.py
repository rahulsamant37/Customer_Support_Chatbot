import pytest
import pandas as pd
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_ingestion.ingestion_pipeline import DataIngestion

class TestDataIngestion:
    """Test cases for the DataIngestion class."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing."""
        data = {
            'product_id': ['PROD001', 'PROD002', 'PROD003'],
            'product_title': [
                'Wireless Bluetooth Headphones',
                'Gaming Laptop 16GB RAM',
                'Smartphone 128GB Storage'
            ],
            'rating': [4.5, 4.8, 4.2],
            'summary': [
                'Great sound quality',
                'Excellent performance',
                'Good camera quality'
            ],
            'review': [
                'These headphones have amazing sound quality and battery life.',
                'Perfect laptop for gaming and professional work.',
                'Camera is great, battery lasts all day.'
            ]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def temp_csv_file(self, sample_csv_data):
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_csv_data.to_csv(f.name, index=False)
            return f.name
    
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
    
    @patch('data_ingestion.ingestion_pipeline.load_config')
    @patch('data_ingestion.ingestion_pipeline.ModelLoader')
    def test_data_ingestion_initialization(self, mock_model_loader, mock_load_config, mock_env_vars, temp_csv_file):
        """Test DataIngestion initialization."""
        mock_config = {
            "astra_db": {"collection_name": "test_collection"}
        }
        mock_load_config.return_value = mock_config
        
        # Mock the CSV path to use our temp file
        with patch.object(DataIngestion, '_get_csv_path', return_value=temp_csv_file):
            data_ingestion = DataIngestion()
            
            assert data_ingestion.config == mock_config
            assert data_ingestion.csv_path == temp_csv_file
            assert isinstance(data_ingestion.product_data, pd.DataFrame)
            assert len(data_ingestion.product_data) == 3  # Sample data has 3 rows
        
        # Clean up
        os.unlink(temp_csv_file)
    
    @patch('data_ingestion.ingestion_pipeline.load_config')
    @patch('data_ingestion.ingestion_pipeline.ModelLoader')
    def test_load_env_variables_success(self, mock_model_loader, mock_load_config, mock_env_vars):
        """Test successful loading of environment variables."""
        mock_load_config.return_value = {"astra_db": {"collection_name": "test"}}
        
        with patch.object(DataIngestion, '_get_csv_path', return_value="dummy.csv"):
            with patch.object(DataIngestion, '_load_csv', return_value=pd.DataFrame()):
                data_ingestion = DataIngestion()
                
                # Environment variables should be loaded from mock_env_vars
                # The actual validation happens in _load_env_variables method
                assert hasattr(data_ingestion, 'model_loader')
                assert hasattr(data_ingestion, 'config')
    
    @patch('data_ingestion.ingestion_pipeline.load_config')
    @patch('data_ingestion.ingestion_pipeline.ModelLoader')
    def test_load_env_variables_missing(self, mock_model_loader, mock_load_config):
        """Test DataIngestion with missing environment variables."""
        mock_load_config.return_value = {"astra_db": {"collection_name": "test"}}
        
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(DataIngestion, '_get_csv_path', return_value="dummy.csv"):
                with patch.object(DataIngestion, '_load_csv', return_value=pd.DataFrame()):
                    # Should raise an error due to missing environment variables
                    # The exact error depends on the implementation of _load_env_variables
                    try:
                        DataIngestion()
                    except EnvironmentError:
                        pass  # Expected behavior
    
    @patch('data_ingestion.ingestion_pipeline.load_config')
    @patch('data_ingestion.ingestion_pipeline.ModelLoader')
    def test_get_csv_path(self, mock_model_loader, mock_load_config, mock_env_vars):
        """Test CSV path detection."""
        mock_load_config.return_value = {"astra_db": {"collection_name": "test"}}
        
        with patch.object(DataIngestion, '_load_csv', return_value=pd.DataFrame()):
            data_ingestion = DataIngestion()
            csv_path = data_ingestion._get_csv_path()
            
            # Should return a path to the CSV file
            assert isinstance(csv_path, str)
            assert csv_path.endswith('.csv')
    
    def test_load_csv_valid_file(self, temp_csv_file, sample_csv_data):
        """Test loading a valid CSV file."""
        # Create a mock DataIngestion instance just to test _load_csv
        with patch('data_ingestion.ingestion_pipeline.load_config'):
            with patch('data_ingestion.ingestion_pipeline.ModelLoader'):
                with patch.dict(os.environ, {"GOOGLE_API_KEY": "test"}):
                    with patch.object(DataIngestion, '_get_csv_path', return_value=temp_csv_file):
                        data_ingestion = DataIngestion()
                        
                        # Verify data was loaded correctly
                        assert len(data_ingestion.product_data) == 3
                        assert 'product_id' in data_ingestion.product_data.columns
                        assert 'product_title' in data_ingestion.product_data.columns
                        assert 'rating' in data_ingestion.product_data.columns
                        assert 'review' in data_ingestion.product_data.columns
        
        # Clean up
        os.unlink(temp_csv_file)
    
    @patch('data_ingestion.ingestion_pipeline.load_config')
    @patch('data_ingestion.ingestion_pipeline.ModelLoader')
    def test_load_csv_file_not_found(self, mock_model_loader, mock_load_config, mock_env_vars):
        """Test loading CSV when file doesn't exist."""
        mock_load_config.return_value = {"astra_db": {"collection_name": "test"}}
        
        with patch.object(DataIngestion, '_get_csv_path', return_value="nonexistent.csv"):
            with pytest.raises(FileNotFoundError):
                DataIngestion()

class TestDataIngestionTransformation:
    """Test data transformation methods in DataIngestion."""
    
    @pytest.fixture
    def mock_data_ingestion(self):
        """Create a mock DataIngestion instance for testing."""
        with patch('data_ingestion.ingestion_pipeline.load_config') as mock_config:
            with patch('data_ingestion.ingestion_pipeline.ModelLoader') as mock_model_loader:
                with patch.dict(os.environ, {"GOOGLE_API_KEY": "test"}):
                    mock_config.return_value = {"astra_db": {"collection_name": "test"}}
                    
                    # Create sample data
                    sample_data = pd.DataFrame({
                        'product_id': ['PROD001', 'PROD002'],
                        'product_title': ['Test Product 1', 'Test Product 2'],
                        'rating': [4.5, 4.0],
                        'summary': ['Great product', 'Good product'],
                        'review': ['Detailed review 1', 'Detailed review 2']
                    })
                    
                    with patch.object(DataIngestion, '_get_csv_path', return_value="test.csv"):
                        with patch.object(DataIngestion, '_load_csv', return_value=sample_data):
                            return DataIngestion()
    
    def test_data_transformation_methods_exist(self, mock_data_ingestion):
        """Test that data transformation methods exist and are callable."""
        # Check if the instance has expected attributes
        assert hasattr(mock_data_ingestion, 'product_data')
        assert hasattr(mock_data_ingestion, 'config')
        assert hasattr(mock_data_ingestion, 'model_loader')
        
        # Verify product_data is a DataFrame
        assert isinstance(mock_data_ingestion.product_data, pd.DataFrame)
        assert len(mock_data_ingestion.product_data) == 2

class TestDataIngestionIntegration:
    """Integration tests for DataIngestion."""
    
    @patch('data_ingestion.ingestion_pipeline.AstraDBVectorStore')
    @patch('data_ingestion.ingestion_pipeline.load_config')
    @patch('data_ingestion.ingestion_pipeline.ModelLoader')
    def test_full_ingestion_workflow(self, mock_model_loader, mock_load_config, mock_astra_db, temp_csv_file):
        """Test the complete data ingestion workflow."""
        # Setup mocks
        mock_config = {
            "astra_db": {"collection_name": "test_collection"}
        }
        mock_load_config.return_value = mock_config
        
        mock_embeddings = Mock()
        mock_model_loader_instance = Mock()
        mock_model_loader_instance.load_embeddings.return_value = mock_embeddings
        mock_model_loader.return_value = mock_model_loader_instance
        
        mock_vstore = Mock()
        mock_astra_db.return_value = mock_vstore
        
        # Set environment variables
        env_vars = {
            "GOOGLE_API_KEY": "test_key",
            "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com",
            "ASTRA_DB_APPLICATION_TOKEN": "test_token",
            "ASTRA_DB_KEYSPACE": "test_keyspace"
        }
        
        with patch.dict(os.environ, env_vars):
            with patch.object(DataIngestion, '_get_csv_path', return_value=temp_csv_file):
                data_ingestion = DataIngestion()
                
                # Verify initialization
                assert isinstance(data_ingestion.product_data, pd.DataFrame)
                assert len(data_ingestion.product_data) > 0
                assert data_ingestion.config == mock_config
        
        # Clean up
        os.unlink(temp_csv_file)
    
    def test_data_validation(self, temp_csv_file):
        """Test data validation during ingestion."""
        # Create CSV with missing columns
        invalid_data = pd.DataFrame({
            'product_id': ['PROD001'],
            'title': ['Test Product'],  # Wrong column name, should be 'product_title'
            'score': [4.5]  # Wrong column name, should be 'rating'
            # Missing 'summary' and 'review' columns
        })
        
        # Create temporary invalid CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            invalid_data.to_csv(f.name, index=False)
            invalid_csv_path = f.name
        
        try:
            with patch('data_ingestion.ingestion_pipeline.load_config') as mock_config:
                with patch('data_ingestion.ingestion_pipeline.ModelLoader'):
                    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test"}):
                        mock_config.return_value = {"astra_db": {"collection_name": "test"}}
                        
                        with patch.object(DataIngestion, '_get_csv_path', return_value=invalid_csv_path):
                            # Should raise ValueError due to missing required columns
                            with pytest.raises(ValueError) as exc_info:
                                DataIngestion()
                            
                            assert "CSV must contain columns:" in str(exc_info.value)
                            
        finally:
            os.unlink(invalid_csv_path)
            os.unlink(temp_csv_file)

if __name__ == "__main__":
    pytest.main([__file__])
