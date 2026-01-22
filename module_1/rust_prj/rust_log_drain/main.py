import json
import time
from datetime import datetime
import clickhouse_connect

def get_client():
    return clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='default',
        password='',
        database='default'
    )

def create_table(client):
    # Удаляем таблицу, если она существует, для чистоты эксперимента (как в Rust скрипте)
    client.command('DROP TABLE IF EXISTS app_logs')
    client.command('''
        CREATE TABLE IF NOT EXISTS app_logs (
            timestamp String,
            level String,
            action String,
            user_id UInt32,
            duration_ms UInt64
        ) ENGINE = MergeTree()
        ORDER BY timestamp
    ''')

def main():
    start_time = time.time()
    client = get_client()
    create_table(client)

    batch_size = 100_000
    batch = []
    count = 0

    print("Starting log drain...")

    try:
        with open('app_logs.jsonl', 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                entry = json.loads(line)
                # Подготавливаем кортеж для вставки (порядок должен соответствовать схеме)
                row = (
                    entry['timestamp'],
                    entry['level'],
                    entry['action'],
                    entry['user_id'],
                    entry['duration_ms']
                )
                batch.append(row)
                count += 1

                if len(batch) >= batch_size:
                    client.insert('app_logs', batch, column_names=['timestamp', 'level', 'action', 'user_id', 'duration_ms'])
                    batch = []
                    print(f"Processed {count} lines...")

        # Вставляем остатки
        if batch:
            client.insert('app_logs', batch, column_names=['timestamp', 'level', 'action', 'user_id', 'duration_ms'])

    except FileNotFoundError:
        print("Error: app_logs.jsonl not found")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    end_time = time.time()
    print("Logs successfully drained to ClickHouse!")
    print(f"Processed {count} lines total.")
    print(f"Time: {end_time - start_time:.2f}s")

if __name__ == '__main__':
    main()
