"""
User Onboarding Agent
Entry point of the system - Collects and validates structured user data during first interaction
Conversationally guides users through multilingual data collection with voice/text support
Validates fields like Aadhaar, phone, income format and saves standardized JSON
Works offline/low-connectivity with voice + translation + memory
"""

import os
import json
import time
from groq import Groq
from typing import Dict, Any, Optional, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, validate_user_data, extract_language_from_text, generate_cache_key
from .translation_agent import TranslationAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UserOnboardingAgent:
    def __init__(self, groq_api_key: str = None):
        """
        Initialize User Onboarding Agent with GROQ for language processing
        
        Args:
            groq_api_key: GROQ API key (optional, loads from environment if not provided)
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ API key is required. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
        
        self.client = Groq(api_key=self.groq_api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.cache = {}
        self.translator = TranslationAgent(self.groq_api_key)
        
        # Standardized user data schema
        self.user_data_schema = {
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
        
    def extract_user_info(self, user_input: str, language: str = "english", existing_data: Dict = None) -> Dict[str, Any]:
        """
        Extract user information from natural language input and structure it
        
        Args:
            user_input (str): Raw user input (voice transcription or text)
            language (str): Target language for response
            existing_data (Dict): Existing user data to update
            
        Returns:
            Dict: Structured user information
        """
        
        # Auto-detect language if not specified
        detected_lang = extract_language_from_text(user_input)
        if language == "english" and detected_lang != "english":
            language = detected_lang
        
        # Get user's preferred language from existing data
        user_preferred_language = "english"
        if existing_data:
            user_preferred_language = self.translator.get_user_preferred_language(existing_data)
        
        # Translate user input to English for processing
        english_input = user_input
        if language != "english":
            translation_result = self.translator.translate_to_english(user_input, language)
            if translation_result["success"]:
                english_input = translation_result["translated_text"]
        
        # Check cache
        cache_key = generate_cache_key({"input": english_input, "lang": language})
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            # Translate response back to user's preferred language
            if user_preferred_language != "english" and "response" in cached_result:
                cached_result["response"] = self.translator.translate_response_to_user_language(
                    cached_result["response"], {"preferred_language": user_preferred_language}
                )
            return cached_result
        
        # Get language-specific system prompt
        system_prompt = get_language_prompt(language, "onboarding_system")
        
        # Create extraction prompt
        extraction_prompt = f"""
{system_prompt}

Extract the following information from the user's input and return it as a structured JSON. Fill only the fields mentioned by the user, leave others empty.

Required JSON structure:
{{
    "personal_info": {{
        "full_name": "",
        "age": "",
        "gender": "",
        "preferred_language": "",
        "aadhaar_number": "",
        "phone_number": "",
        "marital_status": "",
        "voter_id": ""
    }},
    "household_location": {{
        "village_name": "",
        "district": "",
        "state": "Karnataka",
        "pincode": "",
        "house_type": "",
        "electricity_connection": "",
        "number_of_dependents": ""
    }},
    "occupation_income": {{
        "primary_occupation": "",
        "secondary_income_sources": "",
        "monthly_income": "",
        "monthly_expenses": "",
        "seasonal_variation": ""
    }},
    "financial_details": {{
        "bank_account_status": "",
        "bank_name": "",
        "existing_loans": "",
        "repayment_history": "",
        "savings_per_month": "",
        "group_membership": "",
        "past_loan_amounts": ""
    }},
    "land_property": {{
        "owns_land": "",
        "land_area": "",
        "land_type": "",
        "patta_or_katha_number": "",
        "property_location": ""
    }},
    "digital_literacy": {{
        "owns_smartphone": "",
        "knows_how_to_use_apps": "",
        "preferred_mode_of_communication": "",
        "internet_availability": ""
    }},
    "additional_notes": {{
        "user_notes": "",
        "agent_observations": ""
    }}
}}

User Input: {user_input}

Extract information and return ONLY the JSON structure:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": extraction_prompt}
                ],
                max_tokens=1500,
                temperature=0  # Deterministic output
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Parse JSON from response
            if extracted_text.startswith('```json'):
                extracted_text = extracted_text.split('```json')[1].split('```')[0]
            elif extracted_text.startswith('```'):
                extracted_text = extracted_text.split('```')[1]
                
            extracted_data = json.loads(extracted_text)
            
            # Merge with existing data if provided
            if existing_data:
                for category, fields in extracted_data.items():
                    if category in existing_data:
                        for field, value in fields.items():
                            if value:  # Only update non-empty values
                                existing_data[category][field] = value
                    else:
                        existing_data[category] = fields
                extracted_data = existing_data
                
            # Validate data structure
            validated_data = validate_user_data(extracted_data)
            
            # Cache result
            self.cache[cache_key] = validated_data
            
            return validated_data
            
        except Exception as e:
            print(f"Error extracting user info: {e}")
            return validate_user_data({})
    
    def conversational_data_collection(self, user_input: str, conversation_state: Dict = None, language: str = "english") -> Dict[str, Any]:
        """
        Conversationally guide user through complete data collection process
        
        Args:
            user_input (str): User's response to current question
            conversation_state (Dict): Current state of conversation and collected data
            language (str): User's preferred language
            
        Returns:
            Dict: Updated conversation state with collected data and next question
        """
        
        if not conversation_state:
            conversation_state = {
                "stage": "greeting",
                "collected_data": self.get_empty_user_template(),
                "current_field": None,
                "completed_sections": [],
                "conversation_history": []
            }
        
        # Extract information from current input
        if user_input.strip():
            extracted = self.extract_user_info(user_input, language, conversation_state["collected_data"])
            conversation_state["collected_data"] = extracted
            
            # Add to conversation history
            conversation_state["conversation_history"].append({
                "user_input": user_input,
                "timestamp": time.time(),
                "language": language
            })
        
        # Determine next question based on current completeness
        validation = self.validate_completeness(conversation_state["collected_data"])
        
        if validation["is_complete"]:
            next_question = self._generate_completion_message(conversation_state["collected_data"], language)
            conversation_state["stage"] = "completed"
        else:
            next_question = self._generate_next_question(conversation_state, language)
            
        conversation_state["next_question"] = next_question
        conversation_state["completeness_score"] = validation["completeness_score"]
        
        return conversation_state
    
    def generate_conversational_questions(self, partial_data: Dict[str, Any], language: str = "english") -> List[str]:
        """
        Generate conversational questions to collect missing information
        
        Args:
            partial_data (Dict): Partially collected user data
            language (str): Target language for questions
            
        Returns:
            List[str]: List of conversational questions
        """
        
        # Identify missing fields
        validation = self.validate_completeness(partial_data)
        missing_fields = validation.get("missing_required_fields", [])
        
        # Generate questions for missing fields
        questions = []
        for field in missing_fields[:5]:  # Limit to 5 questions
            question = self._generate_localized_question(field, language)
            if question:
                questions.append(question)
        
        return questions
    
    def validate_field_format(self, field_name: str, field_value: str) -> Dict[str, Any]:
        """
        Validate specific field formats (Aadhaar, phone, income, etc.)
        
        Args:
            field_name (str): Name of the field to validate
            field_value (str): Value to validate
            
        Returns:
            Dict: Validation result with status and suggestions
        """
        
        validation_result = {
            "is_valid": True,
            "formatted_value": field_value,
            "error_message": "",
            "suggestions": []
        }
        
        # Aadhaar number validation
        if field_name == "aadhaar_number":
            # Remove spaces and check if 12 digits
            clean_aadhaar = ''.join(filter(str.isdigit, field_value))
            if len(clean_aadhaar) == 12:
                validation_result["formatted_value"] = f"{clean_aadhaar[:4]} {clean_aadhaar[4:8]} {clean_aadhaar[8:]}"
            else:
                validation_result["is_valid"] = False
                validation_result["error_message"] = "Aadhaar number should be 12 digits"
                validation_result["suggestions"] = ["Please provide your 12-digit Aadhaar number"]
        
        # Phone number validation
        elif field_name == "phone_number":
            clean_phone = ''.join(filter(str.isdigit, field_value))
            if len(clean_phone) == 10:
                validation_result["formatted_value"] = clean_phone
            elif len(clean_phone) == 11 and clean_phone.startswith('0'):
                validation_result["formatted_value"] = clean_phone[1:]
            else:
                validation_result["is_valid"] = False
                validation_result["error_message"] = "Phone number should be 10 digits"
                validation_result["suggestions"] = ["Please provide your 10-digit mobile number"]
        
        # Income validation
        elif field_name in ["monthly_income", "monthly_expenses", "savings_per_month"]:
            try:
                income_value = float(''.join(filter(str.isdigit, field_value)))
                if income_value > 0:
                    validation_result["formatted_value"] = str(int(income_value))
                else:
                    validation_result["is_valid"] = False
                    validation_result["error_message"] = "Amount should be greater than 0"
            except:
                validation_result["is_valid"] = False
                validation_result["error_message"] = "Please provide amount in numbers"
                validation_result["suggestions"] = ["Example: 15000 for fifteen thousand rupees"]
        
        return validation_result
    
    def _generate_next_question(self, conversation_state: Dict, language: str) -> str:
        """Generate contextual next question based on conversation state"""
        
        collected_data = conversation_state["collected_data"]
        
        # Priority order for data collection
        priority_fields = [
            ("personal_info", "full_name", "What is your full name?"),
            ("personal_info", "age", "How old are you?"),
            ("personal_info", "phone_number", "What is your mobile phone number?"),
            ("household_location", "village_name", "Which village are you from?"),
            ("household_location", "district", "Which district is your village in?"),
            ("occupation_income", "primary_occupation", "What is your main occupation or work?"),
            ("occupation_income", "monthly_income", "What is your approximate monthly income?"),
            ("financial_details", "bank_account_status", "Do you have a bank account?"),
            ("land_property", "owns_land", "Do you own any land or property?")
        ]
        
        # Find next missing field
        for category, field, question in priority_fields:
            if not collected_data.get(category, {}).get(field):
                return self._localize_question(question, language)
        
        # If all priority fields collected, ask for optional details
        return self._generate_completion_message(collected_data, language)
    
    def _generate_completion_message(self, user_data: Dict, language: str) -> str:
        """Generate completion message with summary"""
        
        name = user_data.get("personal_info", {}).get("full_name", "")
        village = user_data.get("household_location", {}).get("village_name", "")
        occupation = user_data.get("occupation_income", {}).get("primary_occupation", "")
        
        if language == "hindi":
            return f"धन्यवाद {name} जी! आपकी जानकारी पूरी हो गई है। आप {village} गांव से हैं और {occupation} का काम करते हैं। क्या यह जानकारी सही है?"
        elif language == "kannada":
            return f"ಧನ್ಯವಾದಗಳು {name} ಅವರೇ! ನಿಮ್ಮ ಮಾಹಿತಿ ಪೂರ್ಣಗೊಂಡಿದೆ। ನೀವು {village} ಗ್ರಾಮದಿಂದ ಮತ್ತು {occupation} ಕೆಲಸ ಮಾಡುತ್ತೀರಿ। ಈ ಮಾಹಿತಿ ಸರಿಯಾಗಿದೆಯೇ?"
        else:
            return f"Thank you {name}! I have collected your information. You are from {village} village and work as {occupation}. Is this information correct?"
    
    def _localize_question(self, question: str, language: str) -> str:
        """Localize question to target language"""
        
        question_translations = {
            "What is your full name?": {
                "hindi": "आपका पूरा नाम क्या है?",
                "kannada": "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?"
            },
            "How old are you?": {
                "hindi": "आपकी उम्र कितनी है?",
                "kannada": "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?"
            },
            "What is your mobile phone number?": {
                "hindi": "आपका मोबाइल नंबर क्या है?",
                "kannada": "ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಏನು?"
            },
            "Which village are you from?": {
                "hindi": "आप किस गांव से हैं?",
                "kannada": "ನೀವು ಯಾವ ಗ್ರಾಮದಿಂದ?"
            },
            "Which district is your village in?": {
                "hindi": "आपका गांव किस जिले में है?",
                "kannada": "ನಿಮ್ಮ ಗ್ರಾಮ ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿದೆ?"
            },
            "What is your main occupation or work?": {
                "hindi": "आपका मुख्य काम या व्यवसाय क्या है?",
                "kannada": "ನಿಮ್ಮ ಮುಖ್ಯ ಕೆಲಸ ಅಥವಾ ವ್ಯವಸಾಯ ಏನು?"
            },
            "What is your approximate monthly income?": {
                "hindi": "आपकी लगभग मासिक आय कितनी है?",
                "kannada": "ನಿಮ್ಮ ಅಂದಾಜು ಮಾಸಿಕ ಆದಾಯ ಎಷ್ಟು?"
            },
            "Do you have a bank account?": {
                "hindi": "क्या आपका बैंक खाता है?",
                "kannada": "ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆ ಇದೆಯೇ?"
            },
            "Do you own any land or property?": {
                "hindi": "क्या आपके पास कोई जमीन या संपत्ति है?",
                "kannada": "ನಿಮ್ಮ ಬಳಿ ಯಾವುದೇ ಭೂಮಿ ಅಥವಾ ಆಸ್ತಿ ಇದೆಯೇ?"
            }
        }
        
        if language in question_translations.get(question, {}):
            return question_translations[question][language]
        return question
    
    def get_empty_user_template(self) -> Dict[str, Any]:
        """Get empty user data template"""
        return validate_user_data({})
    
    def ask_clarifying_questions(self, user_data: Dict[str, Any], language: str = "english") -> str:
        """
        Generate clarifying questions for missing or incomplete information
        
        Args:
            user_data (Dict): Current user data
            language (str): Target language for questions
            
        Returns:
            str: Clarifying questions
        """
        
        # Get language-specific system prompt
        system_prompt = get_language_prompt(language, "onboarding_system")
        
        # Find missing critical fields
        missing_fields = []
        critical_fields = [
            ("personal_info", "full_name"),
            ("personal_info", "age"),
            ("personal_info", "phone_number"),
            ("household_location", "village_name"),
            ("occupation_income", "primary_occupation"),
            ("occupation_income", "monthly_income"),
            ("financial_details", "bank_account_status")
        ]
        
        for category, field in critical_fields:
            if not user_data.get(category, {}).get(field):
                missing_fields.append((category, field))
        
        if not missing_fields:
            return "Thank you! I have collected all the necessary information."
        
        question_prompt = f"""
{system_prompt}

Based on the missing information, ask 2-3 friendly clarifying questions to complete the user profile for microfinance services.

Missing fields: {missing_fields}

Current user data: {json.dumps(user_data, indent=2)}

Generate friendly, simple questions that a rural user can easily understand and answer:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": question_prompt}
                ],
                max_tokens=500,
                temperature=0  # Deterministic output
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return "Could you please provide your name, age, and village?"
    
    def validate_completeness(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if user data is complete enough for loan processing
        
        Args:
            user_data (Dict): User data to validate
            
        Returns:
            Dict: Validation results with score and missing fields
        """
        
        required_fields = [
            ("personal_info", "full_name"),
            ("personal_info", "age"), 
            ("personal_info", "phone_number"),
            ("household_location", "village_name"),
            ("household_location", "district"),
            ("occupation_income", "primary_occupation"),
            ("occupation_income", "monthly_income"),
            ("financial_details", "bank_account_status")
        ]
        
        optional_fields = [
            ("personal_info", "aadhaar_number"),
            ("household_location", "pincode"),
            ("financial_details", "existing_loans"),
            ("land_property", "owns_land")
        ]
        
        completed_required = 0
        completed_optional = 0
        missing_required = []
        
        for category, field in required_fields:
            if user_data.get(category, {}).get(field):
                completed_required += 1
            else:
                missing_required.append(f"{category}.{field}")
                
        for category, field in optional_fields:
            if user_data.get(category, {}).get(field):
                completed_optional += 1
        
        completeness_score = (completed_required / len(required_fields)) * 80 + (completed_optional / len(optional_fields)) * 20
        
        return {
            "completeness_score": round(completeness_score, 2),
            "is_complete": completeness_score >= 80,
            "missing_required_fields": missing_required,
            "completed_required": completed_required,
            "total_required": len(required_fields)
        }
    
    def save_user_profile(self, user_data: Dict[str, Any], file_path: str = None) -> bool:
        """
        Save user profile to JSON file
        
        Args:
            user_data (Dict): User data to save
            file_path (str): Path to save file
            
        Returns:
            bool: Success status
        """
        
        if not file_path:
            user_name = user_data.get("personal_info", {}).get("full_name", "unknown")
            file_path = f"data/user_profiles/{user_name.replace(' ', '_').lower()}_profile.json"
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False
    
    def update_preferred_language(self, user_data: Dict[str, Any], new_language: str) -> Dict[str, Any]:
        """
        Update user's preferred language at any time during interaction
        
        Args:
            user_data (Dict): User profile data
            new_language (str): New preferred language (english, hindi, kannada)
            
        Returns:
            Dict: Updated user data and confirmation message
        """
        updated_data = self.translator.update_user_preferred_language(user_data, new_language)
        
        confirmation_messages = {
            "english": f"Language preference updated to {new_language.title()}. All future interactions will be in {new_language}.",
            "hindi": f"भाषा प्राथमिकता {new_language} में अपडेट की गई। भविष्य की सभी बातचीत {new_language} में होगी।",
            "kannada": f"ಭಾಷಾ ಆದ್ಯತೆಯನ್ನು {new_language} ಗೆ ಅಪ್‌ಡೇಟ್ ಮಾಡಲಾಗಿದೆ। ಭವಿಷ್ಯದ ಎಲ್ಲಾ ಸಂವಾದಗಳು {new_language} ನಲ್ಲಿ ಇರುತ್ತವೆ।"
        }
        
        confirmation = confirmation_messages.get(new_language, confirmation_messages["english"])
        
        return {
            "updated_data": updated_data,
            "confirmation_message": confirmation,
            "success": True
        }
    
    def _generate_localized_question(self, field: str, language: str) -> str:
        """
        Generate a localized question for a specific field
        
        Args:
            field (str): Field name to generate question for
            language (str): Target language
            
        Returns:
            str: Localized question
        """
        
        # Question templates by language
        questions = {
            "english": {
                "full_name": "What is your full name?",
                "age": "How old are you?",
                "phone_number": "What is your mobile number?",
                "village_name": "Which village are you from?",
                "primary_occupation": "What is your main occupation?",
                "monthly_income": "What is your monthly income?",
                "bank_account_status": "Do you have a bank account?"
            },
            "hindi": {
                "full_name": "आपका पूरा नाम क्या है?",
                "age": "आपकी उम्र क्या है?",
                "phone_number": "आपका मोबाइल नंबर क्या है?",
                "village_name": "आप किस गांव से हैं?",
                "primary_occupation": "आपका मुख्य व्यवसाय क्या है?",
                "monthly_income": "आपकी मासिक आय कितनी है?",
                "bank_account_status": "क्या आपका बैंक खाता है?"
            },
            "kannada": {
                "full_name": "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?",
                "age": "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?",
                "phone_number": "ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಏನು?",
                "village_name": "ನೀವು ಯಾವ ಗ್ರಾಮದಿಂದ ಬಂದಿದ್ದೀರಿ?",
                "primary_occupation": "ನಿಮ್ಮ ಮುಖ್ಯ ವೃತ್ತಿ ಏನು?",
                "monthly_income": "ನಿಮ್ಮ ಮಾಸಿಕ ಆದಾಯ ಎಷ್ಟು?",
                "bank_account_status": "ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆ ಇದೆಯೇ?"
            }
        }
        
        # Handle nested field names (e.g., "personal_info.full_name")
        if "." in field:
            field = field.split(".")[-1]
        
        # Get question from templates
        lang_questions = questions.get(language, questions["english"])
        return lang_questions.get(field, f"Please provide information about {field}")

# Example usage and testing
if __name__ == "__main__":
    agent = UserOnboardingAgent()
    
    # Test with English input
    test_input_en = "Hi, my name is Ramesh Kumar, I am 35 years old farmer from Davangere village. I have 2 acres of land and earn about 15000 rupees per month."
    result = agent.extract_user_info(test_input_en, "english")
    print("Extracted Data:", json.dumps(result, indent=2))
    
    # Test completeness validation
    validation = agent.validate_completeness(result)
    print("Validation:", validation)
    
    # Test clarifying questions
    questions = agent.ask_clarifying_questions(result, "english")
    print("Questions:", questions)
