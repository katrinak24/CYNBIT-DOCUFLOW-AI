import pytest
from core.document_loader import validate_upload

def test_pdf_is_supported():
    validate_upload("invoice.pdf", 1024)

def test_unsupported_file_is_rejected():
    with pytest.raises(ValueError):
        validate_upload("invoice.exe", 1024)
