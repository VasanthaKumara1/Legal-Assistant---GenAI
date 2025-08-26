
# Legal Assistant GenAI

An enhanced AI-powered legal assistant with advanced features including multi-model AI integration, real-time collaboration, advanced OCR, and comprehensive security.

## 🚀 Features

### Core Capabilities
- **Multi-Model AI Integration** - Leverage GPT-4, Claude-3, and Llama models simultaneously
- **Advanced OCR & Document Processing** - Extract text, tables, and signatures with high accuracy
- **Real-time Collaboration** - Live document editing, comments, and annotations
- **Enhanced Security** - MFA, RBAC, audit trails, and end-to-end encryption
- **Advanced Analytics** - Risk scoring, negotiation tracking, and predictive analytics
- **Integration Ecosystem** - DocuSign, Microsoft 365, Google Workspace connectors
- **Voice Integration** - Voice commands and audio document summarization
- **Mobile-First Design** - Progressive Web App with offline capabilities

### AI-Powered Analysis
- Contract risk assessment with visual heatmaps
- Clause extraction and comparison
- Compliance checking (GDPR, CCPA, SOC 2)
- Legal precedent matching
- Negotiation timeline tracking
- Predictive contract outcome modeling

### Security & Compliance
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)
- Blockchain-style immutable audit logs
- End-to-end document encryption
- GDPR/CCPA compliance features
- SOC 2 Type II controls

## 🏗️ Architecture

### Backend Services
- **FastAPI** - High-performance async API server
- **PostgreSQL** - Primary database with advanced indexing
- **Redis** - Caching and real-time session management
- **WebSocket** - Real-time collaboration support
- **Celery** - Background task processing

### Frontend
- **Streamlit** - Interactive web application
- **React Components** - Real-time collaboration UI
- **Progressive Web App** - Mobile-optimized experience
- **WebSocket Client** - Live updates and collaboration

### AI/ML Services
- **OpenAI GPT-4** - Advanced language understanding
- **Anthropic Claude** - Detailed reasoning and safety
- **Meta Llama** - Open-source alternative
- **Custom Orchestration** - Multi-model consensus and confidence scoring

### External Integrations
- **DocuSign** - E-signature workflows
- **Microsoft 365** - Document sync and Teams notifications
- **Google Workspace** - Drive sync and collaborative editing
- **OCR Services** - Google Vision API, Azure Form Recognizer

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/VasanthaKumara1/Legal-Assistant---GenAI.git
cd Legal-Assistant---GenAI
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Monitoring: http://localhost:3000 (Grafana)

### Manual Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start the backend**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Start the frontend**
```bash
streamlit run frontend/streamlit_app.py
```

## 📋 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `POST /auth/enable-mfa` - Enable multi-factor authentication

### Document Processing
- `POST /documents/upload` - Upload legal documents
- `POST /documents/analyze` - AI-powered document analysis
- `GET /documents/{id}/risk-score` - Contract risk assessment
- `POST /documents/{id}/extract-tables` - Advanced table extraction
- `POST /documents/{id}/detect-signatures` - Signature detection

### Real-time Collaboration
- `WebSocket /ws/collaborate/{document_id}` - Live collaboration
- `GET /collaboration/{id}/users` - Get active collaborators

### Analytics & Insights
- `GET /analytics/dashboard` - Comprehensive analytics dashboard
- `GET /analytics/risk-heatmap` - Risk assessment visualizations
- `GET /analytics/negotiation-timeline/{id}` - Track negotiation progress
- `POST /analytics/find-precedents` - Legal precedent matching
- `POST /analytics/predictive` - Predictive contract analytics

### External Integrations
- `POST /integrations/docusign/send` - Send to DocuSign for e-signature
- `POST /integrations/microsoft365/sync` - Sync with Microsoft 365
- `POST /integrations/google-workspace/sync` - Sync with Google Workspace
- `POST /integrations/webhook` - Configure webhook notifications

### Voice Integration
- `POST /voice/command` - Process voice commands

### Security & Compliance
- `GET /security/audit-logs` - Access audit trail
- `GET /security/events` - Security event monitoring

## 🔧 Configuration

### Environment Variables

Key configuration options:

```bash
# Core Application
DEBUG=false
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
LLAMA_API_KEY=your-llama-key

# External Integrations
DOCUSIGN_INTEGRATION_KEY=your-docusign-key
MICROSOFT_CLIENT_ID=your-microsoft-app-id
GOOGLE_CLIENT_ID=your-google-client-id

# Security
ACCESS_TOKEN_EXPIRE_HOURS=24
AUDIT_LOG_RETENTION_DAYS=2555
```

See `.env.example` for complete configuration options.

## 🚀 Deployment

### Kubernetes Deployment

1. **Apply Kubernetes manifests**
```bash
kubectl apply -f k8s/deployment.yaml
```

2. **Configure secrets**
```bash
kubectl create secret generic legal-assistant-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="your-secret-key" \
  --from-literal=openai-api-key="your-openai-key"
```

### Docker Production Deployment

1. **Build production images**
```bash
docker build -t legal-assistant-genai:latest .
docker build -f Dockerfile.frontend -t legal-assistant-frontend:latest .
```

2. **Deploy with production compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Multi-factor authentication (TOTP)
- Role-based access control (Admin, Lawyer, Paralegal, Client, Viewer)
- Session management with Redis

### Data Protection
- End-to-end encryption for sensitive documents
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- Secure key management and rotation

### Compliance & Auditing
- Immutable audit trail with blockchain-style logging
- GDPR/CCPA compliance features
- SOC 2 Type II controls
- Automated compliance reporting

### Security Monitoring
- Real-time security event detection
- Rate limiting and DDoS protection
- Intrusion detection and alerting
- Vulnerability scanning integration

## 📊 Monitoring & Observability

### Metrics & Monitoring
- Prometheus metrics collection
- Grafana dashboards
- Application performance monitoring
- Custom business metrics

### Logging
- Structured logging with correlation IDs
- Centralized log aggregation
- Error tracking with Sentry
- Audit log retention policies

### Health Checks
- Application health endpoints
- Database connectivity checks
- External service health monitoring
- Automated failover capabilities

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Coverage report
pytest --cov=app tests/
```

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - Service integration testing
- **Security Tests** - Authentication and authorization
- **Performance Tests** - Load and stress testing
- **API Tests** - REST API endpoint validation

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
- Automated testing on push/PR
- Security scanning (CodeQL, Snyk)
- Docker image building and scanning
- Automated deployment to staging
- Production deployment with approval

### Quality Gates
- Code coverage minimum 80%
- Security vulnerability scanning
- Performance benchmark validation
- API contract testing

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run the test suite
6. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use type hints throughout
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation as needed

### Pull Request Process
1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Request review from maintainers
5. Address review feedback

## 📈 Roadmap

### Phase 2.0 - Advanced AI Features
- Custom fine-tuned legal models
- Advanced contract negotiation AI
- Automated compliance monitoring
- Enhanced predictive analytics

### Phase 2.1 - Enterprise Features
- Advanced workflow automation
- Custom integration marketplace
- White-label solutions
- Advanced reporting and dashboards

### Phase 2.2 - Global Expansion
- Multi-language support expansion
- International legal frameworks
- Regional compliance modules
- Localized AI models

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment.md)

### Community
- [GitHub Issues](https://github.com/VasanthaKumara1/Legal-Assistant---GenAI/issues)
- [Discussions](https://github.com/VasanthaKumara1/Legal-Assistant---GenAI/discussions)
- [Discord Server](https://discord.gg/legal-assistant)

### Enterprise Support
For enterprise support, custom integrations, and professional services, contact: support@legal-assistant-genai.com

---

**Built with ❤️ for the legal community**

*Empowering lawyers, paralegals, and legal professionals with AI-driven insights and collaborative tools.*

# Legal Document Demystification AI

## 🎯 **Core Mission**
Transform complex legal documents into clear, accessible guidance that empowers informed decision-making for everyone, regardless of legal background.

## 📋 **Project Overview**
This AI-powered solution demystifies legal jargon by converting complex legal language into plain English, making legal documents accessible to everyday users.

### **Primary Focus Areas:**
1. **Legal Jargon Translation Engine** - AI-powered conversion to plain English
2. **Document Intelligence & Analysis** - Smart parsing and risk assessment  
3. **Interactive Explanation System** - Click-to-explain functionality
4. **Accessibility-First Design** - Multiple reading levels and multi-language support

## 🏗️ **Project Structure**
```
legal-assistant-genai/
├── legal_assistant/          # Main application package
│   ├── core/                # Core functionality modules
│   ├── ai/                  # AI/ML processing components
│   ├── parsers/             # Document parsing utilities
│   ├── simplifiers/         # Text simplification engines
│   └── api/                 # API endpoints and routes
├── frontend/                # User interface components
├── tests/                   # Unit and integration tests
├── docs/                    # Documentation and guides
├── configs/                 # Configuration files
├── notebooks/               # Research and experimentation
├── data/                    # Sample documents and datasets
└── scripts/                 # Utility and deployment scripts
```

## 🚀 **Phase 1: Foundation Setup**
- [x] Project structure establishment
- [ ] Core document processing
- [ ] Basic AI integration
- [ ] Simple UI/UX interface

## 🛠️ **Setup Instructions**
```bash
# Clone the repository
git clone https://github.com/VasanthaKumara1/Legal-Assistant---GenAI.git
cd Legal-Assistant---GenAI

# Install dependencies
pip install -r requirements.txt

# Run the application (coming soon)
# python -m legal_assistant.app
```

## 📝 **Target Document Types**
- Consumer contracts (phone, internet, insurance)
- Employment agreements and handbooks
- Rental and lease agreements
- Terms of service and privacy policies
- Healthcare consent forms
- Financial agreements (loans, credit cards)

## 🎯 **Success Metrics**
- User comprehension improvement
- Time reduction in document review
- User confidence increase in legal decisions
- Accuracy validation by legal professionals

## 📄 **License**
MIT License

## 🤝 **Contributing**
Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

---
*Making legal documents understandable for everyone, one document at a time.*
