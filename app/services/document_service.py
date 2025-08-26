"""
Document parsing and intelligence analysis service.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Import optional dependencies
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

from app.services.translation_service import LegalTranslationEngine
from app.core.config import settings

logger = logging.getLogger(__name__)

# Download required NLTK data
if NLTK_AVAILABLE:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass


class DocumentAnalysisService:
    """Service for analyzing and parsing legal documents."""
    
    def __init__(self):
        self.translation_engine = LegalTranslationEngine()
        
        # Load spaCy model for NLP
        try:
            if SPACY_AVAILABLE:
                self.nlp = spacy.load("en_core_web_sm")
            else:
                self.nlp = None
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Legal document patterns
        self.section_patterns = {
            "definitions": r"(?i)(definitions?|defined terms?)",
            "obligations": r"(?i)(obligations?|duties|responsibilities|shall|must)",
            "rights": r"(?i)(rights?|entitled|may|authorized)",
            "termination": r"(?i)(termination|terminate|end|expir|cancel)",
            "payment": r"(?i)(payment|fee|cost|charge|price|amount)",
            "liability": r"(?i)(liability|liable|responsible|damages)",
            "dispute": r"(?i)(dispute|arbitration|litigation|court|legal action)",
            "privacy": r"(?i)(privacy|confidential|personal information|data)",
            "intellectual_property": r"(?i)(intellectual property|copyright|trademark|patent)",
            "force_majeure": r"(?i)(force majeure|act of god|unforeseeable)"
        }
        
        # Risk indicators
        self.risk_patterns = {
            "automatic_renewal": r"(?i)(automatic|auto).{0,50}(renew|extend)",
            "penalty_clauses": r"(?i)(penalty|fine|liquidated damages)",
            "broad_liability": r"(?i)(unlimited liability|all damages|any loss)",
            "indemnification": r"(?i)(indemnif|hold harmless)",
            "waiver_of_rights": r"(?i)(waive|waiver).{0,30}(right|claim)",
            "binding_arbitration": r"(?i)(binding arbitration|mandatory arbitration)",
            "choice_of_law": r"(?i)(governed by|choice of law|applicable law)",
            "attorney_fees": r"(?i)(attorney.{0,10}fee|legal fee|court cost)"
        }
        
        # Important date patterns
        self.date_patterns = [
            r"(?i)(due|expires?|expiration|deadline|by|before|within)\s+(\d{1,2}\/\d{1,2}\/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})",
            r"(?i)(\d{1,2})\s+(days?|weeks?|months?|years?)\s+(from|after|before)",
            r"(?i)(annually|monthly|quarterly|weekly)\s+(on|by)"
        ]
    
    async def analyze_document(self, content: str, document_type: Optional[str] = None) -> Dict:
        """
        Perform comprehensive document analysis.
        
        Args:
            content: Document text content
            document_type: Type of document for specialized analysis
            
        Returns:
            Complete analysis results
        """
        try:
            analysis_results = {
                "document_structure": await self._analyze_structure(content),
                "readability": self._analyze_readability(content),
                "key_sections": await self._identify_key_sections(content, document_type),
                "risk_assessment": await self._assess_risks(content),
                "important_dates": self._extract_dates(content),
                "legal_terms": await self._extract_legal_terms(content),
                "summary": await self._generate_summary(content, document_type),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            return self._fallback_analysis(content)
    
    async def _analyze_structure(self, content: str) -> Dict:
        """Analyze document structure and organization."""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(content)
            word_count = len(word_tokenize(content))
        else:
            # Simple fallback
            sentences = content.split('.')
            word_count = len(content.split())
        
        paragraphs = content.split('\n\n')
        
        # Basic structure analysis
        structure = {
            "total_characters": len(content),
            "total_words": word_count,
            "total_sentences": len(sentences),
            "total_paragraphs": len([p for p in paragraphs if p.strip()]),
            "average_sentence_length": word_count / len(sentences) if sentences else 0,
            "average_paragraph_length": word_count / len([p for p in paragraphs if p.strip()]) if paragraphs else 0
        }
        
        # Identify potential headers/sections
        potential_headers = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line.isupper() or re.match(r'^\d+\.', line) or re.match(r'^[A-Z][^a-z]*$', line)):
                potential_headers.append(line)
        
        structure["potential_sections"] = potential_headers[:10]  # Limit to first 10
        
        return structure
    
    def _analyze_readability(self, content: str) -> Dict:
        """Analyze document readability metrics."""
        try:
            if TEXTSTAT_AVAILABLE:
                flesch_score = flesch_reading_ease(content)
                fk_grade = flesch_kincaid_grade(content)
            else:
                # Simple fallback based on sentence and word length
                sentences = content.split('.')
                words = content.split()
                avg_sentence_length = len(words) / len(sentences) if sentences else 0
                
                # Rough estimation
                if avg_sentence_length < 10:
                    flesch_score = 80
                    fk_grade = 6
                elif avg_sentence_length < 20:
                    flesch_score = 60
                    fk_grade = 10
                else:
                    flesch_score = 30
                    fk_grade = 14
            
            # Determine reading level
            if flesch_score >= 90:
                reading_level = "Very Easy (5th grade)"
            elif flesch_score >= 80:
                reading_level = "Easy (6th grade)"
            elif flesch_score >= 70:
                reading_level = "Fairly Easy (7th grade)"
            elif flesch_score >= 60:
                reading_level = "Standard (8th-9th grade)"
            elif flesch_score >= 50:
                reading_level = "Fairly Difficult (10th-12th grade)"
            elif flesch_score >= 30:
                reading_level = "Difficult (College level)"
            else:
                reading_level = "Very Difficult (Graduate level)"
            
            return {
                "flesch_reading_ease": flesch_score,
                "flesch_kincaid_grade": fk_grade,
                "reading_level": reading_level,
                "complexity_assessment": "High" if flesch_score < 50 else "Medium" if flesch_score < 70 else "Low"
            }
        except Exception as e:
            logger.error(f"Readability analysis failed: {str(e)}")
            return {
                "flesch_reading_ease": 0,
                "flesch_kincaid_grade": 12,
                "reading_level": "Unknown",
                "complexity_assessment": "High"
            }
    
    async def _identify_key_sections(self, content: str, document_type: Optional[str]) -> List[Dict]:
        """Identify key sections in the document."""
        sections = []
        
        # Find sections based on patterns
        for section_type, pattern in self.section_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                start_pos = match.start()
                
                # Extract context around the match
                context_start = max(0, start_pos - 200)
                context_end = min(len(content), start_pos + 500)
                context = content[context_start:context_end]
                
                # Determine importance based on section type and document type
                importance = self._assess_section_importance(section_type, document_type)
                
                sections.append({
                    "section_type": section_type,
                    "content": context.strip(),
                    "start_position": start_pos,
                    "importance_level": importance,
                    "match_text": match.group()
                })
        
        # Sort by position and limit results
        sections.sort(key=lambda x: x["start_position"])
        return sections[:20]  # Limit to top 20 sections
    
    def _assess_section_importance(self, section_type: str, document_type: Optional[str]) -> str:
        """Assess the importance of a section based on type and document context."""
        high_importance = ["obligations", "termination", "payment", "liability"]
        medium_importance = ["rights", "dispute", "definitions"]
        
        # Document-specific importance adjustments
        if document_type == "employment":
            if section_type in ["obligations", "termination", "payment"]:
                return "critical"
        elif document_type == "lease":
            if section_type in ["payment", "termination", "obligations"]:
                return "critical"
        elif document_type == "privacy_policy":
            if section_type in ["privacy", "rights"]:
                return "critical"
        
        if section_type in high_importance:
            return "high"
        elif section_type in medium_importance:
            return "medium"
        else:
            return "low"
    
    async def _assess_risks(self, content: str) -> Dict:
        """Assess potential risks in the document."""
        risks = []
        risk_score = 0
        
        for risk_type, pattern in self.risk_patterns.items():
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            if matches:
                risk_level = self._calculate_risk_level(risk_type, len(matches))
                risk_score += risk_level
                
                for match in matches[:3]:  # Limit to first 3 matches per type
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(content), match.end() + 100)
                    context = content[context_start:context_end]
                    
                    risks.append({
                        "risk_type": risk_type,
                        "risk_level": "high" if risk_level >= 3 else "medium" if risk_level >= 2 else "low",
                        "description": self._get_risk_description(risk_type),
                        "context": context.strip(),
                        "position": match.start()
                    })
        
        # Overall risk assessment
        if risk_score >= 15:
            overall_risk = "high"
        elif risk_score >= 8:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        return {
            "overall_risk": overall_risk,
            "risk_score": risk_score,
            "risk_factors": risks,
            "recommendations": self._generate_risk_recommendations(risks)
        }
    
    def _calculate_risk_level(self, risk_type: str, occurrence_count: int) -> int:
        """Calculate risk level based on type and frequency."""
        high_risk_types = ["broad_liability", "waiver_of_rights", "binding_arbitration"]
        medium_risk_types = ["automatic_renewal", "penalty_clauses", "indemnification"]
        
        base_score = 3 if risk_type in high_risk_types else 2 if risk_type in medium_risk_types else 1
        return min(base_score + occurrence_count - 1, 5)
    
    def _get_risk_description(self, risk_type: str) -> str:
        """Get human-readable description for risk types."""
        descriptions = {
            "automatic_renewal": "Contract may automatically renew without notice",
            "penalty_clauses": "Contains penalty or fine provisions",
            "broad_liability": "Broad or unlimited liability exposure",
            "indemnification": "Requires you to pay for others' losses",
            "waiver_of_rights": "You may be giving up important rights",
            "binding_arbitration": "Disputes must be resolved through arbitration",
            "choice_of_law": "Different state/country laws may apply",
            "attorney_fees": "You may have to pay the other party's legal costs"
        }
        return descriptions.get(risk_type, "Potential risk identified")
    
    def _generate_risk_recommendations(self, risks: List[Dict]) -> List[str]:
        """Generate recommendations based on identified risks."""
        recommendations = []
        
        risk_types = [risk["risk_type"] for risk in risks]
        
        if "broad_liability" in risk_types:
            recommendations.append("Consider negotiating liability caps or limitations")
        
        if "automatic_renewal" in risk_types:
            recommendations.append("Set calendar reminders before renewal dates")
        
        if "binding_arbitration" in risk_types:
            recommendations.append("Understand that you cannot take disputes to court")
        
        if "waiver_of_rights" in risk_types:
            recommendations.append("Carefully review what rights you're giving up")
        
        if len(risks) > 5:
            recommendations.append("Consider having a lawyer review this document")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _extract_dates(self, content: str) -> List[Dict]:
        """Extract important dates and deadlines."""
        dates = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                context = content[context_start:context_end]
                
                dates.append({
                    "date_text": match.group(),
                    "context": context.strip(),
                    "position": match.start(),
                    "type": "deadline"  # Could be enhanced to classify date types
                })
        
        # Sort by position and limit results
        dates.sort(key=lambda x: x["position"])
        return dates[:10]
    
    async def _extract_legal_terms(self, content: str) -> List[Dict]:
        """Extract and explain legal terms found in the document."""
        # Common legal terms to look for
        legal_terms = [
            "indemnify", "indemnification", "liability", "arbitration", "force majeure",
            "liquidated damages", "breach", "default", "waiver", "severability",
            "intellectual property", "confidentiality", "non-disclosure", "governing law",
            "jurisdiction", "covenant", "warranty", "representations", "assignment"
        ]
        
        found_terms = []
        
        for term in legal_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                context_start = max(0, match.start() - 100)
                context_end = min(len(content), match.end() + 100)
                context = content[context_start:context_end]
                
                found_terms.append({
                    "term": match.group(),
                    "context": context.strip(),
                    "position": match.start()
                })
                break  # Only capture first occurrence of each term
        
        return found_terms[:15]  # Limit to 15 terms
    
    async def _generate_summary(self, content: str, document_type: Optional[str]) -> Dict:
        """Generate an AI-powered summary of the document."""
        try:
            # Create summary prompt based on document type
            summary_prompt = f"Provide a brief summary of this legal document"
            if document_type:
                summary_prompt += f" ({document_type})"
            summary_prompt += ". Focus on key obligations, rights, and important terms."
            
            # Use first 2000 characters for summary to avoid token limits
            content_preview = content[:2000] + "..." if len(content) > 2000 else content
            
            summary_result = await self.translation_engine.translate_legal_text(
                content_preview,
                complexity_level="high_school",
                context=summary_prompt
            )
            
            return {
                "brief_summary": summary_result.get("simplified_text", "Summary not available"),
                "key_points": summary_result.get("key_points", []),
                "main_parties": self._identify_parties(content),
                "document_purpose": self._infer_document_purpose(content, document_type),
                "confidence_score": summary_result.get("confidence_score", 0.7)
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return {
                "brief_summary": "Summary generation temporarily unavailable",
                "key_points": [],
                "main_parties": [],
                "document_purpose": "Unknown",
                "confidence_score": 0.0
            }
    
    def _identify_parties(self, content: str) -> List[str]:
        """Identify the main parties in the document."""
        # Simple party identification - could be enhanced with NER
        party_patterns = [
            r"(?i)(company|corporation|llc|inc\.?|ltd\.?)",
            r"(?i)(client|customer|user|member|tenant|employee|contractor)"
        ]
        
        parties = []
        for pattern in party_patterns:
            matches = re.findall(pattern, content[:1000])  # Check first 1000 chars
            parties.extend(matches[:2])  # Limit to 2 per pattern
        
        return list(set(parties))[:5]  # Remove duplicates and limit
    
    def _infer_document_purpose(self, content: str, document_type: Optional[str]) -> str:
        """Infer the main purpose of the document."""
        if document_type:
            purposes = {
                "contract": "Establish contractual relationship and obligations",
                "lease": "Rental agreement for property",
                "employment": "Define employment terms and conditions",
                "privacy_policy": "Explain data collection and usage practices",
                "terms_of_service": "Set rules for using a service or platform",
                "insurance": "Provide insurance coverage terms",
                "loan": "Define loan terms and repayment conditions"
            }
            return purposes.get(document_type, "Legal agreement")
        
        # Infer from content
        if re.search(r"(?i)(rent|lease|premises|landlord|tenant)", content):
            return "Property rental agreement"
        elif re.search(r"(?i)(employ|job|salary|wage|benefits)", content):
            return "Employment agreement"
        elif re.search(r"(?i)(privacy|data|personal information)", content):
            return "Privacy policy"
        else:
            return "Legal agreement"
    
    def _fallback_analysis(self, content: str) -> Dict:
        """Provide fallback analysis when AI services fail."""
        return {
            "document_structure": {
                "total_characters": len(content),
                "total_words": len(content.split()),
                "analysis_note": "Basic structure analysis only"
            },
            "readability": {
                "complexity_assessment": "Unknown",
                "analysis_note": "Readability analysis unavailable"
            },
            "key_sections": [],
            "risk_assessment": {
                "overall_risk": "unknown",
                "analysis_note": "Risk assessment unavailable"
            },
            "important_dates": [],
            "legal_terms": [],
            "summary": {
                "brief_summary": "Document analysis temporarily unavailable",
                "analysis_note": "Please try again later"
            },
            "analysis_timestamp": datetime.utcnow().isoformat()
        }