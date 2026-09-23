"""
Semantic similarity utilities for AI StudyMate.

Provides cosine similarity calculations and
vector comparison methods.
"""

import math
from typing import List

class SemanticSimilarity:
    """
    A similarity calculator that measures how "close" two vectors are.
    
    In real AI systems, words are converted to vectors (lists of numbers).
    Words with similar meanings have similar vectors!
    
    Notice how king and queen have similar numbers? That's the magic!
    """
    
    def __init__(self):
        
        print("Semantic Similarity Calculator ready")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        
        
        if len(vec1) != len(vec2):
            raise ValueError(f"Vectors must be same length! Got {len(vec1)} and {len(vec2)}")
        
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))  
        
       
        magnitude1 = math.sqrt(sum(a * a for a in vec1))  
        
        
        magnitude2 = math.sqrt(sum(b * b for b in vec2))  
        
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        
        similarity = dot_product/(magnitude1 * magnitude2) 
        
        return similarity
    
    def interpret_similarity(self, score: float) -> str:
        
       
        if score >= 0.9:
            return "Nearly identical!"  
        elif score >= 0.7:
            return "Very similar"  
        elif score >= 0.5:
            return "Somewhat similar"  
        elif score >= 0.3:
            return "A bit related"  
        else:
            return "Quite different"  
    
    def compare_multiple(self, base_vec: List[float], compare_vecs: dict) -> dict:
        
        results = {}
        
        
        for name, vec in compare_vecs.items():
            
            similarity = self.cosine_similarity(base_vec, vec) 
            results[name] = similarity
        
        
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True)) 
        
        return sorted_results


