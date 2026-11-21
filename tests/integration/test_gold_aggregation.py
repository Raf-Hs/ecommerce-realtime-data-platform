"""Integration test: Gold product engagement aggregation (Spark)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("PYSPARK_PYTHON", "python3")

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StringType, StructType, StructField, TimestampType
    from datetime import datetime
    SPARK_AVAILABLE = True
except Exception:
    SPARK_AVAILABLE = False


@pytest.mark.skipif(not SPARK_AVAILABLE, reason="Spark not available")
def test_product_engagement_aggregation() -> None:
    from src.transformations.product_engagement import compute_product_engagement

    spark = SparkSession.builder.master("local[1]").appName("gold-test").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    schema = StructType(
        [
            StructField("event_id", StringType()),
            StructField("event_type", StringType()),
            StructField("event_ts", TimestampType()),
            StructField("entity_id", StringType()),
        ]
    )
    rows = [
        ("e1", "view", datetime(2015, 6, 1, 0, 0), "rr:item:100"),
        ("e2", "view", datetime(2015, 6, 1, 0, 5), "rr:item:100"),
        ("e3", "addtocart", datetime(2015, 6, 1, 0, 10), "rr:item:100"),
        ("e4", "view", datetime(2015, 6, 1, 1, 0), "rr:item:200"),
    ]
    df = spark.createDataFrame(rows, schema)
    gold = compute_product_engagement(df, window_duration="1 hour")
    result = {r["product_id"]: r for r in gold.collect()}
    assert result["rr:item:100"]["views"] == 2
    assert result["rr:item:100"]["cart_additions"] == 1
    assert abs(result["rr:item:100"]["view_to_cart_ratio"] - 0.5) < 1e-9
    assert result["rr:item:200"]["views"] == 1
    assert result["rr:item:200"]["cart_additions"] == 0
    spark.stop()