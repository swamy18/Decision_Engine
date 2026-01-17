from typing import Any, Dict, Protocol
from app.domain.models import RawInput

class LLMClient(Protocol):
    """Protocol for LLM Model Adapters to ensure pluggability."""
    
    async def extract_structured_data(self, raw_input: RawInput, schema_desc: str) -> Dict[str, Any]:
        """
        Extract structured data from raw input matching the target schema description.
        Returns a dictionary or raises ModelIntegrationError.
        """
        ...
        
    async def get_confidence_scores(self, extraction: Dict[str, Any]) -> Dict[str, float]:
        """
        Optional: Ask the model to rate its own confidence per field.
        """
        ...
