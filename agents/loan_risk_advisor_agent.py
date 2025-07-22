"""
Loan Risk Advisor Agent
Provides loan risk analysis and approval recommendations
Supports English, Hindi, and Kannada
"""

import os
import json
from groq import Groq
from typing import Dict, Any, Optional, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, generate_cache_key
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LoanRiskAdvisorAgent:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ API key is required. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
        self.client = Groq(api_key=self.groq_api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.cache = {}
        
        # Loan types and their risk parameters
        self.loan_types = {
            "agriculture": {
                "max_amount": 500000,
                "interest_rate_range": [8.5, 12.0],
                "typical_tenure": [12, 60],
                "collateral_required": False,
                "seasonal_considerations": True
            },
            "micro_business": {
                "max_amount": 200000,
                "interest_rate_range": [10.0, 14.0],
                "typical_tenure": [6, 36],
                "collateral_required": False,
                "seasonal_considerations": False
            },
            "personal": {
                "max_amount": 100000,
                "interest_rate_range": [12.0, 18.0],
                "typical_tenure": [3, 24],
                "collateral_required": False,
                "seasonal_considerations": False
            },
            "housing": {
                "max_amount": 1000000,
                "interest_rate_range": [8.0, 11.0],
                "typical_tenure": [60, 240],
                "collateral_required": True,
                "seasonal_considerations": False
            },
            "education": {
                "max_amount": 300000,
                "interest_rate_range": [9.0, 13.0],
                "typical_tenure": [12, 84],
                "collateral_required": False,
                "seasonal_considerations": False
            }
        }
        
        # Risk assessment criteria
        self.risk_factors = {
            "income_stability": {"weight": 0.25, "threshold": 60},
            "debt_to_income": {"weight": 0.20, "threshold": 40},
            "credit_history": {"weight": 0.25, "threshold": 65},
            "collateral_value": {"weight": 0.15, "threshold": 70},
            "social_capital": {"weight": 0.15, "threshold": 50}
        }
    
    def assess_loan_risk(self, user_data: Dict[str, Any], loan_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess loan risk based on user data and loan request
        
        Args:
            user_data (Dict): User profile data
            loan_request (Dict): Loan application details
            
        Returns:
            Dict: Risk assessment results
        """
        
        # Extract loan details
        loan_amount = float(loan_request.get("amount", 0))
        loan_type = loan_request.get("type", "personal").lower()
        loan_purpose = loan_request.get("purpose", "")
        
        # Calculate individual risk scores
        risk_scores = {}
        
        # Income stability assessment
        risk_scores["income_stability"] = self._assess_income_stability(user_data, loan_amount)
        
        # Debt-to-income ratio
        risk_scores["debt_to_income"] = self._assess_debt_to_income(user_data, loan_amount)
        
        # Credit history
        risk_scores["credit_history"] = self._assess_credit_history(user_data)
        
        # Collateral value (if applicable)
        risk_scores["collateral_value"] = self._assess_collateral_value(user_data, loan_amount, loan_type)
        
        # Social capital
        risk_scores["social_capital"] = self._assess_social_capital(user_data)
        
        # Calculate overall risk score
        overall_risk_score = sum(
            score * self.risk_factors[factor]["weight"] 
            for factor, score in risk_scores.items()
        )
        
        # Determine risk category
        risk_category = self._categorize_risk(overall_risk_score)
        
        return {
            "overall_risk_score": round(overall_risk_score, 2),
            "risk_category": risk_category,
            "individual_scores": risk_scores,
            "loan_details": {
                "requested_amount": loan_amount,
                "loan_type": loan_type,
                "purpose": loan_purpose
            },
            "risk_factors_analysis": self._analyze_risk_factors(risk_scores),
            "approval_recommendation": self._generate_approval_recommendation(overall_risk_score, loan_type, loan_amount)
        }
    
    def recommend_loan_terms(self, risk_assessment: Dict[str, Any], language: str = "english") -> Dict[str, Any]:
        """
        Recommend optimal loan terms based on risk assessment
        
        Args:
            risk_assessment (Dict): Risk assessment results
            language (str): Target language for recommendations
            
        Returns:
            Dict: Loan term recommendations
        """
        
        # Check cache
        cache_key = generate_cache_key({"risk": risk_assessment, "lang": language})
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        risk_score = risk_assessment["overall_risk_score"]
        loan_type = risk_assessment["loan_details"]["loan_type"]
        requested_amount = risk_assessment["loan_details"]["requested_amount"]
        
        # Get loan type parameters
        loan_params = self.loan_types.get(loan_type, self.loan_types["personal"])
        
        # Adjust terms based on risk
        if risk_score >= 80:  # Low risk
            interest_rate = loan_params["interest_rate_range"][0]
            approved_amount = min(requested_amount, loan_params["max_amount"])
            tenure_max = loan_params["typical_tenure"][1]
        elif risk_score >= 60:  # Medium risk
            interest_rate = sum(loan_params["interest_rate_range"]) / 2
            approved_amount = min(requested_amount * 0.8, loan_params["max_amount"])
            tenure_max = loan_params["typical_tenure"][1] * 0.8
        else:  # High risk
            interest_rate = loan_params["interest_rate_range"][1]
            approved_amount = min(requested_amount * 0.5, loan_params["max_amount"] * 0.5)
            tenure_max = loan_params["typical_tenure"][0] * 1.5
        
        # Calculate EMI
        monthly_interest = interest_rate / 12 / 100
        tenure_months = min(tenure_max, 36)
        
        if monthly_interest > 0:
            emi = approved_amount * monthly_interest * ((1 + monthly_interest) ** tenure_months) / (((1 + monthly_interest) ** tenure_months) - 1)
        else:
            emi = approved_amount / tenure_months
        
        recommendations = {
            "recommended_amount": round(approved_amount, 2),
            "interest_rate": round(interest_rate, 2),
            "tenure_months": int(tenure_months),
            "monthly_emi": round(emi, 2),
            "total_interest": round((emi * tenure_months) - approved_amount, 2),
            "total_repayment": round(emi * tenure_months, 2),
            "processing_fee": round(approved_amount * 0.01, 2),  # 1% processing fee
            "collateral_required": loan_params["collateral_required"] and risk_score < 70,
            "guarantor_required": risk_score < 60,
            "terms_explanation": ""
        }
        
        # Add explanation after creating the recommendations dict
        recommendations["terms_explanation"] = self._explain_loan_terms(risk_assessment, recommendations, language)
        
        # Cache result
        self.cache[cache_key] = recommendations
        
        return recommendations
    
    def generate_approval_recommendation(self, risk_assessment: Dict[str, Any], loan_terms: Dict[str, Any], language: str = "english") -> str:
        """
        Generate detailed approval recommendation with reasoning
        
        Args:
            risk_assessment (Dict): Risk assessment results
            loan_terms (Dict): Recommended loan terms
            language (str): Target language for recommendation
            
        Returns:
            str: Detailed approval recommendation
        """
        
        system_prompt = get_language_prompt(language, "risk_system")
        
        recommendation_prompt = f"""
{system_prompt}

Generate a comprehensive loan approval recommendation based on the risk assessment and proposed terms.

Risk Assessment: {json.dumps(risk_assessment, indent=2)}
Recommended Terms: {json.dumps(loan_terms, indent=2)}

Provide a detailed recommendation covering:
1. Approval decision (Approve/Conditional Approve/Reject)
2. Key strengths of the applicant
3. Risk concerns and mitigation strategies
4. Rationale for recommended terms
5. Conditions for approval (if any)
6. Alternative suggestions if applicable
7. Next steps for the applicant

Format as a professional loan officer's recommendation:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": recommendation_prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating approval recommendation: {e}")
            return f"Unable to generate recommendation: {e}"
    
    def compare_loan_options(self, user_data: Dict[str, Any], loan_options: List[Dict[str, Any]], language: str = "english") -> Dict[str, Any]:
        """
        Compare multiple loan options for the user
        
        Args:
            user_data (Dict): User profile data
            loan_options (List[Dict]): List of loan options to compare
            language (str): Target language for comparison
            
        Returns:
            Dict: Loan options comparison
        """
        
        comparisons = []
        
        for option in loan_options:
            # Assess risk for each option
            risk_assessment = self.assess_loan_risk(user_data, option)
            
            # Get recommended terms
            loan_terms = self.recommend_loan_terms(risk_assessment, language)
            
            comparisons.append({
                "loan_option": option,
                "risk_assessment": risk_assessment,
                "recommended_terms": loan_terms,
                "affordability_score": self._calculate_affordability(user_data, loan_terms)
            })
        
        # Rank options by overall suitability
        comparisons.sort(key=lambda x: (
            x["risk_assessment"]["overall_risk_score"] * 0.4 +
            x["affordability_score"] * 0.6
        ), reverse=True)
        
        return {
            "loan_comparisons": comparisons,
            "recommended_option": comparisons[0] if comparisons else None,
            "comparison_summary": self._generate_comparison_summary(comparisons, language)
        }
    
    def provide_detailed_loan_recommendation(self, user_data: Dict[str, Any], credit_result: Dict[str, Any], 
                                           property_verification: Dict[str, Any] = None, 
                                           language: str = "english") -> Dict[str, Any]:
        """
        Provide comprehensive loan recommendation with detailed risk analysis and reasoning
        MFI advice agent should suggest the user the risk levels and everything and tell detailed analysis
        if he can issue a loan to the borrower
        
        Args:
            user_data (Dict): Complete user profile
            credit_result (Dict): Credit scoring results
            property_verification (Dict): Property verification results if available
            language (str): Response language
            
        Returns:
            Dict: Detailed loan recommendation with comprehensive analysis
        """
        
        system_prompt = get_language_prompt(language, "risk_advisor_system")
        
        # Prepare comprehensive analysis prompt
        analysis_prompt = f"""
{system_prompt}

As an MFI Risk Advisor, provide comprehensive loan recommendation with detailed analysis.

USER PROFILE: {json.dumps(user_data, indent=2)}
CREDIT ASSESSMENT: {json.dumps(credit_result, indent=2)}
PROPERTY VERIFICATION: {json.dumps(property_verification or {}, indent=2)}

Provide detailed analysis as JSON:
{{
    "loan_recommendation": {{
        "decision": "APPROVE/CONDITIONAL_APPROVE/REJECT",
        "confidence": "high/medium/low",
        "maximum_loan_amount": "recommended amount in rupees",
        "interest_rate_suggestion": "suggested rate percentage",
        "repayment_period": "recommended months",
        "collateral_requirement": "required/not_required/optional"
    }},
    "detailed_risk_analysis": {{
        "overall_risk_score": "numerical score 0-100",
        "risk_category": "very_low/low/medium/high/very_high",
        "key_risk_factors": [
            {{
                "factor": "specific risk factor",
                "impact": "high/medium/low",
                "explanation": "detailed explanation of why this is risky",
                "mitigation_strategy": "how to reduce this risk"
            }}
        ],
        "positive_factors": [
            {{
                "factor": "positive aspect",
                "impact": "high/medium/low", 
                "explanation": "why this reduces risk"
            }}
        ]
    }},
    "financial_health_assessment": {{
        "income_stability": {{
            "rating": "excellent/good/fair/poor",
            "reasoning": "detailed assessment of income consistency",
            "seasonal_considerations": "impact of seasonal variations"
        }},
        "debt_capacity": {{
            "current_debt_to_income": "calculated ratio",
            "recommended_max_emi": "amount in rupees",
            "debt_servicing_ability": "strong/moderate/weak"
        }},
        "savings_pattern": {{
            "assessment": "disciplined/irregular/poor",
            "emergency_fund_status": "adequate/inadequate/none",
            "recommendation": "specific advice for savings improvement"
        }}
    }},
    "detailed_recommendation_reasoning": {{
        "primary_reasons_for_decision": [
            "main factor 1 with detailed explanation",
            "main factor 2 with detailed explanation"
        ],
        "conditions_if_conditional_approval": [
            {{
                "condition": "specific requirement",
                "rationale": "why this condition is necessary",
                "impact_if_not_met": "consequences"
            }}
        ],
        "monitoring_requirements": [
            {{
                "parameter": "what to monitor",
                "frequency": "how often",
                "action_triggers": "when to take action"
            }}
        ]
    }},
    "alternative_recommendations": {{
        "if_rejected": [
            {{
                "option": "alternative solution",
                "requirements": "what user needs to do",
                "timeline": "when to reapply"
            }}
        ],
        "product_alternatives": [
            {{
                "product": "alternative loan product",
                "suitability": "why this might be better",
                "terms": "different terms offered"
            }}
        ]
    }},
    "final_summary": {{
        "executive_summary": "concise 2-3 sentence summary of recommendation",
        "key_next_steps": ["immediate actions for MFI"],
        "borrower_communication": "how to communicate decision to borrower"
    }}
}}

Provide comprehensive, actionable analysis:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": analysis_prompt}
                ],
                max_tokens=3000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
            
            try:
                detailed_analysis = json.loads(result_text)
                
                # Add quantitative metrics
                detailed_analysis = self._add_quantitative_metrics(detailed_analysis, user_data, credit_result)
                
                return detailed_analysis
            except json.JSONDecodeError:
                print("Warning: Could not parse JSON response, generating fallback recommendation")
                return self._fallback_detailed_recommendation(user_data, credit_result, language)
            
        except Exception as e:
            print(f"Error generating detailed loan recommendation: {e}")
            return self._fallback_detailed_recommendation(user_data, credit_result, language)
    
    def _add_quantitative_metrics(self, analysis: Dict[str, Any], user_data: Dict[str, Any], credit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Add calculated quantitative metrics to the analysis"""
        
        try:
            # Calculate debt-to-income ratio
            monthly_income = user_data.get("occupation_income", {}).get("monthly_income", 0)
            if isinstance(monthly_income, str):
                monthly_income = float(monthly_income.replace(",", "")) if monthly_income.replace(",", "").replace(".", "").isdigit() else 0
            
            existing_loans = user_data.get("financial_history", {}).get("existing_loans", 0)
            if isinstance(existing_loans, str):
                existing_loans = float(existing_loans.replace(",", "")) if existing_loans.replace(",", "").replace(".", "").isdigit() else 0
            
            debt_to_income = (existing_loans / monthly_income * 100) if monthly_income > 0 else 0
            
            # Update financial health assessment with calculated values
            if "financial_health_assessment" in analysis:
                analysis["financial_health_assessment"]["debt_capacity"]["current_debt_to_income"] = f"{debt_to_income:.1f}%"
                analysis["financial_health_assessment"]["debt_capacity"]["recommended_max_emi"] = f"₹{monthly_income * 0.4:.0f}"
            
            return analysis
            
        except Exception as e:
            print(f"Error adding quantitative metrics: {e}")
            return analysis
    
    def _fallback_detailed_recommendation(self, user_data: Dict[str, Any], credit_result: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Fallback detailed recommendation when LLM fails"""
        
        credit_score = credit_result.get("credit_score", 0)
        risk_level = credit_result.get("risk_level", "Unknown")
        
        if credit_score >= 70:
            decision = "APPROVE"
            max_amount = "₹50,000"
            interest_rate = "12%"
        elif credit_score >= 50:
            decision = "CONDITIONAL_APPROVE" 
            max_amount = "₹25,000"
            interest_rate = "14%"
        else:
            decision = "REJECT"
            max_amount = "₹0"
            interest_rate = "N/A"
        
        return {
            "loan_recommendation": {
                "decision": decision,
                "confidence": "medium",
                "maximum_loan_amount": max_amount,
                "interest_rate_suggestion": interest_rate,
                "repayment_period": "12 months",
                "collateral_requirement": "not_required"
            },
            "detailed_risk_analysis": {
                "overall_risk_score": credit_score,
                "risk_category": risk_level.lower(),
                "key_risk_factors": [
                    {
                        "factor": "Credit score assessment",
                        "impact": "high",
                        "explanation": f"Credit score of {credit_score} indicates {risk_level.lower()} risk",
                        "mitigation_strategy": "Improve financial habits and repayment history"
                    }
                ],
                "positive_factors": [
                    {
                        "factor": "Application completeness",
                        "impact": "medium",
                        "explanation": "User provided complete information for assessment"
                    }
                ]
            },
            "final_summary": {
                "executive_summary": f"Based on credit score of {credit_score}, recommendation is {decision}",
                "key_next_steps": ["Review application details", "Verify documents", "Communicate decision"],
                "borrower_communication": "Explain decision clearly with improvement suggestions"
            }
        }
    
    def _assess_income_stability(self, user_data: Dict[str, Any], loan_amount: float) -> float:
        """Assess income stability (0-100)"""
        score = 50  # Base score
        
        occupation = user_data.get("occupation_income", {})
        
        # Monthly income
        monthly_income = occupation.get("monthly_income", "")
        if monthly_income:
            income_value = float(''.join(filter(str.isdigit, str(monthly_income))))
            income_to_loan_ratio = (income_value * 12) / loan_amount if loan_amount > 0 else 0
            
            if income_to_loan_ratio > 2:
                score += 30
            elif income_to_loan_ratio > 1:
                score += 20
            elif income_to_loan_ratio > 0.5:
                score += 10
        
        # Occupation type
        primary_occ = occupation.get("primary_occupation", "").lower()
        if "government" in primary_occ:
            score += 20
        elif "farming" in primary_occ:
            score += 10
        elif "business" in primary_occ:
            score += 15
        
        # Seasonal variation penalty
        if occupation.get("seasonal_variation", "").lower() == "yes":
            score -= 10
        
        return min(100, max(0, score))
    
    def _assess_debt_to_income(self, user_data: Dict[str, Any], loan_amount: float) -> float:
        """Assess debt-to-income ratio (0-100)"""
        score = 70  # Base score
        
        occupation = user_data.get("occupation_income", {})
        financial = user_data.get("financial_details", {})
        
        monthly_income = occupation.get("monthly_income", "")
        existing_loans = financial.get("existing_loans", "").lower()
        
        if monthly_income and "no" not in existing_loans:
            income_value = float(''.join(filter(str.isdigit, str(monthly_income))))
            
            # Estimate new EMI (rough calculation)
            estimated_emi = loan_amount * 0.02  # Assume 2% of loan amount as EMI
            debt_ratio = estimated_emi / income_value if income_value > 0 else 1
            
            if debt_ratio < 0.3:
                score += 20
            elif debt_ratio < 0.4:
                score += 10
            elif debt_ratio < 0.5:
                score -= 10
            else:
                score -= 30
        
        return min(100, max(0, score))
    
    def _assess_credit_history(self, user_data: Dict[str, Any]) -> float:
        """Assess credit history (0-100)"""
        score = 60  # Base score for new customers
        
        financial = user_data.get("financial_details", {})
        
        # Repayment history
        repayment = financial.get("repayment_history", "").lower()
        if "excellent" in repayment:
            score += 30
        elif "good" in repayment:
            score += 20
        elif "late" in repayment:
            score -= 20
        elif "missed" in repayment:
            score -= 40
        
        # Bank account status
        if financial.get("bank_account_status", "").lower() == "yes":
            score += 10
        
        return min(100, max(0, score))
    
    def _assess_collateral_value(self, user_data: Dict[str, Any], loan_amount: float, loan_type: str) -> float:
        """Assess collateral value (0-100)"""
        score = 50  # Base score
        
        land_property = user_data.get("land_property", {})
        
        if land_property.get("owns_land", "").lower() == "yes":
            score += 30
            
            # Land area consideration
            area = land_property.get("land_area", "")
            if area and any(char.isdigit() for char in area):
                score += 20
        
        # House type as collateral
        household = user_data.get("household_location", {})
        house_type = household.get("house_type", "").lower()
        if "pucca" in house_type:
            score += 20
        elif "semi" in house_type:
            score += 10
        
        return min(100, max(0, score))
    
    def _assess_social_capital(self, user_data: Dict[str, Any]) -> float:
        """Assess social capital (0-100)"""
        score = 40  # Base score
        
        financial = user_data.get("financial_details", {})
        
        # Group membership
        if financial.get("group_membership", "").lower() == "yes":
            score += 30
        
        # Community ties
        if financial.get("bank_account_status", "").lower() == "yes":
            score += 20
        
        # Phone ownership (connectivity)
        personal = user_data.get("personal_info", {})
        if personal.get("phone_number"):
            score += 10
        
        return min(100, max(0, score))
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize overall risk level"""
        if risk_score >= 80:
            return "Low Risk"
        elif risk_score >= 60:
            return "Medium Risk"
        elif risk_score >= 40:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _analyze_risk_factors(self, risk_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Analyze individual risk factors"""
        analysis = []
        
        for factor, score in risk_scores.items():
            threshold = self.risk_factors.get(factor, {}).get("threshold", 60)
            
            if score >= threshold:
                status = "Strong"
            elif score >= threshold - 20:
                status = "Adequate"
            else:
                status = "Weak"
            
            analysis.append({
                "factor": factor,
                "score": score,
                "status": status,
                "threshold": threshold,
                "weight": self.risk_factors.get(factor, {}).get("weight", 0)
            })
        
        return analysis
    
    def _generate_approval_recommendation(self, risk_score: float, loan_type: str, loan_amount: float) -> str:
        """Generate basic approval recommendation"""
        if risk_score >= 75:
            return "APPROVED - Low risk applicant, standard terms recommended"
        elif risk_score >= 60:
            return "CONDITIONAL APPROVAL - Medium risk, enhanced terms recommended"
        elif risk_score >= 45:
            return "CONDITIONAL APPROVAL - High risk, strict conditions apply"
        else:
            return "REJECTED - Very high risk, alternative products suggested"
    
    def _calculate_affordability(self, user_data: Dict[str, Any], loan_terms: Dict[str, Any]) -> float:
        """Calculate affordability score (0-100)"""
        occupation = user_data.get("occupation_income", {})
        monthly_income = occupation.get("monthly_income", "")
        monthly_expenses = occupation.get("monthly_expenses", "")
        
        if not monthly_income:
            return 50
        
        income_value = float(''.join(filter(str.isdigit, str(monthly_income))))
        expense_value = float(''.join(filter(str.isdigit, str(monthly_expenses)))) if monthly_expenses else income_value * 0.7
        
        disposable_income = income_value - expense_value
        emi = loan_terms.get("monthly_emi", 0)
        
        if disposable_income <= 0:
            return 0
        
        affordability_ratio = emi / disposable_income
        
        if affordability_ratio <= 0.3:
            return 100
        elif affordability_ratio <= 0.4:
            return 80
        elif affordability_ratio <= 0.5:
            return 60
        elif affordability_ratio <= 0.6:
            return 40
        else:
            return 20
    
    def _explain_loan_terms(self, risk_assessment: Dict[str, Any], loan_terms: Dict[str, Any], language: str) -> str:
        """Generate explanation of loan terms"""
        # Simplified explanation for now
        risk_category = risk_assessment["risk_category"]
        amount = loan_terms["recommended_amount"]
        rate = loan_terms["interest_rate"]
        tenure = loan_terms["tenure_months"]
        emi = loan_terms["monthly_emi"]
        
        return f"Based on your {risk_category.lower()} profile, we recommend a loan of ₹{amount:,.0f} at {rate}% interest for {tenure} months. Your monthly EMI would be ₹{emi:,.0f}."
    
    def _generate_comparison_summary(self, comparisons: List[Dict[str, Any]], language: str) -> str:
        """Generate summary of loan option comparisons"""
        if not comparisons:
            return "No loan options available for comparison."
        
        best_option = comparisons[0]
        summary = f"Recommended: {best_option['loan_option']['type']} loan of ₹{best_option['recommended_terms']['recommended_amount']:,.0f} "
        summary += f"at {best_option['recommended_terms']['interest_rate']}% interest with EMI of ₹{best_option['recommended_terms']['monthly_emi']:,.0f}."
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    advisor = LoanRiskAdvisorAgent()
    
    # Test with sample user data and loan request
    sample_user = {
        "personal_info": {"full_name": "Ramesh Kumar", "phone_number": "9876543210"},
        "occupation_income": {
            "primary_occupation": "farmer",
            "monthly_income": "15000",
            "monthly_expenses": "10000",
            "seasonal_variation": "yes"
        },
        "financial_details": {
            "bank_account_status": "yes",
            "existing_loans": "small agriculture loan",
            "repayment_history": "good",
            "group_membership": "yes"
        },
        "land_property": {"owns_land": "yes", "land_area": "2 acres"},
        "household_location": {"house_type": "semi-pucca"}
    }
    
    loan_request = {
        "amount": 50000,
        "type": "agriculture",
        "purpose": "crop cultivation"
    }
    
    # Assess risk
    risk_assessment = advisor.assess_loan_risk(sample_user, loan_request)
    print("Risk Assessment:")
    print(f"Overall Risk Score: {risk_assessment['overall_risk_score']}")
    print(f"Risk Category: {risk_assessment['risk_category']}")
    print(f"Approval Recommendation: {risk_assessment['approval_recommendation']}")
    
    # Get loan terms
    loan_terms = advisor.recommend_loan_terms(risk_assessment)
    print(f"\nRecommended Terms:")
    print(f"Amount: ₹{loan_terms['recommended_amount']:,.0f}")
    print(f"Interest Rate: {loan_terms['interest_rate']}%")
    print(f"EMI: ₹{loan_terms['monthly_emi']:,.0f}")
    print(f"Tenure: {loan_terms['tenure_months']} months")
