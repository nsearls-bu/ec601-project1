'''Contains fixtures for pytest'''
import json
from neo4j import GraphDatabase
from kafka import KafkaProducer, KafkaConsumer
import pytest
import psycopg2


@pytest.fixture(scope="session",name="postgres_connection")
def fixture_postgres_connection():
    """
    Fixture for setting up a PostgreSQL connection. Yields an active connection
    and closes it after the test completes.
    """
    conn = psycopg2.connect(
        dbname="db",
        user="user",
        password="mypassword",
        host="localhost",
        port="5430"
    )
    yield conn
    conn.close()


@pytest.fixture(autouse=True, scope="session", name="cleanup_tables")
def fixtures_cleanup_tables(postgres_connection):
    """
    Automatically cleans up tables in PostgreSQL before each test by truncating
    `users`, `orders`, and `inventory` tables.
    """
    with postgres_connection.cursor() as cursor:
        cursor.execute("TRUNCATE users, orders, inventory CASCADE")
        postgres_connection.commit()


@pytest.fixture(name="neo4j_session",scope="session")
def fixture_neo4j_session():
    """
    Fixture for setting up a Neo4j session. Yields an active session and
    closes it after the test completes.
    """
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    session = driver.session()
    yield session
    session.close()
    driver.close()


@pytest.fixture(scope="session", name="kafka_producer")
def fixture_kafka_producer():
    """
    Fixture for setting up a Kafka producer. Yields an active producer and
    closes it after the test completes.
    """
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    yield producer
    producer.close()


@pytest.fixture(scope="session", name="kafka_consumer")
def fixture_kafka_consumer():
    """
    Fixture for setting up a Kafka consumer. Yields an active consumer and
    closes it after the test completes.
    """
    consumer = KafkaConsumer(
        'postgres_updates',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    yield consumer
    consumer.close()
