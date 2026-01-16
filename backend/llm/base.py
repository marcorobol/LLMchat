from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, 
                                prompt: str, 
                                context_documents: List[str] = [], 
                                images: List[bytes] = []) -> Dict[str, Union[str, List[str]]]:
        """
        Generates a response based on the prompt and context.
        
        Args:
            prompt: The user's question.
            context_documents: Text content from uploaded documents.
            images: List of image bytes (for multimodal support).

        Returns:
            Dict containing 'answer' (str) and 'citations' (List[str]).
        """
        pass
