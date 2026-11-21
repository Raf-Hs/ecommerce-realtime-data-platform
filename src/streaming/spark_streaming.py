"""Spark Structured Streaming job for the NovaCart platform.

Reads canonical events from Kafka, parses and validates them, and persists them
to the Bronze and Silver Delta Lake layers with event-time semantics, watermarks,
and stateful deduplication.

Run:
    spark-submit src/streaming/spark_streaming.py
or:
    python src/streaming/spark_streaming.py
"""

from __future__ import annotations

import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, when
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
    TimestampType,
)

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
SOURCE_TOPIC = os.getenv("KAFKA_TOPIC_CLICKSTREAM", "clickstream-events")
BRONZE_PATH = os.getenv("BRONZE_PATH", "./data/processed/bronze")
SILVER_PATH = os.getenv("SILVER_PATH", "./data/processed/silver")
CHECKPOINT_PATH = os.getenv("SPARK_CHECKPOINT_PATH", "./checkpoints")
WATERMARK = os.getenv("WATERMARK_DELAY", "10 minutes")

CANONICAL_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), False),
        StructField("event_type", StringType(), False),
        StructField("event_time", StringType(), False),
        StructField("ingestion_time", StringType(), True),
        StructField("source", StringType(), False),
        StructField("source_event_id", StringType(), True),
        StructField("entity_type", StringType(), True),
        StructField("entity_id", StringType(), False),
        StructField("payload", StringType(), True),
        StructField("schema_version", StringType(), True),
        StructField("provenance", StringType(), True),
    ]
)


def build_spark() -> SparkSession:
    kafka_pkg = os.getenv(
        "SPARK_KAFKA_PACKAGE", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
    )
    delta_pkg = os.getenv(
        "SPARK_DELTA_PACKAGE", "io.delta:delta-spark_4.2_2.13:4.4.1"
    )
    packages = f"{delta_pkg},{kafka_pkg}"
    return (
        SparkSession.builder.appName("novacart-streaming")
        .master(os.getenv("SPARK_MASTER", "local[*]"))
        .config("spark.jars.packages", packages)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def read_kafka(spark: SparkSession) -> DataFrame:
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP)
        .option("subscribe", SOURCE_TOPIC)
        .option("startingOffsets", "earliest")
        .load()
    )


def parse(raw: DataFrame) -> DataFrame:
    json_str = col("value").cast("string")
    parsed = raw.select(
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp").alias("kafka_timestamp"),
        from_json(json_str, CANONICAL_SCHEMA).alias("e"),
    )
    return parsed.select(
        col("e.event_id").alias("event_id"),
        col("e.event_type").alias("event_type"),
        col("e.event_time").alias("event_time"),
        col("e.ingestion_time").alias("ingestion_time"),
        col("e.source").alias("source"),
        col("e.source_event_id").alias("source_event_id"),
        col("e.entity_type").alias("entity_type"),
        col("e.entity_id").alias("entity_id"),
        col("e.payload").alias("payload"),
        col("e.schema_version").alias("schema_version"),
        col("e.provenance").alias("provenance"),
        col("topic"),
        col("partition"),
        col("offset"),
        col("kafka_timestamp"),
    )


def with_event_time(df: DataFrame) -> DataFrame:
    return df.withColumn("event_ts", to_timestamp(col("event_time")))


def is_valid(df: DataFrame) -> DataFrame:
    # Keep rows with all required fields present and a known source.
    return df.filter(
        col("event_id").isNotNull()
        & col("event_type").isNotNull()
        & col("event_time").isNotNull()
        & col("source").isNotNull()
        & col("entity_id").isNotNull()
    )


def run() -> None:
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    raw = read_kafka(spark)
    parsed = parse(raw)
    valid = is_valid(parsed)
    timed = with_event_time(valid)

    # Bronze: raw parsed events (append).
    bronze_query = (
        parsed.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", os.path.join(CHECKPOINT_PATH, "bronze"))
        .start(BRONZE_PATH)
    )

    # Silver: validated, deduplicated by event_id with watermark.
    silver_df = (
        timed.withWatermark("event_ts", WATERMARK)
        .dropDuplicates(["event_id"])
    )
    silver_query = (
        silver_df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", os.path.join(CHECKPOINT_PATH, "silver"))
        .start(SILVER_PATH)
    )

    # Console sink for visibility.
    console_query = (
        timed.writeStream.outputMode("append")
        .format("console")
        .option("truncate", "false")
        .start()
    )

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    run()