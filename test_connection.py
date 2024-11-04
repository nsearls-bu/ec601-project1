import pytest
import json
import select
import time
from contextlib import contextmanager
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from server.server import initial_sync

@pytest.fixture
def postgres_connection():
    import psycopg2
    conn = psycopg2.connect(
        dbname="db",
        user="user",
        password="mypassword",
        host="localhost",
        port="5430"
    )
    yield conn
    conn.close()

@pytest.fixture(autouse=True)
def cleanup_tables(postgres_connection):
    with postgres_connection.cursor() as cursor:
        cursor.execute("TRUNCATE users, orders, inventory CASCADE")
        postgres_connection.commit()

@pytest.fixture
def neo4j_session():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    session = driver.session()
    yield session
    session.close()
    driver.close()

@pytest.fixture
def kafka_producer():
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    yield producer
    producer.close()

@pytest.fixture
def kafka_consumer():
    from kafka import KafkaConsumer
    consumer = KafkaConsumer(
        'postgres_updates',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    yield consumer
    consumer.close()

def trigger_exists(postgres_connection, trigger_name, table_name):
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
    import psycopg2
    listen_conn = psycopg2.connect(dsn)
    try:
        listen_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        yield listen_conn
    finally:
        listen_conn.close()

def test_postgres_trigger(postgres_connection):
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
                    trigger_cursor.execute("INSERT INTO users (id, name) VALUES (1, 'Test User') RETURNING id, name")
                    postgres_connection.commit()
                except Exception as e:
                    pytest.fail(f"Failed to insert data: {e}")

                max_attempts = 5
                notification_received = False
                for attempt in range(max_attempts):
                    if select.select([listen_conn], [], [], 1) != ([], [], []):
                        listen_conn.poll()
                        while listen_conn.notifies:
                            notify = listen_conn.notifies.pop(0)
                            assert 'Test User' in notify.payload, f"Expected 'Test User' in payload, got '{notify.payload}'"
                            notification_received = True
                        if notification_received:
                            break
                    time.sleep(0.2)
                
                assert notification_received, "Notification for INSERT was not received."
