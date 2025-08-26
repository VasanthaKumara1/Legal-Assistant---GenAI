# Legal Document Demystification AI

A focused AI solution designed to demystify and simplify complex legal documents. This tool transforms legal jargon into clear, accessible guidance for everyday users.

## 🎯 Core Mission
Transform complex legal documents into clear, actionable guidance that empowers informed decision-making for everyone, regardless of legal background.

## ✨ Key Features

### 1. Legal Jargon Translation Engine
- AI-powered conversion of complex legal language to plain English
- Context-aware explanations that maintain legal accuracy
- Progressive complexity levels (Elementary, High School, College, Expert)
- Industry-specific translations (Consumer, Business, Real Estate, Employment)

### 2. Document Intelligence & Analysis
- Smart document parsing that identifies key sections
- Automatic highlighting of critical clauses and obligations
- Risk assessment with clear explanations
- Timeline extraction (deadlines, renewal dates, key milestones)
- Rights and obligations breakdown for each party

### 3. Interactive Explanation System
- Click-to-explain functionality for any legal term
- Visual decision trees for complex scenarios
- “What does this mean for me?” personalized insights
- Comparison tools for similar document types
- Scenario-based impact analysis

### 4. Accessibility-First Design
- Multiple reading levels (5th grade to professional)
- Audio narration of simplified content (coming soon)
- Visual summaries with icons and infographics
- Multi-language support for immigrant communities (coming soon)
- Screen reader compatibility

## 📄 Supported Document Types
- Consumer contracts (phone, internet, insurance)
- Employment agreements and handbooks
- Rental and lease agreements
- Terms of service and privacy policies
- Healthcare consent forms
- Financial agreements (loans, credit cards)
- Legal notices and court documents

## 🏗️ Repository Structure
```
legal-assistant-genai/
├── legal_assistant/          # Main application package
│   ├── core/                 # Core functionality modules
│   ├── ai/                   # AI/ML processing components
│   ├── parsers/              # Document parsing utilities
│   ├── simplifiers/          # Text simplification engines
│   └── api/                  # API endpoints and routes
├── frontend/                 # User interface components
├── tests/                    # Unit and integration tests
├── docs/                     # Documentation and guides
├── configs/                  # Configuration files
├── notebooks/                # Research and experimentation
├── data/                     # Sample documents and datasets
└── scripts/                  # Utility and deployment scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/VasanthaKumara1/Legal-Assistant---GenAI.git
   cd Legal-Assistant---GenAI
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (optional - for AI features)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if you want full AI functionality
   ```
4. Run the application
   ```bash
   python run.py
   ```
5. Open your browser: http://localhost:8000

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# AI API Keys (optional - for enhanced AI features)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=sqlite:///legal_assistant.db

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### AI Features
- Without AI keys: Rule-based simplification and predefined legal term definitions
- With AI keys: Advanced AI-powered translation, context-aware explanations, and dynamic term definitions

## 📖 Usage

### Web Interface
1. Upload Document: Drag and drop or select your legal document (PDF, DOCX, TXT)
2. Choose Settings: Select document type and reading level
3. Analyze: Click “Analyze Document” to process
4. Review Results: Explore simplified content, risk assessment, and legal terms

### API Usage

Upload Document
```bash
curl -X POST -F "file=@document.pdf" \
     -F "document_type=contract" \
     http://localhost:8000/api/documents/upload
```

Simplify Text
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"complexity_level": "high_school", "language": "en"}' \
     "http://localhost:8000/api/translation/simplify?text=Your legal text here"
```

Look up Legal Term
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"term": "liability", "complexity_level": "high_school"}' \
     http://localhost:8000/api/terms/lookup
```

## 🏗️ Phase 1: Foundation Setup
- [x] Project structure establishment
- [ ] Core document processing
- [ ] Basic AI integration
- [ ] Simple UI/UX interface

## 🛡️ Privacy & Security
- No Data Storage: Documents are processed in memory only
- Local Processing: Core functionality works without external API calls
- Secure Upload: File validation and size limits
- Privacy First: No personal data collection

## ⚖️ Legal Disclaimer
This tool provides simplified explanations for educational purposes only. It is not a substitute for professional legal advice. Always consult with a qualified attorney for legal matters.

## 🤝 Contributing
We welcome contributions! Please see our contributing guidelines for details.

## 📝 License
MIT License

## 🆘 Support
- Documentation: Full API documentation available at `/api/docs` in development
- Issues: Report bugs or request features via GitHub Issues
- Community: Join discussions for help and feedback

---
Making legal documents accessible to everyone. 📚⚖️✨