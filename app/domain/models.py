from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ConfidenceLevel(str, Enum):
    HIGH = "high"       # > 0.9
    MEDIUM = "medium"   # > 0.7
    LOW = "low"         # < 0.7
    CRITICAL = "critical" # Manual review required

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"    
    CONTRADICTION = "contradiction"
    MISSING_DATA = "missing_data"

class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str = "system"
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(frozen=True)

class EscalationPolicy(BaseModel):
    requires_human_review: bool = False
    reason: Optional[str] = None
    severity: ConfidenceLevel = ConfidenceLevel.LOW

class RawInput(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    content_hash: str
    source_metadata: Dict[str, Any]
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TranslationResult(BaseModel):
    """Represents the raw extraction from the model before verification."""
    extracted_data: Dict[str, Any]
    confidence_scores: Dict[str, float]  # Field-level confidence (0.0 - 1.0)
    provider_metadata: Dict[str, Any] # model name, tokens, etc
    raw_llm_output: str

class VerificationResult(BaseModel):
    """Result of consistency checks and business rule validation."""
    is_consistent: bool
    contradictions: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    logic_checks: Dict[str, bool] = Field(default_factory=dict)
    status: ValidationStatus

class DecisionObject(BaseModel):
    """The final VERIFIED object ready for downstream consumption."""
    id: UUID = Field(default_factory=uuid4)
    raw_input_id: UUID
    
    # The clean, verified data
    final_data: Dict[str, Any]
    provider_metadata: Optional[Dict[str, Any]] = None
    
    # Meta
    confidence_score: float = Field(..., description="Overall confidence 0.0-1.0")
    confidence_level: ConfidenceLevel
    
    # Evidence
    verification_result: VerificationResult
    escalation: EscalationPolicy
    
    # Audit
    audit_trail: List[AuditEvent]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0 and 1')
        return v
