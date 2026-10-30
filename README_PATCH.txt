DOCUFLOW INTEGRITY PATCH

Before applying:
1. Stop Streamlit with Ctrl+C.
2. Back up the entire CYNBIT_DOCUFLOW_AI folder.

Extract this ZIP into the existing project folder and overwrite:
- app.py
- database/db.py

Add these new files:
- core/evidence.py
- tests/test_evidence.py
- tests/test_duplicate_lookup.py

No database file is deleted. Existing records remain in SQLite.

Then run:
python -m pytest -v

Start:
streamlit run app.py

Expected behaviour:
- Extracted scalar values are searched against source text.
- Exact source lines are shown as evidence.
- No match means "Not verified", not a fabricated confidence score.
- Duplicate vendor + invoice number is detected before saving.
- A duplicate upload is not inserted as a new database record.

Limitations:
- Matching is conservative and line-based. Some valid values may not match if OCR
  or PDF extraction changes punctuation/layout.
- A match only proves text presence, not factual correctness.
- Duplicate key is vendor name + invoice number; this is a prototype policy.
