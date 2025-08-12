# Project Structure

This document describes the refactored project structure for the LectureHub Chatbot.

## Directory Layout

```
lecturehub-chatbot/
├── src/                          # Main source code
│   ├── core/                     # Core application components
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration constants
│   │   ├── main.py              # Main entry point
│   │   └── rag_chatbot.py       # Main RAG chatbot orchestrator
│   ├── database/                 # Database operations
│   │   ├── __init__.py
│   │   ├── database.py          # PostgreSQL and pgvector operations
│   │   └── vectorstore.py       # Vector store management
│   ├── llm/                      # LLM and language processing
│   │   ├── __init__.py
│   │   ├── llm_chain.py         # LLM chain management
│   │   └── keyword_extractor.py # Keyword extraction and relevance
│   ├── ui/                       # User interface components
│   │   ├── __init__.py
│   │   ├── chat_manager.py      # Chat history and interactions
│   │   └── ui_components.py     # UI components and sidebar
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── document_loader.py   # Document loading and processing
│   └── __init__.py
├── tests/                        # Test files
│   ├── test_components.py       # Component tests
│   └── test_database_config.py  # Database configuration tests
├── docs/                         # Documentation
│   ├── README.md                # Main documentation
│   └── PROJECT_STRUCTURE.md     # This file
├── config/                       # Configuration files
│   ├── env.template             # Environment template
│   └── example.env              # Example environment
├── docker/                       # Docker configuration
│   ├── docker-compose.yml       # Docker Compose setup
│   ├── docker-setup.sh          # Docker management script
│   ├── docker.env               # Docker environment
│   └── init.sql                 # Database initialization
├── data/                         # Data files
│   └── lectures/                # Lecture materials
├── main.py                      # Application entry point
├── setup.py                     # Package setup
├── requirements.txt             # Python dependencies
└── .dockerignore               # Docker ignore file
```

## Module Descriptions

### Core (`src/core/`)
- **config.py**: Centralized configuration constants and environment variable loading
- **main.py**: Main application entry point
- **rag_chatbot.py**: Main orchestrator class that coordinates all components

### Database (`src/database/`)
- **database.py**: PostgreSQL connection management and pgvector operations
- **vectorstore.py**: Vector store operations and embedding management

### LLM (`src/llm/`)
- **llm_chain.py**: LLM chain building and QA operations
- **keyword_extractor.py**: Keyword extraction and relevance checking

### UI (`src/ui/`)
- **chat_manager.py**: Chat history management and message processing
- **ui_components.py**: Streamlit UI components and sidebar management

### Utils (`src/utils/`)
- **document_loader.py**: Document loading and processing functionality

## Benefits of This Structure

### 1. **Modularity**
- Each module has a single responsibility
- Clear separation of concerns
- Easy to understand and maintain

### 2. **Scalability**
- Easy to add new features
- Simple to extend existing functionality
- Clear import paths

### 3. **Testability**
- Each module can be tested independently
- Clear test organization
- Easy to mock dependencies

### 4. **Maintainability**
- Logical grouping of related functionality
- Clear naming conventions
- Easy to locate specific functionality

### 5. **Reusability**
- Components can be reused in other projects
- Clear interfaces between modules
- Well-defined dependencies

## Import Patterns

### Internal Imports
```python
# From core to other modules
from ..database import DatabaseManager
from ..llm import LLMChainBuilder
from ..ui import ChatManager

# From other modules to core
from ..core.config import PROBLEM_ID
```

### External Imports
```python
# Standard library
import os
import sys
from typing import Optional

# Third-party
import streamlit as st
from langchain.chains import RetrievalQA
```

## Development Workflow

### Adding New Features
1. Identify the appropriate module for the new feature
2. Create new files in the relevant directory
3. Update `__init__.py` files to export new classes/functions
4. Add tests in the `tests/` directory
5. Update documentation

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_components.py
```

### Running the Application
```bash
# Development
python main.py

# Production
streamlit run main.py
```

## Configuration Management

### Environment Variables
- Use `config/` directory for configuration files
- Load environment variables in `src/core/config.py`
- Use `.env` files for local development

### Docker Configuration
- All Docker-related files in `docker/` directory
- Use `docker.env` for Docker-specific settings
- Manage with `docker-setup.sh` script

## Best Practices

### Code Organization
- Keep related functionality together
- Use clear, descriptive names
- Follow Python naming conventions

### Documentation
- Document all public interfaces
- Keep documentation up to date
- Use type hints for better IDE support

### Testing
- Write tests for all new functionality
- Maintain good test coverage
- Use descriptive test names

### Error Handling
- Use consistent error handling patterns
- Provide meaningful error messages
- Log errors appropriately
