# Development Guide

## Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Basic Setup (Minimal Dependencies)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Legal-Assistant---GenAI
   pip install fastapi uvicorn pydantic-settings sqlalchemy loguru streamlit requests
   ```

2. **Start the application**:
   ```bash
   ./start.sh
   ```

3. **Access the application**:
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend UI: http://localhost:8501

### Full Setup (All Features)

1. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils libmagic1
   
   # macOS
   brew install tesseract poppler libmagic
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Start the application**:
   ```bash
   ./start.sh
   ```

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload Document
```bash
curl -X POST -F "file=@your_document.txt" http://localhost:8000/documents/upload
```

### Process Document
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"document_id": 1, "process_ocr": true, "process_ai": true}' \
  http://localhost:8000/documents/1/process
```

### Get Document Content
```bash
curl http://localhost:8000/documents/1/content
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │     OpenAI      │
│   Frontend      │────│    Backend      │────│     GPT-4       │
│  (Port 8501)    │    │  (Port 8000)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Tesseract     │
                       │      OCR        │
                       └─────────────────┘
```

## Available Features by Dependencies

| Feature | Dependencies | Status |
|---------|-------------|---------|
| Text file upload/processing | ✅ Core dependencies | Always available |
| PDF text extraction | PyPDF2 | Optional |
| PDF OCR processing | pdf2image, Tesseract | Optional |
| DOCX processing | python-docx | Optional |
| Image OCR | Pillow, pytesseract | Optional |
| AI simplification | openai, tiktoken | Optional |
| MIME type detection | python-magic | Optional (fallback available) |

## Development Commands

### Run Backend Only
```bash
cd backend
python -m uvicorn main:app --reload
```

### Run Frontend Only
```bash
cd frontend
streamlit run app.py
```

### Run Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
isort .
flake8 .
```

## Docker Development

### Build and Run
```bash
docker-compose up --build
```

### Backend Only
```bash
docker build -t legal-assistant-backend .
docker run -p 8000:8000 legal-assistant-backend
```

## Troubleshooting

### Common Issues

1. **OpenAI API not working**:
   - Check if OpenAI API key is set in `.env`
   - Verify API key has sufficient credits
   - Check `/ai/status` endpoint

2. **OCR not working**:
   - Install Tesseract: `sudo apt-get install tesseract-ocr`
   - Install Python packages: `pip install pytesseract pdf2image`

3. **Document processing fails**:
   - Check file size limits (10MB default)
   - Verify file format is supported
   - Check logs in `logs/app.log`

### Logs

Application logs are available in:
- Console output (when running directly)
- `logs/app.log` (file logging)

### Database

The application uses SQLite by default:
- Database file: `legal_assistant.db`
- Tables: `documents`, `processing_logs`

## API Endpoints

### Documents
- `POST /documents/upload` - Upload document
- `POST /documents/{id}/process` - Process document
- `GET /documents/{id}/content` - Get document content
- `GET /documents/{id}/status` - Get processing status
- `GET /documents/` - List all documents

### AI
- `POST /ai/simplify` - Simplify text directly
- `POST /ai/explain-term` - Explain legal term
- `GET /ai/status` - Check AI service status

### System
- `GET /health` - Health check
- `GET /info` - Application information