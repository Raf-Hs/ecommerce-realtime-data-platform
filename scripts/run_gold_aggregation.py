"""Run the Gold-layer product engagement aggregation.

Reads Silver Delta, computes per-product engagement metrics, writes them to
Gold Delta and upserts into PostgreSQL.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("PYSPARK_PYTHON", "python3")

from src.storage.delta import read_delta, write_delta
from src.storage.postgres import ensure_gold_tables, get_connection, upsert_product_engagement
from src.streaming.spark_streaming import build_spark
from src.transformations.product_engagement import compute_product_engagement

SILVER_PATH = os.getenv("SILVER_PATH", "./data/processed/silver")
GOLD_PATH = os.getenv("GOLD_PATH", "./data/processed/gold/product_engagement")


def main() -> int:
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    silver = read_delta(spark, SILVER_PATH)
    gold = compute_product_engagement(silver, window_duration="1 hour")
    print("gold rows:", gold.count())
    gold.show(10, truncate=False)

    write_delta(gold, GOLD_PATH, mode="overwrite")

    # Upsert into Postgres
    rows = [
        (
            r["window_start"],
            r["window_end"],
            r["product_id"],
            int(r["views"]),
            int(r["cart_additions"]),
            r["view_to_cart_ratio"],
        )
        for r in gold.collect()
    ]
    conn = get_connection()
    ensure_gold_tables(conn)
    n = upsert_product_engagement(conn, rows)
    conn.close()
    print(f"upserted {n} rows into Postgres gold_product_engagement")

    spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())