"""Gold-layer product engagement aggregation.

Computes per-product, per-time-window engagement metrics from the Silver Delta
layer:
- views
- cart_additions
- view_to_cart_ratio (null-safe)
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    count,
    countDistinct,
    when,
    window,
)

SILVER_PATH = None  # set by caller


def compute_product_engagement(silver: DataFrame, window_duration: str = "1 hour") -> DataFrame:
    """Aggregate Silver events into per-product engagement metrics."""
    filtered = silver.filter(col("event_type").isin("view", "addtocart"))
    agg = (
        filtered.groupBy(window(col("event_ts"), window_duration), col("entity_id"))
        .agg(
            count(when(col("event_type") == "view", True)).alias("views"),
            count(when(col("event_type") == "addtocart", True)).alias("cart_additions"),
        )
    )
    result = agg.select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("entity_id").alias("product_id"),
        col("views"),
        col("cart_additions"),
        when(col("views") > 0, col("cart_additions") / col("views")).otherwise(None).alias("view_to_cart_ratio"),
    )
    return result