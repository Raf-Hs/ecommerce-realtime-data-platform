"""Continuous (streaming) Gold-layer product engagement aggregation.

Reads the Silver Delta table as a stream, computes windowed product engagement
metrics with event-time semantics, and writes them to the Gold Delta table in
append mode with checkpointing for recovery.

Run:
    spark-submit --packages ... src/streaming/gold_streaming.py
"""

from __future__ import annotations

import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, window, to_timestamp

from src.streaming.spark_streaming import build_spark

SILVER_PATH = os.getenv("SILVER_PATH", "./data/processed/silver")
GOLD_PATH = os.getenv("GOLD_PATH", "./data/processed/gold/product_engagement")
CHECKPOINT_PATH = os.getenv("SPARK_CHECKPOINT_PATH", "./checkpoints")
WATERMARK = os.getenv("WATERMARK_DELAY", "10 minutes")
WINDOW = os.getenv("GOLD_WINDOW", "1 hour")


def run() -> None:
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    silver = (
        spark.readStream.format("delta")
        .option("maxFilesPerTrigger", 100)
        .load(SILVER_PATH)
    )

    # Ensure event_ts column exists.
    if "event_ts" not in silver.columns:
        silver = silver.withColumn("event_ts", to_timestamp(col("event_time")))

    filtered = silver.filter(col("event_type").isin("view", "addtocart"))

    agg = (
        filtered.withWatermark("event_ts", WATERMARK)
        .groupBy(window(col("event_ts"), WINDOW), col("entity_id"))
        .agg(
            count(when(col("event_type") == "view", True)).alias("views"),
            count(when(col("event_type") == "addtocart", True)).alias("cart_additions"),
        )
    )

    gold = agg.select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("entity_id").alias("product_id"),
        col("views"),
        col("cart_additions"),
        when(col("views") > 0, col("cart_additions") / col("views"))
        .otherwise(None)
        .alias("view_to_cart_ratio"),
    )

    query = (
        gold.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", os.path.join(CHECKPOINT_PATH, "gold"))
        .start(GOLD_PATH)
    )

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    run()