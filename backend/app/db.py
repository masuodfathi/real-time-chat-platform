import os

import psycopg


def connect_db():
    # Open a connection to the local PostgreSQL service.
    return psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname="realtime_chat",
        user="chat_dev",
        password=os.environ["CHAT_DB_PASSWORD"],
        connect_timeout=5,
    )