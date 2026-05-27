CREATE TABLE transactions_v2 (
    transaction_id Utf8 NOT NULL,
    customer_id Utf8,
    transaction_timestamp Utf8,
    amount Double,
    merchant_category Utf8,
    is_fraud Int32,
    year Int32,
    month Int32,
    PRIMARY KEY (transaction_id)
);