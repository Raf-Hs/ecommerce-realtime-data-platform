"""PostgreSQL serving helpers for Gold-layer metrics."""

from __future__ import annotations

import os

import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        dbname=os.getenv("POSTGRES_DB", "novacart"),
        user=os.getenv("POSTGRES_USER", "novacart"),
        password=os.getenv("POSTGRES_PASSWORD", "novacart"),
    )


def ensure_gold_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_product_engagement (
                window_start TIMESTAMP NOT NULL,
                window_end TIMESTAMP NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                views BIGINT,
                cart_additions BIGINT,
                view_to_cart_ratio DOUBLE PRECISION,
                PRIMARY KEY (window_start, product_id)
            );
            """
        )
    conn.commit()


def upsert_product_engagement(conn, rows: list[tuple]) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO gold_product_engagement
                (window_start, window_end, product_id, views, cart_additions, view_to_cart_ratio)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (window_start, product_id) DO UPDATE SET
                window_end = EXCLUDED.window_end,
                views = EXCLUDED.views,
                cart_additions = EXCLUDED.cart_additions,
                view_to_cart_ratio = EXCLUDED.view_to_cart_ratio;
            """,
            rows,
        )
    conn.commit()
    return len(rows)