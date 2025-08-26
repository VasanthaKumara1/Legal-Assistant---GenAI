// Legal Document Demystification AI - Main JavaScript

class LegalDocumentAnalyzer {
    constructor() {
        this.currentDocument = null;
        this.analysisResults = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileUpload();
    }

    setupEventListeners() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');

        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        analyzeBtn.addEventListener('click', this.analyzeDocument.bind(this));

        // Drag and drop
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', this.handleNavigation.bind(this));
        });

        // Example tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target.getAttribute('onclick');
                if (target) {
                    eval(target);
                }
            });
        });
    }

    setupFileUpload() {
        // Enable drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, this.preventDefaults, false);
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFileSelect({ target: { files } });
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['.pdf', '.docx', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            this.showNotification('Error', `File type ${fileExtension} is not supported. Please use PDF, DOCX, or TXT files.`, 'error');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('Error', 'File is too large. Maximum size is 10MB.', 'error');
            return;
        }

        this.currentDocument = file;
        this.updateUploadUI(file);
        document.getElementById('analyzeBtn').disabled = false;
    }

    updateUploadUI(file) {
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <div class="upload-content">
                <i class="fas fa-file-alt upload-icon" style="color: var(--success-color);"></i>
                <h3>File Selected</h3>
                <p><strong>${file.name}</strong></p>
                <p class="upload-note">Size: ${this.formatFileSize(file.size)}</p>
                <p class="upload-note">Click to select a different file</p>
            </div>
        `;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async analyzeDocument() {
        if (!this.currentDocument) return;

        const documentType = document.getElementById('documentType').value;
        const complexity = document.getElementById('complexity').value;

        this.showLoadingModal();

        try {
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('file', this.currentDocument);
            formData.append('document_type', documentType);
            formData.append('language', 'en');

            // Upload document
            const uploadResponse = await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error(`Upload failed: ${uploadResponse.statusText}`);
            }

            const uploadResult = await uploadResponse.json();
            this.updateProgress(50, 'Analyzing document structure...');

            // Get simplified version
            const simplifyResponse = await fetch(`/api/translation/${uploadResult.document.id}/simplify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    complexity_level: complexity,
                    language: 'en'
                })
            });

            this.updateProgress(75, 'Generating explanations...');

            if (!simplifyResponse.ok) {
                throw new Error(`Simplification failed: ${simplifyResponse.statusText}`);
            }

            const simplifyResult = await simplifyResponse.json();
            this.updateProgress(100, 'Complete!');

            // Store results
            this.analysisResults = {
                document: uploadResult.document,
                analysis: uploadResult.analysis,
                simplified: simplifyResult
            };

            // Show results
            setTimeout(() => {
                this.hideLoadingModal();
                this.showResults();
            }, 1000);

        } catch (error) {
            console.error('Analysis failed:', error);
            this.hideLoadingModal();
            this.showNotification('Error', `Analysis failed: ${error.message}`, 'error');
        }
    }

    showResults() {
        // Hide hero section and show results
        document.querySelector('.hero').style.display = 'none';
        document.getElementById('results').style.display = 'block';

        // Populate results
        this.populateOverview();
        this.populateRiskAssessment();
        this.populateImportantDates();
        this.populateLegalTerms();
        this.populateDocumentContent();

        // Scroll to results
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }

    populateOverview() {
        const overviewContent = document.getElementById('overviewContent');
        const analysis = this.analysisResults.analysis;
        const doc = this.analysisResults.document;

        overviewContent.innerHTML = `
            <div class="overview-item">
                <strong>Document Type:</strong> ${doc.document_type || 'Auto-detected'}
            </div>
            <div class="overview-item">
                <strong>File Size:</strong> ${this.formatFileSize(doc.file_size)}
            </div>
            <div class="overview-item">
                <strong>Complexity:</strong> ${analysis.readability?.complexity_assessment || 'High'}
            </div>
            <div class="overview-item">
                <strong>Reading Level:</strong> ${analysis.readability?.reading_level || 'Graduate level'}
            </div>
            <div class="overview-item">
                <strong>Key Sections:</strong> ${analysis.key_sections?.length || 0} identified
            </div>
        `;
    }

    populateRiskAssessment() {
        const riskContent = document.getElementById('riskContent');
        const risks = this.analysisResults.analysis.risk_assessment;

        let riskHTML = `
            <div class="risk-overview">
                <div class="risk-level risk-${risks.overall_risk || 'medium'}">
                    Overall Risk: ${(risks.overall_risk || 'medium').toUpperCase()}
                </div>
            </div>
        `;

        if (risks.risk_factors && risks.risk_factors.length > 0) {
            riskHTML += '<div class="risk-factors">';
            risks.risk_factors.slice(0, 3).forEach(risk => {
                riskHTML += `
                    <div class="risk-item">
                        <div class="risk-type risk-${risk.risk_level}">${risk.risk_type.replace(/_/g, ' ')}</div>
                        <div class="risk-description">${risk.description}</div>
                    </div>
                `;
            });
            riskHTML += '</div>';
        }

        if (risks.recommendations && risks.recommendations.length > 0) {
            riskHTML += '<div class="recommendations">';
            riskHTML += '<strong>Recommendations:</strong>';
            riskHTML += '<ul>';
            risks.recommendations.slice(0, 3).forEach(rec => {
                riskHTML += `<li>${rec}</li>`;
            });
            riskHTML += '</ul></div>';
        }

        riskContent.innerHTML = riskHTML;
    }

    populateImportantDates() {
        const datesContent = document.getElementById('datesContent');
        const dates = this.analysisResults.analysis.important_dates || [];

        if (dates.length === 0) {
            datesContent.innerHTML = '<p>No specific dates identified in this document.</p>';
            return;
        }

        let datesHTML = '';
        dates.slice(0, 5).forEach(dateItem => {
            datesHTML += `
                <div class="date-item">
                    <div class="date-text"><strong>${dateItem.date_text}</strong></div>
                    <div class="date-context">${dateItem.context}</div>
                </div>
            `;
        });

        datesContent.innerHTML = datesHTML;
    }

    populateLegalTerms() {
        const termsContent = document.getElementById('termsContent');
        const terms = this.analysisResults.analysis.legal_terms || [];

        if (terms.length === 0) {
            termsContent.innerHTML = '<p>No specific legal terms highlighted.</p>';
            return;
        }

        let termsHTML = '';
        terms.slice(0, 5).forEach(termItem => {
            termsHTML += `
                <div class="term-item">
                    <span class="legal-term" onclick="explainTerm('${termItem.term}')">
                        ${termItem.term}
                    </span>
                </div>
            `;
        });

        termsContent.innerHTML = termsHTML;
    }

    populateDocumentContent() {
        const documentContent = document.getElementById('documentContent');
        const simplified = this.analysisResults.simplified;

        documentContent.innerHTML = `
            <div class="document-header">
                <h3>${this.analysisResults.document.title}</h3>
                <div class="complexity-badge">Reading Level: ${simplified.complexity_level.replace('_', ' ')}</div>
            </div>
            
            <div class="document-body">
                <div class="simplified-content">
                    ${this.formatSimplifiedContent(simplified.simplified_content)}
                </div>
                
                <div class="key-points">
                    <h4><i class="fas fa-key"></i> Key Points:</h4>
                    <ul>
                        ${simplified.key_points?.map(point => `<li>${point}</li>`).join('') || '<li>No key points identified</li>'}
                    </ul>
                </div>
                
                ${simplified.rights_obligations ? `
                <div class="rights-obligations">
                    <h4><i class="fas fa-balance-scale"></i> Rights & Obligations:</h4>
                    ${this.formatRightsObligations(simplified.rights_obligations)}
                </div>
                ` : ''}
                
                ${simplified.red_flags && simplified.red_flags.length > 0 ? `
                <div class="red-flags">
                    <h4><i class="fas fa-exclamation-triangle"></i> Red Flags:</h4>
                    <ul>
                        ${simplified.red_flags.map(flag => `<li class="red-flag">${flag}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `;
    }

    formatSimplifiedContent(content) {
        // Add line breaks and basic formatting
        return content.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
    }

    formatRightsObligations(rightsObligations) {
        let html = '';
        
        if (rightsObligations.your_rights) {
            html += '<div class="rights-section"><h5>Your Rights:</h5><ul>';
            rightsObligations.your_rights.forEach(right => {
                html += `<li class="right-item">${right}</li>`;
            });
            html += '</ul></div>';
        }
        
        if (rightsObligations.your_obligations) {
            html += '<div class="obligations-section"><h5>Your Obligations:</h5><ul>';
            rightsObligations.your_obligations.forEach(obligation => {
                html += `<li class="obligation-item">${obligation}</li>`;
            });
            html += '</ul></div>';
        }
        
        return html;
    }

    showLoadingModal() {
        document.getElementById('loadingModal').style.display = 'flex';
        this.updateProgress(10, 'Uploading document...');
    }

    hideLoadingModal() {
        document.getElementById('loadingModal').style.display = 'none';
    }

    updateProgress(percentage, message) {
        document.getElementById('progressFill').style.width = `${percentage}%`;
        document.getElementById('progressText').textContent = message;
    }

    showNotification(title, message, type = 'info') {
        // Simple notification - in production, use a proper notification library
        alert(`${title}: ${message}`);
    }

    handleNavigation(e) {
        e.preventDefault();
        const target = e.target.getAttribute('href');
        
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        e.target.classList.add('active');
        
        // Smooth scroll to section
        if (target && target.startsWith('#')) {
            const section = document.querySelector(target);
            if (section) {
                section.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
}

// Global functions for UI interactions
function showOriginal() {
    document.querySelectorAll('.results-actions .btn-secondary').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show original document content
    const documentContent = document.getElementById('documentContent');
    documentContent.innerHTML = `
        <div class="document-header">
            <h3>Original Document</h3>
            <div class="complexity-badge">Original Legal Text</div>
        </div>
        <div class="document-body">
            <div class="original-content legal-text">
                ${analyzer.currentDocument ? 'Original document content would be displayed here...' : 'No document loaded'}
            </div>
        </div>
    `;
}

function showSimplified() {
    document.querySelectorAll('.results-actions .btn-secondary').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Re-populate simplified content
    if (analyzer.analysisResults) {
        analyzer.populateDocumentContent();
    }
}

function showComparison() {
    document.querySelectorAll('.results-actions .btn-secondary').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show side-by-side comparison
    const documentContent = document.getElementById('documentContent');
    documentContent.innerHTML = `
        <div class="document-header">
            <h3>Original vs Simplified</h3>
        </div>
        <div class="comparison-view">
            <div class="comparison-grid">
                <div class="comparison-card">
                    <h4>Original</h4>
                    <div class="text-content legal-text">
                        Original legal document content would be displayed here...
                    </div>
                </div>
                <div class="comparison-card">
                    <h4>Simplified</h4>
                    <div class="text-content simplified-text">
                        ${analyzer.analysisResults?.simplified?.simplified_content || 'Simplified version would be displayed here...'}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showComplexitySelector() {
    // Simple implementation - in production, use a proper modal
    const newLevel = prompt('Choose complexity level:\n1. Elementary\n2. High School\n3. College\n4. Expert\n\nEnter 1-4:');
    const levels = ['', 'elementary', 'high_school', 'college', 'expert'];
    
    if (newLevel && levels[newLevel]) {
        document.getElementById('complexity').value = levels[newLevel];
    }
}

async function explainTerm(term) {
    try {
        const response = await fetch('/api/terms/lookup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                term: term,
                complexity_level: 'high_school'
            })
        });

        if (!response.ok) {
            throw new Error('Failed to lookup term');
        }

        const result = await response.json();
        showTermModal(term, result);

    } catch (error) {
        console.error('Term lookup failed:', error);
        showTermModal(term, {
            definition: 'Definition not available at this time.',
            simple_definition: 'Please try again later.',
            examples: []
        });
    }
}

function showTermModal(term, definition) {
    document.getElementById('termTitle').textContent = term;
    document.getElementById('termExplanation').innerHTML = `
        <div class="term-definition">
            <h4>Simple Definition:</h4>
            <p>${definition.simple_definition || definition.definition}</p>
        </div>
        
        ${definition.examples && definition.examples.length > 0 ? `
        <div class="term-examples">
            <h4>Examples:</h4>
            <ul>
                ${definition.examples.map(example => `<li>${example}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
        
        <div class="term-confidence">
            <small>Confidence: ${Math.round((definition.confidence_score || 0.8) * 100)}%</small>
        </div>
    `;
    
    document.getElementById('termModal').style.display = 'flex';
}

function closeTermModal() {
    document.getElementById('termModal').style.display = 'none';
}

function showExample(type) {
    // Hide all panels
    document.querySelectorAll('.example-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected panel
    document.getElementById(type).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// Initialize the application
const analyzer = new LegalDocumentAnalyzer();