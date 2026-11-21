# Failure Recovery

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Scenarios

### 1. Kafka producer failure
- **Detection:** send() raises KafkaError; stats.failed incremented.
- **Recovery:** producer retries (retries=5, backoff). Failed messages routed to
  dead-letter-events topic. Replay is idempotent via deterministic event_id.

### 2. Consumer crash
- **Detection:** process exits; consumer group offsets may be partially committed.
- **Recovery:** restart consumer with same group_id; auto_offset_reset=earliest
  ensures reprocessing from last committed offset. Idempotent downstream writes
  (Delta merge / upsert) prevent duplicates.

### 3. Spark job failure
- **Detection:** Spark UI / logs show failed query.
- **Recovery:** restart with the same checkpoint path; Spark resumes from the
  last committed offset. Checkpoint path must be durable.

### 4. Invalid / poison messages
- **Detection:** ValidatingConsumer routes to invalid-events / dead-letter-events.
- **Recovery:** inspect DLQ topic, fix source or schema, replay corrected events.

### 5. Late-arriving events
- **Detection:** events with event_time < watermark are dropped by Spark.
- **Recovery:** documented limitation (M7); tune watermark or reprocess from
  Bronze if needed.

## Recovery commands

```bash
# Restart Kafka
docker compose restart kafka

# Recreate topics (idempotent)
python scripts/create_topics.py

# Replay from beginning
# (set REPLAY_SPEED_MULTIPLIER and run producer)

# Spark recovery: restart job with same checkpoint path
```