import httpx

async def get_model_context_length(model_id: str) -> int:
    """
    Connects to LM Studio REST API and retrieves the maximum context length for the specific model.
    """
    try:
        # Use simple REST API call instead of heavy SDK
        async with httpx.AsyncClient() as client:
            response = await client.get("http://bears.disi.unitn.it:1234/api/v0/models", timeout=5.0)
            
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
