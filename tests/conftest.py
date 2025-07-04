"""
Test configuration and fixtures for the Customer Support Chatbot project.
"""
import pytest
import os
import sys
import tempfile
import pandas as pd
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def sample_product_data():
    """Create sample product data for testing."""
    return pd.DataFrame({
        'product_id': [
            'PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD005'
        ],
        'product_title': [
            'Wireless Bluetooth Headphones Premium',
            'Gaming Laptop 16GB RAM Intel i7',
            'Smartphone 128GB Storage Dual Camera',
            'Mechanical Gaming Keyboard RGB',
            'Portable Bluetooth Speaker Waterproof'
        ],
        'rating': [4.5, 4.8, 4.2, 4.6, 4.3],
        'summary': [
            'Excellent sound quality',
            'Outstanding performance',
            'Great camera and battery',
            'Perfect for gaming',
            'Amazing sound for size'
        ],
        'review': [
            'These headphones provide crystal clear audio with deep bass. Battery lasts for 20+ hours. Highly recommended for music lovers.',
            'This laptop handles all modern games at high settings. The 16GB RAM ensures smooth multitasking. Perfect for work and gaming.',
            'The camera quality is impressive, especially in low light. Battery easily lasts a full day with heavy usage.',
            'The mechanical switches are responsive and the RGB lighting is customizable. Great build quality for the price.',
            'Despite its compact size, this speaker delivers powerful sound. Waterproof design is perfect for outdoor use.'
        ]
    })

@pytest.fixture
def mock_environment_variables():
    """Mock all required environment variables."""
    return {
        "GOOGLE_API_KEY": "test_google_api_key_12345",
        "ASTRA_DB_API_ENDPOINT": "https://test-database-id.apps.astra.datastax.com",
        "ASTRA_DB_APPLICATION_TOKEN": "AstraCS:test_token_12345",
        "ASTRA_DB_KEYSPACE": "test_keyspace"
    }

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "astra_db": {
            "collection_name": "test_ecommerce_data"
        },
        "embedding_model": {
            "provider": "google",
            "model_name": "models/text-embedding-004"
        },
        "retriever": {
            "top_k": 10
        },
        "llm": {
            "provider": "google",
            "model_name": "gemini-2.0-flash"
        }
    }

@pytest.fixture
def temp_csv_file(sample_product_data):
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_product_data.to_csv(f.name, index=False)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup - check if file exists before deleting
    if os.path.exists(temp_file):
        os.unlink(temp_file)

@pytest.fixture
def mock_langchain_documents():
    """Create mock LangChain documents for testing."""
    from langchain_core.documents import Document
    
    return [
        Document(
            page_content="Wireless Bluetooth Headphones Premium - Rating: 4.5 - Excellent sound quality - These headphones provide crystal clear audio",
            metadata={"product_id": "PROD001", "rating": 4.5}
        ),
        Document(
            page_content="Gaming Laptop 16GB RAM Intel i7 - Rating: 4.8 - Outstanding performance - This laptop handles all modern games",
            metadata={"product_id": "PROD002", "rating": 4.8}
        ),
        Document(
            page_content="Smartphone 128GB Storage Dual Camera - Rating: 4.2 - Great camera and battery - The camera quality is impressive",
            metadata={"product_id": "PROD003", "rating": 4.2}
        )
    ]

@pytest.fixture
def mock_embeddings():
    """Create a mock embeddings model."""
    mock_embeddings = Mock()
    mock_embeddings.embed_query.return_value = [0.1] * 768  # Mock 768-dimensional embedding
    mock_embeddings.embed_documents.return_value = [[0.1] * 768] * 3  # Mock embeddings for 3 documents
    return mock_embeddings

@pytest.fixture
def mock_llm():
    """Create a mock LLM model."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = "This is a helpful response about the requested product based on customer reviews and ratings."
    return mock_llm

@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    mock_store = Mock()
    mock_retriever = Mock()
    mock_store.as_retriever.return_value = mock_retriever
    return mock_store, mock_retriever

class MockAstraDBVectorStore:
    """Mock class for AstraDB vector store."""
    
    def __init__(self, **kwargs):
        self.embedding = kwargs.get('embedding')
        self.collection_name = kwargs.get('collection_name')
        self.api_endpoint = kwargs.get('api_endpoint')
        self.token = kwargs.get('token')
        self.namespace = kwargs.get('namespace')
        self._documents = []
    
    def add_documents(self, documents):
        """Mock adding documents to the store."""
        self._documents.extend(documents)
        return [f"doc_{i}" for i in range(len(documents))]
    
    def similarity_search(self, query, k=3):
        """Mock similarity search."""
        # Return a subset of stored documents
        return self._documents[:k]
    
    def as_retriever(self, **kwargs):
        """Return a mock retriever."""
        mock_retriever = Mock()
        mock_retriever.invoke = lambda query: self.similarity_search(query, k=kwargs.get('search_kwargs', {}).get('k', 3))
        return mock_retriever

@pytest.fixture
def mock_astra_db_store():
    """Create a mock AstraDB vector store."""
    return MockAstraDBVectorStore

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark API tests
        if "api" in item.nodeid.lower() or "test_main" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # Mark slow tests
        if any(keyword in item.nodeid.lower() for keyword in ["full_workflow", "integration", "complete"]):
            item.add_marker(pytest.mark.slow)
        
        # Default to unit test if no other marker
        if not any(marker.name in ["integration", "api", "slow"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
