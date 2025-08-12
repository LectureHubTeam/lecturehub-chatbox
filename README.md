# 🤖 LectureHub Chatbot - Complete Documentation

A comprehensive guide to the LectureHub Chatbot, a Streamlit-based RAG (Retrieval-Augmented Generation) chatbot for educational content.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Development](#development)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## 🎯 Overview

The LectureHub Chatbot is a sophisticated RAG application designed to help students and educators interact with educational content. It combines:

- **🔍 Retrieval-Augmented Generation (RAG)** for accurate, context-aware responses
- **🗄️ PostgreSQL with pgvector** for efficient vector storage and similarity search
- **🧠 Google Gemini LLM** for natural language processing (with mock fallback)
- **🌐 Streamlit** for an intuitive web interface
- **🏗️ Modular architecture** for maintainability and extensibility

### ✨ Key Features

- **📄 Multi-format Document Support**: PDF, Markdown, and Python code
- **🎯 Smart Question Handling**: Accepts all questions without strict relevance filtering
- **⚡ Vector Similarity Search**: Fast and accurate document retrieval
- **🐳 Docker Integration**: Easy setup with containerized database
- **🔧 Modular Design**: Clean, maintainable codebase
- **🔄 Mock LLM Support**: Works without API key for testing

## 🏗️ Architecture

### 📁 Project Structure

```
lecturehub-chatbot/
├── src/                          # Main source code
│   ├── core/                     # Core application components
│   │   ├── config.py            # Configuration constants
│   │   ├── main.py              # Main entry point
│   │   ├── chatbot_logic.py     # Core chatbot logic
│   │   └── rag_chatbot.py       # Main orchestrator
│   ├── database/                 # Database operations
│   │   ├── database.py          # PostgreSQL and pgvector
│   │   └── vectorstore.py       # Vector store management
│   ├── llm/                      # LLM and language processing
│   │   ├── llm_chain.py         # LLM chain management
│   │   ├── mock_llm_chain.py    # Mock LLM for testing
│   │   └── keyword_extractor.py # Keyword extraction
│   ├── ui/                       # User interface
│   │   ├── chat_manager.py      # Chat management
│   │   └── ui_components.py     # UI components
│   └── utils/                    # Utilities
│       └── document_loader.py   # Document processing
├── tests/                        # Test files
├── docs/                         # Documentation
├── config/                       # Configuration files
├── docker/                       # Docker setup
└── data/                         # Data files
```

### 🔧 Core Components

#### 1. RAGChatbot (`src/core/rag_chatbot.py`)
The main orchestrator that coordinates all components:
- 🎮 Manages application lifecycle
- 🔗 Coordinates database, LLM, and UI components
- 🛡️ Handles error scenarios gracefully

#### 2. Database Management (`src/database/`)
- **🗄️ DatabaseManager**: PostgreSQL connection and pgvector operations
- **🔍 VectorStoreManager**: Vector store operations and embedding management

#### 3. LLM Processing (`src/llm/`)
- **🧠 LLMChainBuilder**: Creates and manages QA chains
- **🔑 KeywordExtractor**: Extracts keywords for relevance checking
- **🎯 MockLLMChainBuilder**: Provides mock responses for testing
- **✅ SmartRelevanceChecker**: Determines if questions are relevant (currently disabled)

#### 4. User Interface (`src/ui/`)
- **💬 ChatManager**: Manages chat history and interactions
- **⚙️ SidebarManager**: Handles configuration UI
- **🖥️ MainUIManager**: Manages main UI components

#### 5. Utilities (`src/utils/`)
- **📄 DocumentLoader**: Loads and processes documents
- **✂️ DocumentProcessor**: Handles text chunking and metadata

## 🚀 Installation

### 📋 Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for database)
- Google Gemini API key (optional - mock LLM available)

### 📦 Step-by-Step Installation

1. **📥 Clone the repository:**
   ```bash
   git clone <repository-url>
   cd lecturehub-chatbot
   ```

2. **📦 Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **🐳 Start the database:**
   ```bash
   ./docker/docker-setup.sh start
   ```

4. **⚙️ Configure environment (optional):**
   ```bash
   cp env.template .env
   # Edit .env with your GEMINI_API_KEY (optional)
   ```

5. **🧪 Test the setup:**
   ```bash
   chmod +x ./docker/docker-setup.sh
   ./docker/docker-setup.sh test
   ```

## ⚙️ Configuration

### 🔧 Environment Variables

The application uses environment variables for configuration. Key variables include:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=embedding
DB_USER=root
DB_PASSWORD=root_password

# LLM Configuration (Optional)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# Application Configuration
PROBLEM_ID=ma_de_001
```

### 📁 Configuration Files

- **`config/env.template`**: Template for environment variables
- **`config/example.env`**: Example configuration
- **`docker/docker.env`**: Docker-specific configuration

### 🗄️ Database Configuration

The application supports two database configuration methods:

1. **🔧 Individual Parameters:**
   ```python
   db = DatabaseManager(
       host="localhost",
       port="5432",
       database="embedding",
       user="root",
       password="root_password"
   )
   ```

2. **🔗 Connection String:**
   ```python
   db = DatabaseManager(
       connection_string="postgresql+psycopg://user:pass@host:5432/db"
   )
   ```

## 🎮 Usage

### 🚀 Running the Application

```bash
# Development mode
python main.py

# Production mode
streamlit run main.py
```

### 💬 Using the Chatbot

1. **🚀 Start the application** and navigate to the web interface
2. **⚙️ Configure settings** in the sidebar:
   - Database connection parameters
   - Google Gemini API key (optional)
   - Application settings
3. **📥 Ingest documents** by clicking "Ingest dữ liệu"
4. **❓ Ask questions** about your educational content

### 📄 Document Requirements

Place these files in the `data/lectures/mmceasar2/` directory:
- `mmceasar2.pdf` - Problem statement
- `mmceasar2.md` - Lecture content  
- `mmceasar2.py` - Solution code

### 💬 Chat Interface

The chatbot provides:
- **⚡ Real-time responses** based on your documents
- **📚 Source citations** showing which documents were used
- **🎯 Flexible question handling** - accepts all questions
- **💾 Chat history** for continued conversations

## 🛠️ Development

### 🔧 Project Setup

1. **📦 Install in development mode:**
   ```bash
   pip install -e .
   ```

2. **🔗 Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### 🆕 Adding New Features

#### 1. New Document Types
Extend the `DocumentLoader` class in `src/utils/document_loader.py`:

```python
def _load_new_format(self, file_path: str) -> List[Any]:
    # Implementation for new document type
    pass
```

#### 2. New UI Components
Add components to `src/ui/ui_components.py`:

```python
class NewUIManager:
    def render_new_component(self):
        # Implementation
        pass
```

#### 3. New LLM Models
Extend `LLMChainBuilder` in `src/llm/llm_chain.py`:

```python
def build_new_chain(self, retriever) -> NewChain:
    # Implementation for new chain type
    pass
```

### 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused

## 🧪 Testing

### 🚀 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_components.py

# Run with coverage
python -m pytest tests/ --cov=src
```

### 📁 Test Structure

- **`tests/test_components.py`**: Tests for individual components
- **`tests/test_database_config.py`**: Database configuration tests
- **`tests/test_docker_db.py`**: Docker database integration tests
- **`tests/test_relevance.py`**: Relevance checker tests

### ✍️ Writing Tests

```python
def test_new_feature():
    """Test description."""
    # Arrange
    component = Component()
    
    # Act
    result = component.method()
    
    # Assert
    assert result == expected_value
```

## 🚀 Deployment

### 🐳 Docker Deployment

1. **🔨 Build the application:**
   ```bash
   docker build -t lecturehub-chatbot .
   ```

2. **🚀 Run with Docker Compose:**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

### 🏭 Production Considerations

- **🔐 Environment Variables**: Use production environment variables
- **🗄️ Database**: Use production PostgreSQL instance
- **🛡️ Security**: Implement proper authentication and authorization
- **📊 Monitoring**: Add logging and monitoring
- **⚖️ Scaling**: Consider load balancing for multiple users

## 🔧 Troubleshooting

### 🚨 Common Issues

#### 1. Database Connection Issues
```bash
# Check database status
./docker/docker-setup.sh status

# View database logs
./docker/docker-setup.sh logs

# Restart database
./docker/docker-setup.sh restart
```

#### 2. LLM API Issues
- Verify `GEMINI_API_KEY` is set correctly (optional)
- Check API quota and limits
- Ensure network connectivity
- **💡 Tip**: Application works with mock LLM without API key

#### 3. Document Loading Issues
- Verify required files exist in `data/lectures/mmceasar2/`
- Check file permissions
- Ensure file formats are supported

#### 4. Import Errors
- Verify Python path includes `src/` directory
- Check that all dependencies are installed
- Ensure `__init__.py` files exist in all packages

### 🐛 Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

### 🆘 Getting Help

1. Check the logs for error messages
2. Verify configuration settings
3. Test individual components
4. Consult the project documentation

## 🔄 Recent Changes

### 🆕 Latest Updates

- **🔄 Migrated from psycopg2 to psycopg**: Updated all database connections
- **🎯 Disabled strict relevance checking**: Chatbot now accepts all questions
- **🤖 Added mock LLM support**: Works without API key for testing
- **🔧 Improved error handling**: Better fallback mechanisms
- **📝 Updated documentation**: Comprehensive guides and examples

### 🎯 Key Improvements

- **✅ No more "Xin lỗi, tôi chỉ hỗ trợ hỏi về bài giảng này thôi." responses**
- **✅ Works without Google API key**
- **✅ Better database compatibility**
- **✅ Enhanced user experience**

## 🤝 Contributing

### 🔄 Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

### 👀 Code Review Process

- All code must pass tests
- Documentation must be updated
- Code style must follow project guidelines
- Security considerations must be addressed

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🆘 Support

For support and questions:
- 📖 Check the documentation
- 🔧 Review the troubleshooting section
- 🐛 Open an issue on GitHub
- 📧 Contact the development team

---

**🎉 Happy coding with LectureHub Chatbot! 🚀**
