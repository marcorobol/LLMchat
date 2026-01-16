from typing import List, Dict, Union
from openai import AsyncOpenAI
from .base import LLMProvider

class ZaiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "glm-4.7"):
        self.api_key = api_key
        # Use default if model is z-pro (placeholder), otherwise use passed model
        self.model = "glm-4.7" if model == "z-pro" else model
        
        # Z.ai is OpenAI compatible
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.z.ai/api/paas/v4/"
        )

    async def generate_response(self, 
                                prompt: str, 
                                context_documents: List[str] = [], 
                                images: List[bytes] = []) -> Dict[str, Union[str, List[str]]]:
        
        try:
            # Prepare messages
            messages = []
            
            # System prompt with context
            if context_documents:
                context_str = "\n\n".join(context_documents)
                system_content = f"You are a helpful assistant. Use the following context to answer the user's question:\n\n{context_str}"
                messages.append({"role": "system", "content": system_content})
            else:
                messages.append({"role": "system", "content": "You are a helpful assistant."})

            # User prompt
            messages.append({"role": "user", "content": prompt})

            # Call Z.ai API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "citations": ["Z.ai Model"] # Placeholder for now
            }
            
        except Exception as e:
            return {
                "answer": f"Error communicating with Z.ai: {str(e)}",
                "citations": []
            }
