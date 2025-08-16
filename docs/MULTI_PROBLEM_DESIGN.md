# Multi-Problem RAG Chatbot Design

## Tổng quan

Hệ thống đã được thiết kế lại để hỗ trợ **multiple problems** thay vì chỉ một problem cố định. Mỗi problem được tổ chức trong thư mục riêng với các file tài liệu tương ứng.

## Cấu trúc dữ liệu

### Thư mục Problems
```
data/lectures/
├── mmceasar2/
│   ├── mmceasar2.pdf
│   ├── mmceasar2.md
│   └── mmceasar2.py
├── problem2/
│   ├── problem2.pdf
│   ├── problem2.md
│   └── problem2.py
└── problem3/
    ├── problem3.pdf
    ├── problem3.md
    └── problem3.py
```

### Vector Database Structure
- **Collection naming**: `rag_<problem-name>`
- **Metadata filtering**: Mỗi document có `problem_name` trong metadata
- **Isolation**: Mỗi problem có collection riêng biệt

## Thay đổi chính

### 1. Configuration (`src/core/config.py`)
- ✅ Xóa hardcoded `PROBLEM_ID` và `COLLECTION_NAME`
- ✅ Thêm `LECTURES_DIR` constant
- ✅ Thêm functions:
  - `get_available_problems()` - Tìm tất cả problems
  - `get_problem_files(problem_name)` - Lấy files của problem
  - `get_collection_name(problem_name)` - Tạo collection name

### 2. Document Loading (`src/utils/document_loader.py`)
- ✅ Cập nhật `DocumentLoader` để hỗ trợ problem-specific loading
- ✅ Thêm `load_problem_documents(problem_name)` method
- ✅ Cập nhật metadata với `problem_name` thay vì `problem_id`
- ✅ Cập nhật `DocumentProcessor` để hỗ trợ problem_name

### 3. Vector Store (`src/database/vectorstore.py`)
- ✅ Cập nhật `VectorStoreManager` để nhận `problem_name`
- ✅ Tự động tạo collection name từ problem name
- ✅ Thêm filtering theo `problem_name` trong retriever
- ✅ Đảm bảo chỉ trả về documents của problem hiện tại

### 4. Chatbot Logic (`src/core/chatbot_logic.py`)
- ✅ Thêm `current_problem` state
- ✅ Cập nhật tất cả methods để nhận `problem_name` parameter
- ✅ Cập nhật `initialize_system()` để nhận problem_name
- ✅ Cập nhật convenience functions

### 5. UI Components (`src/ui/ui_components.py`)
- ✅ **Xóa Database Configuration section**
- ✅ **Xóa LLM Configuration section**
- ✅ Thêm **Problem Selection section**
- ✅ Hiển thị files trong problem folder
- ✅ Cập nhật title để hiển thị problem name

### 6. Main Application (`src/core/rag_chatbot.py`)
- ✅ Thêm problem switching logic
- ✅ Clear chat history khi switch problem
- ✅ Reset system state khi switch problem
- ✅ Auto-ingest khi chọn problem mới
- ✅ Cập nhật page title và messages

## Workflow

### 1. Problem Detection
```python
# Tự động detect problems từ data/lectures/
problems = get_available_problems()
# Returns: ['mmceasar2', 'problem2', 'problem3']
```

### 2. Problem Selection (UI)
- User chọn problem từ dropdown
- Hiển thị files trong problem folder
- Auto-switch context

### 3. Document Loading
```python
# Load documents cho problem cụ thể
docs = loader.load_problem_documents("mmceasar2")
# Metadata: {"problem_name": "mmceasar2", "file_type": "pdf"}
```

### 4. Vector Store Setup
```python
# Tạo collection riêng cho problem
collection_name = "rag_mmceasar2"
vs = PGVector(collection_name=collection_name)
```

### 5. Retrieval with Filtering
```python
# Chỉ trả về documents của problem hiện tại
retriever = vs.as_retriever()
# Filter: doc.metadata["problem_name"] == current_problem
```

## Lợi ích

### 1. Scalability
- Hỗ trợ unlimited problems
- Mỗi problem isolated
- Dễ dàng thêm/xóa problems

### 2. User Experience
- UI đơn giản hơn (bỏ config phức tạp)
- Auto-detection problems
- Clear context switching

### 3. Performance
- Chỉ load documents cần thiết
- Vector search focused trên problem hiện tại
- Memory efficient

### 4. Maintainability
- Code modular hơn
- Dễ test và debug
- Clear separation of concerns

## Cách sử dụng

### 1. Tạo Problem mới
```bash
# Tạo thư mục problem
mkdir data/lectures/my_problem

# Thêm files
cp lecture.pdf data/lectures/my_problem/
cp notes.md data/lectures/my_problem/
cp code.py data/lectures/my_problem/
```

### 2. Chạy ứng dụng
```bash
streamlit run main.py
```

### 3. Test system
```bash
python test_multi_problem.py
```

## Migration từ Single-Problem

### 1. Cấu trúc dữ liệu
- Move files từ root vào `data/lectures/mmceasar2/`
- Update file paths trong code

### 2. Database
- Old collection: `rag_ma_de_001`
- New collection: `rag_mmceasar2`
- Rebuild vector store với problem name mới

### 3. Configuration
- Remove hardcoded problem references
- Use dynamic problem detection

## Testing

### Test Scripts
- `test_multi_problem.py` - Test toàn bộ system
- `scripts/check_database.py` - Check database state
- `tests/test_docker_db.py` - Test database setup

### Test Cases
1. **Problem Detection**: Tìm tất cả problems
2. **Document Loading**: Load documents cho từng problem
3. **Vector Store**: Setup và query vector store
4. **UI Integration**: Test problem switching
5. **Chat Functionality**: Test chat với từng problem

## Troubleshooting

### Common Issues
1. **No problems found**: Check `data/lectures/` directory
2. **Import errors**: Ensure correct Python path
3. **Database connection**: Check PostgreSQL setup
4. **Vector store errors**: Check pgvector extension

### Debug Commands
```bash
# Check available problems
python -c "from src.core.config import get_available_problems; print(get_available_problems())"

# Test document loading
python test_multi_problem.py

# Check database
python scripts/check_database.py
```
