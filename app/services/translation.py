import json
from typing import Dict, Any, Optional
from app.domain.models import RawInput, TranslationResult
from app.core.errors import ModelIntegrationError
from app.core.interfaces import LLMClient
from app.core.utils import with_retry

class MockLLMAdapter(LLMClient):
    """
    Simulates a smart model. In reality this would call OpenAI/Anthropic.
    """
    
    async def extract_structured_data(self, raw_input: RawInput, schema_desc: str) -> Dict[str, Any]:
        # Simulating possible network jitters
        if "error" in raw_input.content.lower():
            raise ModelIntegrationError("Simulated provider outage")
            
        return {
            "intent": "process_request",
            "entities_found": [word for word in raw_input.content.split() if word.istitle()],
            "sentiment": "neutral",
            "summary": f"Processed content of length {len(raw_input.content)}"
        }

    async def get_confidence_scores(self, extraction: Dict[str, Any]) -> Dict[str, float]:
        # Logic: Length of entities determines integrity for this mock
        entities = extraction.get("entities_found", [])
        return {
            "intent": 0.95,
            "entities_found": 0.85 if entities else 0.5,
            "sentiment": 0.70
        }

# Global instance for now (could be replaced by Dependency Injection)
_default_client = MockLLMAdapter()

@with_retry(exceptions=(ModelIntegrationError,), retries=3)
async def translate_content(raw_input: RawInput, client: Optional[LLMClient] = None) -> TranslationResult:
    """
    Uses an LLMClient to extract data. Retries on failure.
    """
    if client is None:
        client = _default_client
        
    try:
        # 1. Extraction
        extracted = await client.extract_structured_data(raw_input, "generic_schema")
        
        # 2. Confidence Scoring (Self-Correction/Reflection step)
        confidences = await client.get_confidence_scores(extracted)
        
        # 3. Serialize raw output for audit
        raw_output = json.dumps(extracted)
        
        return TranslationResult(
            extracted_data=extracted,
            confidence_scores=confidences,
            provider_metadata={"provider": client.__class__.__name__},
            raw_llm_output=raw_output
        )
    except Exception as e:
        # If retry failed or other error occurred
        raise ModelIntegrationError(f"Translation failed after retries: {str(e)}")
