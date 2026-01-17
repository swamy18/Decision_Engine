import pytest
import asyncio
from app.workflow import process_document
from app.services.ingestion import ingest_text
from app.core.errors import IngestionError, ModelIntegrationError
from app.domain.models import ValidationStatus, ConfidenceLevel, DecisionObject

@pytest.mark.asyncio
async def test_happy_path():
    """Test the ideal flow works."""
    content = "Subject: Invoice 101. Total: $500."
    metadata = {"source": "unit_test"}
    
    decision = await process_document(content, metadata)
    
    assert decision.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
    assert decision.verification_result.status == ValidationStatus.VALID
    assert decision.provider_metadata is not None
    assert decision.audit_trail[0].details["penalties_applied"] is False

@pytest.mark.asyncio
async def test_ingestion_empty_content():
    """Test that empty content raises IngestionError immediately."""
    with pytest.raises(IngestionError):
        await ingest_text("   ", "test_source")

@pytest.mark.asyncio
async def test_logic_contradiction_penalty():
    """
    Test that contradictory data (simulated) results in downgraded confidence.
    The MockLLMAdapter returns specific data, but we can verify how the system *handles* 
    a contradiction if we could inject it. 
    
    Since we are using the MockAdapter, we know:
    - Intent: 'process_request'
    - Entities: Found if words are Title Case.
    
    Scenario: Content with no Title Case words -> No entities -> Contradiction 
    (because intent defaults to 'process_request').
    """
    # unexpected content (lowercase) -> No entities found -> Logic check fails
    content = "all lowercase content request" 
    metadata = {"source": "test_contradiction"}
    
    decision = await process_document(content, metadata)
    
    # 1. Verification should Flag Contradiction
    assert decision.verification_result.status == ValidationStatus.CONTRADICTION
    assert not decision.verification_result.is_consistent
    assert "Intent is process_request but no entities found." in decision.verification_result.contradictions
    
    # 2. Confidence should be penalized (50% of base)
    # Base is roughly (0.95 + 0.5 + 0.70) / 3 ~= 0.71
    # Penalized: 0.71 * 0.5 ~= 0.35
    assert decision.confidence_score < 0.5
    assert decision.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.CRITICAL]
    
    # 3. Escalation should be triggered
    assert decision.escalation.requires_human_review is True

@pytest.mark.asyncio
async def test_model_failure_retry_logic():
    """
    The Mock adapter raises ModelIntegrationError if content contains 'error'.
    The service has retries. It should eventually fail after retries.
    """
    content = "This content contains an error trigger."
    metadata = {"source": "test_failure"}
    
    with pytest.raises(ModelIntegrationError) as excinfo:
        await process_document(content, metadata)
    
    assert "Simulation provider outage" in str(excinfo.value) or "Translation failed" in str(excinfo.value)

if __name__ == "__main__":
    # verification script wrapper
    async def run_all():
        try:
            print("Running test_happy_path...")
            await test_happy_path()
            print("PASS")
            
            print("Running test_ingestion_empty_content...")
            await test_ingestion_empty_content()
            print("PASS")
            
            print("Running test_logic_contradiction_penalty...")
            await test_logic_contradiction_penalty()
            print("PASS")
            
            print("Running test_model_failure_retry_logic...")
            await test_model_failure_retry_logic()
            print("PASS")
            
            print("\nALL TESTS PASSED SUCCESSFULLY.")
        except Exception as e:
            print(f"\nFAILED: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run(run_all())
