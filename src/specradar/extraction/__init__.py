"""Stage [3]: evidence-anchored extraction. The AI reads, never invents."""

from specradar.extraction.extractor import (
    Extractor,
    LLMClient,
    extract_attributes,
)
from specradar.extraction.verifier import verify_evidence, verify_extracted_value

__all__ = [
    "Extractor",
    "LLMClient",
    "extract_attributes",
    "verify_evidence",
    "verify_extracted_value",
]
