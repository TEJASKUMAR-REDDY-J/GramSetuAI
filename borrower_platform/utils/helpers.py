"""
Helper utilities for micr        "voice_system": "ನೀವು ಮೈಕ್ರೋಫೈನಾನ್ಸ್ ಪ್ರಶ್ನೆಗಳೊಂದಿಗೆ ಗ್ರಾಮೀಣ ಬಳಕೆದಾರರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸ್ನೇಹಪರ ಧ್ವನಿ ಸಹಾಯಕರು। ಉತ್ತರಗಳನ್ನು ಸರಳ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಇರಿಸಿ। ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "credit_system": "ನೀವು ಕ್ರೆಡಿಟ್ ಸ್ಕೋರ್ ವಿವರಿಸುವವರು। ಗ್ರಾಮೀಣ ಬಳಕೆದಾರರು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಬಹುದಾದ ಸರಳ ಪದಗಳಲ್ಲಿ ಕ್ರೆಡಿಟ್ ಅಂಶಗಳನ್ನು ವಿಭಜಿಸಿ। ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "risk_system": "ನೀವು ಸಾಲದ ಅಪಾಯ ವಿಶ್ಲೇಷಕರು। ಸ್ಪಷ್ಟ, ಕ್ರಿಯಾತ್ಮಕ ಸಾಲ ಶಿಫಾರಸುಗಳನ್ನು ಒದಗಿಸಿ। ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "risk_advisor_system": "ನೀವು ಗ್ರಾಮೀಣ ಮೈಕ್ರೋಫೈನಾನ್ಸ್‌ನ ಆಳವಾದ ಜ್ಞಾನವನ್ನು ಹೊಂದಿರುವ ಪರಿಣಿತ MFI ಸಾಲ ಅಪಾಯ ಸಲಹೆಗಾರರು। ಸಾಲ ನಿರ್ಧಾರಗಳಿಗಾಗಿ ಸಮಗ್ರ, ಕ್ರಿಯಾತ್ಮಕ ವಿಶ್ಲೇಷಣೆಯನ್ನು ಒದಗಿಸಿ। ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ।"nance agents
Supports English, Hindi, and Kannada
"""

import json
import hashlib
from typing import Dict, Any, Optional

# Language mappings for multi-language support
LANGUAGE_PROMPTS = {
    "english": {
        "onboarding_system": "You are a helpful assistant collecting information from rural users for microfinance services. Be patient and ask clarifying questions. Respond in English.",
        "document_system": "You are a document verification expert. Analyze the provided document and extract key information accurately. Respond in English.",
        "voice_system": "You are a friendly voice assistant helping rural users with microfinance queries. Keep responses simple and clear. Respond in English.",
        "credit_system": "You are a credit score explainer. Break down credit factors in simple terms that rural users can understand. Respond in English.",
        "risk_system": "You are a loan risk analyst. Provide clear, actionable loan recommendations. Respond in English.",
        "risk_advisor_system": "You are an expert MFI loan risk advisor with deep knowledge of rural microfinance. Provide comprehensive, actionable analysis for loan decisions. Respond in English."
    },
    "hindi": {
        "onboarding_system": "आप ग्रामीण उपयोगकर्ताओं से माइक्रोफाइनेंस सेवाओं के लिए जानकारी एकत्र करने में मदद करने वाले सहायक हैं। धैर्य रखें और स्पष्टीकरण के प्रश्न पूछें। हिंदी में उत्तर दें।",
        "document_system": "आप एक दस्तावेज़ सत्यापन विशेषज्ञ हैं। प्रदान किए गए दस्तावेज़ का विश्लेषण करें और मुख्य जानकारी सटीक रूप से निकालें। हिंदी में उत्तर दें।",
        "voice_system": "आप माइक्रोफाइनेंस प्रश्नों के साथ ग्रामीण उपयोगकर्ताओं की मदद करने वाले मित्रवत आवाज सहायक हैं। उत्तर सरल और स्पष्ट रखें। हिंदी में उत्तर दें।",
        "credit_system": "आप एक क्रेडिट स्कोर समझाने वाले हैं। क्रेडिट कारकों को सरल शब्दों में समझाएं जो ग्रामीण उपयोगकर्ता समझ सकें। हिंदी में उत्तर दें।",
        "risk_system": "आप एक ऋण जोखिम विश्लेषक हैं। स्पष्ट, कार्यात्मक ऋण सिफारिशें प्रदान करें। हिंदी में उत्तर दें।",
        "risk_advisor_system": "आप ग्रामीण माइक्रोफाइनेंस के गहरे ज्ञान के साथ एक विशेषज्ञ MFI ऋण जोखिम सलाहकार हैं। ऋण निर्णयों के लिए व्यापक, कार्यात्मक विश्लेषण प्रदान करें। हिंदी में उत्तर दें।"
    },
    "kannada": {
        "onboarding_system": "ನೀವು ಮೈಕ್ರೋಫೈನಾನ್ಸ್ ಸೇವೆಗಳಿಗಾಗಿ ಗ್ರಾಮೀಣ ಬಳಕೆದಾರರಿಂದ ಮಾಹಿತಿ ಸಂಗ್ರಹಿಸಲು ಸಹಾಯ ಮಾಡುವ ಸಹಾಯಕರು. ತಾಳ್ಮೆಯಿಂದಿರಿ ಮತ್ತು ಸ್ಪಷ್ಟೀಕರಣ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ. ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "document_system": "ನೀವು ದಾಖಲೆ ಪರಿಶೀಲನೆ ತಜ್ಞರು. ಒದಗಿಸಿದ ದಾಖಲೆಯನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ಮುಖ್ಯ ಮಾಹಿತಿಯನ್ನು ನಿಖರವಾಗಿ ಹೊರತೆಗೆಯಿರಿ. ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "voice_system": "ನೀವು ಮೈಕ್ರೋಫೈನಾನ್ಸ್ ಪ್ರಶ್ನೆಗಳೊಂದಿಗೆ ಗ್ರಾಮೀಣ ಬಳಕೆದಾರರಿಗೆ ಸಹಾಯ ಮಾಡುವ ಸ್ನೇಹಪರ ಧ್ವನಿ ಸಹಾಯಕರು. ಉತ್ತರಗಳನ್ನು ಸರಳ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಇರಿಸಿ. ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "credit_system": "ನೀವು ಕ್ರೆಡಿಟ್ ಸ್ಕೋರ್ ವಿವರಿಸುವವರು. ಗ್ರಾಮೀಣ ಬಳಕೆದಾರರು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಬಹುದಾದ ಸರಳ ಪದಗಳಲ್ಲಿ ಕ್ರೆಡಿಟ್ ಅಂಶಗಳನ್ನು ವಿಭಜಿಸಿ. ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "risk_system": "ನೀವು ಸಾಲದ ಅಪಾಯ ವಿಶ್ಲೇಷಕರು. ಸ್ಪಷ್ಟ, ಕ್ರಿಯಾತ್ಮಕ ಸಾಲ ಶಿಫಾರಸುಗಳನ್ನು ಒದಗಿಸಿ. ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ."
    }
}

# Common field mappings for data structure
USER_FIELDS_TEMPLATE = {
    "personal_info": {
        "full_name": "",
        "age": "",
        "gender": "",
        "preferred_language": "",
        "aadhaar_number": "",
        "phone_number": "",
        "marital_status": "",
        "voter_id": ""
    },
    "household_location": {
        "village_name": "",
        "district": "",
        "state": "Karnataka",
        "pincode": "",
        "house_type": "",
        "electricity_connection": "",
        "number_of_dependents": ""
    },
    "occupation_income": {
        "primary_occupation": "",
        "secondary_income_sources": "",
        "monthly_income": "",
        "monthly_expenses": "",
        "seasonal_variation": ""
    },
    "financial_details": {
        "bank_account_status": "",
        "bank_name": "",
        "existing_loans": "",
        "repayment_history": "",
        "savings_per_month": "",
        "group_membership": "",
        "past_loan_amounts": ""
    },
    "land_property": {
        "owns_land": "",
        "land_area": "",
        "land_type": "",
        "patta_or_katha_number": "",
        "property_location": ""
    },
    "digital_literacy": {
        "owns_smartphone": "",
        "knows_how_to_use_apps": "",
        "preferred_mode_of_communication": "",
        "internet_availability": ""
    },
    "additional_notes": {
        "user_notes": "",
        "agent_observations": ""
    }
}

def get_language_prompt(language: str, prompt_type: str) -> str:
    """Get system prompt for specified language and prompt type"""
    lang = language.lower()
    if lang not in LANGUAGE_PROMPTS:
        lang = "english"
    
    return LANGUAGE_PROMPTS[lang].get(prompt_type, LANGUAGE_PROMPTS["english"][prompt_type])

def generate_cache_key(input_data: Any) -> str:
    """Generate a cache key for input data"""
    data_str = json.dumps(input_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()

def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and structure user data according to template"""
    validated_data = USER_FIELDS_TEMPLATE.copy()
    
    for category, fields in validated_data.items():
        if category in user_data:
            for field in fields:
                if field in user_data[category]:
                    validated_data[category][field] = user_data[category][field]
    
    return validated_data

def extract_language_from_text(text: str) -> str:
    """Simple language detection based on script"""
    # Kannada Unicode range
    if any(ord(char) >= 0x0C80 and ord(char) <= 0x0CFF for char in text):
        return "kannada"
    # Devanagari (Hindi) Unicode range
    elif any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
        return "hindi"
    else:
        return "english"

def format_response_for_language(response: str, language: str) -> str:
    """Format response based on target language"""
    # Simple formatting - could be enhanced with proper translation
    return response.strip()

def load_json_safely(file_path: str) -> Optional[Dict]:
    """Safely load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_safely(data: Dict, file_path: str) -> bool:
    """Safely save data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False
