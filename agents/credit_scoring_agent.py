"""
Credit Scoring Agent
Calculates custom credit score based on structured user input using explainable rule-based or AI logic
Analyzes personal, income, group, and repayment data with domain-specific scoring
Outputs structured JSON with credit_score, risk_level, recommendation, and key_risk_factors
"""

import os
import json
from groq import Groq
from typing import Dict, Any, Optional, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, generate_cache_key
from .translation_agent import TranslationAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CreditScoringAgent:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or parameters")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        self.cache = {}
        self.translator = TranslationAgent(self.groq_api_key)
        
        # Complete user data schema for validation
        self.required_fields = {
            "full_name": str,
            "age": int,
            "gender": str,
            "preferred_language": str,
            "aadhaar_number": str,
            "phone_number": str,
            "marital_status": str,
            "voter_id": str,
            "village_name": str,
            "district": str,
            "state": str,
            "pincode": str,
            "house_type": str,
            "electricity_connection": str,
            "number_of_dependents": int,
            "primary_occupation": str,
            "secondary_income_sources": str,
            "monthly_income": int,
            "monthly_expenses": int,
            "seasonal_variation": str,
            "bank_account_status": str,
            "bank_name": str,
            "existing_loans": str,
            "repayment_history": str,
            "savings_per_month": int,
            "group_membership": str,
            "past_loan_amounts": str,
            "owns_land": str,
            "land_area": str,
            "land_type": str,
            "patta_or_katha_number": str,
            "property_location": str,
            "owns_smartphone": str,
            "knows_how_to_use_apps": str,
            "preferred_mode_of_communication": str,
            "internet_availability": str,
            "user_notes": str,
            "agent_observations": str
        }
        
        # Domain-specific scoring weights for rural microfinance
        self.scoring_weights = {
            "income_stability": 25,      # Regular income source reliability
            "repayment_history": 30,     # Past loan repayment track record
            "social_capital": 20,        # Group membership, community ties
            "asset_ownership": 15,       # Land, property ownership
            "financial_behavior": 10     # Savings habits, bank usage
        }
        
        # Risk level thresholds
        self.risk_thresholds = {
            "low": 70,      # Score >= 70: Low risk
            "medium": 50,   # Score 50-69: Medium risk
            "high": 30,     # Score 30-49: High risk
            "very_high": 0  # Score < 30: Very high risk
        }
    
    def check_data_completeness(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check data completeness against required schema
        
        Args:
            user_data (Dict): User profile data
            
        Returns:
            Dict: Completeness analysis
        """
        missing_fields = []
        provided_fields = []
        
        for field_name, field_type in self.required_fields.items():
            if field_name in user_data and user_data[field_name] is not None and str(user_data[field_name]).strip():
                provided_fields.append(field_name)
            else:
                missing_fields.append(field_name)
        
        total_fields = len(self.required_fields)
        provided_count = len(provided_fields)
        missing_count = len(missing_fields)
        
        completeness_percentage = round((provided_count / total_fields) * 100, 1)
        
        return {
            "completeness_percentage": completeness_percentage,
            "total_fields": total_fields,
            "provided_fields": provided_count,
            "missing_fields": missing_count,
            "missing_field_names": missing_fields,
            "provided_field_names": provided_fields
        }
    
    def explain_credit_scoring_system(self, user_data: Dict[str, Any] = None) -> str:
        """
        Explain how the credit scoring system works
        
        Args:
            user_data (Dict): Optional user data for personalized explanation
            
        Returns:
            str: Explanation of credit scoring system
        """
        user_language = "english"
        if user_data:
            user_language = self.translator.get_user_preferred_language(user_data)
        
        explanation = f"""
**How Our Credit Scoring System Works**

Our microfinance credit scoring system evaluates your loan eligibility based on 5 key factors:

**1. Income Stability (25% weight):**
- Primary occupation reliability
- Monthly income amount and consistency
- Seasonal income variations
- Secondary income sources

**2. Repayment History (30% weight):**
- Past loan repayment record
- Payment timeliness
- Default history
- Existing loan status

**3. Social Capital (20% weight):**
- Group membership (SHG, cooperatives)
- Community relationships
- Social guarantees
- Local references

**4. Asset Ownership (15% weight):**
- Land ownership and area
- Property ownership
- Agricultural assets
- Collateral availability

**5. Financial Behavior (10% weight):**
- Banking habits
- Savings patterns
- Digital literacy
- Financial discipline

**Scoring Scale:**
- 80-100: Very Low Risk (Excellent)
- 70-79: Low Risk (Good)
- 50-69: Medium Risk (Fair)
- 30-49: High Risk (Poor)
- 0-29: Very High Risk (Very Poor)

The system uses both rule-based calculations and AI analysis to provide fair, transparent scoring suitable for rural microfinance customers in Karnataka.
"""
        
        # Translate to user's preferred language if needed
        if user_language != "english":
            translated_explanation = self.translator.translate_response_to_user_language(explanation, user_data or {"preferred_language": user_language})
            return translated_explanation
        
        return explanation
    
    def calculate_credit_score(self, user_data: Dict[str, Any], scoring_method: str = "rule_based") -> Dict[str, Any]:
        """
        Calculate comprehensive credit score using rule-based or AI-backed logic
        
        Args:
            user_data (Dict): Structured user profile data
            scoring_method (str): "rule_based" or "ai_backed"
            
        Returns:
            Dict: Complete credit assessment with score, risk level, and factors
        """
        
        # Check cache
        cache_key = generate_cache_key({"data": user_data, "method": scoring_method})
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if scoring_method == "ai_backed":
            result = self._ai_backed_scoring(user_data)
        else:
            result = self._rule_based_scoring(user_data)
        
        # Add risk level and recommendation
        result["risk_level"] = self._determine_risk_level(result["credit_score"])
        result["recommendation"] = self._generate_recommendation(result)
        result["key_risk_factors"] = self._identify_key_risk_factors(result, user_data)
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    def _rule_based_scoring(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rule-based credit scoring using point-based system
        """
        
        scores = {}
        
        # 1. Income Stability (25 points)
        income_score = self._score_income_stability(user_data)
        scores["income_stability"] = income_score
        
        # 2. Repayment History (30 points)
        repayment_score = self._score_repayment_history(user_data)
        scores["repayment_history"] = repayment_score
        
        # 3. Social Capital (20 points)
        social_score = self._score_social_capital(user_data)
        scores["social_capital"] = social_score
        
        # 4. Asset Ownership (15 points)
        asset_score = self._score_asset_ownership(user_data)
        scores["asset_ownership"] = asset_score
        
        # 5. Financial Behavior (10 points)
        financial_score = self._score_financial_behavior(user_data)
        scores["financial_behavior"] = financial_score
        
        # Calculate weighted total score
        total_score = (
            (income_score * self.scoring_weights["income_stability"]) +
            (repayment_score * self.scoring_weights["repayment_history"]) +
            (social_score * self.scoring_weights["social_capital"]) +
            (asset_score * self.scoring_weights["asset_ownership"]) +
            (financial_score * self.scoring_weights["financial_behavior"])
        ) / 100
        
        return {
            "credit_score": round(total_score, 1),
            "scoring_method": "rule_based",
            "factor_scores": scores,
            "calculation_details": {
                "weighted_contributions": {
                    "income_stability": round((income_score * self.scoring_weights["income_stability"]) / 100, 2),
                    "repayment_history": round((repayment_score * self.scoring_weights["repayment_history"]) / 100, 2),
                    "social_capital": round((social_score * self.scoring_weights["social_capital"]) / 100, 2),
                    "asset_ownership": round((asset_score * self.scoring_weights["asset_ownership"]) / 100, 2),
                    "financial_behavior": round((financial_score * self.scoring_weights["financial_behavior"]) / 100, 2)
                }
            }
        }
    
    def _ai_backed_scoring(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-backed credit scoring using LLM analysis
        """
        
        system_prompt = """You are an expert credit analyst for rural microfinance in India. 
        Analyze the user profile and provide a comprehensive credit assessment."""
        
        analysis_prompt = f"""
        Analyze this rural user profile for microfinance credit scoring:

        User Data: {json.dumps(user_data, indent=2)}

        Provide credit assessment as JSON:
        {{
            "credit_score": "score from 0-100",
            "scoring_method": "ai_backed",
            "factor_scores": {{
                "income_stability": "0-100 based on occupation, income regularity",
                "repayment_history": "0-100 based on past loans, payment behavior", 
                "social_capital": "0-100 based on group membership, community ties",
                "asset_ownership": "0-100 based on land, property ownership",
                "financial_behavior": "0-100 based on savings, banking habits"
            }},
            "ai_analysis": {{
                "strengths": ["list of positive factors"],
                "concerns": ["list of risk factors"],
                "unique_factors": ["special considerations for this profile"],
                "confidence_level": "high/medium/low"
            }}
        }}

        Analyze and return ONLY the JSON:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1000,
                temperature=0  # Deterministic output
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                
            ai_result = json.loads(result_text)
            return ai_result
            
        except Exception as e:
            print(f"Error in AI-backed scoring: {e}")
            # Fallback to rule-based scoring
            return self._rule_based_scoring(user_data)
    
    def _score_income_stability(self, user_data: Dict[str, Any]) -> int:
        """Score income stability (0-100)"""
        score = 40  # Base score
        
        occupation = user_data.get("occupation_income", {})
        
        # Primary occupation scoring
        primary_occ = occupation.get("primary_occupation", "").lower()
        if any(word in primary_occ for word in ["government", "teacher", "clerk"]):
            score += 35  # Very stable income
        elif any(word in primary_occ for word in ["farming", "farmer", "agriculture"]):
            score += 20  # Seasonal but predictable
        elif any(word in primary_occ for word in ["business", "shop", "trade"]):
            score += 25  # Variable but self-controlled
        elif any(word in primary_occ for word in ["labor", "worker", "daily"]):
            score += 10  # Uncertain income
        else:
            score += 15  # Other occupations
        
        # Income amount consideration
        monthly_income = occupation.get("monthly_income", "")
        if monthly_income:
            try:
                income_value = float(''.join(filter(str.isdigit, str(monthly_income))))
                if income_value >= 20000:
                    score += 15
                elif income_value >= 15000:
                    score += 10
                elif income_value >= 10000:
                    score += 5
            except:
                pass
        
        # Seasonal variation penalty
        if occupation.get("seasonal_variation", "").lower() in ["yes", "high"]:
            score -= 10
        
        # Secondary income bonus
        if occupation.get("secondary_income_sources", "").strip():
            score += 10
        
        return min(100, max(0, score))
    
    def _score_repayment_history(self, user_data: Dict[str, Any]) -> int:
        """Score repayment history (0-100)"""
        score = 50  # Base score for new customers
        
        financial = user_data.get("financial_details", {})
        
        # Repayment history analysis
        repayment = financial.get("repayment_history", "").lower()
        if any(word in repayment for word in ["excellent", "perfect", "always on time"]):
            score += 40
        elif any(word in repayment for word in ["good", "regular", "no issues"]):
            score += 30
        elif any(word in repayment for word in ["fair", "occasional delay"]):
            score += 10
        elif any(word in repayment for word in ["late", "missed", "defaulted"]):
            score -= 30
        elif any(word in repayment for word in ["bad", "poor", "irregular"]):
            score -= 40
        
        # Existing loans impact
        existing_loans = financial.get("existing_loans", "").lower()
        if "no" in existing_loans or not existing_loans:
            score += 10  # No current debt burden
        elif any(word in existing_loans for word in ["small", "minor", "manageable"]):
            score += 5
        elif any(word in existing_loans for word in ["large", "multiple", "heavy"]):
            score -= 15
        
        # Past loan experience
        past_loans = financial.get("past_loan_amounts", "")
        if past_loans and "never" not in past_loans.lower():
            score += 10  # Has borrowing experience
        
        return min(100, max(0, score))
    
    def _score_social_capital(self, user_data: Dict[str, Any]) -> int:
        """Score social capital and community ties (0-100)"""
        score = 30  # Base score
        
        financial = user_data.get("financial_details", {})
        personal = user_data.get("personal_info", {})
        
        # Group membership (very important in microfinance)
        group_membership = financial.get("group_membership", "").lower()
        if "yes" in group_membership or any(word in group_membership for word in ["shg", "cooperative", "society"]):
            score += 40  # Strong community ties
        
        # Bank account (financial inclusion)
        if financial.get("bank_account_status", "").lower() == "yes":
            score += 20
        
        # Phone number (connectivity and reachability)
        if personal.get("phone_number", "").strip():
            score += 10
        
        return min(100, max(0, score))
    
    def _score_asset_ownership(self, user_data: Dict[str, Any]) -> int:
        """Score asset ownership (0-100)"""
        score = 20  # Base score
        
        land_property = user_data.get("land_property", {})
        household = user_data.get("household_location", {})
        
        # Land ownership (major asset)
        if land_property.get("owns_land", "").lower() == "yes":
            score += 50
            
            # Land area bonus
            area = land_property.get("land_area", "")
            if area:
                if any(word in area.lower() for word in ["acres", "acre"]):
                    score += 15
                elif any(word in area.lower() for word in ["guntas", "gunta"]):
                    score += 10
        
        # House type
        house_type = household.get("house_type", "").lower()
        if "pucca" in house_type:
            score += 20
        elif "semi" in house_type:
            score += 10
        elif "kachcha" in house_type:
            score += 5
        
        # Electricity connection
        if household.get("electricity_connection", "").lower() == "yes":
            score += 5
        
        return min(100, max(0, score))
    
    def _score_financial_behavior(self, user_data: Dict[str, Any]) -> int:
        """Score financial behavior and savings habits (0-100)"""
        score = 40  # Base score
        
        financial = user_data.get("financial_details", {})
        occupation = user_data.get("occupation_income", {})
        
        # Savings habit
        savings = financial.get("savings_per_month", "")
        if savings and savings.strip():
            try:
                savings_value = float(''.join(filter(str.isdigit, str(savings))))
                if savings_value > 0:
                    score += 30
                    if savings_value >= 2000:
                        score += 10  # Good savings habit
            except:
                pass
        
        # Income vs expenses management
        income = occupation.get("monthly_income", "")
        expenses = occupation.get("monthly_expenses", "")
        if income and expenses:
            try:
                income_val = float(''.join(filter(str.isdigit, str(income))))
                expense_val = float(''.join(filter(str.isdigit, str(expenses))))
                if income_val > expense_val:
                    score += 20  # Lives within means
            except:
                pass
        
        return min(100, max(0, score))
    
    def _determine_risk_level(self, credit_score: float) -> str:
        """Determine risk level based on credit score"""
        if credit_score >= self.risk_thresholds["low"]:
            return "Low"
        elif credit_score >= self.risk_thresholds["medium"]:
            return "Medium"
        elif credit_score >= self.risk_thresholds["high"]:
            return "High"
        else:
            return "Very High"
    
    def _generate_recommendation(self, credit_result: Dict[str, Any]) -> str:
        """Generate loan recommendation based on credit assessment"""
        score = credit_result["credit_score"]
        risk_level = credit_result["risk_level"]
        
        if risk_level == "Low":
            return "Approved"
        elif risk_level == "Medium":
            return "Needs Support"
        else:
            return "Rejected"
    
    def _identify_key_risk_factors(self, credit_result: Dict[str, Any], user_data: Dict[str, Any]) -> List[str]:
        """Identify top 3 risk factors affecting the score"""
        
        factor_scores = credit_result.get("factor_scores", {})
        risk_factors = []
        
        # Sort factors by score (lowest first)
        sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1])
        
        for factor, score in sorted_factors[:3]:
            if score < 60:  # Consider as risk factor if below 60
                if factor == "income_stability":
                    risk_factors.append("Irregular or low income source")
                elif factor == "repayment_history":
                    risk_factors.append("Poor or no repayment track record")
                elif factor == "social_capital":
                    risk_factors.append("Limited community ties or group membership")
                elif factor == "asset_ownership":
                    risk_factors.append("Insufficient collateral or asset ownership")
                elif factor == "financial_behavior":
                    risk_factors.append("Poor financial management or savings habits")
        
        return risk_factors[:3] if risk_factors else ["No significant risk factors identified"]
    
    def calculate_rule_based_score(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate credit score using rule-based method (alias for backwards compatibility)
        
        Args:
            user_data (Dict): User profile data
            
        Returns:
            Dict: Credit scoring results
        """
        return self.calculate_credit_score(user_data, "rule_based")
    
    def generate_ai_backed_score(self, user_data: Dict[str, Any], language: str = "english") -> Dict[str, Any]:
        """
        Generate AI-backed credit score (alias for backwards compatibility)
        
        Args:
            user_data (Dict): User profile data
            language (str): Response language
            
        Returns:
            Dict: AI-backed credit scoring results
        """
        return self.calculate_credit_score(user_data, "ai_backed")

# Example usage and testing
if __name__ == "__main__":
    agent = CreditScoringAgent()
    
    # Test with sample user data
    sample_user = {
        "personal_info": {
            "full_name": "Ramesh Kumar",
            "age": "35",
            "phone_number": "9876543210"
        },
        "occupation_income": {
            "primary_occupation": "farmer",
            "monthly_income": "15000",
            "monthly_expenses": "10000",
            "seasonal_variation": "yes",
            "secondary_income_sources": "dairy farming"
        },
        "financial_details": {
            "bank_account_status": "yes",
            "existing_loans": "small agriculture loan",
            "repayment_history": "good",
            "savings_per_month": "2000",
            "group_membership": "yes - farmers cooperative"
        },
        "land_property": {
            "owns_land": "yes",
            "land_area": "2 acres"
        },
        "household_location": {
            "house_type": "semi-pucca",
            "electricity_connection": "yes"
        }
    }
    
    # Test rule-based scoring
    result = agent.calculate_credit_score(sample_user, "rule_based")
    print("Rule-based Credit Assessment:")
    print(f"Credit Score: {result['credit_score']}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Key Risk Factors: {result['key_risk_factors']}")
    
    # Test AI-backed scoring
    ai_result = agent.calculate_credit_score(sample_user, "ai_backed")
    print(f"\nAI-backed Credit Score: {ai_result['credit_score']}/100")
