# Testing Documentation

This document provides comprehensive information about the test suite for the Customer Support Chatbot project.

## 📁 Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared fixtures and configuration
├── test_main.py                   # FastAPI application tests
├── test_retrieval.py              # Vector retrieval system tests
├── test_model_loader.py           # AI model loading tests
├── test_config_loader.py          # Configuration loading tests
├── test_prompt_library.py         # Prompt template tests
├── test_data_ingestion.py         # Data processing tests
├── test_setup_database.py         # Database setup script tests
└── pytest.ini                    # Pytest configuration
```

## 🧪 Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Coverage**: Utils, prompt library, configuration loading
- **Run with**: `python run_tests.py --type unit`

### Integration Tests
- **Purpose**: Test component interactions
- **Coverage**: End-to-end workflows, database operations
- **Run with**: `python run_tests.py --type integration`

### API Tests
- **Purpose**: Test FastAPI endpoints and HTTP interfaces
- **Coverage**: REST API endpoints, request/response handling
- **Run with**: `python run_tests.py --type api`

## 🚀 Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run specific test type
python run_tests.py --type unit --verbose
```

### Advanced Usage
```bash
# Run tests with HTML coverage report
python run_tests.py --coverage --format html

# Run integration tests only
python run_tests.py --type integration

# Run with JUnit XML output (for CI/CD)
python run_tests.py --format junit

# Install dependencies and run tests
python run_tests.py --install-deps --coverage
```

### Direct Pytest Usage
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run tests matching pattern
pytest -k "test_retrieval"

# Run with verbose output
pytest -v

# Run only failed tests from last run
pytest --lf
```

## 📊 Test Coverage

### Current Coverage Areas

1. **FastAPI Application (`test_main.py`)**
   - Endpoint functionality
   - Request/response handling
   - Error handling
   - CORS configuration
   - Static file serving

2. **Retrieval System (`test_retrieval.py`)**
   - Vector store initialization
   - Document retrieval
   - Environment variable validation
   - Configuration loading
   - Error handling

3. **Model Loading (`test_model_loader.py`)**
   - Embedding model loading
   - LLM initialization
   - Configuration validation
   - API error handling
   - Model switching

4. **Configuration System (`test_config_loader.py`)**
   - YAML file parsing
   - Nested configuration handling
   - Error handling for invalid files
   - Unicode and special character support

5. **Prompt Templates (`test_prompt_library.py`)**
   - Template structure validation
   - Placeholder formatting
   - Template extensibility
   - Content validation

6. **Data Ingestion (`test_data_ingestion.py`)**
   - CSV data loading
   - Data transformation
   - Vector store population
   - Error handling

7. **Database Setup (`test_setup_database.py`)**
   - Environment validation
   - Initialization workflow
   - Error handling

### Coverage Targets
- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical paths**: 100% coverage for main user flows

## 🔧 Test Configuration

### Fixtures (`conftest.py`)
- **project_root**: Project directory path
- **sample_product_data**: Mock product data for testing
- **mock_environment_variables**: Environment variable mocks
- **mock_config**: Configuration mocks
- **temp_csv_file**: Temporary CSV files for testing
- **mock_langchain_documents**: LangChain document mocks
- **mock_embeddings**: Embedding model mocks
- **mock_llm**: Language model mocks

### Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API tests
- `@pytest.mark.slow`: Slow-running tests

### Configuration Files
- **pytest.ini**: Main pytest configuration
- **conftest.py**: Shared fixtures and test configuration

## 🎯 Testing Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Mock external dependencies

### 2. Test Naming
- Use descriptive test names
- Follow pattern: `test_[what]_[condition]_[expected]`
- Group related tests in classes

### 3. Mock Strategy
- Mock external APIs (Google AI, AstraDB)
- Mock file system operations
- Mock environment variables

### 4. Assertions
- Use specific assertions
- Test both positive and negative cases
- Verify error messages and types

### 5. Test Data
- Use realistic test data
- Include edge cases
- Test with various data types

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure project root is in Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Missing Dependencies**
   ```bash
   # Install test dependencies
   python run_tests.py --install-deps
   ```

3. **Environment Variables**
   ```bash
   # Tests use mocked environment variables
   # Check conftest.py for mock values
   ```

4. **File Path Issues**
   ```bash
   # Run tests from project root directory
   cd /path/to/Customer_Support_Chatbot
   python run_tests.py
   ```

### Debug Mode
```bash
# Run with debug output
pytest -v -s

# Run single test with debug
pytest tests/test_main.py::TestAPI::test_root_endpoint -v -s

# Drop into debugger on failure
pytest --pdb
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - run: pip install -r requirements.txt
    - run: python run_tests.py --coverage --format junit
    - uses: codecov/codecov-action@v1
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: python run_tests.py --type unit
        language: system
        pass_filenames: false
```

## 🔄 Adding New Tests

### 1. Create Test File
```python
# tests/test_new_feature.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from your_module import YourClass

class TestYourClass:
    def test_your_method(self):
        # Test implementation
        assert True
```

### 2. Add Fixtures if Needed
```python
# In conftest.py or test file
@pytest.fixture
def your_fixture():
    return "test_data"
```

### 3. Update Documentation
- Add test description to this file
- Update coverage targets
- Document any special requirements

## 📝 Test Reporting

### Coverage Reports
```bash
# Generate HTML coverage report
python run_tests.py --coverage --format html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI)
python run_tests.py --coverage --format xml
```

### JUnit XML Reports
```bash
# Generate JUnit XML for CI/CD systems
python run_tests.py --format junit
# Creates test-results.xml
```

### Custom Reports
```bash
# Verbose test output
python run_tests.py --verbose

# Quiet output (errors only)
python run_tests.py

# Show test durations
pytest --durations=10
```

## 🎓 Testing Resources

### Pytest Documentation
- [Pytest Official Docs](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/mark.html)

### FastAPI Testing
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [TestClient Usage](https://fastapi.tiangolo.com/reference/testclient/)

### Mock Libraries
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

---

**Happy Testing! 🧪✨**
