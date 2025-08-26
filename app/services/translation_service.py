"""
Legal jargon translation engine using multiple AI models.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import AI libraries only if available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class LegalTranslationEngine:
    """AI-powered legal jargon translation engine."""
    
    def __init__(self):
        # Initialize AI clients only if API keys are available and libraries are installed
        self.openai_client = None
        self.anthropic_client = None
        
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        if ANTHROPIC_AVAILABLE and settings.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
        
        # Complexity level prompts
        self.complexity_prompts = {
            "elementary": "Explain this like you're talking to a 5th grader. Use simple words and short sentences.",
            "high_school": "Explain this in plain English that a high school student would understand.",
            "college": "Provide a clear explanation with some technical detail, suitable for a college-level reader.",
            "expert": "Provide a comprehensive explanation maintaining legal precision while improving clarity."
        }
    
    async def translate_legal_text(
        self, 
        text: str, 
        complexity_level: str = "high_school",
        context: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Translate legal text to specified complexity level.
        
        Args:
            text: Legal text to translate
            complexity_level: Target complexity level
            context: Additional context about the document
            document_type: Type of document (contract, lease, etc.)
            
        Returns:
            Dictionary with simplified text and metadata
        """
        try:
            # Build context-aware prompt
            system_prompt = self._build_system_prompt(complexity_level, document_type)
            user_prompt = self._build_user_prompt(text, context)
            
            # Try multiple models for best result
            results = []
            
            if self.openai_client:
                openai_result = await self._translate_with_openai(system_prompt, user_prompt)
                if openai_result:
                    results.append(openai_result)
            
            if self.anthropic_client:
                anthropic_result = await self._translate_with_anthropic(system_prompt, user_prompt)
                if anthropic_result:
                    results.append(anthropic_result)
            
            # Return best result or fallback
            if results:
                return self._select_best_translation(results, text)
            else:
                return self._fallback_translation(text, complexity_level)
                
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return self._fallback_translation(text, complexity_level)
    
    def _build_system_prompt(self, complexity_level: str, document_type: Optional[str]) -> str:
        """Build system prompt for translation."""
        base_prompt = f"""You are a legal expert specializing in making legal documents accessible to everyone.

Your task is to translate complex legal language into clear, understandable text while maintaining accuracy.

Complexity Level: {self.complexity_prompts.get(complexity_level, self.complexity_prompts['high_school'])}

Guidelines:
1. Maintain legal accuracy - never change the meaning
2. Replace legal jargon with everyday terms
3. Break down complex sentences into shorter ones
4. Explain obligations and rights clearly
5. Highlight important deadlines and consequences
6. Point out potential risks or red flags
7. Use active voice when possible
8. Provide specific examples when helpful

"""
        
        if document_type:
            base_prompt += f"Document Type: {document_type}\n"
            base_prompt += self._get_document_specific_guidance(document_type)
        
        base_prompt += """
Response Format (JSON):
{
    "simplified_text": "The simplified version of the legal text",
    "key_points": ["bullet point 1", "bullet point 2"],
    "what_it_means": "What this means for the reader in practical terms",
    "red_flags": ["potential issue 1", "potential issue 2"],
    "confidence_score": 0.85,
    "legal_terms_used": [{"term": "legal term", "definition": "simple definition"}]
}
"""
        return base_prompt
    
    def _build_user_prompt(self, text: str, context: Optional[str]) -> str:
        """Build user prompt with text and context."""
        prompt = f"Please simplify this legal text:\n\n{text}"
        
        if context:
            prompt += f"\n\nAdditional Context: {context}"
        
        return prompt
    
    def _get_document_specific_guidance(self, document_type: str) -> str:
        """Get document type specific guidance."""
        guidance = {
            "contract": "Focus on obligations, payment terms, cancellation rights, and penalties.",
            "lease": "Emphasize rent, deposits, maintenance responsibilities, and termination conditions.",
            "employment": "Highlight job duties, compensation, benefits, termination clauses, and non-compete terms.",
            "privacy_policy": "Explain data collection, usage, sharing, and user rights clearly.",
            "terms_of_service": "Focus on user rights, restrictions, liability, and account termination.",
            "insurance": "Clarify coverage, exclusions, deductibles, and claim procedures.",
            "loan": "Emphasize interest rates, payment schedules, penalties, and default consequences."
        }
        
        return guidance.get(document_type, "Focus on key obligations, rights, and important terms.")
    
    async def _translate_with_openai(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """Translate using OpenAI GPT."""
        if not self.openai_client:
            return None
            
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.LEGAL_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["model_used"] = "openai-gpt"
            return result
            
        except Exception as e:
            logger.error(f"OpenAI translation failed: {str(e)}")
            return None
    
    async def _translate_with_anthropic(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """Translate using Anthropic Claude."""
        if not self.anthropic_client:
            return None
            
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            result = json.loads(response.content[0].text)
            result["model_used"] = "anthropic-claude"
            return result
            
        except Exception as e:
            logger.error(f"Anthropic translation failed: {str(e)}")
            return None
    
    def _select_best_translation(self, results: List[Dict], original_text: str) -> Dict:
        """Select the best translation from multiple results."""
        # For now, select based on confidence score
        # In production, could use more sophisticated selection criteria
        best_result = max(results, key=lambda x: x.get("confidence_score", 0))
        
        # Add metadata
        best_result["translation_timestamp"] = datetime.utcnow().isoformat()
        best_result["alternatives_count"] = len(results) - 1
        
        return best_result
    
    def _fallback_translation(self, text: str, complexity_level: str) -> Dict:
        """Fallback translation when AI models are unavailable."""
        return {
            "simplified_text": text,  # Return original text
            "key_points": ["Unable to process with AI - original text preserved"],
            "what_it_means": "AI translation service temporarily unavailable. Please review the original text or try again later.",
            "red_flags": [],
            "confidence_score": 0.0,
            "legal_terms_used": [],
            "model_used": "fallback",
            "translation_timestamp": datetime.utcnow().isoformat()
        }


class LegalTermsDatabase:
    """Legal terms definition and explanation service."""
    
    def __init__(self):
        self.translation_engine = LegalTranslationEngine()
        
        # Common legal terms with definitions
        self.common_terms = {
            "indemnify": {
                "definition": "To compensate someone for harm or loss",
                "simple": "Pay for any damage or losses you cause",
                "example": "If you break something, you'll pay to fix it"
            },
            "liability": {
                "definition": "Legal responsibility for something",
                "simple": "Being responsible when something goes wrong",
                "example": "If you cause an accident, you're liable for the damages"
            },
            "arbitration": {
                "definition": "Settling disputes outside of court with a neutral party",
                "simple": "Having someone else decide your dispute instead of going to court",
                "example": "Instead of suing, you both agree to let a mediator decide"
            },
            "force majeure": {
                "definition": "Unforeseeable circumstances preventing contract fulfillment",
                "simple": "Events beyond anyone's control that make contracts impossible to complete",
                "example": "Natural disasters, wars, or pandemics that stop business"
            }
        }
    
    async def explain_term(self, term: str, complexity_level: str = "high_school", context: str = None) -> Dict:
        """Explain a legal term at the specified complexity level."""
        term_lower = term.lower()
        
        # Check if we have a predefined definition
        if term_lower in self.common_terms:
            base_info = self.common_terms[term_lower]
            
            # Use AI to adjust complexity if needed
            if complexity_level != "high_school":
                enhanced = await self.translation_engine.translate_legal_text(
                    f"Legal term: {term}\nDefinition: {base_info['definition']}\nExample: {base_info['example']}",
                    complexity_level=complexity_level,
                    context=context
                )
                
                return {
                    "term": term,
                    "definition": enhanced.get("simplified_text", base_info["simple"]),
                    "simple_definition": base_info["simple"],
                    "examples": [base_info["example"]],
                    "confidence_score": enhanced.get("confidence_score", 0.8),
                    "source": "database_enhanced"
                }
            
            return {
                "term": term,
                "definition": base_info["definition"],
                "simple_definition": base_info["simple"],
                "examples": [base_info["example"]],
                "confidence_score": 0.9,
                "source": "database"
            }
        
        # Use AI to define unknown terms
        definition_prompt = f"Define the legal term '{term}' and provide a simple explanation and example."
        if context:
            definition_prompt += f" Context: {context}"
        
        result = await self.translation_engine.translate_legal_text(
            definition_prompt,
            complexity_level=complexity_level,
            context=context
        )
        
        return {
            "term": term,
            "definition": result.get("simplified_text", f"Definition for '{term}' not found"),
            "simple_definition": result.get("what_it_means", ""),
            "examples": result.get("key_points", []),
            "confidence_score": result.get("confidence_score", 0.5),
            "source": "ai_generated"
        }