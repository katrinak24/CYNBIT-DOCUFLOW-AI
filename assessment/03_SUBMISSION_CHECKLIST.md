# Cynbit AI/ML Engineer Intern Assessment - Submission Checklist

## Required deliverables

- [x] AI Opportunity Report - `assessment/01_AI_OPPORTUNITY_REPORT.md` and PDF copy.
- [x] Functional AI/ML proof of concept - complete DocuFlow AI source project.
- [x] Technical Approach Report - `assessment/02_TECHNICAL_APPROACH_REPORT.md` and PDF copy.
- [x] Setup and execution instructions - `README.md`.
- [x] Automated test suite - `tests/` (46 tests in final regression run).
- [x] Synthetic image-only scanned invoice - `samples/invoices/DocuFlow_Scanned_Test_Invoice.pdf`.

## Before portal submission

- [ ] Run `python -m pytest -v` on the target Windows machine and save the terminal output.
- [ ] Confirm Ollama is running and the configured model is installed.
- [ ] Confirm `tesseract --version` and `tesseract --list-langs` show Tesseract and `eng`.
- [ ] Run `streamlit run app.py` and capture the app home screen.
- [ ] Upload the scanned test invoice and capture `pdf_ocr`, extracted fields, evidence table, and validation output.
- [ ] Capture Review & approve and History & exports screens.
- [ ] Create a public GitHub repository from the project source (do not commit confidential invoices, API keys, `.venv`, local cache, or personal records).
- [ ] Add the README, both reports, sample synthetic invoice, and test instructions to the repository.
- [ ] Open the repository in a clean environment and follow the README from scratch.
- [ ] Submit the public GitHub URL and setup notes through Cynbit's candidate portal.

## Claims to keep accurate

- The sample invoice is synthetic.
- The 46 automated tests passed in the final regression run; rerun them on the target Windows machine before portal submission.
- The manual OCR demonstration was performed on one synthetic scanned invoice; it is not a benchmark across a large invoice dataset.
- Evidence verification means source-text support, not proof of authenticity or truth.
- This PoC does not claim to be a production accounting, compliance, or fraud-detection platform.
