import pytest

import time


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

@pytest.fixture
def neo4j_session():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    session = driver.session()
    yield session
    session.close()
    driver.close()


@pytest.fixture(autouse=True)
def cleanup_tables(postgres_connection):
    with postgres_connection.cursor() as cursor:
        cursor.execute("TRUNCATE users, orders, inventory CASCADE")
        postgres_connection.commit()

def insert_into_postgres(cursor, table_name, data):
    placeholders = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.execute(query, data)

def check_in_neo4j(session, query, parameters):
    result = session.run(query, parameters)
    return result.single() is not None

# Test function to verify synchronization
@pytest.mark.parametrize("entry", [
    (1, 'Alice', 'example@test.com'),
    (2, 'Bob', 'bob@test.com'),
    (3, 'Charlie', 'charlie@test.com')
])
def test_data_sync(postgres_connection, neo4j_session, entry):
    table_name = 'users'
    neo4j_check_query = "MATCH (n:User {id: $id}) RETURN n"

    with postgres_connection.cursor() as cursor:
        insert_into_postgres(cursor, table_name, entry)
        postgres_connection.commit()

    time.sleep(2) 

    check_params = {'id': entry[0]}
    is_synced = check_in_neo4j(neo4j_session, neo4j_check_query, check_params)

    assert is_synced, f"Data for {entry[1]} should be synced to Neo4j, but it was not found."