import httpx
from typing import List, Dict, Optional

LM_STUDIO_API = "http://bears.disi.unitn.it:1234/api/v0"

async def load_model(model_id: str) -> Dict:
    """
    Load a model in LM Studio.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LM_STUDIO_API}/models/{model_id}/load",
                timeout=60.0  # Loading can take a while
            )
            if response.status_code == 200:
                return response.json()
            return {"error": f"Failed to load model: {response.status_code}"}
    except Exception as e:
        print(f"LM Studio Load Error: {e}")
        return {"error": str(e)}

async def unload_model(model_id: str) -> Dict:
    """
    Unload a model from LM Studio.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LM_STUDIO_API}/models/{model_id}/unload",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            return {"error": f"Failed to unload model: {response.status_code}"}
    except Exception as e:
        print(f"LM Studio Unload Error: {e}")
        return {"error": str(e)}

async def get_models_list() -> List[Dict]:
    """
    Fetches all models from LM Studio REST API with their full information.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LM_STUDIO_API}/models", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])

            return []

    except Exception as e:
        print(f"LM Studio API Error: {e}")
        return []

async def get_model_info(model_id: str) -> Optional[Dict]:
    """
    Fetches information about a specific model from LM Studio REST API.
    Returns None if model not found.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LM_STUDIO_API}/models", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                for model in data.get("data", []):
                    if model.get("id") == model_id:
                        return model

            return None

    except Exception as e:
        print(f"LM Studio API Error: {e}")
        return None

async def get_model_context_length(model_id: str) -> int:
    """
    Connects to LM Studio REST API and retrieves the maximum context length for the specific model.
    """
    try:
        # Use simple REST API call instead of heavy SDK
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LM_STUDIO_API}/models", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                for model in data.get("data", []):
                    if model.get("id") == model_id:
                        # Return the max_context_length directly
                        return model.get("max_context_length", 4096)
            
        print(f"Model {model_id} not found in LM Studio API response.")
        return guess_context_length(model_id)

    except Exception as e:
        print(f"LM Studio API Error: {e}")
        return guess_context_length(model_id) 
        
def guess_context_length(model_id: str) -> int:
    """Fallback heuristic if SDK connection fails."""
    lower_id = model_id.lower()
    if 'devstral' in lower_id:
        return 393216 # ~393k tokens
    if '70b' in lower_id or 'llama-3.3' in lower_id:
        return 131072 # ~128k tokens
    if 'gpt-4' in lower_id:
        return 128000
    if '8b' in lower_id or 'gpt-3.5' in lower_id:
        return 16000 # ~16k tokens
    return 4096 # Default 4k 
