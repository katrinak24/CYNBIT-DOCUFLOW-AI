import json
import pandas as pd
import streamlit as st
from config import MAX_UPLOAD_MB, OLLAMA_MODEL
from core.document_loader import validate_upload
from core.text_extractor import extract_text
from core.ai_extractor import extract_invoice
from core.evidence import verify_invoice_evidence
from core.validator import validate_invoice
from core.schemas import InvoiceData
from database.db import init_db, find_duplicate, save_invoice, list_invoices, update_status, update_invoice_review, get_invoice_source, update_invoice_evidence, list_verification_audit
from utils.export import csv_bytes, json_bytes
from core.verification_summary import build_verification_summary, normalize_verification
from core.approval import approval_blockers

st.set_page_config(page_title="Cynbit DocuFlow AI", page_icon="📄", layout="wide")
init_db()

CONFIDENCE_FIELDS = [
    "vendor_name", "invoice_number", "invoice_date", "due_date", "currency",
    "subtotal", "tax_amount", "total_amount", "payment_status"
]

def confidence_label(score):
    return "Evidence found" if score >= 1.0 else "Not verified"

def confidence_table(data_dict):
    scores = data_dict.get("field_confidence", {}) or {}
    evidence = data_dict.get("field_evidence", {}) or {}
    verification = data_dict.get("field_verification", {}) or {}
    rows = []
    for field in CONFIDENCE_FIELDS:
        value = data_dict.get(field)
        score = float(scores.get(field, 0.0) or 0.0)
        rows.append({
            "Field": field.replace("_", " ").title(),
            "Extracted value": "—" if value is None else str(value),
            "Evidence match": "Yes" if score >= 1.0 else "No",
            "Verification": verification.get(field, confidence_label(score)),
            "Source evidence": evidence.get(field, "") or "No matching source line"
        })
    return pd.DataFrame(rows)

st.title("📄 Cynbit DocuFlow AI")
st.caption("AI-powered invoice extraction, validation and human approval | Local prototype")

with st.sidebar:
    st.header("System status")
    st.write(f"**AI model:** `{OLLAMA_MODEL}`")
    st.write("**Inference:** Local Ollama")
    st.write("**Database:** SQLite")
    st.info("AI-extracted financial information must be reviewed by a human before use.")
    st.caption("Evidence match means the extracted value was found in source text. It does not prove the document is truthful.")

tab_upload, tab_review, tab_history = st.tabs(["1. Process document", "2. Review & approve", "3. History & exports"])

with tab_upload:
    st.subheader("Upload an invoice")
    uploaded = st.file_uploader("Choose a PDF or image", type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"])
    if uploaded:
        try:
            file_bytes = uploaded.getvalue()
            validate_upload(uploaded.name, len(file_bytes), MAX_UPLOAD_MB)
            st.success(f"File received: {uploaded.name} ({len(file_bytes)/1024:.1f} KB)")
            if uploaded.type.startswith("image/"):
                st.image(file_bytes, caption="Uploaded document", use_container_width=True)
            if st.button("Extract and validate invoice", type="primary"):
                with st.spinner("Reading document..."):
                    source_text, method = extract_text(uploaded.name, file_bytes)
                st.write(f"**Extraction method:** `{method}`")
                with st.expander("View extracted source text"):
                    st.text(source_text[:12000] if source_text else "No text detected.")
                with st.spinner(f"Extracting structured fields with {OLLAMA_MODEL}..."):
                    data = extract_invoice(source_text)
                data = verify_invoice_evidence(data, source_text)
                duplicate = find_duplicate(data.vendor_name, data.invoice_number)
                st.session_state["last_invoice_json"] = data.model_dump()
                st.session_state["last_source_text"] = source_text
                if duplicate:
                    st.session_state["duplicate_match"] = duplicate
                    st.session_state["last_issues"] = []
                else:
                    st.session_state.pop("duplicate_match", None)
                    issues = validate_invoice(data, duplicate=False)
                    record_id = save_invoice(uploaded.name, data, issues, source_text=source_text)
                    st.session_state["last_record_id"] = record_id
                    st.session_state["last_issues"] = issues
                    st.success(f"Extraction complete. Record #{record_id} saved for review.")
        except Exception as exc:
            st.error(str(exc))

    if "last_invoice_json" in st.session_state:
        data_dict = st.session_state["last_invoice_json"]
        st.subheader("Latest extraction")
        st.json(data_dict)
        st.subheader("Evidence verification")
        st.caption("The system checks each extracted field against field-specific source context. A match is not a probability or truth guarantee.")
        st.dataframe(confidence_table(data_dict), use_container_width=True, hide_index=True)
        not_verified = [
            f for f in CONFIDENCE_FIELDS
            if (data_dict.get("field_verification") or {}).get(f) != "Verified"
        ]
        if not_verified:
            st.warning("Fields requiring manual source verification: " + ", ".join(not_verified))
        else:
            st.success("All nine tracked fields have field-specific source evidence.")
        issues = st.session_state.get("last_issues", [])
        for issue in issues:
            if issue["severity"] == "error":
                st.error(issue["message"])
            else:
                st.warning(issue["message"])
        duplicate_info = st.session_state.get("duplicate_match")
        if duplicate_info:
            st.subheader("Processing status")
            st.warning(
                f"Duplicate of record #{duplicate_info['id']} "
                f"({duplicate_info['filename']}, workflow status: {duplicate_info['status']}). "
                "No new database record was created."
            )

with tab_review:
    st.subheader("Pending review")
    review_records = list_invoices()
    pending = [r for r in review_records if r["status"] == "Pending Review"]
    status_counts = {status: sum(r["status"] == status for r in review_records)
                     for status in ("Pending Review", "Approved", "Rejected")}
    count_cols = st.columns(3)
    for col, status in zip(count_cols, ("Pending Review", "Approved", "Rejected")):
        col.metric(status, status_counts[status])
    st.caption("Workflow status is read directly from SQLite. Approved and rejected records are not part of the pending queue.")
    if not pending:
        st.info("No documents are waiting for review.")
    for record in pending:
        data = json.loads(record["extracted_json"])
        issues = json.loads(record["issues_json"])
        with st.expander(f"#{record['id']} · {record['filename']} · {data.get('vendor_name') or 'Unknown vendor'}"):
            st.dataframe(confidence_table(data), use_container_width=True, hide_index=True)
            edited = st.text_area("Review or correct extracted JSON", value=json.dumps(data, indent=2), height=360, key=f"edit_{record['id']}")
            for issue in issues:
                st.write(f"- **{issue['severity'].upper()}**: {issue['message']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Approve", key=f"approve_{record['id']}", type="primary"):
                    try:
                        corrected = InvoiceData.model_validate_json(edited)
                        # Recompute evidence against the original stored OCR text;
                        # never trust stale evidence metadata carried in edited JSON.
                        original_source = get_invoice_source(record["id"])
                        if not original_source.strip():
                            st.error("Original source text is unavailable for this legacy record. Reprocess the document before approving.")
                            st.stop()
                        corrected = verify_invoice_evidence(corrected, original_source)
                        new_issues = validate_invoice(corrected)
                        missing_evidence = approval_blockers(corrected)
                        if any(x["severity"] == "error" for x in new_issues):
                            st.error("Blocking validation errors remain.")
                        elif missing_evidence:
                            st.error("Cannot approve until required fields are completed and populated fields have field-specific evidence: " + ", ".join(missing_evidence))
                        else:
                            update_invoice_review(record["id"], corrected, new_issues, "Approved")
                            st.success("Corrections and approval status saved to SQLite.")
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Could not approve: {exc}")
            with col2:
                if st.button("Reject", key=f"reject_{record['id']}"):
                    update_status(record["id"], "Rejected")
                    st.warning("Invoice rejected.")
                    st.rerun()

with tab_history:
    st.subheader("Processed documents")
    records = list_invoices()
    if records:
        display = []
        for r in records:
            details = json.loads(r["extracted_json"])
            summary = build_verification_summary(details.get("field_verification"))
            display.append({
                "ID": r["id"], "Filename": r["filename"], "Vendor": r["vendor_name"],
                "Invoice number": r["invoice_number"], "Total": r["total_amount"],
                "Workflow status": r["status"], "Verification": summary["status"],
                "Verified fields": f"{summary['verified_fields']}/{summary['total_fields']}",
                "Re-evaluations": len(list_verification_audit(r["id"])),
                "Created": r["created_at"]
            })
        st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("Download CSV", csv_bytes(records), "docuflow_invoices.csv", "text/csv")
        with c2:
            st.download_button("Download JSON", json_bytes(records), "docuflow_invoices.json", "application/json")

        st.divider()
        st.subheader("Evidence re-evaluation")
        st.caption("Re-check an existing invoice against its original PDF or image. This updates evidence metadata and creates an audit entry; it does not change the invoice values or Approved/Pending/Rejected status.")
        options = {
            f"#{r['id']} · {r['filename']} · {r.get('vendor_name') or 'Unknown vendor'} · {r['status']}": r
            for r in records
        }
        selected_label = st.selectbox("Select an existing invoice", list(options.keys()), key="reeval_record")
        reeval_file = st.file_uploader(
            "Upload the source PDF or image for this record",
            type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"],
            key="reeval_source_file"
        )
        confirm_recheck = st.checkbox(
            "I confirm this file is the source document for the selected invoice.",
            key="reeval_confirm"
        )
        if st.button("Re-evaluate evidence without changing workflow status", disabled=not (reeval_file and confirm_recheck), key="reeval_run"):
            selected = options[selected_label]
            try:
                source_bytes = reeval_file.getvalue()
                validate_upload(reeval_file.name, len(source_bytes), MAX_UPLOAD_MB)
                with st.spinner("Extracting source text and re-checking stored invoice fields..."):
                    source_text, extraction_method = extract_text(reeval_file.name, source_bytes)
                    if not source_text.strip():
                        raise ValueError("No readable text was extracted from the supplied source file.")
                    stored_data = InvoiceData.model_validate_json(selected["extracted_json"])
                    checked = verify_invoice_evidence(stored_data, source_text)
                    outcome = update_invoice_evidence(selected["id"], checked, source_text, reeval_file.name)
                st.success(
                    f"Evidence re-evaluation saved (audit #{outcome['audit_id']}). "
                    f"Workflow status remains {outcome['workflow_status']}. "
                    f"Verification: {outcome['verification_summary']['status']}."
                )
                st.json(outcome["verification_summary"])
                st.rerun()
            except Exception as exc:
                st.error(f"Evidence re-evaluation failed: {exc}")

        audit_entries = list_verification_audit()
        with st.expander(f"Evidence audit history ({len(audit_entries)} event(s))"):
            if audit_entries:
                audit_display = [{
                    "Audit ID": a["audit_id"], "Invoice ID": a["invoice_id"],
                    "Source file": a["source_filename"],
                    "Workflow status preserved": a["original_workflow_status"],
                    "Re-evaluated at": a["created_at"],
                    "Source SHA-256": a["source_text_sha256"][:16] + "…"
                } for a in audit_entries]
                st.dataframe(pd.DataFrame(audit_display), use_container_width=True, hide_index=True)
            else:
                st.info("No evidence re-evaluations have been recorded yet.")
    else:
        st.info("No processed documents yet.")

st.divider()
st.caption("Prototype disclaimer: AI extraction can be wrong. Verify all fields against the original document before approval.")
