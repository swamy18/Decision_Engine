import hashlib
from typing import Dict, Any
from app.core.errors import IngestionError
from app.domain.models import RawInput

async def ingest_text(content: str, source: str) -> RawInput:
    """
    Ingests raw text content, computes hash, and returns input object.
    
    Args:
        content: The raw text to process
        source: A string identifier for the source (e.g. filename, email subject)
    """
    if not content or not content.strip():
        raise IngestionError("Content cannot be empty or whitespace only.")

    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    return RawInput(
        content=content,
        content_hash=content_hash,
        source_metadata={"source": source, "size": len(content)}
    )
