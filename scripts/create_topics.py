"""Create the standard Kafka topics for the NovaCart platform.

Idempotent: topics that already exist are skipped.
"""

import sys

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

BOOTSTRAP = "localhost:9092"

TOPICS = [
    ("clickstream-events", 6),
    ("transaction-events", 6),
    ("product-events", 3),
    ("inventory-events", 3),
    ("invalid-events", 3),
    ("dead-letter-events", 3),
]


def main() -> int:
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP, client_id="topic-admin")
    created = 0
    for name, partitions in TOPICS:
        try:
            admin.create_topics([NewTopic(name=name, num_partitions=partitions, replication_factor=1)])
            print(f"created: {name} (partitions={partitions})")
            created += 1
        except TopicAlreadyExistsError:
            print(f"exists:  {name}")
    admin.close()
    print(f"Done. {created} new topic(s) created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())