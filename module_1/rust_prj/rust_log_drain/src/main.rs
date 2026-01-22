use std::fs::File;
use std::io::{BufRead, BufReader};
use serde::{Deserialize, Serialize};
use std::error::Error;
use clickhouse::{Client, Row};
use std::time::Instant;
fn get_client() -> Client {
    Client::default()
        .with_url("http://localhost:8123")
        .with_user("default")
        .with_database("default")
}

async fn create_table(client: &Client) -> Result<(), clickhouse::error::Error> {
    client
        .query("
            CREATE TABLE IF NOT EXISTS app_logs (
                timestamp String,
                level String,
                action String,
                user_id UInt32,
                duration_ms UInt64
            ) ENGINE = MergeTree()
            ORDER BY timestamp
        ")
        .execute()
        .await
}

#[derive(Debug, Deserialize, Serialize, Row)]
struct LogEntry {
    timestamp: String,
    level: String, 
    action: String,
    user_id: u32,
    duration_ms: u64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let start = Instant::now();
    let file = File::open("app_logs.jsonl")?;
    let reader = BufReader::with_capacity(1024 * 1024, file);
    let client = get_client();
    
    create_table(&client).await?;

    let mut inserter = client.inserter::<LogEntry>("app_logs")
        .with_max_rows(500_000);

    let mut count = 0;
    for line_result in reader.lines() {
        let line = line_result?;
        let entry: LogEntry = serde_json::from_str(&line)?;
        
        inserter.write(&entry).await?;

        count += 1;
        if count % 100_000 == 0 {
            println!("Processed {} lines...", count);
        }
    }

    inserter.end().await?;

    println!("Logs successfully drained to ClickHouse!");
    let duration = start.elapsed();
    println!("Time: {:?}", duration);
    Ok(())
}
