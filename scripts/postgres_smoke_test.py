"""PostgreSQL connectivity smoke test."""

import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5433, dbname="novacart", user="novacart", password="novacart"
)
print("postgres ok, server version:", conn.server_version)
conn.close()