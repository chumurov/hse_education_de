import json
import random
from datetime import datetime

levels = ["INFO", "WARN", "ERROR", "DEBUG"]
actions = ["login", "logout", "purchase", "view"]

with open("app_logs.jsonl", "w") as f:
    for i in range(100_000_0):
        log = {
            "timestamp": datetime.now().isoformat(),
            "level": random.choice(levels),
            "action": random.choice(actions),
            "user_id": random.randint(1000, 9999),
            "duration_ms": random.randint(10, 500)
        }
        f.write(json.dumps(log) + "\n")
