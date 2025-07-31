"""
Credit Metrics Explainer
Explains user's credit score factors in simple terms using dynamic ML model weights
Supports English, Hindi, and Kannada
"""

import os
import json
from groq import Groq
from typing import Dict, Any, Optional, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, generate_cache_key
from .credit_scoring_agent import CreditScoringAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CreditMetricsExplainer:
    def __init__(self, groq_api_key: str = None):
        """
        Initialize Credit Metrics Explainer with GROQ for AI explanations
        
        Args:
            groq_api_key: GROQ API key (optional, loads from environment if not provided)
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ API key is required. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
        self.client = Groq(api_key=self.groq_api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.cache = {}
        
        # Initialize credit scoring agent to get dynamic model weights
        self.credit_scorer = CreditScoringAgent(groq_api_key)
        
        # Credit scoring factors for rural microfinance (will be updated from model)
        self.credit_factors = {
            "income_stability": {
                "weight": self.credit_scorer.scoring_weights.get("income_stability", 25),
                "description": "Regular and stable income source"
            },
            "repayment_history": {
                "weight": self.credit_scorer.scoring_weights.get("repayment_history", 30),
                "description": "Past loan repayment track record"
            },
            "asset_ownership": {
                "weight": self.credit_scorer.scoring_weights.get("asset_ownership", 20),
                "description": "Land, property, and asset ownership"
            },
            "social_capital": {
                "weight": self.credit_scorer.scoring_weights.get("social_capital", 15),
                "description": "Community ties and group membership"
            },
            "financial_behavior": {
                "weight": self.credit_scorer.scoring_weights.get("financial_behavior", 10),
                "description": "Savings habits and financial discipline"
            }
        }
        
        # Score ranges
        self.score_ranges = {
            "excellent": {"min": 750, "max": 900, "description": "Very low risk, excellent credit"},
            "good": {"min": 650, "max": 749, "description": "Low risk, good credit history"},
            "fair": {"min": 550, "max": 649, "description": "Medium risk, some concerns"},
            "poor": {"min": 450, "max": 549, "description": "High risk, limited credit access"},
            "very_poor": {"min": 300, "max": 449, "description": "Very high risk, poor credit"}
        }
    
    def calculate_credit_score(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate credit score using the ML model-based credit scoring agent
        
        Args:
            user_data (Dict): User profile data
            
        Returns:
            Dict: Credit score calculation results with dynamic weights
        """
        
        # Use the credit scoring agent for calculation
        credit_result = self.credit_scorer.calculate_credit_score(user_data, "rule_based")
        
        # Extract scores and add explainer-specific formatting
        factor_scores = credit_result.get("factor_scores", {})
        credit_score = credit_result.get("credit_score", 0)
        
        # Calculate weighted contributions using dynamic weights
        weighted_contributions = {}
        for factor, score in factor_scores.items():
            weight = self.credit_scorer.scoring_weights.get(factor, 0)
            contribution = (score * weight) / 100
            weighted_contributions[factor] = {
                "raw_score": score,
                "weight_percentage": weight,
                "weighted_contribution": round(contribution, 2),
                "max_possible": weight
            }
        
        return {
            "credit_score": credit_score,
            "score_range": self._determine_score_range(credit_score),
            "factor_scores": factor_scores,
            "weighted_contributions": weighted_contributions,
            "model_weights": self.credit_scorer.scoring_weights,
            "model_status": "ML Model" if hasattr(self.credit_scorer, 'ml_model') and self.credit_scorer.ml_model else "Rule-based",
            "calculation_details": credit_result.get("calculation_details", {}),
            "risk_level": credit_result.get("risk_level", "Unknown"),
            "recommendation": credit_result.get("recommendation", "Unknown")
        }
    
    def _determine_score_range(self, credit_score: float) -> str:
        """Determine score range category"""
        for range_name, range_info in self.score_ranges.items():
            if range_info["min"] <= credit_score <= range_info["max"]:
                return range_name
        return "unknown"
    
    def explain_credit_score(self, credit_calculation: Dict[str, Any], language: str = "english") -> str:
        """
        Generate human-readable explanation of credit score using dynamic ML model weights
        
        Args:
            credit_calculation (Dict): Credit score calculation results from ML model
            language (str): Target language for explanation
            
        Returns:
            str: Detailed credit score explanation with dynamic weights
        """
        
        # Check cache
        cache_key = generate_cache_key({"calc": credit_calculation, "lang": language})
        if cache_key in self.cache:
            return self.cache[cache_key]

        system_prompt = get_language_prompt(language, "credit_system")
        
        # Get current model weights and status
        model_weights = credit_calculation.get("model_weights", self.credit_scorer.scoring_weights)
        model_status = credit_calculation.get("model_status", "Unknown")
        
        explanation_prompt = f"""
{system_prompt}

Explain this credit score calculation in simple terms that a rural user can understand.

Credit Score Data: {json.dumps(credit_calculation, indent=2)}

IMPORTANT: This credit score is calculated using {model_status} with these ACTUAL weights:
- Income Stability: {model_weights.get('income_stability', 25)}%
- Repayment History: {model_weights.get('repayment_history', 30)}%  
- Social Capital: {model_weights.get('social_capital', 20)}%
- Asset Ownership: {model_weights.get('asset_ownership', 15)}%
- Financial Behavior: {model_weights.get('financial_behavior', 10)}%

Credit Factors Explanation:
{json.dumps(self.credit_factors, indent=2)}

Provide a clear explanation covering:
1. Overall credit score ({credit_calculation.get('credit_score', 'N/A')}/900) and what it means
2. Breakdown of each factor using the ACTUAL model weights shown above
3. What the user is doing well (highlight high-scoring factors)
4. Areas for improvement (focus on factors with highest weights that score poorly)
5. Practical steps to improve the score based on weight importance
6. How this affects loan eligibility and terms

CRITICAL: Use the actual model weights in your explanation, not generic percentages. 
Emphasize factors with higher weights more strongly in your recommendations.

Use simple language and relatable examples from rural life:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": explanation_prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            explanation = response.choices[0].message.content.strip()
            
            # Cache the result
            self.cache[cache_key] = explanation
            
            return explanation
            
        except Exception as e:
            print(f"Error explaining credit score: {e}")
            return f"Unable to generate explanation: {e}"
    
    def identify_improvement_areas(self, credit_calculation: Dict[str, Any], user_data: Dict[str, Any], language: str = "english") -> Dict[str, Any]:
        """
        Identify specific areas for credit score improvement using dynamic ML weights
        
        Args:
            credit_calculation (Dict): Credit score calculation results from ML model
            user_data (Dict): User profile data
            language (str): Target language for recommendations
            
        Returns:
            Dict: Improvement recommendations prioritized by ML model weights
        """
        
        # Get model weights and factor scores
        model_weights = credit_calculation.get("model_weights", self.credit_scorer.scoring_weights)
        factor_scores = credit_calculation.get("factor_scores", {})
        
        # Prioritize improvements based on weight * impact potential
        improvement_priority = []
        for factor, score in factor_scores.items():
            weight = model_weights.get(factor, 0)
            # Lower scores with higher weights get higher priority
            improvement_potential = weight * (100 - score) / 100
            improvement_priority.append({
                "factor": factor,
                "current_score": score,
                "weight": weight,
                "improvement_potential": improvement_potential
            })
        
        # Sort by improvement potential (highest first)
        improvement_priority.sort(key=lambda x: x["improvement_potential"], reverse=True)
        
        return {
            "top_priority_areas": improvement_priority[:3],
            "model_weights": model_weights,
            "factor_scores": factor_scores,
            "recommendations": self._generate_improvement_recommendations(improvement_priority[:3])
        }
    
    def _generate_improvement_recommendations(self, priority_areas: List[Dict]) -> List[str]:
        """Generate specific recommendations for improvement areas"""
        recommendations = []
        
        for area in priority_areas:
            factor = area["factor"]
            weight = area["weight"]
            score = area["current_score"]
            
            if factor == "income_stability":
                recommendations.append(f"Focus on income stability ({weight}% of score): Diversify income sources, maintain consistent earnings")
            elif factor == "repayment_history":
                recommendations.append(f"Improve repayment history ({weight}% of score): Join SHG, maintain timely loan payments")
            elif factor == "social_capital":
                recommendations.append(f"Build social capital ({weight}% of score): Join community groups, maintain good relationships")
            elif factor == "asset_ownership":
                recommendations.append(f"Strengthen asset ownership ({weight}% of score): Document land ownership, acquire productive assets")
            elif factor == "financial_behavior":
                recommendations.append(f"Improve financial behavior ({weight}% of score): Maintain regular savings, use banking services")
        
        return recommendations

# For backwards compatibility, keep the old scoring methods available
# These are now mainly for reference since we use the CreditScoringAgent
