"""
Analytics Service - Advanced Analytics Dashboard
Provides contract risk scoring, negotiation timeline tracking, and predictive analytics
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np

from app.models.schemas import (
    AnalyticsDashboard, DocumentMetrics, UserActivity,
    DocumentType, RiskLevel
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Advanced analytics service for legal documents and user activity"""
    
    def __init__(self):
        # Mock data storage (use database in production)
        self.document_analytics = {}
        self.user_analytics = {}
        self.risk_trends = {}
        self.negotiation_timelines = {}
        self.contract_precedents = {}
        
    async def get_dashboard_data(self, user_id: str, time_period: str = "30_days") -> AnalyticsDashboard:
        """Get comprehensive analytics dashboard data"""
        try:
            # Calculate time range
            end_date = datetime.utcnow()
            if time_period == "7_days":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30_days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90_days":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=365)
            
            # Generate document metrics
            document_metrics = await self._calculate_document_metrics(user_id, start_date, end_date)
            
            # Generate user activity metrics
            user_activity = await self._calculate_user_activity(user_id, start_date, end_date)
            
            # Generate risk trends
            risk_trends = await self._calculate_risk_trends(user_id, start_date, end_date)
            
            # Generate collaboration stats
            collaboration_stats = await self._calculate_collaboration_stats(user_id, start_date, end_date)
            
            return AnalyticsDashboard(
                user_id=user_id,
                time_period=time_period,
                document_metrics=document_metrics,
                user_activity=user_activity,
                risk_trends=risk_trends,
                collaboration_stats=collaboration_stats,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            raise
    
    async def _calculate_document_metrics(self, user_id: str, 
                                        start_date: datetime, 
                                        end_date: datetime) -> DocumentMetrics:
        """Calculate document processing metrics"""
        
        # Mock data - in production, query from database
        total_documents = 156
        documents_by_type = {
            DocumentType.CONTRACT: 45,
            DocumentType.AGREEMENT: 32,
            DocumentType.TERMS_OF_SERVICE: 28,
            DocumentType.PRIVACY_POLICY: 21,
            DocumentType.LEGAL_BRIEF: 18,
            DocumentType.COMPLIANCE_DOCUMENT: 12
        }
        
        # Calculate processing times
        processing_times = [2.3, 1.8, 3.2, 2.1, 4.5, 1.9, 2.7, 3.1, 2.0, 2.8]
        average_processing_time = sum(processing_times) / len(processing_times)
        
        # Calculate success rate
        successful_processes = 153
        success_rate = successful_processes / total_documents
        
        return DocumentMetrics(
            total_documents=total_documents,
            documents_by_type=documents_by_type,
            average_processing_time=average_processing_time,
            success_rate=success_rate
        )
    
    async def _calculate_user_activity(self, user_id: str,
                                     start_date: datetime,
                                     end_date: datetime) -> UserActivity:
        """Calculate user activity metrics"""
        
        # Mock data - in production, query from database
        documents_processed = 23
        time_spent = 42.5  # hours
        most_used_features = [
            "Document Analysis",
            "Risk Assessment", 
            "Clause Extraction",
            "Real-time Collaboration",
            "AI Multi-model Analysis"
        ]
        collaboration_events = 87
        
        return UserActivity(
            documents_processed=documents_processed,
            time_spent=time_spent,
            most_used_features=most_used_features,
            collaboration_events=collaboration_events
        )
    
    async def _calculate_risk_trends(self, user_id: str,
                                   start_date: datetime,
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """Calculate risk assessment trends"""
        
        # Generate mock trend data
        days = (end_date - start_date).days
        risk_trends = []
        
        for i in range(min(days, 30)):  # Last 30 days max
            date = start_date + timedelta(days=i)
            
            # Simulate risk scores with some variation
            base_risk = 65
            variation = np.sin(i * 0.2) * 10 + np.random.normal(0, 5)
            risk_score = max(0, min(100, base_risk + variation))
            
            # Simulate document counts
            documents_analyzed = max(0, int(np.random.poisson(3)))
            
            risk_trends.append({
                "date": date.isoformat(),
                "average_risk_score": round(risk_score, 1),
                "documents_analyzed": documents_analyzed,
                "high_risk_documents": int(documents_analyzed * 0.2) if risk_score > 70 else 0,
                "medium_risk_documents": int(documents_analyzed * 0.5),
                "low_risk_documents": int(documents_analyzed * 0.3)
            })
        
        return risk_trends
    
    async def _calculate_collaboration_stats(self, user_id: str,
                                           start_date: datetime,
                                           end_date: datetime) -> Dict[str, Any]:
        """Calculate collaboration statistics"""
        
        # Mock collaboration data
        collaboration_stats = {
            "total_sessions": 45,
            "active_collaborators": 8,
            "documents_shared": 23,
            "comments_added": 156,
            "annotations_created": 89,
            "average_session_duration": 35.2,  # minutes
            "most_collaborative_documents": [
                {"document": "Service_Agreement_2024.docx", "sessions": 12},
                {"document": "Master_Contract_Template.pdf", "sessions": 8},
                {"document": "Employment_Agreement_Draft.docx", "sessions": 6}
            ],
            "collaboration_by_day": self._generate_collaboration_timeline(start_date, end_date)
        }
        
        return collaboration_stats
    
    def _generate_collaboration_timeline(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate collaboration activity timeline"""
        timeline = []
        days = min((end_date - start_date).days, 30)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            
            # Simulate collaboration activity (higher on weekdays)
            day_of_week = date.weekday()
            base_activity = 8 if day_of_week < 5 else 3  # Weekday vs weekend
            
            sessions = max(0, int(np.random.poisson(base_activity)))
            comments = max(0, int(np.random.poisson(base_activity * 2)))
            
            timeline.append({
                "date": date.isoformat(),
                "collaboration_sessions": sessions,
                "comments_added": comments,
                "unique_collaborators": min(sessions, 5)
            })
        
        return timeline
    
    async def calculate_contract_risk_heatmap(self, documents: List[str]) -> Dict[str, Any]:
        """Generate risk assessment heatmap for contracts"""
        
        # Mock risk categories and scores
        risk_categories = [
            "Financial Risk",
            "Legal Compliance", 
            "Operational Risk",
            "Intellectual Property",
            "Data Privacy",
            "Termination Clauses",
            "Liability Exposure",
            "Force Majeure"
        ]
        
        document_risks = {}
        
        for doc in documents:
            doc_risks = {}
            for category in risk_categories:
                # Generate realistic risk scores
                base_risk = np.random.uniform(20, 80)
                doc_risks[category] = round(base_risk, 1)
            
            document_risks[doc] = doc_risks
        
        # Calculate average risks per category
        category_averages = {}
        for category in risk_categories:
            scores = [doc_risks[category] for doc_risks in document_risks.values()]
            category_averages[category] = round(sum(scores) / len(scores), 1)
        
        return {
            "document_risks": document_risks,
            "category_averages": category_averages,
            "overall_risk_score": round(sum(category_averages.values()) / len(category_averages), 1),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def track_negotiation_timeline(self, contract_id: str) -> Dict[str, Any]:
        """Track and analyze contract negotiation timeline"""
        
        # Mock negotiation phases
        phases = [
            {
                "phase": "Initial Draft",
                "start_date": "2024-01-01T10:00:00",
                "end_date": "2024-01-03T17:00:00",
                "duration_hours": 55,
                "status": "completed",
                "key_activities": ["Document creation", "Initial review", "Stakeholder input"],
                "participants": ["legal_team", "business_team"]
            },
            {
                "phase": "First Review",
                "start_date": "2024-01-04T09:00:00", 
                "end_date": "2024-01-07T16:00:00",
                "duration_hours": 79,
                "status": "completed",
                "key_activities": ["Risk assessment", "Clause analysis", "Compliance check"],
                "participants": ["legal_team", "compliance_team", "client"]
            },
            {
                "phase": "Negotiations",
                "start_date": "2024-01-08T10:00:00",
                "end_date": "2024-01-16T18:00:00",
                "duration_hours": 192,
                "status": "completed",
                "key_activities": ["Terms negotiation", "Risk mitigation", "Compromise discussions"],
                "participants": ["legal_team", "client", "counterparty"]
            },
            {
                "phase": "Revisions",
                "start_date": "2024-01-17T09:00:00",
                "end_date": "2024-01-22T15:00:00",
                "duration_hours": 126,
                "status": "completed",
                "key_activities": ["Document updates", "Final reviews", "Approval process"],
                "participants": ["legal_team", "business_team"]
            },
            {
                "phase": "Final Review",
                "start_date": "2024-01-23T10:00:00",
                "end_date": "2024-01-25T14:00:00",
                "duration_hours": 52,
                "status": "in_progress",
                "key_activities": ["Final approval", "Signature preparation"],
                "participants": ["legal_team", "executives"]
            }
        ]
        
        # Calculate metrics
        total_duration = sum(phase["duration_hours"] for phase in phases if phase["status"] == "completed")
        completed_phases = len([p for p in phases if p["status"] == "completed"])
        
        return {
            "contract_id": contract_id,
            "phases": phases,
            "total_duration_hours": total_duration,
            "completed_phases": completed_phases,
            "total_phases": len(phases),
            "progress_percentage": round((completed_phases / len(phases)) * 100, 1),
            "estimated_completion": "2024-01-26T17:00:00",
            "critical_path": ["Negotiations", "Revisions"],
            "bottlenecks": ["Stakeholder availability", "Counterparty response time"]
        }
    
    async def find_contract_precedents(self, contract_text: str, contract_type: str) -> List[Dict[str, Any]]:
        """Find similar contracts and legal precedents"""
        
        # Mock precedent data
        precedents = [
            {
                "precedent_id": "PREC_001",
                "case_name": "Tech Corp v. Software Solutions Inc.",
                "similarity_score": 0.87,
                "contract_type": "Software Development Agreement",
                "key_similarities": [
                    "IP ownership clauses",
                    "Liability limitations", 
                    "Payment terms structure"
                ],
                "outcome": "Settled out of court",
                "settlement_terms": "Revised IP ownership, liability cap added",
                "lessons_learned": [
                    "Clear IP ownership prevents disputes",
                    "Liability caps are essential for vendor protection"
                ],
                "risk_factors": ["Unlimited liability", "Vague IP terms"],
                "date": "2023-08-15",
                "jurisdiction": "California"
            },
            {
                "precedent_id": "PREC_002", 
                "case_name": "Digital Innovations LLC v. Cloud Services Provider",
                "similarity_score": 0.76,
                "contract_type": "Service Level Agreement",
                "key_similarities": [
                    "Performance metrics",
                    "Penalty clauses",
                    "Termination procedures"
                ],
                "outcome": "Court ruling favored plaintiff",
                "settlement_terms": "Service credits awarded, contract restructured",
                "lessons_learned": [
                    "Specific SLA metrics prevent disputes",
                    "Penalty clauses must be reasonable"
                ],
                "risk_factors": ["Unrealistic SLA targets", "Excessive penalties"],
                "date": "2023-11-22",
                "jurisdiction": "New York"
            },
            {
                "precedent_id": "PREC_003",
                "case_name": "Global Enterprise Corp Contract Dispute",
                "similarity_score": 0.68,
                "contract_type": "Master Service Agreement",
                "key_similarities": [
                    "Multi-year terms",
                    "Renewal clauses",
                    "Price adjustment mechanisms"
                ],
                "outcome": "Mediated settlement",
                "settlement_terms": "Price adjustments agreed, contract extended",
                "lessons_learned": [
                    "Price escalation clauses protect against inflation",
                    "Clear renewal terms prevent misunderstandings"
                ],
                "risk_factors": ["Fixed pricing over long term", "Ambiguous renewal terms"],
                "date": "2024-01-10",
                "jurisdiction": "Delaware"
            }
        ]
        
        # Sort by similarity score
        precedents.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return precedents
    
    async def generate_predictive_analytics(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive analytics for contract outcomes"""
        
        # Mock predictive model results
        contract_type = contract_data.get("type", "unknown")
        risk_factors = contract_data.get("risk_factors", [])
        
        # Simulate ML model predictions
        base_probabilities = {
            "successful_completion": 0.75,
            "renegotiation_required": 0.15,
            "dispute_likelihood": 0.08,
            "early_termination": 0.02
        }
        
        # Adjust probabilities based on risk factors
        risk_multiplier = 1 + (len(risk_factors) * 0.05)
        
        predictions = {
            "contract_outcome_probabilities": {
                "successful_completion": max(0.1, base_probabilities["successful_completion"] / risk_multiplier),
                "renegotiation_required": min(0.8, base_probabilities["renegotiation_required"] * risk_multiplier),
                "dispute_likelihood": min(0.6, base_probabilities["dispute_likelihood"] * risk_multiplier),
                "early_termination": min(0.3, base_probabilities["early_termination"] * risk_multiplier)
            },
            "timeline_predictions": {
                "negotiation_duration_days": max(7, int(14 * risk_multiplier)),
                "approval_duration_days": max(2, int(5 * risk_multiplier)),
                "total_duration_days": max(14, int(30 * risk_multiplier))
            },
            "cost_predictions": {
                "legal_fees_estimate": max(5000, int(15000 * risk_multiplier)),
                "potential_dispute_cost": max(25000, int(75000 * risk_multiplier)),
                "total_cost_range": {
                    "min": max(5000, int(15000 * risk_multiplier)),
                    "max": max(50000, int(150000 * risk_multiplier))
                }
            },
            "key_risk_indicators": [
                {"factor": "Payment terms", "impact": "medium", "probability": 0.6},
                {"factor": "Liability clauses", "impact": "high", "probability": 0.8},
                {"factor": "IP ownership", "impact": "medium", "probability": 0.4},
                {"factor": "Termination rights", "impact": "low", "probability": 0.3}
            ],
            "recommendations": [
                "Consider adding liability cap to limit exposure",
                "Clarify intellectual property ownership terms",
                "Include force majeure provisions",
                "Add dispute resolution mechanisms"
            ],
            "confidence_level": max(0.6, 0.9 / risk_multiplier),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return predictions
    
    async def analyze_clause_patterns(self, documents: List[str]) -> Dict[str, Any]:
        """Analyze clause patterns across multiple documents"""
        
        # Mock clause analysis
        clause_types = [
            "Payment Terms",
            "Liability Limitations", 
            "Intellectual Property",
            "Termination Rights",
            "Confidentiality",
            "Force Majeure",
            "Dispute Resolution",
            "Governing Law"
        ]
        
        clause_analysis = {}
        
        for clause_type in clause_types:
            # Simulate clause frequency and risk analysis
            frequency = np.random.uniform(0.6, 0.95)  # 60-95% of documents
            avg_risk_score = np.random.uniform(30, 80)
            
            # Generate common variations
            variations = {
                "Payment Terms": ["Net 30", "Net 15", "Upon delivery", "Milestone-based"],
                "Liability Limitations": ["Contract value cap", "Unlimited", "$1M cap", "Mutual caps"],
                "Intellectual Property": ["Work for hire", "Shared ownership", "Client owns", "Vendor retains"],
                "Termination Rights": ["30-day notice", "For cause only", "Mutual rights", "90-day notice"]
            }.get(clause_type, ["Standard", "Modified", "Custom", "Missing"])
            
            clause_analysis[clause_type] = {
                "frequency_percentage": round(frequency * 100, 1),
                "average_risk_score": round(avg_risk_score, 1),
                "risk_level": "High" if avg_risk_score > 70 else "Medium" if avg_risk_score > 40 else "Low",
                "common_variations": variations[:3],
                "recommendation": f"Review {clause_type.lower()} for consistency and risk mitigation"
            }
        
        return {
            "clause_analysis": clause_analysis,
            "total_documents_analyzed": len(documents),
            "analysis_date": datetime.utcnow().isoformat(),
            "overall_recommendations": [
                "Standardize payment terms across contracts",
                "Implement consistent liability limitations", 
                "Clarify IP ownership in all agreements",
                "Add force majeure clauses where missing"
            ]
        }