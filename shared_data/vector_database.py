"""
Vector Database for RAG (Retrieval Augmented Generation)
Handles PDF processing and vector storage for financial education content
"""

import os
import json
import pickle
from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime
import hashlib

# PDF processing
import PyPDF2
from io import BytesIO

# Vector embeddings
from sentence_transformers import SentenceTransformer
import faiss

# Text processing
import re
from nltk.tokenize import sent_tokenize
import nltk

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
except:
    pass

class VectorDatabase:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "..", "general chat database")
        
        self.data_dir = data_dir
        self.vector_db_dir = os.path.join(os.path.dirname(__file__), "vector_db")
        os.makedirs(self.vector_db_dir, exist_ok=True)
        
        # Files for storing the vector database
        self.index_file = os.path.join(self.vector_db_dir, "faiss_index.bin")
        self.metadata_file = os.path.join(self.vector_db_dir, "metadata.json")
        self.embeddings_file = os.path.join(self.vector_db_dir, "embeddings.pkl")
        
        # Initialize sentence transformer model
        print("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension of the model
        
        # Initialize FAISS index
        self.index = None
        self.metadata = []
        
        # Load existing database or create new one
        self.load_or_create_database()
    
    def load_or_create_database(self):
        """Load existing database or create new one if it doesn't exist"""
        if self._database_exists():
            print("Loading existing vector database...")
            self._load_database()
        else:
            print("Creating new vector database...")
            self._create_database()
    
    def _database_exists(self) -> bool:
        """Check if vector database files exist"""
        return (os.path.exists(self.index_file) and 
                os.path.exists(self.metadata_file) and 
                os.path.exists(self.embeddings_file))
    
    def _load_database(self):
        """Load existing vector database"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_file)
            
            # Load metadata
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            print(f"Loaded vector database with {len(self.metadata)} documents")
        except Exception as e:
            print(f"Error loading database: {e}")
            print("Creating new database...")
            self._create_database()
    
    def _create_database(self):
        """Create new vector database from PDF files"""
        print("Processing PDF files...")
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found in the directory")
            # Create empty database
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.metadata = []
            self._save_database()
            return
        
        all_texts = []
        all_metadata = []
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file}")
            file_path = os.path.join(self.data_dir, pdf_file)
            
            try:
                # Extract text from PDF
                text_chunks = self._extract_text_from_pdf(file_path)
                
                # Create metadata for each chunk
                for i, chunk in enumerate(text_chunks):
                    metadata = {
                        'file_name': pdf_file,
                        'chunk_id': i,
                        'total_chunks': len(text_chunks),
                        'file_path': file_path,
                        'content': chunk,
                        'processed_date': datetime.now().isoformat()
                    }
                    all_texts.append(chunk)
                    all_metadata.append(metadata)
                    
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
                continue
        
        if not all_texts:
            print("No text extracted from PDFs")
            # Create empty database
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.metadata = []
            self._save_database()
            return
        
        print(f"Generating embeddings for {len(all_texts)} text chunks...")
        
        # Generate embeddings
        embeddings = self.model.encode(all_texts, show_progress_bar=True)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.metadata = all_metadata
        
        # Save database
        self._save_database()
        
        print(f"Vector database created with {len(all_texts)} documents")
    
    def _extract_text_from_pdf(self, file_path: str) -> List[str]:
        """Extract and chunk text from PDF file"""
        text_chunks = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                full_text = ""
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                if full_text.strip():
                    # Clean and chunk the text
                    chunks = self._chunk_text(full_text)
                    text_chunks.extend(chunks)
                
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
        
        return text_chunks
    
    def _chunk_text(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Split text into manageable chunks"""
        # Clean text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Split into sentences
        try:
            sentences = sent_tokenize(text)
        except:
            # Fallback if NLTK fails
            sentences = text.split('. ')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        chunks = [chunk for chunk in chunks if len(chunk.split()) >= 5]
        
        return chunks
    
    def _save_database(self):
        """Save vector database to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)
            
            # Save metadata
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            # Save embeddings info (for backup)
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump({
                    'embedding_dim': self.embedding_dim,
                    'model_name': 'all-MiniLM-L6-v2',
                    'total_vectors': self.index.ntotal if self.index else 0,
                    'created_date': datetime.now().isoformat()
                }, f)
            
            print("Vector database saved successfully")
            
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.index or self.index.ntotal == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1 and idx < len(self.metadata):  # Valid index
                    result = self.metadata[idx].copy()
                    result['similarity_score'] = float(score)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query"""
        search_results = self.search(query, top_k=3)
        
        if not search_results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        total_length = 0
        
        for result in search_results:
            content = result['content']
            file_name = result['file_name']
            
            # Add source info
            source_info = f"\n\n[Source: {file_name}]\n"
            full_content = content + source_info
            
            if total_length + len(full_content) <= max_context_length:
                context_parts.append(full_content)
                total_length += len(full_content)
            else:
                # Add partial content if it fits
                remaining_space = max_context_length - total_length
                if remaining_space > 100:  # Only add if there's meaningful space
                    partial_content = content[:remaining_space-len(source_info)] + "..."
                    context_parts.append(partial_content + source_info)
                break
        
        return "\n".join(context_parts)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        return {
            'total_documents': len(self.metadata),
            'total_vectors': self.index.ntotal if self.index else 0,
            'embedding_dimension': self.embedding_dim,
            'model_name': 'all-MiniLM-L6-v2',
            'unique_files': len(set(meta['file_name'] for meta in self.metadata)),
            'database_size_mb': self._get_database_size_mb()
        }
    
    def _get_database_size_mb(self) -> float:
        """Calculate total size of database files"""
        total_size = 0
        for file_path in [self.index_file, self.metadata_file, self.embeddings_file]:
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        return round(total_size / (1024 * 1024), 2)

# Global instance
vector_db = None

def get_vector_database():
    """Get global vector database instance"""
    global vector_db
    if vector_db is None:
        vector_db = VectorDatabase()
    return vector_db

# Test function
def test_vector_database():
    """Test the vector database functionality"""
    print("Testing Vector Database...")
    
    db = get_vector_database()
    stats = db.get_database_stats()
    
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test search
    test_queries = [
        "microfinance and loans",
        "savings account benefits",
        "financial planning for children",
        "investment options",
        "loan repayment"
    ]
    
    print("\nTesting search functionality:")
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = db.search(query, top_k=2)
        
        if results:
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['file_name']} (Score: {result['similarity_score']:.3f})")
                print(f"     {result['content'][:100]}...")
        else:
            print("  No results found")
    
    print("\nVector database test completed!")

if __name__ == "__main__":
    test_vector_database()
