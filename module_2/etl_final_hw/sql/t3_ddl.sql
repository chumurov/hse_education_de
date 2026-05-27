CREATE TABLE loan_applications_flat (
    application_id Utf8 NOT NULL,
    customer_id Utf8,
    region Utf8,
    loan_amount Int64,
    term_months Int32,
    scoring_score Int32,
    risk_level Utf8,
    first_document_type Utf8,
    first_document_status Utf8,
    documents_count Int32,
    decision_status Utf8,
    submitted_at Utf8,
    kafka_topic Utf8,
    kafka_partition Int32,
    kafka_offset Int64,
    processed_at Utf8,
    PRIMARY KEY (application_id)
);