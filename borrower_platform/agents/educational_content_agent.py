"""
Educational Content Agent
Explains credit scores and improvement strategies in simple rural-friendly language
Acts as a friendly financial teacher, tailored to local context (Kannada/Hindi, respectful tone)
Provides personalized advice and increases financial literacy among SHG members and new borrowers
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

class EducationalContentAgent:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ API key is required. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
        self.client = Groq(api_key=self.groq_api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.cache = {}
        
        # Educational content categories
        self.content_categories = {
            "credit_score_basics": "Understanding what credit score means",
            "improvement_strategies": "How to improve credit score",
            "financial_planning": "Basic financial planning for rural families", 
            "loan_process": "Understanding loan application and approval process",
            "savings_habits": "Developing good savings and spending habits",
            "group_benefits": "Benefits of SHG and cooperative membership",
            "digital_banking": "Using mobile banking and digital payments",
            "risk_management": "Managing financial risks in farming and business"
        }
        
        # Local context considerations
        self.local_context = {
            "karnataka_specific": {
                "crops": ["cotton", "sugarcane", "sunflower", "maize", "ragi"],
                "festivals": ["Ugadi", "Gowri Ganesha", "Dasara", "Diwali"],
                "local_banks": ["Karnataka Bank", "Canara Bank", "Vijaya Bank"],
                "government_schemes": ["PM Kisan", "Raitha Samparka", "Bhoomi"]
            },
            "rural_occupations": ["farmer", "weaver", "dairy", "poultry", "shopkeeper", "driver"],
            "common_challenges": ["seasonal income", "crop failure", "medical emergencies", "education expenses"]
        }
    
    def explain_credit_score(self, credit_result: Dict[str, Any], user_data: Dict[str, Any], language: str = "english") -> str:
        """
        Explain credit score in simple, rural-friendly language with local context
        
        Args:
            credit_result (Dict): Credit scoring results
            user_data (Dict): User profile data for personalization
            language (str): Target language for explanation
            
        Returns:
            str: Simple, personalized credit score explanation
        """
        
        # Check cache
        cache_key = generate_cache_key({"score": credit_result, "user": user_data, "lang": language})
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        system_prompt = self._get_educational_system_prompt(language)
        
        # Get user context for personalization
        name = user_data.get("personal_info", {}).get("full_name", "")
        occupation = user_data.get("occupation_income", {}).get("primary_occupation", "")
        village = user_data.get("household_location", {}).get("village_name", "")
        
        explanation_prompt = f"""
{system_prompt}

Explain this credit score to a rural user in very simple language with local examples.

User Profile:
- Name: {name}
- Occupation: {occupation} 
- Village: {village}

Credit Score Results: {json.dumps(credit_result, indent=2)}

Create a friendly, encouraging explanation that:
1. Explains what the credit score means in simple terms
2. Uses local examples and analogies (farming, village life)
3. Highlights what they're doing well
4. Explains areas for improvement without being negative
5. Gives hope and motivation to improve
6. Uses respectful tone appropriate for rural Karnataka

Keep it conversational and under 200 words:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": explanation_prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content.strip()
            
            # Cache result
            self.cache[cache_key] = explanation
            
            return explanation
            
        except Exception as e:
            print(f"Error explaining credit score: {e}")
            return self._fallback_explanation(credit_result, language)
    
    def provide_improvement_advice(self, credit_result: Dict[str, Any], user_data: Dict[str, Any], language: str = "english") -> Dict[str, Any]:
        """
        Provide personalized advice for improving credit score with local context
        
        Args:
            credit_result (Dict): Credit scoring results
            user_data (Dict): User profile data
            language (str): Target language
            
        Returns:
            Dict: Structured improvement advice with actionable steps
        """
        
        system_prompt = self._get_educational_system_prompt(language)
        
        # Get user's actual occupation and details from flat structure
        occupation = user_data.get("primary_occupation", "").lower()
        seasonal_variation = user_data.get("seasonal_variation", "")
        monthly_income = user_data.get("monthly_income", 0)
        village = user_data.get("village_name", "")
        district = user_data.get("district", "")
        house_type = user_data.get("house_type", "")
        current_score = credit_result.get("total_score", 0)
        
        # Create occupation-specific and score-based advice
        advice_prompt = f"""
{system_prompt}

You are providing personalized financial advice to a rural user based on their specific occupation and credit profile.

User Details:
- Occupation: {occupation}
- Village: {village}, {district}
- Monthly Income: ₹{monthly_income}
- Current Credit Score: {current_score}/900
- Seasonal Income Variation: {seasonal_variation}
- House Type: {house_type}

Credit Score Analysis: {json.dumps(credit_result, indent=2)}

Provide occupation-specific advice that is:
1. Tailored to their specific job ({occupation})
2. Realistic for their income level (₹{monthly_income})
3. Appropriate for their location ({village}, {district})
4. Considers seasonal variations if applicable
5. Gives specific, actionable steps

DO NOT give generic advice. 
DO NOT recommend agricultural practices if they are not a farmer.
DO NOT suggest investments they cannot afford.

Focus on their actual occupation and provide relevant financial tips:
- For IT professionals: Tech-based savings, online banking, SIP investments
- For teachers: Regular income management, education loan benefits
- For shopkeepers: Business cash flow, inventory management, GST compliance
- For farmers: Crop insurance, seasonal planning, government schemes
- For laborers: Emergency fund building, skill development, regular savings
- For drivers: Vehicle maintenance costs, fuel efficiency, insurance

Provide specific, actionable recommendations. Be encouraging and realistic.

Create practical improvement advice as JSON with this structure:
{{
    "immediate_actions": ["action 1", "action 2"],
    "short_term_goals": ["goal 1", "goal 2"],
    "long_term_strategies": ["strategy 1", "strategy 2"],
    "local_resources": ["resource 1", "resource 2"],
    "motivation_message": "encouraging message"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": advice_prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error generating improvement advice: {e}")
            return self._fallback_advice(credit_result, user_data, language)
    
    def create_financial_education_content(self, topic: str, user_context: Dict[str, Any], language: str = "english") -> str:
        """
        Create educational content on specific financial topics
        
        Args:
            topic (str): Topic from content_categories
            user_context (Dict): User context for personalization
            language (str): Target language
            
        Returns:
            str: Educational content tailored to user context
        """
        
        if topic not in self.content_categories:
            topic = "credit_score_basics"
        
        system_prompt = self._get_educational_system_prompt(language)
        
        content_prompt = f"""
{system_prompt}

Create educational content about: {self.content_categories[topic]}

User Context: {json.dumps(user_context, indent=2)}

Create content that:
1. Explains the topic in very simple language
2. Uses local examples from Karnataka rural life
3. Gives practical, actionable advice
4. Includes stories or analogies they can relate to
5. Addresses common concerns of rural borrowers
6. Provides hope and motivation

Keep it conversational and under 300 words:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": content_prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error creating educational content: {e}")
            return f"Unable to create content about {topic}. Please try again."
    
    def generate_seasonal_financial_tips(self, user_data: Dict[str, Any], current_season: str, language: str = "english") -> List[str]:
        """
        Generate season-specific financial tips for farmers and rural users
        
        Args:
            user_data (Dict): User profile data
            current_season (str): Current agricultural season
            language (str): Target language
            
        Returns:
            List[str]: Season-specific financial tips
        """
        
        occupation = user_data.get("occupation_income", {}).get("primary_occupation", "")
        has_land = user_data.get("land_property", {}).get("owns_land", "").lower() == "yes"
        
        system_prompt = self._get_educational_system_prompt(language)
        
        tips_prompt = f"""
{system_prompt}

Generate 5 practical financial tips for this user based on the current season.

User Profile:
- Occupation: {occupation}
- Owns Land: {has_land}
- Current Season: {current_season}

Consider:
- Seasonal income patterns in Karnataka agriculture
- Harvest times and cash flow
- Festival expenses and planning
- Weather-related financial risks

Provide tips as a simple list, each under 50 words:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": tips_prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            tips_text = response.choices[0].message.content.strip()
            # Split into individual tips
            tips = [tip.strip() for tip in tips_text.split('\n') if tip.strip() and not tip.strip().startswith('#')]
            
            return tips[:5]  # Return top 5 tips
            
        except Exception as e:
            print(f"Error generating seasonal tips: {e}")
            return self._fallback_seasonal_tips(current_season, language)
    
    def _get_educational_system_prompt(self, language: str) -> str:
        """Get language-specific educational system prompt"""
        
        if language == "hindi":
            return """आप एक मित्रवत वित्तीय शिक्षक हैं जो ग्रामीण भारत के लिए सरल भाषा में वित्तीय शिक्षा प्रदान करते हैं। 
            आपकी भाषा सम्मानजनक, सरल और स्थानीय संदर्भ के अनुकूल होनी चाहिए। कर्नाटक के कृषि और ग्रामीण जीवन के उदाहरण दें।"""
        elif language == "kannada":
            return """ನೀವು ಗ್ರಾಮೀಣ ಭಾರತಕ್ಕೆ ಸರಳ ಭಾಷೆಯಲ್ಲಿ ಹಣಕಾಸು ಶಿಕ್ಷಣ ನೀಡುವ ಸ್ನೇಹಪರ ಹಣಕಾಸು ಶಿಕ್ಷಕರಾಗಿದ್ದೀರಿ। 
            ನಿಮ್ಮ ಭಾಷೆ ಗೌರವಾನ್ವಿತ, ಸರಳ ಮತ್ತು ಸ್ಥಳೀಯ ಸಂದರ್ಭಕ್ಕೆ ಸೂಕ್ತವಾಗಿರಬೇಕು. ಕರ್ನಾಟಕದ ಕೃಷಿ ಮತ್ತು ಗ್ರಾಮೀಣ ಜೀವನದ ಉದಾಹರಣೆಗಳನ್ನು ನೀಡಿ।"""
        else:
            return """You are a friendly financial teacher providing financial education in simple language for rural India. 
            Your language should be respectful, simple, and tailored to local context. Use examples from Karnataka agriculture and rural life."""
    
    def _fallback_explanation(self, credit_result: Dict[str, Any], language: str) -> str:
        """Fallback explanation when LLM fails"""
        
        score = credit_result.get("credit_score", 0)
        risk_level = credit_result.get("risk_level", "Unknown")
        
        if language == "hindi":
            return f"आपका क्रेडिट स्कोर {score} है, जो {risk_level} जोखिम श्रेणी में है। यह स्कोर आपकी आर्थिक स्थिति और ऋण चुकाने की क्षमता को दर्शाता है।"
        elif language == "kannada":
            return f"ನಿಮ್ಮ ಕ್ರೆಡಿಟ್ ಸ್ಕೋರ್ {score} ಇದೆ, ಇದು {risk_level} ಅಪಾಯ ವರ್ಗದಲ್ಲಿದೆ. ಈ ಸ್ಕೋರ್ ನಿಮ್ಮ ಆರ್ಥಿಕ ಸ್ಥಿತಿ ಮತ್ತು ಸಾಲ ಮರುಪಾವತಿ ಸಾಮರ್ಥ್ಯವನ್ನು ತೋರಿಸುತ್ತದೆ."
        else:
            return f"Your credit score is {score}, which falls in the {risk_level} risk category. This score reflects your financial health and ability to repay loans."
    
    def _fallback_advice(self, credit_result: Dict[str, Any], user_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Fallback advice structure when LLM fails"""
        
        # Get user's actual occupation to customize fallback advice
        occupation = user_data.get("primary_occupation", "").lower()
        is_farmer = any(word in occupation for word in ["farm", "agriculture", "crop"])
        
        immediate_action = {
            "action": "Document and formalize your assets",
            "explanation": "Having proper documentation increases your credibility with lenders",
            "local_example": "Get land documents, property papers, or business licenses organized"
        }
        
        if not user_data.get("bank_account_status") or user_data.get("bank_account_status", "").lower() == "no":
            immediate_action = {
                "action": "Open a bank account if you don't have one",
                "explanation": "Banks help you save money safely and build financial history",
                "local_example": "Visit your nearest bank branch with Aadhaar card"
            }
        
        seasonal_tip = "Plan your finances month by month"
        if is_farmer:
            seasonal_tip = "SHGs help during lean agricultural seasons"
        elif "engineer" in occupation or "it" in occupation:
            seasonal_tip = "Build an emergency fund for career transitions"
        
        return {
            "immediate_actions": [immediate_action],
            "short_term_goals": [
                {
                    "goal": "Increase your savings rate consistently",
                    "steps": ["Save at least 20% of monthly income", "Use systematic investment plans"],
                    "benefit": "Shows excellent financial discipline to lenders"
                }
            ],
            "long_term_strategies": [
                {
                    "strategy": "Build multiple income sources" if not is_farmer else "Join a Self Help Group (SHG)",
                    "timeline": "Benefits visible in 6-12 months",
                    "seasonal_tip": seasonal_tip
                }
            ],
            "local_resources": [
                {
                    "resource": "Local banks and cooperative societies",
                    "how_to_access": "Contact nearest branch with proper documentation",
                    "benefit": "Access to formal credit and financial services"
                }
            ],
            "motivation_message": "Your strong income foundation gives you excellent potential for building an outstanding credit profile."
        }
    
    def _fallback_seasonal_tips(self, season: str, language: str) -> List[str]:
        """Fallback seasonal tips when LLM fails"""
        
        tips = [
            "Save a portion of your harvest income for the next season",
            "Plan for festival expenses in advance",
            "Keep some money aside for medical emergencies",
            "Consider crop insurance to protect against losses",
            "Join group savings schemes in your village"
        ]
        
        return tips

# Example usage and testing
if __name__ == "__main__":
    agent = EducationalContentAgent()
    
    # Test with sample data
    sample_credit_result = {
        "credit_score": 67,
        "risk_level": "Medium",
        "recommendation": "Needs Support",
        "key_risk_factors": ["Seasonal income variation", "Limited savings habits"]
    }
    
    sample_user = {
        "personal_info": {"full_name": "Ramesh Kumar"},
        "occupation_income": {"primary_occupation": "farmer", "seasonal_variation": "yes"},
        "household_location": {"village_name": "Davangere Village"}
    }
    
    # Test credit score explanation
    explanation = agent.explain_credit_score(sample_credit_result, sample_user, "english")
    print("Credit Score Explanation:")
    print(explanation)
    
    # Test improvement advice
    advice = agent.provide_improvement_advice(sample_credit_result, sample_user, "english")
    print(f"\nImprovement Advice: {len(advice.get('immediate_actions', []))} immediate actions suggested")
    
    # Test seasonal tips
    tips = agent.generate_seasonal_financial_tips(sample_user, "Kharif", "english")
    print(f"\nSeasonal Tips: {len(tips)} tips generated")
