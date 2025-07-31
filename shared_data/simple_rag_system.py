"""
Simple RAG Chat System using basic text search
Fallback implementation when full vector database is not available
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Try to import PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PyPDF2 not available - PDF processing disabled")

load_dotenv()

class SimpleRAGSystem:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "..", "general chat database")
        
        self.data_dir = data_dir
        self.knowledge_base_file = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        
        # Initialize Groq client
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        else:
            self.client = None
            print("Warning: GROQ_API_KEY not found")
        
        # Load or create knowledge base
        self.knowledge_base = self._load_or_create_knowledge_base()
        
        # Chat history
        self.chat_history = []
        self.max_history = 10
    
    def _load_or_create_knowledge_base(self) -> Dict:
        """Load existing knowledge base or create new one"""
        if os.path.exists(self.knowledge_base_file):
            try:
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    knowledge_base = json.load(f)
                print(f"Loaded knowledge base with {len(knowledge_base.get('documents', []))} documents")
                return knowledge_base
            except Exception as e:
                print(f"Error loading knowledge base: {e}")
        
        # Create new knowledge base
        return self._create_knowledge_base()
    
    def _create_knowledge_base(self) -> Dict:
        """Create knowledge base from PDF files"""
        print("Creating knowledge base from PDF files...")
        
        if not os.path.exists(self.data_dir):
            print(f"Data directory not found: {self.data_dir}")
            return {"documents": [], "created_date": datetime.now().isoformat()}
        
        documents = []
        pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found")
            return {"documents": [], "created_date": datetime.now().isoformat()}
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file}")
            try:
                text = self._extract_text_from_pdf(os.path.join(self.data_dir, pdf_file))
                if text:
                    # Split into chunks
                    chunks = self._chunk_text(text)
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            "file_name": pdf_file,
                            "chunk_id": i,
                            "content": chunk,
                            "keywords": self._extract_keywords(chunk)
                        })
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
                continue
        
        knowledge_base = {
            "documents": documents,
            "created_date": datetime.now().isoformat(),
            "total_files": len(pdf_files),
            "total_chunks": len(documents)
        }
        
        # Save knowledge base
        try:
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
            print(f"Knowledge base created with {len(documents)} documents")
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
        
        return knowledge_base
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            return ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _chunk_text(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Split text into chunks"""
        # Clean text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter very short chunks
        chunks = [chunk for chunk in chunks if len(chunk.split()) >= 5]
        return chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        text = text.lower()
        keywords = []
        
        # Financial terms
        financial_terms = [
            'loan', 'credit', 'microfinance', 'saving', 'investment', 'bank', 'interest',
            'repayment', 'emi', 'collateral', 'guarantee', 'insurance', 'pension',
            'budget', 'income', 'expense', 'profit', 'debt', 'equity', 'fund',
            'scheme', 'government', 'subsidy', 'tax', 'business', 'entrepreneur',
            'sme', 'msme', 'startup', 'agriculture', 'rural', 'urban'
        ]
        
        for term in financial_terms:
            if term in text:
                keywords.append(term)
        
        return keywords
    
    def search_knowledge_base(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search knowledge base using simple text matching"""
        query_lower = query.lower()
        results = []
        
        for doc in self.knowledge_base.get('documents', []):
            content_lower = doc['content'].lower()
            score = 0
            
            # Simple scoring based on keyword matches
            query_words = query_lower.split()
            for word in query_words:
                if word in content_lower:
                    score += 1
                if word in doc.get('keywords', []):
                    score += 2
            
            if score > 0:
                results.append({
                    'content': doc['content'],
                    'file_name': doc['file_name'],
                    'score': score,
                    'keywords': doc.get('keywords', [])
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_response(self, user_query: str, user_type: str = "borrower") -> str:
        """Get response using simple RAG approach"""
        try:
            # Search knowledge base
            search_results = self.search_knowledge_base(user_query)
            
            # Build context
            context = self._build_context(search_results)
            
            # Generate response
            if self.client:
                response = self._generate_ai_response(user_query, context, user_type)
            else:
                response = self._generate_fallback_response(user_query, search_results, user_type)
            
            # Update chat history
            self._update_chat_history(user_query, response)
            
            return response
            
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your question. Please try again. Error: {str(e)}"
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Build context from search results"""
        if not search_results:
            return "No specific information found in knowledge base."
        
        context_parts = []
        for result in search_results:
            context_parts.append(f"[From {result['file_name']}]: {result['content']}")
        
        return "\n\n".join(context_parts)
    
    def _generate_ai_response(self, query: str, context: str, user_type: str) -> str:
        """Generate AI response using context"""
        if user_type == "borrower":
            system_role = """You are a helpful financial advisor for microfinance borrowers in India. 
            Provide clear, practical advice in simple language about loans, savings, and financial planning."""
        else:
            system_role = """You are an expert financial advisor for microfinance institutions in India. 
            Provide professional insights on portfolio management, risk assessment, and lending practices."""
        
        prompt = f"""
{system_role}

KNOWLEDGE BASE CONTEXT:
{context}

USER QUESTION: {query}

Based on the knowledge base and your expertise, provide a helpful and practical response.
Keep it clear and actionable.

Response:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return self._generate_fallback_response(query, [], user_type)
    
    def _generate_fallback_response(self, query: str, search_results: List[Dict], user_type: str) -> str:
        """Generate fallback response when AI is not available"""
        if search_results:
            response = "Based on our knowledge base:\n\n"
            for result in search_results[:2]:
                response += f"• {result['content'][:200]}...\n\n"
            response += f"[Source: {result['file_name']}]"
            return response
        else:
            if user_type == "borrower":
                return """I'd be happy to help with your financial question! Here are some general guidelines:

• **For loans**: Ensure you have proper documentation and a clear repayment plan
• **For savings**: Start with small amounts and be consistent
• **For investments**: Always understand the risks before investing
• **For government schemes**: Check eligibility criteria and application deadlines

Please ask more specific questions for detailed guidance."""
            else:
                return """Here are some general MFI best practices:

• **Risk Management**: Regularly monitor PAR rates and portfolio health
• **Compliance**: Stay updated with RBI guidelines and regulations
• **Technology**: Use digital tools for efficiency and better tracking
• **Borrower Education**: Invest in financial literacy programs

Please ask more specific questions for detailed guidance."""
    
    def _update_chat_history(self, query: str, response: str):
        """Update chat history"""
        self.chat_history.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    def get_suggested_questions(self, user_type: str = "borrower") -> List[str]:
        """Get suggested questions"""
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
        else:
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
        """Get database information"""
        kb = self.knowledge_base
        return {
            "status": "available",
            "stats": {
                "total_documents": len(kb.get('documents', [])),
                "total_files": kb.get('total_files', 0),
                "created_date": kb.get('created_date', 'Unknown')
            },
            "message": f"Knowledge base contains {len(kb.get('documents', []))} documents from {kb.get('total_files', 0)} PDF files"
        }

# Global instance
simple_rag_system = None

def get_simple_rag_system():
    """Get global simple RAG system instance"""
    global simple_rag_system
    if simple_rag_system is None:
        try:
            simple_rag_system = SimpleRAGSystem()
        except Exception as e:
            print(f"Error initializing simple RAG system: {e}")
            return None
    return simple_rag_system

# Test function
def test_simple_rag():
    """Test the simple RAG system"""
    print("Testing Simple RAG System...")
    
    rag = get_simple_rag_system()
    if not rag:
        print("Failed to initialize RAG system")
        return
    
    # Test database info
    db_info = rag.get_database_info()
    print(f"Database Info: {db_info}")
    
    # Test search
    test_queries = [
        "What is microfinance?",
        "How do I apply for a loan?",
        "What are savings accounts?"
    ]
    
    for query in test_queries:
        print(f"\nQ: {query}")
        response = rag.get_response(query, "borrower")
        print(f"A: {response[:200]}...")
    
    print("\nSimple RAG test completed!")

if __name__ == "__main__":
    test_simple_rag()
