"""
Legal terms lookup and explanation endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List

from app.models.pydantic_models import TermLookupRequest, LegalTermResponse
from app.services.translation_service import LegalTermsDatabase

router = APIRouter()
terms_database = LegalTermsDatabase()


@router.post("/lookup")
async def lookup_term(request: TermLookupRequest):
    """
    Look up and explain a legal term.
    
    Provides definitions at different complexity levels with examples.
    """
    try:
        result = await terms_database.explain_term(
            term=request.term,
            complexity_level=request.complexity_level,
            context=request.context
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Term lookup failed: {str(e)}"
        )


@router.get("/common")
async def get_common_terms():
    """Get a list of commonly used legal terms with simple explanations."""
    return {
        "common_legal_terms": [
            {
                "term": "Liability",
                "simple_definition": "Being responsible when something goes wrong",
                "category": "responsibility"
            },
            {
                "term": "Indemnify",
                "simple_definition": "Pay for any damage or losses you cause",
                "category": "financial"
            },
            {
                "term": "Arbitration",
                "simple_definition": "Having someone else decide your dispute instead of going to court",
                "category": "dispute_resolution"
            },
            {
                "term": "Force Majeure",
                "simple_definition": "Events beyond anyone's control that make contracts impossible to complete",
                "category": "circumstances"
            },
            {
                "term": "Breach",
                "simple_definition": "Breaking the rules or terms of an agreement",
                "category": "violation"
            },
            {
                "term": "Waiver",
                "simple_definition": "Giving up a right or claim",
                "category": "rights"
            },
            {
                "term": "Severability",
                "simple_definition": "If one part of the contract is invalid, the rest still applies",
                "category": "contract_structure"
            },
            {
                "term": "Governing Law",
                "simple_definition": "Which state or country's laws apply to this agreement",
                "category": "jurisdiction"
            }
        ],
        "categories": [
            "responsibility",
            "financial", 
            "dispute_resolution",
            "circumstances",
            "violation",
            "rights",
            "contract_structure",
            "jurisdiction"
        ]
    }


@router.get("/glossary/{document_type}")
async def get_document_type_glossary(document_type: str):
    """Get legal terms specific to a document type."""
    glossaries = {
        "employment": [
            {
                "term": "At-will employment",
                "definition": "Employment that can be ended by either party at any time without cause",
                "importance": "high"
            },
            {
                "term": "Non-compete clause",
                "definition": "Agreement not to work for competitors for a certain time",
                "importance": "high"
            },
            {
                "term": "Vesting",
                "definition": "When you earn the right to keep benefits like stock options",
                "importance": "medium"
            }
        ],
        "lease": [
            {
                "term": "Security deposit",
                "definition": "Money paid upfront to cover potential damages",
                "importance": "high"
            },
            {
                "term": "Subletting",
                "definition": "Renting your rented space to someone else",
                "importance": "medium"
            },
            {
                "term": "Lease term",
                "definition": "How long the rental agreement lasts",
                "importance": "high"
            }
        ],
        "contract": [
            {
                "term": "Consideration",
                "definition": "Something of value exchanged between parties",
                "importance": "high"
            },
            {
                "term": "Material breach",
                "definition": "A serious violation that defeats the contract's purpose",
                "importance": "high"
            },
            {
                "term": "Assignment",
                "definition": "Transferring your contract rights to someone else",
                "importance": "medium"
            }
        ]
    }
    
    if document_type not in glossaries:
        raise HTTPException(
            status_code=404,
            detail=f"Glossary for document type '{document_type}' not found"
        )
    
    return {
        "document_type": document_type,
        "terms": glossaries[document_type]
    }


@router.get("/search")
async def search_terms(query: str, limit: int = 10):
    """Search for legal terms by name or definition."""
    # In a real app, this would search a comprehensive legal terms database
    
    sample_results = [
        {
            "term": "Liability",
            "simple_definition": "Being responsible when something goes wrong",
            "relevance_score": 0.95
        },
        {
            "term": "Limited Liability",
            "simple_definition": "Having only some responsibility, not unlimited",
            "relevance_score": 0.85
        }
    ]
    
    # Filter based on query (simple demo implementation)
    filtered_results = [
        term for term in sample_results 
        if query.lower() in term["term"].lower() or query.lower() in term["simple_definition"].lower()
    ]
    
    return {
        "query": query,
        "results": filtered_results[:limit],
        "total_found": len(filtered_results)
    }


@router.get("/red-flags")
async def get_legal_red_flags():
    """Get common legal red flags to watch out for."""
    return {
        "red_flags": [
            {
                "category": "Financial Risk",
                "flags": [
                    {
                        "term": "Unlimited liability",
                        "warning": "You could be responsible for all damages, no matter how large",
                        "what_to_do": "Look for liability caps or limitations"
                    },
                    {
                        "term": "Liquidated damages",
                        "warning": "Pre-set penalties that you'll pay if you break the agreement",
                        "what_to_do": "Make sure the penalty amounts are reasonable"
                    }
                ]
            },
            {
                "category": "Rights and Control",
                "flags": [
                    {
                        "term": "Waiver of rights",
                        "warning": "You're giving up important legal protections",
                        "what_to_do": "Understand exactly what rights you're losing"
                    },
                    {
                        "term": "Automatic renewal",
                        "warning": "Contract continues without your active choice",
                        "what_to_do": "Set calendar reminders before renewal dates"
                    }
                ]
            },
            {
                "category": "Dispute Resolution",
                "flags": [
                    {
                        "term": "Binding arbitration",
                        "warning": "You cannot take disputes to court",
                        "what_to_do": "Understand the arbitration process and costs"
                    },
                    {
                        "term": "Attorney fee shifting",
                        "warning": "You might have to pay the other party's lawyer costs",
                        "what_to_do": "Consider if you can afford this risk"
                    }
                ]
            }
        ]
    }


@router.post("/explain-multiple")
async def explain_multiple_terms(
    terms: List[str],
    complexity_level: str = "high_school",
    context: Optional[str] = None
):
    """Explain multiple legal terms at once."""
    try:
        explanations = []
        
        for term in terms[:10]:  # Limit to 10 terms
            result = await terms_database.explain_term(
                term=term,
                complexity_level=complexity_level,
                context=context
            )
            explanations.append(result)
        
        return {
            "terms_explained": len(explanations),
            "complexity_level": complexity_level,
            "explanations": explanations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multiple term explanation failed: {str(e)}"
        )