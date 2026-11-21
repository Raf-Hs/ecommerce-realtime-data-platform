"""Benchmark Kafka producer throughput using synthetic events.

Measures how many events per second the replay producer can publish to Kafka.
Results are printed and should be recorded in
docs/benchmarks/PERFORMANCE_BENCHMARKS.md (never fabricated).
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.producers.replay import ReplayProducer
from src.producers.synthetic import generate_inventory_events


def main() -> int:
    n = 5000
    events = list(generate_inventory_events([f"syn:product:{i}" for i in range(100)], n, seed=42))

    producer = ReplayProducer(topic="novacart-bench-test", replay_speed=1000.0, batch_size=500)
    start = time.monotonic()
    stats = producer.publish(events)
    elapsed = time.monotonic() - start
    producer.close()

    eps = stats["sent"] / elapsed if elapsed > 0 else 0
    print(f"events={n} sent={stats['sent']} failed={stats['failed']} elapsed={elapsed:.3f}s eps={eps:.1f}")

    # Clean up topic (best effort, ignore errors)
    try:
        from kafka.admin import KafkaAdminClient

        admin = KafkaAdminClient(bootstrap_servers="localhost:9092")
        admin.delete_topics(["novacart-bench-test"])
        admin.close()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())