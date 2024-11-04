'''Test the kafka connectin between postgres and Neo4J'''

import select
import time
from contextlib import contextmanager
import pytest
import psycopg2


def trigger_exists(postgres_connection, trigger_name, table_name):
    """
    Checks if a specified trigger exists on a given table in PostgreSQL.

    Args:
        postgres_connection: The PostgreSQL connection fixture.
        trigger_name (str): Name of the trigger to check.
        table_name (str): Name of the table the trigger should exist on.

    Returns:
        bool: True if the trigger exists, False otherwise.
    """
    with postgres_connection.cursor() as cursor:
        cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM pg_trigger
            WHERE tgname = %s AND tgrelid = %s::regclass
        );
        """, (trigger_name, table_name))
        return cursor.fetchone()[0]


@contextmanager
def get_notification_listener(dsn):
    """
    Context manager to set up a listener for PostgreSQL notifications.

    Args:
        dsn (str): The database source name for connecting to PostgreSQL.

    Yields:
        listen_conn: A connection that listens for notifications.
    """
    listen_conn = psycopg2.connect(dsn)
    try:
        listen_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        yield listen_conn
    finally:
        listen_conn.close()


def test_postgres_trigger(postgres_connection):
    """
    Test to verify that the trigger on the `users` table in PostgreSQL works by listening
    for a notification after an INSERT operation.

    Args:
        postgres_connection: The PostgreSQL connection fixture.
    """
    trigger_name = "users_update_trigger"
    table_name = "users"
    with postgres_connection.cursor() as cursor:
        cursor.execute("""
            SELECT tgname FROM pg_trigger 
            WHERE tgrelid = 'users'::regclass 
            AND tgname = %s
        """, (trigger_name,))
        if not cursor.fetchone():
            pytest.fail(f"Trigger '{trigger_name}' does not exist on table '{table_name}'.")

    dsn = "dbname=db user=user password=mypassword host=localhost port=5430"
    with get_notification_listener(dsn) as listen_conn:
        with listen_conn.cursor() as listen_cursor:
            listen_cursor.execute("LISTEN table_update;")
            with postgres_connection.cursor() as trigger_cursor:
                try:
                    trigger_cursor.execute('''INSERT INTO users (id, name) VALUES
                                           (1, 'Test User') RETURNING id, name''')
                    postgres_connection.commit()
                except Exception as error: # pylint: disable=broad-exception-caught
                    pytest.fail(f"Failed to insert data: {error}")

                max_attempts = 5
                notification_received = False
                for _ in range(max_attempts):
                    if select.select([listen_conn], [], [], 1) != ([], [], []):
                        listen_conn.poll()
                        while listen_conn.notifies:
                            notify = listen_conn.notifies.pop(0)
                            assert 'Test User' in notify.payload, f'''
                            Expected 'Test User' in payload, got "{notify.payload}"'''
                            notification_received = True
                        if notification_received:
                            break
                    time.sleep(0.2)

                assert notification_received, "Notification for INSERT was not received."
