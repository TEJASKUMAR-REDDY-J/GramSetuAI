"""
Credit Scoring Agent
Calculates custom credit score based on structured user input using explainable rule-based or AI logic
Analyzes personal, income, group, and repayment data with domain-specific scoring
Outputs structured JSON with credit_score, risk_level, recommendation, and key_risk_factors
"""

import os
import json
import pickle
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
        
        # Domain-specific scoring weights for rural microfinance (fallback if model loading fails)
        self.scoring_weights = {
            "income_stability": 25,      # Regular income source reliability
            "repayment_history": 30,     # Past loan repayment track record
            "social_capital": 20,        # Group membership, community ties
            "asset_ownership": 15,       # Land, property ownership
            "financial_behavior": 10     # Savings habits, bank usage
        }
        
        # Load machine learning model for weights (will override scoring_weights if successful)
        self.ml_model = None
        self.model_weights = None
        self._load_model_weights()
        
        # Complete user data schema for validation (matching Gradio app structure)
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
        
        # Risk level thresholds for 300-900 score range (higher score = lower risk)
        self.risk_thresholds = {
            "very_low": 750,    # Score >= 750: Very Low risk (Excellent)
            "low": 650,         # Score 650-749: Low risk (Good)
            "medium": 550,      # Score 550-649: Medium risk (Fair)
            "high": 450,        # Score 450-549: High risk (Needs Improvement)
            "very_high": 300    # Score < 450: Very High risk (Poor)
        }
    
    def _load_model_weights(self):
        """Load machine learning model weights from pickle file"""
        try:
            model_path = "C:\\Users\\chann\\OneDrive\\Desktop\\GramSetuAI-main\\GramSetuAI-main\\student_pipeline_model.pkl"
            
            # Try loading with different protocols to handle version compatibility
            try:
                with open(model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
                print("✓ Model loaded successfully with standard pickle")
            except Exception as e1:
                print(f"Standard pickle failed: {e1}")
                try:
                    # Try with protocol 4 for compatibility
                    try:
                        import pickle5
                        with open(model_path, 'rb') as f:
                            self.ml_model = pickle5.load(f)
                        print("✓ Model loaded successfully with pickle5")
                    except ImportError:
                        print("pickle5 not available, trying joblib...")
                        # Try with joblib which often handles sklearn models better
                        try:
                            import joblib
                            self.ml_model = joblib.load(model_path)
                            print("✓ Model loaded successfully with joblib")
                        except ImportError:
                            print("joblib not available, trying pickle with compatibility settings")
                            # Try loading with ignore protocol errors
                            with open(model_path, 'rb') as f:
                                try:
                                    self.ml_model = pickle.load(f, encoding='latin1')
                                    print("✓ Model loaded with latin1 encoding")
                                except:
                                    self.ml_model = pickle.load(f, fix_imports=True, encoding='latin1')
                                    print("✓ Model loaded with fix_imports and latin1")
                except Exception as e2:
                    print(f"All loading attempts failed: {e2}")
                    print("Using fallback rule-based weights")
                    return
            
            # Extract weights from the model (assuming it has feature_importances_ or coef_)
            weights = None
            
            # Try different ways to extract weights
            if hasattr(self.ml_model, 'feature_importances_'):
                weights = self.ml_model.feature_importances_
                print("Found feature_importances_ in model")
            elif hasattr(self.ml_model, 'coef_'):
                weights = self.ml_model.coef_[0] if len(self.ml_model.coef_.shape) > 1 else self.ml_model.coef_
                print("Found coef_ in model")
            elif hasattr(self.ml_model, 'named_steps'):
                # Try to access the model from a pipeline
                print("Searching in pipeline steps...")
                for step_name, step in self.ml_model.named_steps.items():
                    print(f"Checking step: {step_name}")
                    if hasattr(step, 'feature_importances_'):
                        weights = step.feature_importances_
                        print(f"Found feature_importances_ in step {step_name}")
                        break
                    elif hasattr(step, 'coef_'):
                        weights = step.coef_[0] if len(step.coef_.shape) > 1 else step.coef_
                        print(f"Found coef_ in step {step_name}")
                        break
            elif hasattr(self.ml_model, 'steps'):
                # Alternative pipeline format
                print("Searching in pipeline steps (alternative format)...")
                for step_name, step in self.ml_model.steps:
                    print(f"Checking step: {step_name}")
                    if hasattr(step, 'feature_importances_'):
                        weights = step.feature_importances_
                        print(f"Found feature_importances_ in step {step_name}")
                        break
                    elif hasattr(step, 'coef_'):
                        weights = step.coef_[0] if len(step.coef_.shape) > 1 else step.coef_
                        print(f"Found coef_ in step {step_name}")
                        break
            
            if weights is None:
                print("Warning: Could not extract weights from model, using default weights")
                return
            
            print(f"Extracted weights: {weights[:min(10, len(weights))]}")  # Show first 10 weights
            
            # Map model weights to our scoring categories (assuming 5 main features)
            if len(weights) >= 5:
                # Normalize weights to percentages
                total_weight = sum(abs(w) for w in weights[:5])
                if total_weight > 0:
                    new_weights = {
                        "income_stability": round((abs(weights[0]) / total_weight) * 100, 1),
                        "repayment_history": round((abs(weights[1]) / total_weight) * 100, 1),
                        "social_capital": round((abs(weights[2]) / total_weight) * 100, 1),
                        "asset_ownership": round((abs(weights[3]) / total_weight) * 100, 1),
                        "financial_behavior": round((abs(weights[4]) / total_weight) * 100, 1)
                    }
                    print(f"Calculated new weights: {new_weights}")
                    self.scoring_weights = new_weights
                    print(f"Assigned weights to self.scoring_weights: {self.scoring_weights}")
                    print(f"Model weights loaded successfully: {self.scoring_weights}")
                else:
                    print("Warning: All model weights are zero, using default weights")
            else:
                print(f"Warning: Model has {len(weights)} features, expected at least 5, using default weights")
                
        except Exception as e:
            print(f"Warning: Could not load model weights from {model_path}: {e}")
            print("Using default scoring weights")
    
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
            field_value = user_data.get(field_name)
            
            # Check if field has meaningful data
            is_provided = False
            if field_value is not None:
                if isinstance(field_value, str):
                    # String field is provided if it's not empty and not just whitespace
                    is_provided = field_value.strip() != ""
                elif isinstance(field_value, (int, float)):
                    # Numeric field is provided if it's not zero (assuming zero means not provided)
                    is_provided = field_value != 0
                else:
                    # Other types are provided if they exist
                    is_provided = True
            
            if is_provided:
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
        Explain how the credit scoring system works based on actual model weights
        
        Args:
            user_data (Dict): Optional user data for personalized explanation
            
        Returns:
            str: Dynamic explanation of credit scoring system
        """
        
        # Get current weights (either from model or fallback)
        current_weights = self.scoring_weights
        model_status = "ML Model" if hasattr(self, 'ml_model') and self.ml_model else "Rule-based"
        
        explanation = f"""
**How Our Credit Scoring System Works ({model_status})**

Our microfinance credit scoring system evaluates your loan eligibility based on 5 key factors with the following weightings:

**1. Repayment History ({current_weights['repayment_history']}% weight):**
- Past loan repayment track record
- Credit history from banks or microfinance institutions
- Consistency in meeting financial obligations
- Group loan performance if applicable

**2. Income Stability ({current_weights['income_stability']}% weight):**
- Primary occupation reliability and consistency
- Monthly income amount and seasonal variations
- Secondary income sources and diversification
- Income growth trends over time

**3. Social Capital ({current_weights['social_capital']}% weight):**
- Membership in Self Help Groups (SHGs)
- Community standing and references
- Family and social network support
- Participation in local organizations

**4. Asset Ownership ({current_weights['asset_ownership']}% weight):**
- Land ownership and property assets
- Livestock, equipment, and productive assets
- Collateral availability for securing loans
- Asset quality and market value

**5. Financial Behavior ({current_weights['financial_behavior']}% weight):**
- Banking relationship and account usage
- Savings patterns and financial discipline
- Digital payment adoption
- Money management skills

**Credit Score Range: 300-900 (Higher Score = Lower Risk)**
- 750-900: Very Low Risk (Excellent Credit)
- 650-749: Low Risk (Good Credit)
- 550-649: Medium Risk (Fair Credit)
- 450-549: High Risk (Needs Improvement)
- 300-449: Very High Risk (Poor Credit)
"""

        # Add personalized section if user data provided
        if user_data:
            try:
                score_result = self.calculate_credit_score(user_data)
                score = score_result.get('credit_score', 0)
                factor_scores = score_result.get('factor_scores', {})
                
                explanation += f"""

**Your Current Profile Analysis:**
- **Overall Credit Score:** {score}/900
- **Risk Category:** {self._determine_risk_level(score)}

**Your Factor Breakdown:**
"""
                for factor, score_val in factor_scores.items():
                    weight = current_weights.get(factor, 0)
                    contribution = (score_val * weight) / 100
                    factor_name = factor.replace('_', ' ').title()
                    explanation += f"- **{factor_name}:** {score_val}/100 (Contributes {contribution:.1f} points)\n"
                
                # Add improvement suggestions
                explanation += self._generate_improvement_suggestions(factor_scores)
                
            except Exception as e:
                explanation += f"\n*Note: Unable to calculate personalized analysis: {e}*"
        
        return explanation

    def _generate_improvement_suggestions(self, factor_scores: Dict[str, Any]) -> str:
        """Generate personalized improvement suggestions based on factor scores"""
        suggestions = "\n**Areas for Improvement:**\n"
        
        # Find the lowest scoring factors
        sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1])
        
        for factor, score in sorted_factors[:3]:  # Top 3 areas for improvement
            if score < 70:  # Only suggest improvements for scores below 70
                factor_name = factor.replace('_', ' ').title()
                if factor == 'repayment_history':
                    suggestions += f"- **{factor_name}**: Consider joining an SHG to build credit history\n"
                elif factor == 'income_stability':
                    suggestions += f"- **{factor_name}**: Diversify income sources or improve business consistency\n"
                elif factor == 'social_capital':
                    suggestions += f"- **{factor_name}**: Join local groups or cooperative societies\n"
                elif factor == 'asset_ownership':
                    suggestions += f"- **{factor_name}**: Document and formalize asset ownership\n"
                elif factor == 'financial_behavior':
                    suggestions += f"- **{factor_name}**: Maintain regular savings and bank account usage\n"
        
        return suggestions

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
        
        # 1. Income Stability (0-100)
        income_score = min(100, max(0, self._score_income_stability(user_data)))
        scores["income_stability"] = income_score
        
        # 2. Repayment History (0-100)
        repayment_score = min(100, max(0, self._score_repayment_history(user_data)))
        scores["repayment_history"] = repayment_score
        
        # 3. Social Capital (0-100)
        social_score = min(100, max(0, self._score_social_capital(user_data)))
        scores["social_capital"] = social_score
        
        # 4. Asset Ownership (0-100)
        asset_score = min(100, max(0, self._score_asset_ownership(user_data)))
        scores["asset_ownership"] = asset_score
        
        # 5. Financial Behavior (0-100)
        financial_score = min(100, max(0, self._score_financial_behavior(user_data)))
        scores["financial_behavior"] = financial_score
        
        # Calculate weighted total score (0-100 range)
        # Each factor score is 0-100, and weights are percentages that sum to 100
        total_score = (
            (income_score * self.scoring_weights["income_stability"] / 100) +
            (repayment_score * self.scoring_weights["repayment_history"] / 100) +
            (social_score * self.scoring_weights["social_capital"] / 100) +
            (asset_score * self.scoring_weights["asset_ownership"] / 100) +
            (financial_score * self.scoring_weights["financial_behavior"] / 100)
        )
        
        # Ensure total_score is within 0-100 range
        total_score = min(100, max(0, total_score))
        
        # Convert to 300-900 credit score range
        credit_score_300_900 = 300 + (total_score * 6.0)  # Maps 0-100 to 300-900
        
        return {
            "credit_score": round(credit_score_300_900, 0),
            "scoring_method": "rule_based",
            "factor_scores": scores,
            "calculation_details": {
                "total_base_score": round(total_score, 2),
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
            "credit_score": "score from 300-900",
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
            
            # Convert AI score to 300-900 range if it's in 0-100 range
            if "credit_score" in ai_result:
                score = float(ai_result["credit_score"])
                if score <= 100:  # If score is in 0-100 range, convert to 300-900
                    ai_result["credit_score"] = round(300 + (score * 6.0), 0)
            
            return ai_result
            
        except Exception as e:
            print(f"Error in AI-backed scoring: {e}")
            # Fallback to rule-based scoring
            return self._rule_based_scoring(user_data)
    
    def _score_income_stability(self, user_data: Dict[str, Any]) -> int:
        """Score income stability (0-100)"""
        score = 10  # Base score
        
        # Primary occupation scoring - directly from flat structure
        primary_occ = user_data.get("primary_occupation", "").lower()
        if any(word in primary_occ for word in ["government", "teacher", "clerk", "officer", "engineer", "doctor"]):
            score += 40  # Very stable income
        elif any(word in primary_occ for word in ["farming", "farmer", "agriculture"]):
            score += 25  # Seasonal but predictable
        elif any(word in primary_occ for word in ["business", "shop", "trade", "entrepreneur"]):
            score += 30  # Variable but self-controlled
        elif any(word in primary_occ for word in ["labor", "worker", "daily"]):
            score += 15  # Uncertain income
        else:
            score += 20  # Other occupations
        
        # Income amount consideration - directly from flat structure
        monthly_income = user_data.get("monthly_income", 0)
        if monthly_income:
            try:
                income_value = float(monthly_income) if isinstance(monthly_income, (int, float)) else float(''.join(filter(str.isdigit, str(monthly_income))))
                if income_value >= 100000:  # High income
                    score += 25
                elif income_value >= 50000:  # Good income
                    score += 20
                elif income_value >= 20000:  # Decent income
                    score += 15
                elif income_value >= 15000:  # Fair income
                    score += 10
                elif income_value >= 10000:  # Low income
                    score += 5
            except:
                pass
        
        # Seasonal variation penalty - directly from flat structure
        seasonal_var = user_data.get("seasonal_variation", "").lower()
        if seasonal_var in ["yes", "high", "significant"]:
            score -= 5
        elif seasonal_var in ["none", "no", "minimal", "low"]:
            score += 5
        
        # Secondary income bonus - directly from flat structure
        secondary_income = user_data.get("secondary_income_sources", "")
        if secondary_income and secondary_income.strip() and secondary_income.lower() not in ["none", "no"]:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_repayment_history(self, user_data: Dict[str, Any]) -> int:
        """Score repayment history (0-100)"""
        score = 40  # Base score for new customers
        
        # Repayment history analysis - directly from flat structure
        repayment = user_data.get("repayment_history", "").lower()
        if any(word in repayment for word in ["excellent", "perfect", "always on time", "outstanding"]):
            score += 40
        elif any(word in repayment for word in ["good", "regular", "no issues", "consistent"]):
            score += 30
        elif any(word in repayment for word in ["fair", "occasional delay", "sometimes late"]):
            score += 10
        elif any(word in repayment for word in ["late", "missed", "delayed"]):
            score -= 15
        elif any(word in repayment for word in ["bad", "poor", "irregular", "defaulted"]):
            score -= 30
        elif repayment in ["", "none", "no history", "new_borrower", "new borrower"]:
            score += 5  # No negative history is slightly positive
        
        # Existing loans impact - directly from flat structure
        existing_loans = user_data.get("existing_loans", "").lower()
        if existing_loans in ["no", "none", ""] or not existing_loans:
            score += 10  # No current debt burden
        elif any(word in existing_loans for word in ["small", "minor", "manageable", "one"]):
            score += 5
        elif any(word in existing_loans for word in ["large", "multiple", "heavy", "many"]):
            score -= 10
        
        # Past loan experience - directly from flat structure
        past_loans = user_data.get("past_loan_amounts", "")
        if past_loans and past_loans.lower() not in ["never", "none", "no", ""]:
            score += 5  # Has borrowing experience
        
        return min(100, max(0, score))
    
    def _score_social_capital(self, user_data: Dict[str, Any]) -> int:
        """Score social capital and community ties (0-100)"""
        score = 20  # Base score
        
        # Group membership (very important in microfinance) - directly from flat structure
        group_membership = user_data.get("group_membership", "").lower()
        if any(word in group_membership for word in ["shg", "cooperative", "society", "group", "association", "member"]):
            score += 35  # Strong community ties
        elif group_membership in ["yes", "y"]:
            score += 30  # Has some group membership
        elif group_membership in ["no", "none", ""]:
            score += 0  # No penalty for no membership
        
        # Bank account (financial inclusion) - directly from flat structure
        bank_account = user_data.get("bank_account_status", "").lower()
        if any(word in bank_account for word in ["have", "yes", "active", "account"]):
            score += 25
        
        # Phone number (connectivity and reachability) - directly from flat structure
        phone = user_data.get("phone_number", "")
        if phone and phone.strip() and len(phone.strip()) >= 10:
            score += 10
        
        # Digital literacy bonus
        smartphone = user_data.get("owns_smartphone", "").lower()
        if smartphone in ["yes", "y"]:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_asset_ownership(self, user_data: Dict[str, Any]) -> int:
        """Score asset ownership (0-100)"""
        score = 10  # Base score
        
        # Land ownership (major asset) - directly from flat structure
        owns_land = user_data.get("owns_land", "").lower()
        if owns_land in ["yes", "y"]:
            score += 40
            
            # Land area bonus - directly from flat structure
            land_area = user_data.get("land_area", "")
            if land_area:
                area_str = str(land_area).lower()
                # Extract numeric value from land area
                try:
                    area_num = float(''.join(filter(str.isdigit, area_str)))
                    if "acre" in area_str:
                        if area_num >= 5:
                            score += 25  # Large land holding
                        elif area_num >= 2:
                            score += 20  # Medium land holding
                        elif area_num >= 1:
                            score += 15  # Small land holding
                        else:
                            score += 10
                    elif "gunta" in area_str or "cent" in area_str:
                        if area_num >= 100:
                            score += 20
                        elif area_num >= 50:
                            score += 15
                        else:
                            score += 10
                except:
                    score += 10  # Has land area mentioned
            
            # Land type bonus - directly from flat structure
            land_type = user_data.get("land_type", "").lower()
            if "commercial" in land_type:
                score += 15  # Commercial land is more valuable
            elif "agricultural" in land_type or "farm" in land_type:
                score += 10  # Agricultural land
            elif "residential" in land_type:
                score += 12  # Residential land
        
        # House type - directly from flat structure
        house_type = user_data.get("house_type", "").lower()
        if "pucca" in house_type or "concrete" in house_type:
            score += 15
        elif "semi" in house_type:
            score += 10
        elif "kachcha" in house_type or "temporary" in house_type:
            score += 5
        
        # Electricity connection - directly from flat structure
        electricity = user_data.get("electricity_connection", "").lower()
        if electricity in ["yes", "y"]:
            score += 5
        
        return min(100, max(0, score))
    
    def _score_financial_behavior(self, user_data: Dict[str, Any]) -> int:
        """Score financial behavior and savings habits (0-100)"""
        score = 20  # Base score
        
        # Savings habit - directly from flat structure
        savings = user_data.get("savings_per_month", 0)
        if savings:
            try:
                savings_value = float(savings) if isinstance(savings, (int, float)) else float(''.join(filter(str.isdigit, str(savings))))
                if savings_value >= 50000:  # Excellent savings
                    score += 40
                elif savings_value >= 20000:  # Very good savings
                    score += 35
                elif savings_value >= 10000:  # Good savings
                    score += 30
                elif savings_value >= 5000:  # Fair savings
                    score += 25
                elif savings_value >= 2000:  # Some savings
                    score += 20
                elif savings_value > 0:  # Any savings
                    score += 15
            except:
                pass
        
        # Income vs expenses management - directly from flat structure
        monthly_income = user_data.get("monthly_income", 0)
        monthly_expenses = user_data.get("monthly_expenses", 0)
        if monthly_income and monthly_expenses:
            try:
                income_val = float(monthly_income) if isinstance(monthly_income, (int, float)) else float(''.join(filter(str.isdigit, str(monthly_income))))
                expense_val = float(monthly_expenses) if isinstance(monthly_expenses, (int, float)) else float(''.join(filter(str.isdigit, str(monthly_expenses))))
                if income_val > expense_val:
                    ratio = (income_val - expense_val) / income_val
                    if ratio >= 0.5:  # Saves 50%+ of income
                        score += 20
                    elif ratio >= 0.3:  # Saves 30%+ of income
                        score += 15
                    elif ratio >= 0.1:  # Saves 10%+ of income
                        score += 10
                    else:  # Lives within means
                        score += 5
            except:
                pass
        
        # Banking behavior - directly from flat structure
        bank_name = user_data.get("bank_name", "")
        if bank_name and bank_name.strip() and bank_name.lower() not in ["none", "no"]:
            score += 10  # Has specific bank relationship
        
        return min(100, max(0, score))
    
    def _determine_risk_level(self, credit_score: float) -> str:
        """Determine risk level based on credit score (higher score = lower risk)"""
        if credit_score >= self.risk_thresholds["very_low"]:
            return "Very Low"
        elif credit_score >= self.risk_thresholds["low"]:
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
        
        if risk_level in ["Very Low", "Low"]:
            return "Approved"
        elif risk_level == "Medium":
            return "Conditional Approval"
        elif risk_level == "High":
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
