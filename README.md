# Legal Document Demystification AI

A focused AI solution specifically designed for demystifying and simplifying complex legal documents. This tool transforms legal jargon into clear, accessible guidance for everyday users.

## 🎯 Core Mission: Legal Document Demystification

Transform any legal document into clear, actionable guidance that empowers informed decision-making for everyone, regardless of legal background.

## ✨ Key Features

### 1. **Legal Jargon Translation Engine**
- AI-powered conversion of complex legal language to plain English
- Context-aware explanations that maintain legal accuracy
- Progressive complexity levels (Elementary, High School, College, Expert)
- Industry-specific translations (Consumer, Business, Real Estate, Employment)

### 2. **Document Intelligence & Analysis**
- Smart document parsing that identifies key sections
- Automatic highlighting of critical clauses and obligations
- Risk assessment with clear explanations
- Timeline extraction (deadlines, renewal dates, key milestones)
- Rights and obligations breakdown for each party

### 3. **Interactive Explanation System**
- Click-to-explain functionality for any legal term
- Visual decision trees for complex scenarios
- "What does this mean for me?" personalized insights
- Comparison tools for similar document types
- Scenario-based impact analysis

### 4. **Accessibility-First Design**
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

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/VasanthaKumara1/Legal-Assistant---GenAI.git
   cd Legal-Assistant---GenAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional - for AI features)
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys if you want full AI functionality
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Visit `http://localhost:8000` to access the Legal Document Demystification AI

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

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

The application works without AI API keys but provides enhanced functionality when configured:

- **Without AI keys**: Uses rule-based simplification and predefined legal term definitions
- **With AI keys**: Provides advanced AI-powered translation, context-aware explanations, and dynamic term definitions

## 📖 Usage

### Web Interface

1. **Upload Document**: Drag and drop or select your legal document (PDF, DOCX, TXT)
2. **Choose Settings**: Select document type and reading level
3. **Analyze**: Click "Analyze Document" to process
4. **Review Results**: Explore simplified content, risk assessment, and legal terms

### API Usage

The application provides a RESTful API for programmatic access:

#### Upload Document
```bash
curl -X POST -F "file=@document.pdf" \
     -F "document_type=contract" \
     http://localhost:8000/api/documents/upload
```

#### Simplify Text
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"complexity_level": "high_school", "language": "en"}' \
     http://localhost:8000/api/translation/simplify?text="Your legal text here"
```

#### Look up Legal Term
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"term": "liability", "complexity_level": "high_school"}' \
     http://localhost:8000/api/terms/lookup
```

## 🏗️ Architecture

### Backend Services
- **FastAPI**: Modern, fast web framework for building APIs
- **Document Analysis**: Smart parsing and structure analysis
- **AI Translation**: Multi-model pipeline for legal simplification
- **Legal Knowledge**: Built-in legal terms database

### Frontend Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive UI**: Click-to-explain legal terms
- **Progressive Disclosure**: Summary → details → full text
- **Accessibility**: Screen reader compatible, multiple reading levels

### AI/ML Pipeline
- **Multi-Model Support**: OpenAI GPT, Anthropic Claude
- **Legal Domain**: Fine-tuned for legal document processing
- **Confidence Scoring**: Quality assessment for translations
- **Fallback System**: Works without AI dependencies

## 🛡️ Privacy & Security

- **No Data Storage**: Documents are processed in memory only
- **Local Processing**: Core functionality works without external API calls
- **Secure Upload**: File validation and size limits
- **Privacy First**: No personal data collection

## ⚖️ Legal Disclaimer

**Important**: This tool provides simplified explanations for educational purposes only. It is not a substitute for professional legal advice. Always consult with a qualified attorney for legal matters.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Full API documentation available at `/api/docs` when running in development mode
- **Issues**: Report bugs or request features via GitHub Issues
- **Community**: Join our discussions for help and feedback

---

**Making legal documents accessible to everyone.** 📚⚖️✨