from app.db import connect_db


def load_conversation_history(conversation_id):
    # Read the messages for one conversation in message order.
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = %s
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

    # Convert database rows to the message format expected by Groq.
    return [
        {"role": role, "content": content}
        for role, content in rows
    ]

def save_turn(conversation_id: str, user_message: str, assistant_message: str) -> None:
    # Save both messages in one transaction.
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (%s, 'user', %s)
            """,
            (conversation_id, user_message),
        )
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (%s, 'assistant', %s)
            """,
            (conversation_id, assistant_message),
        )