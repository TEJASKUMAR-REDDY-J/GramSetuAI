"""
Translation Agent
Handles multilingual translation for the microfinance system
Supports English, Hindi, and Kannada with fallback mechanisms
"""

import os
from groq import Groq
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TranslationAgent:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or parameters")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        
        self.supported_languages = {
            "english": "en",
            "hindi": "hi", 
            "kannada": "kn"
        }
        
        # Common phrases for quick translation without API calls
        self.common_translations = {
            "english": {
                "hello": "Hello",
                "thank_you": "Thank you",
                "yes": "Yes",
                "no": "No",
                "please_wait": "Please wait",
                "error": "Error occurred"
            },
            "hindi": {
                "hello": "नमस्ते",
                "thank_you": "धन्यवाद",
                "yes": "हाँ",
                "no": "नहीं",
                "please_wait": "कृपया प्रतीक्षा करें",
                "error": "त्रुटि हुई"
            },
            "kannada": {
                "hello": "ನಮಸ್ಕಾರ",
                "thank_you": "ಧನ್ಯವಾದಗಳು",
                "yes": "ಹೌದು",
                "no": "ಇಲ್ಲ",
                "please_wait": "ದಯವಿಟ್ಟು ಕಾಯಿರಿ",
                "error": "ದೋಷ ಸಂಭವಿಸಿದೆ"
            }
        }

    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text
        
        Args:
            text (str): Input text to detect language
            
        Returns:
            str: Detected language (english, hindi, kannada)
        """
        if not text or not text.strip():
            return "english"
            
        # Simple heuristic-based detection
        # Check for Devanagari script (Hindi)
        if any('\u0900' <= char <= '\u097F' for char in text):
            return "hindi"
        
        # Check for Kannada script
        if any('\u0C80' <= char <= '\u0CFF' for char in text):
            return "kannada"
        
        # Default to English for Latin script
        return "english"

    def translate_to_english(self, text: str, source_language: str = "auto") -> Dict[str, Any]:
        """
        Translate text to English
        
        Args:
            text (str): Text to translate
            source_language (str): Source language or 'auto' for detection
            
        Returns:
            Dict: Translation result with metadata
        """
        if not text or not text.strip():
            return {
                "success": False,
                "translated_text": "",
                "source_language": "unknown",
                "error": "Empty text provided"
            }
        
        # Auto-detect language if needed
        if source_language == "auto":
            source_language = self.detect_language(text)
        
        # If already English, return as-is
        if source_language == "english":
            return {
                "success": True,
                "translated_text": text,
                "source_language": "english",
                "target_language": "english"
            }
        
        try:
            prompt = f"""
You are a professional translator for a rural microfinance system in Karnataka, India.

Task: Translate the following {source_language} text to English.

Rules:
1. Maintain the original meaning and context
2. Use simple, clear English suitable for rural microfinance
3. Preserve any technical terms related to banking/finance
4. If the text contains names or places, keep them as-is
5. Only provide the translation, no explanations

{source_language.title()} text: {text}

English translation:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0  # Deterministic output
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": "english"
            }
            
        except Exception as e:
            return {
                "success": False,
                "translated_text": text,  # Fallback to original
                "source_language": source_language,
                "error": str(e)
            }

    def translate_from_english(self, text: str, target_language: str) -> Dict[str, Any]:
        """
        Translate English text to target language
        
        Args:
            text (str): English text to translate
            target_language (str): Target language (hindi, kannada)
            
        Returns:
            Dict: Translation result with metadata
        """
        if not text or not text.strip():
            return {
                "success": False,
                "translated_text": "",
                "target_language": target_language,
                "error": "Empty text provided"
            }
        
        # If target is English, return as-is
        if target_language == "english":
            return {
                "success": True,
                "translated_text": text,
                "source_language": "english",
                "target_language": "english"
            }
        
        # Check for common phrases
        for key, value in self.common_translations["english"].items():
            if text.lower().strip() == value.lower():
                if target_language in self.common_translations:
                    return {
                        "success": True,
                        "translated_text": self.common_translations[target_language][key],
                        "source_language": "english",
                        "target_language": target_language
                    }
        
        try:
            # Cultural context for better translations
            context_info = {
                "hindi": "Use respectful Hindi suitable for rural banking customers in Karnataka. Use formal 'aap' forms.",
                "kannada": "Use respectful Kannada suitable for rural banking customers in Karnataka. Use appropriate honorifics."
            }
            
            prompt = f"""
You are a professional translator for a rural microfinance system in Karnataka, India.

Task: Translate the following English text to {target_language.title()}.

Context: {context_info.get(target_language, "")}

Rules:
1. Maintain the original meaning and context
2. Use respectful, polite language appropriate for rural customers
3. Preserve any technical terms but make them understandable
4. If the text contains English names or technical terms, keep them in parentheses
5. Only provide the translation, no explanations

English text: {text}

{target_language.title()} translation:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0  # Deterministic output
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": "english",
                "target_language": target_language
            }
            
        except Exception as e:
            return {
                "success": False,
                "translated_text": text,  # Fallback to original
                "target_language": target_language,
                "error": str(e)
            }

    def get_user_preferred_language(self, user_data: Dict[str, Any]) -> str:
        """
        Get user's preferred language from user data
        
        Args:
            user_data (Dict): User profile data
            
        Returns:
            str: Preferred language (defaults to english)
        """
        return user_data.get("preferred_language", "english").lower()

    def update_user_preferred_language(self, user_data: Dict[str, Any], new_language: str) -> Dict[str, Any]:
        """
        Update user's preferred language
        
        Args:
            user_data (Dict): User profile data
            new_language (str): New preferred language
            
        Returns:
            Dict: Updated user data
        """
        if new_language.lower() in self.supported_languages:
            user_data["preferred_language"] = new_language.lower()
        return user_data

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.supported_languages

    def translate_user_input_to_english(self, user_input: str, user_data: Dict[str, Any]) -> str:
        """
        Translate user input to English if needed
        
        Args:
            user_input (str): User's input text
            user_data (Dict): User profile data
            
        Returns:
            str: English text
        """
        user_language = self.get_user_preferred_language(user_data)
        
        if user_language == "english":
            return user_input
        
        result = self.translate_to_english(user_input, user_language)
        
        if result["success"]:
            return result["translated_text"]
        else:
            # Fallback to original text
            return user_input

    def translate_response_to_user_language(self, response: str, user_data: Dict[str, Any]) -> str:
        """
        Translate response to user's preferred language
        
        Args:
            response (str): English response text
            user_data (Dict): User profile data
            
        Returns:
            str: Translated response
        """
        user_language = self.get_user_preferred_language(user_data)
        
        if user_language == "english":
            return response
        
        result = self.translate_from_english(response, user_language)
        
        if result["success"]:
            return result["translated_text"]
        else:
            # Fallback to original English text
            return response

# Example usage
if __name__ == "__main__":
    translator = TranslationAgent()
    
    # Test translations
    test_cases = [
        ("ಸಾಲಕ್ಕೆ ಅರ್ಜಿ ಹೇಗೆ ಸಲ್ಲಿಸಬೇಕು?", "kannada"),
        ("मुझे लोन के लिए कैसे अप्लाई करना है?", "hindi"),
        ("How do I apply for a loan?", "english")
    ]
    
    for text, lang in test_cases:
        english_result = translator.translate_to_english(text, lang)
        print(f"Original ({lang}): {text}")
        print(f"English: {english_result['translated_text']}")
        print("-" * 50)
