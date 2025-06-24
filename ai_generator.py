from openai import OpenAI
from transformers import pipeline
import torch
import re
import os

class AINotesGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.local_model = None
        self.stop_generation = False
        
    def initialize_local_model(self):
        if not self.local_model:
            self.local_model = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
    
    def chunk_text(self, text, max_tokens=3000):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            tokens = len(sentence.split())
            if current_length + tokens > max_tokens:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(sentence)
            current_length += tokens
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks
    
    def generate_with_openai(self, text, prompt):
        chunks = self.chunk_text(text)
        notes = []
        
        for chunk in chunks:
            if self.stop_generation:
                break
                
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a study assistant."},
                    {"role": "user", "content": f"{prompt}\n\n{chunk}"}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            notes.append(response.choices[0].message.content)
        
        return "\n\n".join(notes)
    
    def generate_with_local(self, text):
        self.initialize_local_model()
        chunks = self.chunk_text(text, max_tokens=1024)
        summaries = []
        
        for chunk in chunks:
            if self.stop_generation:
                break
            summary = self.local_model(chunk, max_length=150, min_length=30)
            summaries.append(summary[0]['summary_text'])
        
        return "\n\n".join(summaries)
    
    def generate_notes(self, text, prompt):
        try:
            return self.generate_with_openai(text, prompt)
        except Exception:
            return self.generate_with_local(text)
    
    def generate_flashcards(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate Q&A flashcards."},
                    {"role": "user", "content": f"Create flashcards:\n{text}"}
                ],
                temperature=0.3
            )
            return self._parse_flashcards(response.choices[0].message.content)
        except Exception:
            return self._simple_flashcards(text)
    
    def _parse_flashcards(self, text):
        flashcards = []
        pairs = re.split(r'\n\n|\nQ:', text)
        for pair in pairs:
            if 'A:' in pair:
                q, a = pair.split('A:', 1)
                flashcards.append((q.replace('Q:', '').strip(), a.strip()))
        return flashcards
    
    def _simple_flashcards(self, text):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        return [
            (f"What is {sentences[i]}?", sentences[i+1] if i+1 < len(sentences) else "")
            for i in range(0, len(sentences), 2)
        ]
