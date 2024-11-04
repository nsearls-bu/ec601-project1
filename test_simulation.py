'''E2E test of inserting into postgres and checking Neo4J'''

import time
import pytest


def insert_into_postgres(cursor, table_name, data):
    """
    Inserts a row into a specified PostgreSQL table.

    Args:
        cursor: The database cursor for executing SQL commands.
        table_name (str): The name of the table to insert data into.
        data (tuple): The data to insert as a tuple.
    """
    placeholders = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.execute(query, data)

def check_in_neo4j(session, query, parameters):
    """
    Checks for the existence of a node in Neo4j by running a specified query.

    Args:
        session: The Neo4j session to execute the query.
        query (str): The Cypher query to check node existence.
        parameters (dict): Parameters to pass to the Cypher query.

    Returns:
        bool: True if the node exists, False otherwise.
    """
    result = session.run(query, parameters)
    return result.single() is not None

@pytest.mark.parametrize("entry", [
    (1, 'Alice', 'example@test.com'),
    (2, 'Bob', 'bob@test.com'),
    (3, 'Charlie', 'charlie@test.com')
])
def test_data_sync(postgres_connection, neo4j_session, entry):
    """
    Tests data synchronization between PostgreSQL and Neo4j by inserting a user into
    PostgreSQL and checking if it appears in Neo4j after a brief delay.

    Args:
        postgres_connection: The PostgreSQL connection fixture.
        neo4j_session: The Neo4j session fixture.
        entry (tuple): The user entry to be inserted, including user ID, name, and email.
    """
    table_name = 'users'
    neo4j_check_query = "MATCH (n:User {id: $id}) RETURN n"

    with postgres_connection.cursor() as cursor:
        insert_into_postgres(cursor, table_name, entry)
        postgres_connection.commit()

    time.sleep(2)  # Wait for data sync

    check_params = {'id': entry[0]}
    is_synced = check_in_neo4j(neo4j_session, neo4j_check_query, check_params)

    assert is_synced, f"Data for {entry[1]} should be synced to Neo4j, but it was not found."
