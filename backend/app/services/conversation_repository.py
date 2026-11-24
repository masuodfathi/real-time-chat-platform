from app.db import connect_db
from uuid import uuid4


def conversation_exists(conversation_id):
    # Check whether this conversation has a row in PostgreSQL.
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM conversations
            WHERE id = %s
            """,
            (conversation_id,),
        ).fetchone()

    return row is not None

def create_conversation():
    # Generate a UUID for the new conversation.
    conversation_id = uuid4()

    # Insert the conversation and commit when the block exits successfully.
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO conversations (id) VALUES (%s)",
            (conversation_id,),
        )

    return str(conversation_id)