"""Helpers for reading and writing Delta Lake tables."""

from __future__ import annotations

from pyspark.sql import DataFrame


def write_delta(df: DataFrame, path: str, mode: str = "append") -> None:
    """Write a DataFrame to a Delta table at ``path``."""
    df.write.format("delta").mode(mode).save(path)


def read_delta(spark, path: str) -> DataFrame:
    """Read a Delta table from ``path``."""
    return spark.read.format("delta").load(path)