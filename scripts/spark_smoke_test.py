"""Spark smoke test: batch-read from Kafka, parse, and write to Delta.

Validates that the Spark + Delta stack works end to end without running the
long-lived streaming job.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.streaming.spark_streaming import (
    CANONICAL_SCHEMA,
    build_spark,
    parse,
    with_event_time,
)

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC_CLICKSTREAM", "clickstream-events")


def _seed_topic() -> None:
    from kafka import KafkaProducer
    import json
    import time

    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP)
    payload = {
        "event_id": "spark-smoke-event-1",
        "event_type": "view",
        "event_time": "2015-06-01T00:00:00Z",
        "ingestion_time": "2026-01-01T00:00:00Z",
        "source": "retailrocket",
        "source_event_id": "1",
        "entity_type": "product",
        "entity_id": "rr:item:100",
        "payload": "{}",
        "schema_version": "1.0.0",
        "provenance": "{}",
    }
    producer.send(TOPIC, value=json.dumps(payload).encode("utf-8"))
    producer.flush()
    producer.close()
    time.sleep(1)


def main() -> int:
    _seed_topic()
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    raw = (
        spark.read.format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .option("endingOffsets", "latest")
        .load()
    )
    parsed = parse(raw)
    timed = with_event_time(parsed)
    print("rows read:", timed.count())
    timed.show(5, truncate=False)

    out = tempfile.mkdtemp(prefix="novacart-spark-smoke-")
    path = os.path.join(out, "bronze")
    timed.write.format("delta").mode("overwrite").save(path)
    print("wrote delta to:", path)

    # read back
    back = spark.read.format("delta").load(path)
    print("read back rows:", back.count())
    spark.stop()
    print("SPARK SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())