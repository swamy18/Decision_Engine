from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Dict, Any

from app.domain.models import RawInput, TranslationResult, VerificationResult, DecisionObject
from app.services import ingestion, translation, verification, decision
from app import workflow

router = APIRouter()

class ProcessRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]

class DecisionRequest(BaseModel):
    raw_input: RawInput
    translation: TranslationResult
    verification: VerificationResult

@router.post("/process", response_model=DecisionObject)
async def run_full_flow(request: ProcessRequest):
    """
    End-to-end processing: Ingest -> Translate -> Verify -> Decide.
    """
    return await workflow.process_document(request.content, request.metadata)

@router.post("/ingest", response_model=RawInput)
async def ingest_stage(request: ProcessRequest):
    """
    Stateless ingestion step. Returns RawInput with hash.
    """
    return await ingestion.ingest_text(request.content, request.metadata.get("source", "api"))

@router.post("/translate", response_model=TranslationResult)
async def translate_stage(raw_input: RawInput):
    """
    Stateless translation step. Returns extracted data.
    """
    return await translation.translate_content(raw_input)

@router.post("/verify", response_model=VerificationResult)
async def verify_stage(translation_result: TranslationResult):
    """
    Stateless verification step. Checks for logic consistency.
    """
    return await verification.verify_translation(translation_result)

@router.post("/decide", response_model=DecisionObject)
async def decide_stage(request: DecisionRequest):
    """
    Stateless decision step. Assembles final object and audit trail.
    """
    return await decision.make_decision(
        request.raw_input, 
        request.translation, 
        request.verification
    )
