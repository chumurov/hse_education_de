use std::fs::File;
use std::io::{BufRead, BufReader};
use serde::{Deserialize, Serialize};
use clickhouse::{Client, Row};
use std::time::Instant;
fn get_client() -> Client {
    Client::default()
        .with_url("http://localhost:8123")
        .with_user("default")
        .with_database("default")
        .with_option("async_insert", "1")
        .with_option("wait_for_async_insert", "0")
}

// 1. Описываем данные.
// Добавляем Row для работы с ClickHouse
#[derive(Debug, Deserialize, Serialize, Row)]
struct LogEntry {
    timestamp: String,
    level: String,
    action: String,
    user_id: u32,
    duration_ms: u64,
}

async fn create_table(client: &Client) -> Result<(), clickhouse::error::Error> {
    client
        .query("
            CREATE TABLE IF NOT EXISTS logs (
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

async fn insert_batch(client: &Client, batch: Vec<LogEntry>) -> Result<(), clickhouse::error::Error> {
    let mut insert = client.insert::<LogEntry>("logs").await?;
    
    for item in batch {
        insert.write(&item).await?;
    }
    
    insert.end().await
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let start = Instant::now();
    // 2. Открываем файл.
    let file = File::open("app_logs.jsonl")?;
    let reader = BufReader::new(file);
    
    let client = get_client();
    create_table(&client).await?;

    let mut batch = Vec::new();
    let batch_size = 1000;

    for line_result in reader.lines() {
        let line = line_result?;

        match serde_json::from_str::<LogEntry>(&line) {
            Ok(log) => {
                if log.duration_ms > 100 {
                    batch.push(log);
                    
                    if batch.len() >= batch_size {
                        println!("Inserting batch of {}", batch.len());
                        insert_batch(&client, batch.split_off(0)).await?;
                    }
                }
            }
            Err(e) => eprintln!("Failed to parse line: {}", e),
        }
    }

    // Вставляем остатки
    if !batch.is_empty() {
        println!("Inserting final batch of {}", batch.len());
        insert_batch(&client, batch).await?;
    }
    let duration = start.elapsed();
    println!("Time: {:?}", duration);
    Ok(())

}
