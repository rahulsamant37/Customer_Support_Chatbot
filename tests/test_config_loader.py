import pytest
import yaml
import tempfile
import os
import sys

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import load_config

class TestConfigLoader:
    """Test cases for the config loader utility."""
    
    def test_load_config_valid_file(self):
        """Test loading a valid YAML configuration file."""
        # Create a temporary config file
        config_data = {
            "astra_db": {
                "collection_name": "test_collection"
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            result = load_config(temp_config_path)
            
            assert result == config_data
            assert result["astra_db"]["collection_name"] == "test_collection"
            assert result["embedding_model"]["model_name"] == "models/text-embedding-004"
            assert result["retriever"]["top_k"] == 10
            assert result["llm"]["model_name"] == "gemini-2.0-flash"
        finally:
            os.unlink(temp_config_path)
    
    def test_load_config_default_path(self):
        """Test loading config with default path."""
        # This test assumes the default config file exists
        # We'll mock the file reading to avoid dependency on actual file
        import builtins
        
        mock_config_content = """
astra_db:
  collection_name: "ecommercedata"

embedding_model:
  provider: "google"
  model_name: "models/text-embedding-004"

retriever:
  top_k: 10

llm:
  provider: "google"
  model_name: "gemini-2.0-flash"
"""
        
        original_open = builtins.open
        
        def mock_open(*args, **kwargs):
            if args[0] == "config/config.yaml":
                from io import StringIO
                return StringIO(mock_config_content)
            return original_open(*args, **kwargs)
        
        builtins.open = mock_open
        
        try:
            result = load_config()
            
            assert "astra_db" in result
            assert "embedding_model" in result
            assert "retriever" in result
            assert "llm" in result
            assert result["astra_db"]["collection_name"] == "ecommercedata"
        finally:
            builtins.open = original_open
    
    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.yaml")
    
    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML syntax."""
        # Create a temporary file with invalid YAML
        invalid_yaml_content = """
astra_db:
  collection_name: "test_collection"
invalid_yaml: [unclosed_bracket
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml_content)
            temp_config_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_config_path)
        finally:
            os.unlink(temp_config_path)
    
    def test_load_config_empty_file(self):
        """Test loading config from an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Write empty content
            f.write("")
            temp_config_path = f.name
        
        try:
            result = load_config(temp_config_path)
            assert result is None  # yaml.safe_load returns None for empty files
        finally:
            os.unlink(temp_config_path)
    
    def test_load_config_nested_structure(self):
        """Test loading config with deeply nested structure."""
        nested_config = {
            "database": {
                "astra_db": {
                    "connection": {
                        "endpoint": "https://test.endpoint.com",
                        "token": "secret_token",
                        "keyspace": "test_keyspace"
                    },
                    "collection": {
                        "name": "test_collection",
                        "settings": {
                            "vector_size": 768,
                            "similarity_metric": "cosine"
                        }
                    }
                }
            },
            "ai_models": {
                "embedding": {
                    "provider": "google",
                    "config": {
                        "model_name": "models/text-embedding-004",
                        "api_version": "v1"
                    }
                },
                "llm": {
                    "provider": "google",
                    "config": {
                        "model_name": "gemini-2.0-flash",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(nested_config, f)
            temp_config_path = f.name
        
        try:
            result = load_config(temp_config_path)
            
            assert result == nested_config
            assert result["database"]["astra_db"]["connection"]["endpoint"] == "https://test.endpoint.com"
            assert result["ai_models"]["llm"]["config"]["temperature"] == 0.7
        finally:
            os.unlink(temp_config_path)
    
    def test_load_config_with_special_characters(self):
        """Test loading config with special characters and unicode."""
        config_with_special_chars = {
            "app_name": "Customer Support Chatbot 🤖",
            "description": "AI-powered customer support with émojis & spécial chars",
            "features": [
                "Multi-language support",
                "Real-time responses",
                "Product recommendations"
            ],
            "version": "1.0.0-beta",
            "maintainer": {
                "name": "AI Team",
                "email": "ai-team@company.com"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config_with_special_chars, f, allow_unicode=True)
            temp_config_path = f.name
        
        try:
            result = load_config(temp_config_path)
            
            assert result == config_with_special_chars
            assert result["app_name"] == "Customer Support Chatbot 🤖"
            assert "émojis" in result["description"]
            assert len(result["features"]) == 3
        finally:
            os.unlink(temp_config_path)

class TestConfigLoaderEdgeCases:
    """Test edge cases for the config loader."""
    
    def test_load_config_with_none_values(self):
        """Test loading config with null/None values."""
        config_with_nulls = {
            "database_url": None,
            "api_key": "valid_key",
            "optional_feature": None,
            "settings": {
                "debug": True,
                "cache_timeout": None
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_with_nulls, f)
            temp_config_path = f.name
        
        try:
            result = load_config(temp_config_path)
            
            assert result["database_url"] is None
            assert result["api_key"] == "valid_key"
            assert result["optional_feature"] is None
            assert result["settings"]["cache_timeout"] is None
        finally:
            os.unlink(temp_config_path)
    
    def test_load_config_with_boolean_values(self):
        """Test loading config with various boolean representations."""
        config_with_booleans = {
            "feature_enabled": True,
            "debug_mode": False,
            "auto_deploy": "yes",  # YAML interprets this as string
            "strict_mode": "no",   # YAML interprets this as string
            "verbose": 1,          # Number, not boolean
            "quiet": 0             # Number, not boolean
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_with_booleans, f)
            temp_config_path = f.name
        
        try:
            result = load_config(temp_config_path)
            
            assert result["feature_enabled"] is True
            assert result["debug_mode"] is False
            assert result["auto_deploy"] == "yes"  # String, not boolean
            assert result["strict_mode"] == "no"   # String, not boolean
            assert result["verbose"] == 1
            assert result["quiet"] == 0
        finally:
            os.unlink(temp_config_path)

if __name__ == "__main__":
    pytest.main([__file__])
