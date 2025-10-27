"""
Custom Embedding Function cho Vanna sử dụng BAAI/bge-m3 từ Hugging Face
"""

import os
import numpy as np
from typing import List
from huggingface_hub import InferenceClient


class BGE_M3_EmbeddingFunction:
    """
    BGE-M3 Embedding Function using Hugging Face Inference API
    
    Using InferenceClient from huggingface_hub for proper API compatibility.
    Model: BAAI/bge-m3 (1024 dimensions, multilingual support)
    """
    
    def __init__(self, api_key: str = None, model_name: str = "BAAI/bge-m3"):
        """
        Initialize BGE-M3 Embedding Function
        
        Args:
            api_key: Hugging Face API key (từ HUGGINGFACE_API_KEY hoặc HF_TOKEN)
            model_name: Model name on Hugging Face (default: BAAI/bge-m3)
        """
        self.api_key = api_key or os.environ.get('HUGGINGFACE_API_KEY') or os.environ.get('HF_TOKEN')
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found. Set it as environment variable or pass as parameter.")
        
        self.model_name = model_name
        # InferenceClient accepts 'token' parameter, not 'api_key'
        self.client = InferenceClient(token=self.api_key)
        print(f"✅ Initialized {model_name} with InferenceClient")
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            input: List of strings to embed (ChromaDB interface requirement)
            
        Returns:
            List of embedding vectors (normalized)
        """
        texts = input  # ChromaDB passes 'input' parameter
        if not texts:
            return []
        
        embeddings = []
        
        for text in texts:
            try:
                # Use InferenceClient.feature_extraction method
                embedding = self.client.feature_extraction(text, model=self.model_name)
                
                # Convert to numpy array and flatten if needed
                emb_array = np.array(embedding, dtype=np.float32)
                if emb_array.ndim > 1:
                    emb_array = emb_array.flatten()
                
                # Normalize the embedding
                norm = np.linalg.norm(emb_array)
                if norm > 1e-9:
                    emb_array = emb_array / norm
                
                embeddings.append(emb_array.tolist())
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '429' in error_msg:
                    raise Exception(f"⚠️ Rate limit exceeded: {e}")
                elif 'timeout' in error_msg:
                    raise Exception(f"⚠️ Request timeout: {e}")
                elif 'model is currently loading' in error_msg or '503' in error_msg:
                    raise Exception(f"⚠️ Model is loading, retry in a few seconds: {e}")
                else:
                    raise Exception(f"❌ Hugging Face API error: {e}")
        
        return embeddings


class BGE_M3_Local_EmbeddingFunction:
    """
    Local version using sentence-transformers (không cần API key)
    Yêu cầu: pip install sentence-transformers
    """
    
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embeddings.\n"
                "Install it: pip install sentence-transformers"
            )
        
        print("🔄 Loading BGE-M3 model locally (first time may take a few minutes)...")
        self.model = SentenceTransformer('BAAI/bge-m3')
        print("✅ Model loaded successfully!")
        
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings locally (ChromaDB interface)"""
        texts = input  # ChromaDB passes 'input' parameter
        if not texts:
            return []
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,  # Normalize for better similarity search
            show_progress_bar=False
        )
        
        return embeddings.tolist()


# Example usage functions
def test_bge_m3_api():
    """Test BGE-M3 với Hugging Face API"""
    print("=" * 70)
    print("🧪 TEST BGE-M3 EMBEDDING (API)")
    print("=" * 70)
    
    # Initialize
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("❌ Missing HUGGINGFACE_API_KEY")
        print("Get your token: https://huggingface.co/settings/tokens")
        print("Then set: export HUGGINGFACE_API_KEY='hf_...'")
        return
    
    ef = BGE_M3_EmbeddingFunction(api_key=api_key)
    
    # Test texts
    test_texts = [
        "SELECT * FROM customers WHERE id = 1",
        "Tổng doanh thu của tháng này là bao nhiêu?",
        "CREATE TABLE users (id INT, name VARCHAR(100))"
    ]
    
    print("\n📝 Generating embeddings...")
    embeddings = ef(test_texts)
    
    print(f"\n✅ Generated {len(embeddings)} embeddings")
    for i, (text, emb) in enumerate(zip(test_texts, embeddings), 1):
        print(f"\n{i}. Text: {text[:50]}...")
        print(f"   Dimensions: {len(emb)}")
        print(f"   Sample: [{emb[0]:.4f}, {emb[1]:.4f}, {emb[2]:.4f}, ...]")


def test_bge_m3_local():
    """Test BGE-M3 local (không cần API key)"""
    print("=" * 70)
    print("🧪 TEST BGE-M3 EMBEDDING (LOCAL)")
    print("=" * 70)
    
    try:
        ef = BGE_M3_Local_EmbeddingFunction()
        
        test_texts = [
            "SELECT * FROM customers WHERE id = 1",
            "Tổng doanh thu của tháng này là bao nhiêu?",
        ]
        
        print("\n📝 Generating embeddings...")
        embeddings = ef(test_texts)
        
        print(f"\n✅ Generated {len(embeddings)} embeddings")
        for i, (text, emb) in enumerate(zip(test_texts, embeddings), 1):
            print(f"\n{i}. Text: {text[:50]}...")
            print(f"   Dimensions: {len(emb)}")
            print(f"   Sample: [{emb[0]:.4f}, {emb[1]:.4f}, {emb[2]:.4f}, ...]")
            
    except ImportError as e:
        print(f"❌ {e}")


if __name__ == "__main__":
    import sys
    
    print("\n🎯 BGE-M3 Embedding Function for Vanna")
    print("=" * 70)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    
    if mode == "api":
        test_bge_m3_api()
    elif mode == "local":
        test_bge_m3_local()
    else:
        print("Usage: python bge_m3_embedding.py [api|local]")
        print("  api   - Use Hugging Face API (requires API key)")
        print("  local - Run locally (requires sentence-transformers)")
