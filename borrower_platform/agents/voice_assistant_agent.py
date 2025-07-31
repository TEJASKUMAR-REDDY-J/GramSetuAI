"""
Voice Assistant Agent
Handles speech-to-text + Groq LLM + text-to-speech
Supports English, Hindi, and Kannada
"""

import os
import json
import time
from groq import Groq
from typing import Dict, Any, Optional, List
import requests
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, extract_language_from_text, generate_cache_key
from .translation_agent import TranslationAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import assemblyai as aai
    AAI_AVAILABLE = True
except ImportError:
    print("AssemblyAI not installed. Install with: pip install assemblyai")
    AAI_AVAILABLE = False

try:
    from gtts import gTTS
    import pygame
    import io
    GTTS_AVAILABLE = True
except ImportError:
    print("gTTS not installed. Install with: pip install gtts pygame")
    GTTS_AVAILABLE = False

class VoiceAssistantAgent:
    def __init__(self, groq_api_key: str = None, assemblyai_key: str = None):
        """
        Initialize Voice Assistant Agent with GROQ and AssemblyAI for speech processing
        
        Args:
            groq_api_key: GROQ API key (optional, loads from environment if not provided)
            assemblyai_key: AssemblyAI API key (optional, loads from environment if not provided)
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.assemblyai_key = assemblyai_key or os.getenv("ASSEMBLYAI_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ API key is required. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
        
        if not self.assemblyai_key:
            raise ValueError("AssemblyAI API key is required. Set ASSEMBLYAI_API_KEY environment variable or pass assemblyai_key parameter.")
        
        # Initialize clients
        self.client = Groq(api_key=self.groq_api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.translator = TranslationAgent(self.groq_api_key)
        
        # AssemblyAI setup
        if self.assemblyai_key and AAI_AVAILABLE:
            aai.settings.api_key = self.assemblyai_key
        
        self.cache = {}
        self.conversation_history = []
        
        # Language-specific voice settings for gTTS
        self.gtts_languages = {
            "english": "en",
            "hindi": "hi", 
            "kannada": "kn"
        }
    
    def speech_to_text(self, audio_file_path: str, language: str = "auto") -> Dict[str, Any]:
        """
        Convert speech to text using AssemblyAI
        
        Args:
            audio_file_path (str): Path to audio file
            language (str): Target language for transcription
            
        Returns:
            Dict: Transcription results with language detection
        """
        
        try:
            if not AAI_AVAILABLE:
                return {
                    "success": False,
                    "error": "AssemblyAI not available",
                    "text": "",
                    "confidence": 0,
                    "detected_language": "unknown"
                }
            
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                language_detection=True if language == "auto" else False,
                language_code="en" if language == "english" else "hi" if language == "hindi" else "kn" if language == "kannada" else None
            )
            
            transcriber = aai.Transcriber(config=config)
            
            # Transcribe audio
            transcript = transcriber.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                return {
                    "success": False,
                    "error": transcript.error,
                    "text": "",
                    "confidence": 0,
                    "detected_language": "unknown"
                }
            
            # Detect language from transcribed text if auto-detection was used
            detected_language = extract_language_from_text(transcript.text)
            
            return {
                "success": True,
                "text": transcript.text,
                "confidence": transcript.confidence if hasattr(transcript, 'confidence') else 0.9,
                "detected_language": detected_language,
                "processing_time": transcript.audio_duration if hasattr(transcript, 'audio_duration') else 0
            }
            
        except Exception as e:
            print(f"Error in speech-to-text: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0,
                "detected_language": "unknown"
            }
    
    def process_voice_inquiry(self, user_data: Dict[str, Any], inquiry_type: str = "general", language: str = "english") -> Dict[str, Any]:
        """
        Process voice-based inquiries with enhanced multilingual support and local context
        
        Args:
            user_data (Dict): User profile for personalized responses
            inquiry_type (str): Type of inquiry (loan_status, payment_due, balance, general)
            language (str): Response language (english, hindi, kannada)
            
        Returns:
            Dict: Voice response with text and audio
        """
        
        # Get user context for personalization
        name = user_data.get("personal_info", {}).get("full_name", "")
        village = user_data.get("household_location", {}).get("village_name", "")
        occupation = user_data.get("occupation_income", {}).get("primary_occupation", "")
        
        # Enhanced inquiry responses with local context
        responses = {
            "english": {
                "loan_status": f"Hello {name}! Your loan application from {village} is being processed. As a {occupation}, we're reviewing your application carefully. You'll receive an update within 2-3 working days.",
                "payment_due": f"Dear {name}, this is a reminder that your loan payment is due soon. Please visit your nearest center or use mobile banking to make the payment. Thank you for being a valued member from {village}.",
                "balance": f"Hello {name}! Your current loan balance and savings details will be shared with you. For specific amounts, please visit your group meeting or contact your field officer.",
                "general": f"Namaste {name}! How can I help you today? I can assist with loan information, payment reminders, or answer questions about our services in {village}."
            },
            "hindi": {
                "loan_status": f"नमस्ते {name} जी! {village} से आपका ऋण आवेदन प्रक्रिया में है। एक {occupation} के रूप में, हम आपके आवेदन की सावधानीपूर्वक समीक्षा कर रहे हैं। आपको 2-3 कार्य दिवसों में अपडेट मिलेगा।",
                "payment_due": f"प्रिय {name} जी, यह याद दिलाना है कि आपका ऋण भुगतान जल्द ही देय है। कृपया अपने निकटतम केंद्र पर जाएं या मोबाइल बैंकिंग का उपयोग करके भुगतान करें। {village} के एक मूल्यवान सदस्य होने के लिए धन्यवाद।",
                "balance": f"नमस्ते {name} जी! आपका वर्तमान ऋण बैलेंस और बचत विवरण आपके साथ साझा किया जाएगा। विशिष्ट राशि के लिए, कृपया अपनी समूह बैठक में जाएं या अपने फील्ड ऑफिसर से संपर्क करें।",
                "general": f"नमस्ते {name} जी! आज मैं आपकी कैसे मदद कर सकता हूं? मैं {village} में ऋण जानकारी, भुगतान अनुस्मारक, या हमारी सेवाओं के बारे में प्रश्नों में सहायता कर सकता हूं।"
            },
            "kannada": {
                "loan_status": f"ನಮಸ್ಕಾರ {name}! {village} ಇಂದ ನಿಮ್ಮ ಸಾಲದ ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆಯಲ್ಲಿದೆ. ಒಬ್ಬ {occupation} ಆಗಿ, ನಾವು ನಿಮ್ಮ ಅರ್ಜಿಯನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇವೆ. ನೀವು 2-3 ಕೆಲಸದ ದಿನಗಳಲ್ಲಿ ಅಪ್‌ಡೇಟ್ ಪಡೆಯುವಿರಿ.",
                "payment_due": f"ಪ್ರಿಯ {name}, ನಿಮ್ಮ ಸಾಲದ ಪಾವತಿ ಶೀಘ್ರದಲ್ಲೇ ಕೊಡಬೇಕು ಎಂದು ನೆನಪಿಸುತ್ತಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹತ್ತಿರದ ಕೇಂದ್ರಕ್ಕೆ ಹೋಗಿ ಅಥವಾ ಮೊಬೈಲ್ ಬ್ಯಾಂಕಿಂಗ್ ಬಳಸಿ ಪಾವತಿ ಮಾಡಿ. {village} ನ ಮೌಲ್ಯಯುತ ಸದಸ್ಯರಾಗಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು.",
                "balance": f"ನಮಸ್ಕಾರ {name}! ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಸಾಲದ ಬ್ಯಾಲೆನ್ಸ್ ಮತ್ತು ಉಳಿತಾಯ ವಿವರಗಳನ್ನು ನಿಮ್ಮೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಲಾಗುವುದು. ನಿರ್ದಿಷ್ಟ ಮೊತ್ತಕ್ಕಾಗಿ, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಗುಂಪಿನ ಸಭೆಗೆ ಹೋಗಿ ಅಥವಾ ನಿಮ್ಮ ಫೀಲ್ಡ್ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
                "general": f"ನಮಸ್ಕಾರ {name}! ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು? {village} ನಲ್ಲಿ ಸಾಲದ ಮಾಹಿತಿ, ಪಾವತಿ ನೆನಪಿಕೆಗಳು, ಅಥವಾ ನಮ್ಮ ಸೇವೆಗಳ ಬಗ್ಗೆ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ನಾನು ಸಹಾಯ ಮಾಡಬಹುದು."
            }
        }
        
        # Get appropriate response
        response_text = responses.get(language, responses["english"]).get(inquiry_type, responses[language]["general"])
        
        try:
            # Generate audio using gTTS (if available)
            audio_content = None
            if GTTS_AVAILABLE:
                # Get appropriate language code for gTTS
                lang_code = self.gtts_languages.get(language, "en")
                
                # Create gTTS object
                tts = gTTS(text=response_text, lang=lang_code, slow=False)
                
                # Save to bytes buffer
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_content = audio_buffer.getvalue()
            
            return {
                "text_response": response_text,
                "audio_content": audio_content,
                "language": language,
                "inquiry_type": inquiry_type,
                "personalized": True,
                "local_context": {
                    "village": village,
                    "occupation": occupation,
                    "greeting_style": "respectful_rural"
                }
            }
            
        except Exception as e:
            print(f"Error generating voice response: {e}")
            return {
                "text_response": response_text,
                "audio_content": None,
                "language": language,
                "inquiry_type": inquiry_type,
                "personalized": True,
                "error": str(e)
            }
    
    def process_voice_query(self, query_text: str, user_data: Dict[str, Any] = None, context: str = "", language: str = "english") -> Dict[str, Any]:
        """
        Process voice query using Groq LLM with translation support
        
        Args:
            query_text (str): User's voice query
            user_data (Dict): User profile data for personalization and language preference
            context (str): Additional context
            language (str): Language for response (fallback if user_data doesn't have preference)
            
        Returns:
            Dict: LLM response with translation
        """
        
        # Get user's preferred language
        if user_data:
            user_language = self.translator.get_user_preferred_language(user_data)
        else:
            user_language = language
        
        # Translate user query to English for processing
        english_query = self.translator.translate_user_input_to_english(query_text, user_data or {"preferred_language": user_language})
        
        # Check cache
        cache_key = generate_cache_key({"query": english_query, "context": context, "lang": user_language})
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        system_prompt = get_language_prompt(user_language, "voice_system")
        
        # Enhanced prompt with microfinance context
        enhanced_prompt = f"""
{system_prompt}

You are a helpful voice assistant for rural microfinance services. Answer user queries about:
- Loan applications and eligibility
- Documentation requirements
- Interest rates and repayment terms
- Savings and investment options
- Digital banking services
- Government schemes and subsidies

Keep responses simple, clear, and under 100 words for voice output.
Use practical examples relevant to rural Karnataka context.

Additional Context: {context}

User Query: {english_query}

Provide a helpful response:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": enhanced_prompt}
                ],
                max_tokens=300,
                temperature=0  # Deterministic output
            )
            
            english_response = response.choices[0].message.content.strip()
            
            # Translate response back to user's preferred language
            final_response = self.translator.translate_response_to_user_language(
                english_response, 
                user_data or {"preferred_language": user_language}
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": time.time(),
                "user_query": query_text,
                "assistant_response": final_response,
                "language": user_language
            })
            
            result = {
                "success": True,
                "response_text": final_response,
                "language": user_language,
                "response_length": len(final_response),
                "processing_time": time.time()
            }
            
            # Cache result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"Error processing voice query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_text": "Sorry, I couldn't process your request. Please try again.",
                "language": user_language
            }
    
    def text_to_speech(self, text: str, language: str = "english", output_path: str = None) -> Dict[str, Any]:
        """
        Convert text to speech using gTTS
        
        Args:
            text (str): Text to convert to speech
            language (str): Target language for speech
            output_path (str): Path to save audio file
            
        Returns:
            Dict: TTS results
        """
        
        if not GTTS_AVAILABLE:
            return {
                "success": False,
                "error": "gTTS not available. Please install gtts package.",
                "audio_path": None
            }
        
        try:
            # Get language code for gTTS
            lang_code = self.gtts_languages.get(language, "en")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save audio file
            if not output_path:
                timestamp = int(time.time())
                output_path = f"data/audio_output/response_{timestamp}.mp3"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the audio
            tts.save(output_path)
            
            return {
                "success": True,
                "audio_path": output_path,
                "text_length": len(text),
                "language": language,
                "engine": "gTTS"
            }
            
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_path": None
            }
    
    def handle_voice_conversation(self, audio_file_path: str, context: str = "", language: str = "auto") -> Dict[str, Any]:
        """
        Complete voice conversation flow: STT -> LLM -> TTS
        
        Args:
            audio_file_path (str): Path to user's audio input
            context (str): Additional context for processing
            language (str): Target language or 'auto' for detection
            
        Returns:
            Dict: Complete conversation results
        """
        
        # Step 1: Speech to Text
        stt_result = self.speech_to_text(audio_file_path, language)
        
        if not stt_result["success"]:
            return {
                "success": False,
                "error": "Speech transcription failed",
                "stage": "speech_to_text",
                "details": stt_result
            }
        
        # Use detected language if auto-detection was used
        if language == "auto":
            language = stt_result["detected_language"]
        
        # Step 2: Process query with LLM
        llm_result = self.process_voice_query(
            stt_result["text"], 
            context, 
            language
        )
        
        if not llm_result["success"]:
            return {
                "success": False,
                "error": "Query processing failed",
                "stage": "llm_processing",
                "details": llm_result
            }
        
        # Step 3: Text to Speech
        tts_result = self.text_to_speech(
            llm_result["response_text"],
            language
        )
        
        return {
            "success": True,
            "transcription": stt_result,
            "llm_response": llm_result,
            "audio_response": tts_result,
            "conversation_summary": {
                "user_input": stt_result["text"],
                "assistant_response": llm_result["response_text"],
                "language": language,
                "total_processing_time": time.time()
            }
        }
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history
        
        Args:
            limit (int): Number of recent conversations to return
            
        Returns:
            List[Dict]: Recent conversation history
        """
        
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self) -> bool:
        """Clear conversation history"""
        self.conversation_history = []
        return True
    
    def save_conversation_log(self, file_path: str = None) -> bool:
        """
        Save conversation history to file
        
        Args:
            file_path (str): Path to save conversation log
            
        Returns:
            bool: Success status
        """
        
        if not file_path:
            timestamp = int(time.time())
            file_path = f"data/conversation_logs/conversation_{timestamp}.json"
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving conversation log: {e}")
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return ["english", "hindi", "kannada"]
    
    def simulate_voice_interaction(self, text_input: str, language: str = "english") -> Dict[str, Any]:
        """
        Simulate voice interaction without actual audio files (for testing)
        
        Args:
            text_input (str): Simulated user input
            language (str): Target language
            
        Returns:
            Dict: Simulated interaction results
        """
        
        # Simulate STT result
        simulated_stt = {
            "success": True,
            "text": text_input,
            "confidence": 0.95,
            "detected_language": language
        }
        
        # Process with LLM
        llm_result = self.process_voice_query(text_input, "", language)
        
        # Simulate TTS result
        simulated_tts = {
            "success": True,
            "audio_path": f"simulated_audio_{int(time.time())}.mp3",
            "text_length": len(llm_result.get("response_text", "")),
            "language": language
        }
        
        return {
            "success": True,
            "transcription": simulated_stt,
            "llm_response": llm_result,
            "audio_response": simulated_tts,
            "conversation_summary": {
                "user_input": text_input,
                "assistant_response": llm_result.get("response_text", ""),
                "language": language,
                "mode": "simulated"
            }
        }

# Example usage and testing
if __name__ == "__main__":
    agent = VoiceAssistantAgent()
    
    # Test simulated voice interaction
    test_queries = [
        "What documents do I need for a loan application?",
        "How much interest rate for agriculture loan?",
        "Can I apply for loan without collateral?"
    ]
    
    for query in test_queries:
        result = agent.simulate_voice_interaction(query, "english")
        print(f"Query: {query}")
        print(f"Response: {result['llm_response']['response_text']}")
        print("-" * 50)
    
    # Test conversation history
    history = agent.get_conversation_history()
    print(f"Conversation History: {len(history)} entries")
