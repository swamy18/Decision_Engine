from typing import Optional, Dict, Any

class BaseSystemException(Exception):
    """Base class for all system exceptions to ensure consistent error handling."""
    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class IngestionError(BaseSystemException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "INGESTION_ERROR", details)

class ModelIntegrationError(BaseSystemException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "MODEL_ERROR", details)

class VerificationError(BaseSystemException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VERIFICATION_ERROR", details)
