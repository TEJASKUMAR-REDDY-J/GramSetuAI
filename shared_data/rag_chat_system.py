"""
RAG (Retrieval Augmented Generation) Chat System
Provides intelligent responses using the vector database and AI
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from vector_database import get_vector_database
except ImportError:
    print("Warning: Vector database not available. Install required packages.")
    get_vector_database = None

load_dotenv()

class RAGChatSystem:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        
        # Initialize vector database
        self.vector_db = None
        if get_vector_database:
            try:
                self.vector_db = get_vector_database()
                print("Vector database initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize vector database: {e}")
        
        # Chat history for context
        self.chat_history = []
        self.max_history = 10  # Keep last 10 exchanges
    
    def get_response(self, user_query: str, user_type: str = "borrower") -> str:
        """
        Get response using RAG approach
        user_type: "borrower" or "lender"
        """
        try:
            # Get relevant context from vector database
            context = self._get_relevant_context(user_query)
            
            # Generate response using AI with context
            response = self._generate_ai_response(user_query, context, user_type)
            
            # Update chat history
            self._update_chat_history(user_query, response)
            
            return response
            
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your question right now. Please try again. Error: {str(e)}"
    
    def _get_relevant_context(self, query: str) -> str:
        """Get relevant context from the vector database"""
        if not self.vector_db:
            return "Vector database not available. I can still help based on my general knowledge."
        
        try:
            context = self.vector_db.get_context_for_query(query, max_context_length=1500)
            return context
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return "Context retrieval temporarily unavailable."
    
    def _generate_ai_response(self, query: str, context: str, user_type: str) -> str:
        """Generate AI response using the context and query"""
        
        # Get recent chat history for context
        history_context = self._get_chat_history_context()
        
        # Create appropriate system prompt based on user type
        if user_type == "borrower":
            system_role = """You are a helpful financial advisor assistant for microfinance borrowers in India. 
            You help people understand loans, savings, financial planning, government schemes, and banking services. 
            Provide clear, practical advice in simple language. Focus on microfinance, small business loans, 
            savings accounts, and financial literacy. Always be encouraging and supportive."""
        else:  # lender
            system_role = """You are an expert financial advisor for microfinance institutions (MFIs) and lenders in India. 
            You provide insights on portfolio management, risk assessment, regulatory compliance, lending practices, 
            and operational efficiency. Your responses should be professional and data-driven, helping MFIs make 
            informed decisions about their lending operations."""
        
        prompt = f"""
{system_role}

KNOWLEDGE BASE CONTEXT:
{context}

RECENT CONVERSATION HISTORY:
{history_context}

USER QUESTION: {query}

Based on the knowledge base context and your expertise, provide a helpful, accurate, and practical response. 
If the knowledge base doesn't contain specific information, use your general knowledge about Indian microfinance 
and financial services. Always be honest if you're not certain about specific details.

Guidelines:
- Keep responses clear and actionable
- Use simple language (avoid too much jargon)
- Provide specific examples when possible
- Mention relevant government schemes or regulations when applicable
- Be encouraging and supportive
- If suggesting financial products, mention the need to verify current terms and conditions

Response:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I'm experiencing technical difficulties. Please try again in a moment. ({str(e)})"
    
    def _get_chat_history_context(self) -> str:
        """Get formatted chat history for context"""
        if not self.chat_history:
            return "No previous conversation."
        
        recent_history = self.chat_history[-3:]  # Last 3 exchanges
        history_text = ""
        
        for exchange in recent_history:
            history_text += f"User: {exchange['query']}\nAssistant: {exchange['response'][:200]}...\n\n"
        
        return history_text.strip()
    
    def _update_chat_history(self, query: str, response: str):
        """Update chat history with new exchange"""
        self.chat_history.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    def get_suggested_questions(self, user_type: str = "borrower") -> List[str]:
        """Get suggested questions based on user type"""
        if user_type == "borrower":
            return [
                "How do I apply for a microfinance loan?",
                "What documents do I need for a loan application?",
                "How can I improve my credit score?",
                "What are the different types of savings accounts?",
                "How do I start a small business with a loan?",
                "What government schemes are available for entrepreneurs?",
                "How do I plan my finances and create a budget?",
                "What is the difference between secured and unsecured loans?"
            ]
        else:  # lender
            return [
                "How do I assess borrower creditworthiness?",
                "What are the current RBI guidelines for microfinance?",
                "How do I manage portfolio risk effectively?",
                "What are the best practices for loan collections?",
                "How do I calculate appropriate interest rates?",
                "What technology solutions can improve MFI operations?",
                "How do I ensure regulatory compliance?",
                "What are the key metrics to track for portfolio health?"
            ]
    
    def get_database_info(self) -> Dict:
        """Get information about the knowledge base"""
        if not self.vector_db:
            return {"status": "unavailable", "message": "Vector database not initialized"}
        
        try:
            stats = self.vector_db.get_database_stats()
            return {
                "status": "available",
                "stats": stats,
                "message": f"Knowledge base contains {stats['total_documents']} documents from {stats['unique_files']} PDF files"
            }
        except Exception as e:
            return {"status": "error", "message": f"Error accessing database: {e}"}

# Global instance
rag_chat_system = None

def get_rag_chat_system():
    """Get global RAG chat system instance"""
    global rag_chat_system
    if rag_chat_system is None:
        try:
            rag_chat_system = RAGChatSystem()
        except Exception as e:
            print(f"Error initializing RAG chat system: {e}")
            return None
    return rag_chat_system

# Test function
def test_rag_system():
    """Test the RAG chat system"""
    print("Testing RAG Chat System...")
    
    try:
        rag = get_rag_chat_system()
        if not rag:
            print("Failed to initialize RAG system")
            return
        
        # Test database info
        db_info = rag.get_database_info()
        print(f"\nDatabase Info: {db_info}")
        
        # Test questions for borrowers
        print("\nTesting borrower questions:")
        borrower_questions = [
            "What is microfinance?",
            "How do I apply for a small business loan?",
            "What documents do I need for a loan?"
        ]
        
        for question in borrower_questions:
            print(f"\nQ: {question}")
            response = rag.get_response(question, "borrower")
            print(f"A: {response[:200]}...")
        
        # Test questions for lenders
        print("\nTesting lender questions:")
        lender_questions = [
            "How do I assess credit risk for microfinance borrowers?",
            "What are the regulatory requirements for MFIs?"
        ]
        
        for question in lender_questions:
            print(f"\nQ: {question}")
            response = rag.get_response(question, "lender")
            print(f"A: {response[:200]}...")
        
        print("\nRAG system test completed!")
        
    except Exception as e:
        print(f"Error testing RAG system: {e}")

if __name__ == "__main__":
    test_rag_system()
