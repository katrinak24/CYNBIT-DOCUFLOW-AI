
# Changelog

## Final Assessment Release

### Core application
- Local LLM invoice extraction using Ollama and Qwen2.5.
- PDF text extraction and scanned-document OCR.
- Structured invoice extraction using Pydantic.

### Evidence and validation
- Field-specific evidence verification.
- Multi-line GST reconciliation.
- Duplicate invoice detection.
- Human approval and rejection workflow.

### Data management
- SQLite persistence.
- CSV and JSON exports.
- Approval status consistency.
- Evidence re-evaluation and audit history.

### Quality assurance
- 46 automated tests passed on Windows.
- Scanned invoice OCR demonstrated.
