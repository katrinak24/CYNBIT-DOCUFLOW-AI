# DocuFlow AI v3 — Integrity & Approval Consistency

## What's changed
- SQLite is the single source of truth for workflow status.
- Human-review corrections are persisted atomically with approval status.
- Approval re-runs field-specific evidence verification against the original stored OCR text.
- Original extracted source text is stored locally for new records.
- Existing databases are migrated additively with a `source_text` column; existing rows and IDs are preserved.
- Evidence quotes are compacted to the matched field label/value rather than entire OCR-joined lines.
- CSV and JSON exports are generated from the same SQLite record snapshot and include workflow and verification details.
- Review tab shows counts for Pending Review, Approved and Rejected.

## Important note about existing records
The supplied database contains four existing invoice records. They are preserved in this package.
The older records predate source-text retention, so their `source_text` is blank. They remain viewable/exportable, but the new approval flow will ask you to reprocess a legacy document before approving it, because evidence cannot safely be recomputed without its original OCR text.

## Windows setup
1. Extract this ZIP to a new folder or back up your current folder first.
2. Open the `CYNBIT_DOCUFLOW_AI` folder in VS Code.
3. Create/activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Run tests:
   ```powershell
   python -m pytest -v
   ```
6. Start:
   ```powershell
   streamlit run app.py
   ```

Tesseract OCR must be installed separately on Windows. Ensure `tesseract.exe` is on PATH, and `eng` language data is installed. Ollama must be running and the configured model (default `qwen2.5:3b`) must be available.

## Validation
The project test suite passes 32 tests in the build environment. Retest locally with your Windows Python environment, Ollama and Tesseract before using it for assessment submission.
