# Luồng Xử Lý Chatbot RAG

Tài liệu này mô tả logic chính của hệ thống chatbot sử dụng RAG (Retrieval-Augmented Generation) để hỗ trợ học tập.

## Tổng Quan Hệ Thống

Hệ thống chatbot RAG được thiết kế để trả lời câu hỏi dựa trên tài liệu bài giảng được lưu trữ trong cơ sở dữ liệu vector. Hệ thống sử dụng kiến trúc modular với các thành phần chính:

- **Database Layer**: PostgreSQL với pgvector để lưu trữ embeddings
- **Vector Store**: Quản lý và tìm kiếm tài liệu tương tự
- **LLM Chain**: Xử lý câu hỏi và tạo câu trả lời
- **Memory Manager**: Lưu trữ lịch sử hội thoại
- **Document Processor**: Xử lý và chunking tài liệu

## Luồng Khởi Tạo Hệ Thống

```mermaid
flowchart TD
    A[Bắt đầu] --> B[Chọn Problem từ Sidebar]
    B --> C{Problem đã thay đổi?}
    C -->|Có| D[Reset System State]
    C -->|Không| E[Kiểm tra System Status]
    D --> E
    E --> F{System đã khởi tạo?}
    F -->|Không| G[Setup Database]
    F -->|Có| H[Chuyển sang xử lý câu hỏi]
    G --> I[Setup Vector Store]
    I --> J{Vector Store tồn tại?}
    J -->|Có| K[Load từ Database]
    J -->|Không| L[Load và Process Documents]
    L --> M[Ingest vào Vector Store]
    K --> N[Setup Memory Manager]
    M --> N
    N --> O[Setup QA Chain]
    O --> P[System Ready]
    P --> H
```

## Luồng Xử Lý Câu Hỏi

```mermaid
flowchart TD
    A[User Input] --> B[Pre-processing]
    B --> C{Câu chào hỏi?}
    C -->|Có| D[Trả lời chào hỏi]
    C -->|Không| E{Câu hỏi đơn giản?}
    E -->|Có| F[Trả lời đơn giản]
    E -->|Không| G[Thêm vào Memory]
    G --> H[Retrieval từ Vector Store]
    H --> I[Lấy Context Documents]
    I --> J[QA Chain Processing]
    J --> K[Generate Answer]
    K --> L[Thêm Answer vào Memory]
    L --> M[Hiển thị Answer]
    M --> N[Hiển thị Sources]
    D --> O[Kết thúc]
    F --> O
    N --> O
```

## Luồng Ingest Tài Liệu

```mermaid
flowchart TD
    A[Click Ingest Button] --> B[Load Documents từ Problem Folder]
    B --> C{Documents tồn tại?}
    C -->|Không| D[Hiển thị Warning]
    C -->|Có| E[Document Processing]
    E --> F[Chunk Documents]
    F --> G[Generate Embeddings]
    G --> H[Store vào PostgreSQL/pgvector]
    H --> I[Setup Memory Manager]
    I --> J[Setup QA Chain]
    J --> K[Hiển thị Success Message]
    D --> L[Kết thúc]
    K --> L
```

## Kiến Trúc Database

```mermaid
erDiagram
    PROBLEMS {
        string problem_id PK
        string problem_name
        string description
        timestamp created_at
    }

    DOCUMENTS {
        string document_id PK
        string problem_id FK
        string filename
        string content
        timestamp created_at
    }

    EMBEDDINGS {
        string embedding_id PK
        string document_id FK
        vector embedding
        string metadata
        timestamp created_at
    }

    CHAT_HISTORY {
        string message_id PK
        string session_id
        string user_message
        string ai_message
        timestamp created_at
    }

    PROBLEMS ||--o{ DOCUMENTS : contains
    DOCUMENTS ||--o{ EMBEDDINGS : has
```

## Các Thành Phần Chính

### 1. Database Manager
- Quản lý kết nối PostgreSQL
- Đảm bảo schema pgvector được tạo
- Xử lý các thao tác CRUD cơ bản

### 2. Vector Store Manager
- Quản lý embeddings sử dụng HuggingFace
- Tạo và quản lý collections trong pgvector
- Thực hiện similarity search

### 3. LLM Chain Builder
- Tạo ConversationalRetrievalChain với Gemini
- Quản lý prompt templates
- Tích hợp memory vào chain

### 4. Memory Manager
- Lưu trữ lịch sử hội thoại
- Quản lý context window
- Hỗ trợ nhiều loại memory (buffer, window)

### 5. Document Processor
- Load tài liệu từ filesystem
- Chunk documents thành các đoạn nhỏ
- Xử lý metadata

## Luồng Dữ Liệu

```mermaid
flowchart LR
    A[Raw Documents] --> B[Document Loader]
    B --> C[Document Processor]
    C --> D[Chunked Documents]
    D --> E[Embedding Generator]
    E --> F[Vector Store]
    F --> G[Database]

    H[User Question] --> I[Memory Manager]
    I --> J[Vector Search]
    J --> F
    F --> K[Context Documents]
    K --> L[LLM Chain]
    L --> M[Generated Answer]
    M --> I
```

## Xử Lý Lỗi và Fallback

Hệ thống có các cơ chế xử lý lỗi:

1. **Database Connection**: Fallback sang local SQLite nếu PostgreSQL không khả dụng
2. **LLM API**: Hiển thị thông báo lỗi nếu Gemini API không hoạt động
3. **Document Loading**: Warning khi không tìm thấy tài liệu
4. **Vector Store**: Tự động tạo collection mới nếu chưa tồn tại

## Tối Ưu Hóa Hiệu Suất

- **Singleton Pattern**: Sử dụng cho EmbeddingManager và VectorStoreManager
- **Connection Pooling**: Tái sử dụng database connections
- **Memory Management**: Giới hạn context window để tránh memory overflow
- **Caching**: Cache embeddings và vector store instances

## Monitoring và Logging

Hệ thống ghi log các hoạt động chính:
- Database operations
- Document processing
- Vector store operations
- LLM API calls
- Error handling

Logs được lưu trong thư mục `logs/` với format theo ngày tháng.
