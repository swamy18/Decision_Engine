from typing import Dict, Any
from app.services.ingestion import ingest_text
from app.services.translation import translate_content
from app.services.verification import verify_translation
from app.services.decision import make_decision
from app.domain.models import DecisionObject

async def process_document(content: str, source_metadata: Dict[str, Any]) -> DecisionObject:
    """
    Orchestrates the entire flow from raw text to verified decision.
    This is a linear, stateless workflow.
    """
    
    # 1. Ingest
    # Converts raw unstructured data into a tracked system object with hash
    raw_input = await ingest_text(content, source=source_metadata.get("source", "unknown"))
    
    # 2. Translate
    # Uses Model Adapter to extract structured data
    translation = await translate_content(raw_input)
    
    # 3. Verify
    # Deterministic checks against consistency rules
    verification = await verify_translation(translation)
    
    # 4. Decide
    # Final assembly, confidence scoring, and escalation checks
    decision = await make_decision(raw_input, translation, verification)
    
    return decision
