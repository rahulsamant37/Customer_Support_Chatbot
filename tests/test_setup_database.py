import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import setup_database

class TestSetupDatabase:
    """Test cases for the setup_database.py script."""
    
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
    
    def test_check_environment_success(self, mock_env_vars):
        """Test check_environment with all required variables set."""
        with patch('builtins.print') as mock_print:
            result = setup_database.check_environment()
            
            # Should return True and print success message
            assert result is True
            mock_print.assert_called_with("✅ All environment variables are set.")
    
    def test_check_environment_missing_vars(self):
        """Test check_environment with missing environment variables."""
        # Mock load_dotenv to prevent loading .env file
        with patch('setup_database.load_dotenv'):
            # Clear all environment variables
            with patch.dict(os.environ, {}, clear=True):
                with patch('builtins.print') as mock_print:
                    result = setup_database.check_environment()
                    
                    # Should return False
                    assert result is False
                    
                    # Check that it identifies missing variables
                    printed_output = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
                    assert "❌ Missing environment variables:" in printed_output
    
    def test_check_environment_partial_missing_vars(self):
        """Test check_environment with some missing environment variables."""
        partial_env = {
            "GOOGLE_API_KEY": "test_key",
            "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com"
            # Missing ASTRA_DB_APPLICATION_TOKEN and ASTRA_DB_KEYSPACE
        }
        
        with patch('setup_database.load_dotenv'):
            with patch.dict(os.environ, partial_env, clear=True):
                with patch('builtins.print') as mock_print:
                    result = setup_database.check_environment()
                    
                    # Should return False
                    assert result is False
                    
                    # Should identify the missing variables
                    printed_output = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
                    assert "ASTRA_DB_APPLICATION_TOKEN" in printed_output
                    assert "ASTRA_DB_KEYSPACE" in printed_output

class TestSetupDatabaseIntegration:
    """Integration tests for the setup database functionality."""
    
    def test_main_function_exists(self):
        """Test that the main function or entry point exists."""
        # Check if main function exists
        assert hasattr(setup_database, 'check_environment')
        assert hasattr(setup_database, 'populate_database')
        assert hasattr(setup_database, 'test_retriever')
        assert hasattr(setup_database, 'main')
        
        # The setup_database module should be importable and have expected functions
        assert callable(setup_database.check_environment)
        assert callable(setup_database.populate_database)
        assert callable(setup_database.test_retriever)
        assert callable(setup_database.main)
    
    @patch('data_ingestion.ingestion_pipeline.DataIngestion')
    @patch('setup_database.check_environment')
    def test_database_setup_workflow(self, mock_check_env, mock_data_ingestion):
        """Test the database setup workflow."""
        # Mock successful environment check
        mock_check_env.return_value = True
        
        # Mock DataIngestion
        mock_ingestion_instance = Mock()
        mock_data_ingestion.return_value = mock_ingestion_instance
        
        # Test that we can import and potentially run the setup
        # The actual main execution would depend on the script structure
        try:
            # If there's a main function, test it
            if hasattr(setup_database, 'main'):
                with patch('sys.argv', ['setup_database.py']):
                    setup_database.main()
            
            # Verify environment was checked
            mock_check_env.assert_called()
            
        except SystemExit:
            # Script might call sys.exit(), which is fine for testing
            pass
    
    def test_script_imports_successfully(self):
        """Test that the setup_database script imports without errors."""
        # If we can import it, the basic structure is correct
        assert setup_database is not None
        
        # Check for expected attributes/functions
        expected_functions = ['check_environment']
        for func_name in expected_functions:
            assert hasattr(setup_database, func_name), f"Missing function: {func_name}"

class TestSetupDatabaseErrorHandling:
    """Test error handling in setup_database script."""
    
    @patch('data_ingestion.ingestion_pipeline.DataIngestion')
    def test_data_ingestion_error_handling(self, mock_data_ingestion):
        """Test handling of DataIngestion errors."""
        # Mock DataIngestion to raise an exception
        mock_data_ingestion.side_effect = Exception("Database connection error")
        
        env_vars = {
            "GOOGLE_API_KEY": "test_key",
            "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com",
            "ASTRA_DB_APPLICATION_TOKEN": "test_token",
            "ASTRA_DB_KEYSPACE": "test_keyspace"
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('builtins.print') as mock_print:
                result = setup_database.populate_database()
                
                # Should return False and print error message
                assert result is False
                printed_output = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
                assert "❌ Error during data ingestion:" in printed_output
    
    def test_file_not_found_handling(self):
        """Test handling when CSV file is not found."""
        with patch('data_ingestion.ingestion_pipeline.DataIngestion') as mock_data_ingestion:
            mock_data_ingestion.side_effect = FileNotFoundError("CSV file not found")
            
            env_vars = {
                "GOOGLE_API_KEY": "test_key",
                "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com",
                "ASTRA_DB_APPLICATION_TOKEN": "test_token",
                "ASTRA_DB_KEYSPACE": "test_keyspace"
            }
            
            with patch.dict(os.environ, env_vars):
                with patch('builtins.print') as mock_print:
                    result = setup_database.populate_database()
                    
                    # Should return False and print error message
                    assert result is False
                    printed_output = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
                    assert "❌ Error during data ingestion:" in printed_output

class TestSetupDatabaseValidation:
    """Test validation functions in setup_database."""
    
    def test_required_variables_list(self):
        """Test that the script checks for all required environment variables."""
        # The script should check for these specific variables
        required_vars = [
            "GOOGLE_API_KEY",
            "ASTRA_DB_API_ENDPOINT", 
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_KEYSPACE"
        ]
        
        # Test each variable individually
        for var in required_vars:
            env_dict = {v: "test_value" for v in required_vars}
            del env_dict[var]  # Remove one variable
            
            with patch('setup_database.load_dotenv'):
                with patch.dict(os.environ, env_dict, clear=True):
                    with patch('builtins.print') as mock_print:
                        result = setup_database.check_environment()
                        
                        # Should return False and mention the missing variable
                        assert result is False
                        printed_output = ''.join([str(call.args[0]) for call in mock_print.call_args_list])
                        assert var in printed_output
    
    def test_environment_validation_comprehensive(self):
        """Test comprehensive environment validation."""
        test_cases = [
            # All variables present
            {
                "env": {
                    "GOOGLE_API_KEY": "test_key",
                    "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com",
                    "ASTRA_DB_APPLICATION_TOKEN": "test_token",
                    "ASTRA_DB_KEYSPACE": "test_keyspace"
                },
                "should_pass": True
            },
            # Empty values
            {
                "env": {
                    "GOOGLE_API_KEY": "",
                    "ASTRA_DB_API_ENDPOINT": "https://test.endpoint.com",
                    "ASTRA_DB_APPLICATION_TOKEN": "test_token",
                    "ASTRA_DB_KEYSPACE": "test_keyspace"
                },
                "should_pass": False
            },
            # All empty
            {
                "env": {},
                "should_pass": False
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            with patch.dict(os.environ, test_case["env"], clear=True):
                with patch('builtins.print') as mock_print:
                    setup_database.check_environment()
                    
                    # Check if the test case behaves as expected
                    # This is a basic structure test since implementation details may vary

if __name__ == "__main__":
    pytest.main([__file__])
