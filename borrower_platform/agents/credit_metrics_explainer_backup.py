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
            "excellent": {"min": 750, "max": 850, "description": "Very low risk, excellent credit"},
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
        
        # Financial behavior (10%)
        financial_score = self._score_financial_behavior(user_data)
        scores["financial_behavior"] = financial_score
        total_score += financial_score * 0.10
        
        # Determine score range
        score_range = self._get_score_range(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "score_range": score_range,
            "factor_scores": scores,
            "calculation_details": {
                "income_contribution": income_score * 0.25,
                "repayment_contribution": repayment_score * 0.30,
                "asset_contribution": asset_score * 0.20,
                "social_contribution": social_score * 0.15,
                "financial_contribution": financial_score * 0.10
            }
        }
    
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
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": explanation_prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )
            
            explanation = response.choices[0].message.content.strip()
            
            # Cache result
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
    "estimated_score_improvement": "potential score increase with all recommendations"
}}

Analyze and provide ONLY the JSON:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": improvement_prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error identifying improvement areas: {e}")
            return {
                "priority_areas": [],
                "quick_wins": [],
                "long_term_strategies": [],
                "error": str(e)
            }
    
    def compare_with_peers(self, credit_score: float, user_location: str, occupation: str, language: str = "english") -> Dict[str, Any]:
        """
        Compare user's credit score with similar peers
        
        Args:
            credit_score (float): User's credit score
            user_location (str): User's location/district
            occupation (str): User's primary occupation
            language (str): Target language for comparison
            
        Returns:
            Dict: Peer comparison results
        """
        
        # Simulate peer data (in real implementation, this would come from database)
        peer_data = {
            "farmer": {"average_score": 580, "median_score": 575, "top_25_percent": 650},
            "shopkeeper": {"average_score": 620, "median_score": 615, "top_25_percent": 680},
            "weaver": {"average_score": 560, "median_score": 555, "top_25_percent": 630},
            "labor": {"average_score": 520, "median_score": 515, "top_25_percent": 580}
        }
        
        occupation_lower = occupation.lower()
        peer_scores = peer_data.get(occupation_lower, peer_data["farmer"])
        
        # Calculate percentile
        if credit_score >= peer_scores["top_25_percent"]:
            percentile = "top 25%"
        elif credit_score >= peer_scores["median_score"]:
            percentile = "above average"
        elif credit_score >= peer_scores["average_score"] - 50:
            percentile = "average"
        else:
            percentile = "below average"
        
        system_prompt = get_language_prompt(language, "credit_system")
        
        comparison_prompt = f"""
{system_prompt}

Generate a peer comparison explanation for this user.

User Credit Score: {credit_score}
User Occupation: {occupation}
User Location: {user_location}
Peer Averages: {json.dumps(peer_scores, indent=2)}
User Percentile: {percentile}

Provide an encouraging comparison that explains:
1. How they rank among similar users
2. What this means for their loan prospects
3. Motivation to improve
4. Success stories from similar backgrounds

Keep it positive and motivating:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": comparison_prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            comparison_text = response.choices[0].message.content.strip()
            
            return {
                "user_score": credit_score,
                "peer_average": peer_scores["average_score"],
                "peer_median": peer_scores["median_score"],
                "top_25_percent_threshold": peer_scores["top_25_percent"],
                "user_percentile": percentile,
                "comparison_explanation": comparison_text,
                "score_gap_to_average": peer_scores["average_score"] - credit_score,
                "score_gap_to_top_25": peer_scores["top_25_percent"] - credit_score
            }
            
        except Exception as e:
            print(f"Error generating peer comparison: {e}")
            return {
                "error": str(e),
                "user_score": credit_score,
                "peer_average": peer_scores["average_score"]
            }
    
    def generate_credit_report(self, user_data: Dict[str, Any], language: str = "english") -> Dict[str, Any]:
        """
        Generate comprehensive credit report
        
        Args:
            user_data (Dict): User profile data
            language (str): Target language for report
            
        Returns:
            Dict: Complete credit assessment report
        """
        
        # Calculate credit score
        credit_calculation = self.calculate_credit_score(user_data)
        
        # Generate explanation
        explanation = self.explain_credit_score(credit_calculation, language)
        
        # Get improvement recommendations
        improvements = self.identify_improvement_areas(credit_calculation, user_data, language)
        
        # Peer comparison
        user_location = user_data.get("household_location", {}).get("district", "Karnataka")
        user_occupation = user_data.get("occupation_income", {}).get("primary_occupation", "farmer")
        peer_comparison = self.compare_with_peers(
            credit_calculation["total_score"],
            user_location,
            user_occupation,
            language
        )
        
        return {
            "credit_score_calculation": credit_calculation,
            "explanation": explanation,
            "improvement_recommendations": improvements,
            "peer_comparison": peer_comparison,
            "report_metadata": {
                "generated_for": user_data.get("personal_info", {}).get("full_name", "User"),
                "language": language,
                "calculation_date": "current_date",
                "next_review_date": "3_months_from_now"
            }
        }
    
    def _score_income_stability(self, user_data: Dict[str, Any]) -> int:
        """Score income stability factor (0-100)"""
        score = 50  # Base score
        
        occupation = user_data.get("occupation_income", {})
        
        # Primary occupation scoring
        primary_occ = occupation.get("primary_occupation", "").lower()
        if "government" in primary_occ or "teacher" in primary_occ:
            score += 40
        elif "farming" in primary_occ or "farmer" in primary_occ:
            score += 20
        elif "business" in primary_occ or "shop" in primary_occ:
            score += 30
        else:
            score += 10
        
        # Seasonal variation penalty
        if occupation.get("seasonal_variation", "").lower() == "yes":
            score -= 15
        
        # Secondary income bonus
        if occupation.get("secondary_income_sources"):
            score += 15
        
        return min(100, max(0, score))
    
    def _score_repayment_history(self, user_data: Dict[str, Any]) -> int:
        """Score repayment history factor (0-100)"""
        score = 60  # Base score for new customers
        
        financial = user_data.get("financial_details", {})
        
        # Existing loans impact
        existing_loans = financial.get("existing_loans", "").lower()
        if "no" in existing_loans or not existing_loans:
            score += 20  # No existing debt is good
        elif "small" in existing_loans or "minor" in existing_loans:
            score += 10
        else:
            score -= 10
        
        # Repayment history
        repayment = financial.get("repayment_history", "").lower()
        if "good" in repayment or "excellent" in repayment:
            score += 30
        elif "late" in repayment or "missed" in repayment:
            score -= 40
        
        return min(100, max(0, score))
    
    def _score_asset_ownership(self, user_data: Dict[str, Any]) -> int:
        """Score asset ownership factor (0-100)"""
        score = 30  # Base score
        
        # Land ownership
        land_property = user_data.get("land_property", {})
        if land_property.get("owns_land", "").lower() == "yes":
            score += 40
            
            # Land area bonus
            area = land_property.get("land_area", "")
            if area and any(char.isdigit() for char in area):
                score += 20
        
        # Property type
        household = user_data.get("household_location", {})
        house_type = household.get("house_type", "").lower()
        if "pucca" in house_type:
            score += 20
        elif "semi" in house_type:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_social_capital(self, user_data: Dict[str, Any]) -> int:
        """Score social capital factor (0-100)"""
        score = 40  # Base score
        
        financial = user_data.get("financial_details", {})
        
        # Group membership
        group_membership = financial.get("group_membership", "").lower()
        if "yes" in group_membership:
            score += 30
        
        # Bank account
        bank_status = financial.get("bank_account_status", "").lower()
        if "yes" in bank_status:
            score += 20
        
        # Community ties (inferred from phone ownership)
        digital = user_data.get("digital_literacy", {})
        if digital.get("owns_smartphone", "").lower() == "yes":
            score += 10
        
        return min(100, max(0, score))
    
    def _score_financial_behavior(self, user_data: Dict[str, Any]) -> int:
        """Score financial behavior factor (0-100)"""
        score = 50  # Base score
        
        financial = user_data.get("financial_details", {})
        occupation = user_data.get("occupation_income", {})
        
        # Savings habit
        savings = financial.get("savings_per_month", "")
        if savings and any(char.isdigit() for char in str(savings)):
            score += 30
        
        # Income vs expenses ratio
        income = occupation.get("monthly_income", "")
        expenses = occupation.get("monthly_expenses", "")
        if income and expenses:
            # Simplified calculation
            score += 20
        
        return min(100, max(0, score))
    
    def _get_score_range(self, score: float) -> str:
        """Determine score range category"""
        for range_name, range_data in self.score_ranges.items():
            if range_data["min"] <= score <= range_data["max"]:
                return range_name
        return "unknown"

# Example usage and testing
if __name__ == "__main__":
    explainer = CreditMetricsExplainer()
    
    # Test with sample user data
    sample_user = {
        "personal_info": {
            "full_name": "Ramesh Kumar",
            "age": "35"
        },
        "occupation_income": {
            "primary_occupation": "farmer",
            "monthly_income": "15000",
            "monthly_expenses": "12000",
            "seasonal_variation": "yes"
        },
        "financial_details": {
            "bank_account_status": "yes",
            "existing_loans": "small agriculture loan",
            "repayment_history": "good",
            "savings_per_month": "2000",
            "group_membership": "yes"
        },
        "land_property": {
            "owns_land": "yes",
            "land_area": "2 acres"
        },
        "household_location": {
            "house_type": "semi-pucca",
            "district": "Davangere"
        },
        "digital_literacy": {
            "owns_smartphone": "yes"
        }
    }
    
    # Generate credit report
    report = explainer.generate_credit_report(sample_user, "english")
    print("Credit Score:", report["credit_score_calculation"]["total_score"])
    print("Score Range:", report["credit_score_calculation"]["score_range"])
    print("\nExplanation:", report["explanation"][:200] + "...")
    print("\nPeer Comparison Percentile:", report["peer_comparison"]["user_percentile"])
