# Customer Support Chatbot

An intelligent e-commerce customer support chatbot built with LangChain, FastAPI, and Google's Gemini AI. This chatbot provides product recommendations and handles customer queries by leveraging a vector database powered by AstraDB and product review data from Flipkart.

## 🚀 Features

- **AI-Powered Conversations**: Uses Google's Gemini 2.0 Flash model for natural language understanding
- **Vector Search**: Intelligent product retrieval using AstraDB vector store
- **Real-time Chat Interface**: Modern web-based chat UI
- **Product Recommendations**: Context-aware product suggestions based on customer reviews
- **RESTful API**: FastAPI backend with CORS support
- **Scalable Architecture**: Modular design with separate components for ingestion, retrieval, and inference
- **Docker Support**: Containerized deployment ready

## 🏗️ Architecture

```
Customer_Support_Chatbot/
├── main.py                     # FastAPI application entry point
├── data/                       # Product data storage
│   └── flipkart_product_review.csv
├── data_ingestion/             # Data processing and vector store ingestion
│   ├── __init__.py
│   └── ingestion_pipeline.py
├── retriever/                  # Vector search and document retrieval
│   ├── __init__.py
│   └── retrieval.py
├── prompt_library/             # AI prompt templates
│   ├── __init__.py
│   └── prompt.py
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── config_loader.py
│   └── model_loader.py
├── frontend/                   # Web chat interface
│   ├── index.html
│   └── README.md
├── config/                     # Configuration files
│   └── config.yaml
├── notebook/                   # Jupyter notebook for experimentation
│   └── custmor_support.ipynb
└── setup_database.py          # Database initialization script
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.12+
- **AI/ML**: LangChain, Google Gemini AI, Google Text Embeddings
- **Database**: AstraDB (Vector Database)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker, Uvicorn
- **Data Processing**: Pandas

## 📋 Prerequisites

Before running the application, ensure you have:

1. **Python 3.12+** installed
2. **AstraDB account** with vector search enabled
3. **Google AI Studio API key**
4. **Required environment variables** (see setup section)

## ⚙️ Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Customer_Support_Chatbot
```

### 2. Install Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Using uv (recommended):
```bash
uv install
```

### 3. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Google AI API
GOOGLE_API_KEY=your_google_api_key_here

# AstraDB Configuration
ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
ASTRA_DB_KEYSPACE=your_keyspace_name
```

### 4. Configuration

Update `config/config.yaml` if needed:

```yaml
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
```

### 5. Database Setup

Initialize the vector database with product data:

```bash
python setup_database.py
```

This script will:
- Validate your environment variables
- Load product data from `data/flipkart_product_review.csv`
- Create embeddings and populate the AstraDB vector store

### 6. Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **Chat Interface**: http://localhost:8000/chat
- **API Documentation**: http://localhost:8000/docs

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t customer-support-chatbot .

# Run the container
docker run -p 8000:8000 --env-file .env customer-support-chatbot
```

## 📚 API Endpoints

### GET `/`
Health check endpoint
```json
{
  "message": "Welcome to the Product Information Bot API. Use the /get endpoint to chat with the bot."
}
```

### POST `/get`
Chat with the bot
```bash
curl -X POST "http://localhost:8000/get" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "msg=Tell me about bluetooth headphones"
```

Response:
```json
{
  "response": "Based on the product reviews, I can recommend the BoAt Rockerz 235v2..."
}
```

### GET `/chat`
Access the web chat interface

## 🎯 Usage Examples

### Query Product Information
```
User: "What are the best bluetooth headphones under 2000?"
Bot: "Based on customer reviews, I recommend the BoAt Rockerz 235v2..."
```

### Ask About Product Features
```
User: "Tell me about the battery life of BoAt headphones"
Bot: "According to customer reviews, the BoAt Rockerz 235v2 offers..."
```

## 🔧 Component Details

### Data Ingestion Pipeline
- **File**: `data_ingestion/ingestion_pipeline.py`
- **Purpose**: Processes CSV data and creates vector embeddings
- **Features**: Automatic data transformation and AstraDB integration

### Retrieval System
- **File**: `retriever/retrieval.py`
- **Purpose**: Handles vector similarity search
- **Features**: Configurable top-k results, efficient document retrieval

### Model Loader
- **File**: `utils/model_loader.py`
- **Purpose**: Manages AI model initialization
- **Features**: Google Gemini integration, embedding model loading

### Prompt Templates
- **File**: `prompt_library/prompt.py`
- **Purpose**: Contains optimized prompts for the AI model
- **Features**: Context-aware response generation

## 🧪 Development

### Run Tests
The project includes a comprehensive test suite with 68 tests covering all major components:

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing

# Run specific test categories
python -m pytest tests/ -m unit          # Unit tests only
python -m pytest tests/ -m integration   # Integration tests only
python -m pytest tests/ -m api          # API tests only

# Run tests in verbose mode
python -m pytest tests/ -v

# Run tests and stop on first failure
python -m pytest tests/ -x
```

**Test Coverage:**
- **88% overall code coverage**
- **Unit Tests:** Model loading, configuration, prompt templates
- **Integration Tests:** Data ingestion, retrieval workflows, API endpoints
- **API Tests:** FastAPI endpoints, CORS, static file serving
- **Error Handling:** Environment validation, file handling, network errors

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Jupyter Notebook
Explore the project interactively:
```bash
jupyter notebook notebook/custmor_support.ipynb
```

## 🐛 Troubleshooting

### Common Issues

1. **"No product information available" Error**
   - Run `python setup_database.py` to populate the database
   - Verify your AstraDB credentials in the `.env` file

2. **API Key Errors**
   - Ensure your Google API key is valid and has the necessary permissions
   - Check that all environment variables are properly set

3. **Connection Timeouts**
   - Verify your AstraDB endpoint and token
   - Check your internet connection

### Debug Mode
Enable detailed logging by setting:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python main.py
```

## 📈 Performance Optimization

- **Vector Search**: Optimized for sub-second response times
- **Caching**: Environment variables and model loading optimization
- **Async Operations**: FastAPI async support for concurrent requests
- **Memory Management**: Efficient document processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Resources

- [LangChain Documentation](https://python.langchain.com/)
- [AstraDB Vector Search](https://docs.datastax.com/en/astra-serverless/docs/vector-search/overview.html)
- [Google AI Studio](https://makersuite.google.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the API documentation at `/docs`

---

**Built with ❤️ using LangChain and Google AI**