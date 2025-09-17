# ⚖️ Legal Assistant GenAI - Deployment Ready

A working AI-powered legal document assistant that simplifies complex legal jargon into plain, understandable language.

## 🎉 **DEPLOYMENT STATUS: READY** ✅

This application is now fully deployable with **4 core working features**:

### ✨ **Core Features**

1. **🏥 Health Check** - System monitoring and status
2. **📄 Document Upload** - Upload and process legal documents  
3. **🤖 Text Simplification** - AI-powered legal jargon simplification
4. **🎨 Web Interface** - User-friendly Streamlit frontend

## 🚀 **Quick Start (Recommended)**

```bash
# Clone and run
git clone https://github.com/VasanthaKumara1/Legal-Assistant---GenAI.git
cd Legal-Assistant---GenAI
./deploy.sh
```

The deployment script will:
- Install all dependencies
- Start backend API on http://localhost:8000
- Start frontend UI on http://localhost:8501
- Provide API documentation at http://localhost:8000/docs

## 🔧 **Manual Deployment**

### Prerequisites
- Python 3.8+
- pip package manager

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn python-multipart openai python-dotenv aiofiles streamlit requests
```

### Step 2: Start Backend API
```bash
uvicorn app.main_clean:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Start Frontend (New Terminal)
```bash
streamlit run frontend_clean.py --server.port 8501 --server.address 0.0.0.0
```

## 📊 **Testing the Deployment**

### Backend API Tests
```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/api/info

# Text simplification
curl -X POST "http://localhost:8000/api/simplify" \
  -H "Content-Type: application/json" \
  -d '{"text": "The party shall heretofore be known as the licensee", "reading_level": "elementary"}'

# Document upload
curl -X POST "http://localhost:8000/api/upload" -F "file=@your_document.txt"
```

### Frontend UI Features
1. Navigate to http://localhost:8501
2. Test "Direct Text Simplification" mode
3. Test "Document Upload & Processing" mode
4. Try different reading levels (elementary, high_school, college)

## 🔑 **Optional: OpenAI Integration**

For enhanced AI features, add your OpenAI API key to `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Note:** The app works perfectly in "mock mode" without an API key, providing simplified text using built-in transformations.

## 📁 **Key Files**

- `app/main_clean.py` - Main FastAPI backend application
- `frontend_clean.py` - Streamlit frontend interface
- `deploy.sh` - One-click deployment script
- `.env` - Environment configuration

## 🌐 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and system status |
| `/api/info` | GET | Application information |
| `/api/simplify` | POST | Simplify legal text |
| `/api/upload` | POST | Upload document |
| `/api/process/{file_id}` | GET | Process uploaded document |
| `/docs` | GET | Interactive API documentation |

## 🎯 **Use Cases**

- **Document Simplification**: Upload legal documents and get plain English versions
- **Text Processing**: Directly simplify legal jargon in real-time  
- **Educational Tool**: Help students understand complex legal language
- **Accessibility**: Make legal documents accessible to general public

## 🔄 **Deployment Verification**

✅ **Backend Running**: http://localhost:8000/health returns status "healthy"  
✅ **Frontend Running**: http://localhost:8501 shows AI Legal Assistant interface  
✅ **Text Simplification**: Successfully converts legal jargon to plain English  
✅ **Document Upload**: Accepts and processes TXT, PDF, DOCX files  
✅ **API Documentation**: Interactive docs available at /docs  

## 🛠️ **Troubleshooting**

### Backend Issues
- Check if port 8000 is available
- Verify Python dependencies are installed
- Check logs for error messages

### Frontend Issues  
- Check if port 8501 is available
- Ensure backend is running first
- Verify Streamlit is properly installed

### File Upload Issues
- Check `uploads/` directory exists and is writable
- Verify file types are supported (.txt, .pdf, .docx, .doc)
- Check file size limits (10MB max)

## 📈 **Production Deployment**

For production deployment:

1. **Security**: Configure CORS origins in `.env`
2. **SSL**: Use reverse proxy (nginx) with SSL certificates
3. **Database**: Consider PostgreSQL for production data
4. **Monitoring**: Add logging and error tracking
5. **Scaling**: Use Docker containers and orchestration

## 🤝 **Contributing**

The application is now in a deployable state with core functionality working. Future enhancements could include:

- Advanced document parsing (PDF, Word)
- Multiple AI model support
- User authentication
- Document history and management
- Advanced legal term glossary

---

**Status**: ✅ **DEPLOYMENT READY** - All core features tested and working!