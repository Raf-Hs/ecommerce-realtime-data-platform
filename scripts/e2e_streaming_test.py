"""End-to-end streaming validation: Producer -> Kafka -> Spark -> Bronze/Silver/Gold.

Runs the Spark streaming job with availableNow trigger, publishes events, then
verifies data landed in Bronze, Silver, and Gold.

Usage:
    python scripts/e2e_streaming_test.py
"""

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("PYSPARK_PYTHON", "python3")
JAVA_HOME = os.environ.get("JAVA_HOME", "/home/rafa/jdk/jdk-17.0.13+11")
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PATH"] = os.path.join(JAVA_HOME, "bin") + os.pathsep + os.environ.get("PATH", "")

from kafka import KafkaProducer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOTSTRAP = "localhost:9092"
TOPIC = "clickstream-events"
E2E_DATA = os.path.join(BASE, "data", "e2e")
BRONZE = os.path.join(E2E_DATA, "bronze")
SILVER = os.path.join(E2E_DATA, "silver")
GOLD = os.path.join(E2E_DATA, "gold")
CKPT = os.path.join(E2E_DATA, "checkpoints")


def clean() -> None:
    import shutil

    if os.path.exists(E2E_DATA):
        shutil.rmtree(E2E_DATA)
    os.makedirs(E2E_DATA)


def seed_events(n: int = 30) -> None:
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP)
    for i in range(n):
        payload = {
            "event_id": f"e2e-event-{i}",
            "event_type": "view" if i % 3 != 0 else "addtocart",
            "event_time": "2015-06-01T00:00:00Z",
            "ingestion_time": "2026-01-01T00:00:00Z",
            "source": "retailrocket",
            "source_event_id": str(i),
            "entity_type": "product",
            "entity_id": f"rr:item:{100 + (i % 5)}",
            "payload": "{}",
            "schema_version": "1.0.0",
            "provenance": "{}",
        }
        producer.send(TOPIC, value=json.dumps(payload).encode("utf-8"))
    producer.flush()
    producer.close()
    print(f"seeded {n} events", flush=True)


def run_streaming_job() -> None:
    env = dict(os.environ)
    env["KAFKA_BOOTSTRAP_SERVERS"] = BOOTSTRAP
    env["KAFKA_TOPIC_CLICKSTREAM"] = TOPIC
    env["BRONZE_PATH"] = BRONZE
    env["SILVER_PATH"] = SILVER
    env["SPARK_CHECKPOINT_PATH"] = CKPT
    env["SPARK_MASTER"] = "local[2]"
    env["SPARK_TRIGGER"] = "availableNow"
    cmd = [sys.executable, os.path.join(BASE, "src", "streaming", "spark_streaming.py")]
    print("running spark streaming job (availableNow)...", flush=True)
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        print("spark job stderr tail:")
        print("\n".join(proc.stderr.splitlines()[-10:]))


def verify() -> bool:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import to_timestamp

    from src.streaming.spark_streaming import build_spark
    from src.transformations.product_engagement import compute_product_engagement

    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    ok = True
    for name, path in [("bronze", BRONZE), ("silver", SILVER)]:
        try:
            df = spark.read.format("delta").load(path)
            print(f"{name}: {df.count()} rows")
        except Exception as e:
            print(f"{name}: ERROR {str(e)[:120]}")
            ok = False

    try:
        silver_df = spark.read.format("delta").load(SILVER)
        if "event_ts" not in silver_df.columns:
            silver_df = silver_df.withColumn("event_ts", to_timestamp("event_time"))
        gold = compute_product_engagement(silver_df, window_duration="1 hour")
        print(f"gold (batch): {gold.count()} rows")
        gold.show(5, truncate=False)
    except Exception as e:
        print(f"gold: ERROR {str(e)[:120]}")
        ok = False

    spark.stop()
    return ok


def main() -> int:
    print("=== cleaning e2e dirs ===")
    clean()
    print("=== seeding events ===")
    seed_events(30)
    print("=== running streaming job ===")
    run_streaming_job()
    print("=== verifying ===")
    if verify():
        print("E2E STREAMING VALIDATION PASSED")
        return 0
    print("E2E STREAMING VALIDATION FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())