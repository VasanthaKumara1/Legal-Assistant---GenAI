"""
AI service for legal document simplification using OpenAI GPT.
"""
import time
from typing import Tuple, Optional
from loguru import logger
from backend.config.settings import settings

# Import OpenAI with graceful fallback
try:
    import openai
    import tiktoken
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI libraries not available. AI features will be disabled.")


class AIService:
    """Service for AI-powered legal document simplification."""
    
    def __init__(self):
        """Initialize AI service."""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available - AI features will not work.")
            return
            
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        else:
            logger.warning("OpenAI API key not provided. AI features will not work.")
        
        try:
            self.encoding = tiktoken.encoding_for_model(settings.openai_model)
        except Exception as e:
            logger.warning(f"Could not load tiktoken encoding: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        if not self.encoding:
            return len(text.split())  # Fallback to word count
        return len(self.encoding.encode(text))
    
    async def simplify_legal_text(
        self, 
        legal_text: str, 
        context: Optional[str] = None
    ) -> Tuple[str, int, float]:
        """
        Simplify legal text using OpenAI GPT.
        
        Args:
            legal_text: The legal text to simplify
            context: Optional context to help with simplification
            
        Returns:
            Tuple of (simplified_text, tokens_used, processing_time)
        """
        if not OPENAI_AVAILABLE:
            raise ValueError("OpenAI libraries not available")
            
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        start_time = time.time()
        
        try:
            # Create the prompt for legal text simplification
            prompt = self._create_simplification_prompt(legal_text, context)
            
            logger.info(f"Simplifying legal text ({len(legal_text)} chars)")
            
            # Make API call to OpenAI
            response = await openai.ChatCompletion.acreate(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal expert who specializes in making complex legal documents understandable to ordinary people. Your goal is to simplify legal jargon while preserving the essential meaning and important details."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract the simplified text
            simplified_text = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            processing_time = time.time() - start_time
            
            logger.info(f"AI simplification completed in {processing_time:.2f}s, used {tokens_used} tokens")
            
            return simplified_text, tokens_used, processing_time
            
        except Exception as e:
            logger.error(f"AI simplification failed: {str(e)}")
            raise e
    
    def _create_simplification_prompt(self, legal_text: str, context: Optional[str] = None) -> str:
        """Create a prompt for legal text simplification."""
        
        base_prompt = """Please simplify the following legal text to make it understandable to a general audience. Follow these guidelines:

1. Replace complex legal jargon with simple, everyday language
2. Break down long, complex sentences into shorter, clearer ones
3. Explain legal concepts in plain English
4. Preserve all important information and meaning
5. Maintain the structure and organization of the original text
6. Use bullet points or numbered lists where appropriate for clarity
7. Define any technical terms that must be kept

"""
        
        if context:
            base_prompt += f"Additional context: {context}\n\n"
        
        base_prompt += f"Legal text to simplify:\n\n{legal_text}\n\nSimplified version:"
        
        return base_prompt
    
    async def explain_legal_term(self, term: str, context: Optional[str] = None) -> str:
        """
        Explain a specific legal term in simple language.
        
        Args:
            term: The legal term to explain
            context: Optional context for the explanation
            
        Returns:
            Simple explanation of the legal term
        """
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            prompt = f"Explain the legal term '{term}' in simple, everyday language that a non-lawyer can understand."
            
            if context:
                prompt += f" Context: {context}"
            
            response = await openai.ChatCompletion.acreate(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal expert who explains legal terms in simple, accessible language."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content.strip()
            logger.info(f"Explained legal term: {term}")
            
            return explanation
            
        except Exception as e:
            logger.error(f"Legal term explanation failed: {str(e)}")
            raise e
    
    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is working."""
        if not OPENAI_AVAILABLE:
            return False
            
        if not settings.openai_api_key:
            return False
        
        try:
            # Make a simple API call to test the key
            openai.Model.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {str(e)}")
            return False


# Global AI service instance
ai_service = AIService()