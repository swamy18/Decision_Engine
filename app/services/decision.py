from datetime import datetime, timezone
from statistics import mean
from app.domain.models import (
    RawInput, TranslationResult, VerificationResult, DecisionObject, 
    ConfidenceLevel, AuditEvent, EscalationPolicy, ValidationStatus
)
from app.core.config import settings

async def make_decision(
    raw_input: RawInput, 
    translation: TranslationResult, 
    verification: VerificationResult
) -> DecisionObject:
    """
    Synthesizes the final decision, calculates confidence, and determines escalation.
    """
    
    # 1. Calculate Base Confidence
    base_score = 0.0
    if translation.confidence_scores:
        base_score = mean(translation.confidence_scores.values())
        
    avg_score = base_score
        
    # 2. Apply Penalties based on Verification
    # Logic: Contradictions halve the confidence. separate logic for missing data.
    if verification.status == ValidationStatus.CONTRADICTION:
        avg_score = avg_score * 0.5
    elif verification.status == ValidationStatus.MISSING_DATA:
        avg_score = avg_score * 0.8
        
    # 3. Determine Confidence Level
    if avg_score >= settings.CONFIDENCE_THRESHOLD_HIGH:
        level = ConfidenceLevel.HIGH
    elif avg_score >= settings.CONFIDENCE_THRESHOLD_MEDIUM:
        level = ConfidenceLevel.MEDIUM
    # Critical if very low or explicitly invalid? 
    # Let's say < 0.3 is CRITICAL
    elif avg_score < 0.3:
        level = ConfidenceLevel.CRITICAL
    else:
        level = ConfidenceLevel.LOW
        
    # 4. Escalation Policy
    escalation = EscalationPolicy(
        requires_human_review=(level in [ConfidenceLevel.LOW, ConfidenceLevel.CRITICAL] or not verification.is_consistent),
        reason=f"Status: {verification.status}, Score: {avg_score:.2f}",
        severity=level
    )
    
    # 5. Create Audit Trail
    # In a real system, we'd append logs from previous steps. 
    # Here we create a summary event.
    audit_event = AuditEvent(
        action="decision_made",
        details={
            "initial_score": base_score,
            "final_score": avg_score,
            "penalties_applied": not verification.is_consistent,
            "provider": translation.provider_metadata.get("provider") if translation.provider_metadata else "unknown"
        }
    )
    
    return DecisionObject(
        raw_input_id=raw_input.id,
        final_data=translation.extracted_data,
        provider_metadata=translation.provider_metadata,
        confidence_score=max(0.0, min(1.0, round(avg_score, 4))),
        confidence_level=level,
        verification_result=verification,
        escalation=escalation,
        audit_trail=[audit_event]
    )
