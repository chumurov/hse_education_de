CREATE TABLE credit_applications (
    application_id Utf8 NOT NULL,
    event_time Utf8,
    customer_id Int64,
    region_code Utf8,
    product_type Utf8,
    requested_amount Int64,
    term_months Int32,
    credit_score Int32,
    risk_level Utf8,
    decision_status Utf8,
    approved_amount Int64,
    channel Utf8,
    employee_review_flag Utf8,
    processing_time_sec Int32,
    PRIMARY KEY (application_id)
);