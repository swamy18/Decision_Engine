from app.domain.models import TranslationResult, VerificationResult, ValidationStatus

async def verify_translation(translation: TranslationResult) -> VerificationResult:
    """
    Runs deterministic checks on the translation result.
    """
    contradictions = []
    missing_fields = []
    logic_checks = {}
    
    data = translation.extracted_data
    
    # 1. Check for critical fields
    required_fields = ["intent"]
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
            
    # 2. Check for logic contradictions (Example)
    # If intent is 'process_request', we expect entities to be present
    entities = data.get("entities_found")
    if isinstance(entities, list):
        logic_checks["entities_present"] = len(entities) > 0
    else:
        logic_checks["entities_present"] = False
        
    if data.get("intent") == "process_request" and not logic_checks["entities_present"]:
        contradictions.append("Intent is process_request but no entities found.")
        
    # 3. Determine Status
    if contradictions:
        status = ValidationStatus.CONTRADICTION
    elif missing_fields:
        status = ValidationStatus.MISSING_DATA
    else:
        status = ValidationStatus.VALID
        
    return VerificationResult(
        is_consistent=(status == ValidationStatus.VALID),
        contradictions=contradictions,
        missing_fields=missing_fields,
        logic_checks=logic_checks,
        status=status
    )
