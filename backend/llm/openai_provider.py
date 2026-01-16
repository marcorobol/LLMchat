import os
import time
from typing import List, Dict, Union
import base64
from .base import LLMProvider
from openai import AsyncOpenAI

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate_response(self, 
                                prompt: str, 
                                context_documents: List[str] = [], 
                                images: List[bytes] = []) -> Dict[str, Union[str, List[str]]]:
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the user's question. If the answer is not in the context, say so. Cite your sources."}
        ]

        # Add context to system message or as a separate message
        if context_documents:
            context_str = "\n\n".join(context_documents)
            messages.append({"role": "system", "content": f"Context Documents:\n{context_str}"})

        # Prepare content - use simple string if no images for better compatibility
        if not images:
             messages.append({"role": "user", "content": prompt})
        else:
            user_content = [{"type": "text", "text": prompt}]
            for img_bytes in images:
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
            messages.append({"role": "user", "content": user_content})

        try:
            print(f"Sending request to {self.client.base_url} with model {self.model}")
            start_gen = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000
            )
            gen_time = time.time() - start_gen
            print(f"OpenAI/Remote Generation took {gen_time:.2f}s")
            
            answer = response.choices[0].message.content
            print(f"Extracted answer (len={len(answer)}). Returning result.")
             
            # Note: Real citation extraction would require more structured output or specific prompting
            # For now we mock the citations list or extract them if the model follows a format
            citations = ["Generated from OpenAI/Remote"] 
            
            return {
                "answer": answer,
                "citations": citations
            }
        except Exception as e:
            return {
                "answer": f"Error calling OpenAI: {str(e)}",
                "citations": []
            }
