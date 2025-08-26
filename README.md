# AI Legal Assistant 🏛️⚖️

An AI-powered legal document assistant that simplifies complex legal jargon into plain, understandable language. Built with FastAPI, Streamlit, and OpenAI GPT-4.

## 🌟 Features

- **📄 Document Upload**: Support for PDF, Word documents, text files, and images
- **🔍 OCR Processing**: Extract text from scanned documents and images using Tesseract
- **🤖 AI Simplification**: Convert legal jargon to plain English using OpenAI GPT-4
- **👁️ Dual View Interface**: Side-by-side comparison of original and simplified text
- **🚀 FastAPI Backend**: RESTful API with automatic documentation
- **🎨 Streamlit Frontend**: User-friendly web interface
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │     OpenAI      │
│   Frontend      │────│    Backend      │────│     GPT-4       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Tesseract     │
                       │      OCR        │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- Tesseract OCR (installed automatically with Docker)

## 🚀 Quick Start

### Option 1: Using the Startup Script (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/VasanthaKumara1/Legal-Assistant---GenAI.git
   cd Legal-Assistant---GenAI
   ```

2. **Run the startup script**
   ```bash
   ./start.sh
   ```

3. **Configure your API key**
   - The script will create a `.env` file from `.env.example`
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

4. **Access the application**
   - Frontend UI: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR**
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

5. **Start frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run app.py
   ```

### Option 3: Using Docker

1. **Build and run with Docker Compose**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   docker-compose up --build
   ```

2. **Access the application**
   - Frontend: http://localhost:8501
   - Backend: http://localhost:8000

## 📚 Usage

### Document Processing Workflow

1. **Upload Document**
   - Navigate to the Streamlit frontend at http://localhost:8501
   - Upload a PDF, Word document, text file, or image
   - The system will automatically extract text using OCR

2. **AI Simplification**
   - The system will process the extracted text with OpenAI GPT-4
   - View the original and simplified versions side-by-side

3. **Direct Text Simplification**
   - Alternatively, paste legal text directly for immediate simplification
   - No file upload required

### API Usage

The FastAPI backend provides RESTful endpoints:

```python
import requests

# Upload document
files = {'file': open('legal_document.pdf', 'rb')}
response = requests.post('http://localhost:8000/documents/upload', files=files)
document_id = response.json()['id']

# Process document
data = {'document_id': document_id, 'process_ocr': True, 'process_ai': True}
requests.post(f'http://localhost:8000/documents/{document_id}/process', json=data)

# Get results
content = requests.get(f'http://localhost:8000/documents/{document_id}/content')
print(content.json())
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required for AI features) | None |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4 |
| `MAX_TOKENS` | Maximum tokens for AI responses | 1500 |
| `TEMPERATURE` | AI creativity (0.0-1.0) | 0.3 |
| `MAX_FILE_SIZE` | Maximum upload file size in bytes | 10MB |
| `UPLOAD_DIRECTORY` | Directory for uploaded files | uploads |
| `DATABASE_URL` | SQLite database URL | sqlite:///./legal_assistant.db |
| `LOG_LEVEL` | Logging level | INFO |

### Supported File Types

- **PDF**: .pdf
- **Word Documents**: .docx, .doc
- **Text Files**: .txt
- **Images**: .png, .jpg, .jpeg

## 🔧 Development

### Project Structure

```
Legal-Assistant---GenAI/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config/
│   │   └── settings.py      # Configuration settings
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── documents.py     # Document endpoints
│   │   └── ai.py           # AI endpoints
│   ├── services/
│   │   ├── ocr_service.py   # OCR processing
│   │   ├── ai_service.py    # AI text simplification
│   │   └── document_service.py # Document processing pipeline
│   └── utils/
│       └── file_utils.py    # File handling utilities
├── frontend/
│   ├── __init__.py
│   └── app.py              # Streamlit application
├── shared/
│   ├── models/             # Shared data models
│   └── utils/              # Shared utilities
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── start.sh              # Startup script
└── README.md             # This file
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

## 📖 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Key Endpoints

- `POST /documents/upload` - Upload a document
- `POST /documents/{id}/process` - Process document with OCR and AI
- `GET /documents/{id}/content` - Get original and simplified content
- `POST /ai/simplify` - Directly simplify text
- `GET /health` - Health check

## 🔐 Security Considerations

- Store your OpenAI API key securely in the `.env` file
- The `.env` file is gitignored to prevent accidental exposure
- Consider using environment-specific API keys for development/production
- Uploaded files are stored locally - implement cloud storage for production

## 🚀 Deployment

### Production Deployment

1. **Set up environment variables**
2. **Use a production WSGI server** (already configured with uvicorn)
3. **Set up reverse proxy** (nginx recommended)
4. **Configure HTTPS**
5. **Set up monitoring and logging**

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the logs in the `logs/` directory
3. Ensure your OpenAI API key is valid and has sufficient credits
4. Verify Tesseract OCR is properly installed

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Streamlit](https://streamlit.io/) - Beautiful web apps for ML/AI
- [OpenAI](https://openai.com/) - AI language models
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [SQLAlchemy](https://sqlalchemy.org/) - Database toolkit