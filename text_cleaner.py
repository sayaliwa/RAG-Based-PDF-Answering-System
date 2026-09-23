"""
Text preprocessing utility for AI StudyMate.

Provides functions for cleaning, tokenizing,
and counting words in text documents.
"""
import re
import string

class TextCleaner:
    """
    Utility class for text cleaning and preprocessing.
    """
    def __init__(self):
        """
        Initialize our cleaner with Python's built-in punctuation list.
        
        Fun fact: string.punctuation contains: !"#$%&()*+,-./:;<=>?@[\\]^_`{|}~
        """

        self.punctuation = string.punctuation  
        
        print("TextCleaner ready!")
    
    def clean_text(self, text):
        """
        Clean text by removing special characters and extra spaces.
        """
        
        text =text.lower()  
        
        text = text.strip() 
        
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        text = re.sub(r'\s+', ' ', text) 
        
        return text
    
    def tokenize(self, text):
        
        cleaned = self.clean_text(text) 
        
        tokens = cleaned.split() 
        
        return tokens
    
    def get_word_count(self, text):
        """
        Count how many words are in the text.
        
        This is super useful for understanding document length!
        """
       
        tokens = self.tokenize(text)  
        return len(tokens) 


