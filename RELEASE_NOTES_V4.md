# DocuFlow AI v4 — Export Verification Consistency

## Fixes
- Corrected CSV verification counts for records that contain `field_confidence` and `field_evidence` but predate `field_verification`.
- JSON exports now include the same normalized `field_verification` map and `verification_summary` as CSV.
- Legacy records with no evidence metadata are explicitly marked `Not evaluated`; they are not falsely counted as verified.
- Workflow status remains sourced from SQLite and remains independent from evidence status.

## Test results
- Existing v3 tests: 32 passed.
- Added v4 regression tests: 4.
- Full suite: 36 passed.

## Important
The v4 export layer normalizes and reports existing metadata. It does not retroactively re-run OCR or independently re-validate evidence for old records. A stored `field_confidence=1.0` plus non-empty evidence is interpreted as a prior evidence match for export reporting. Human approval remains a separate workflow status.
