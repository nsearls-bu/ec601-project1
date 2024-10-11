import psycopg2
from kafka import KafkaProducer, KafkaConsumer
from neo4j import GraphDatabase
import json

# PostgreSQL connection
pg_conn = psycopg2.connect(
    dbname="db",
    user="user",
    password="mypassword",
    host="localhost",
    port="5430"
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'postgres_updates',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def get_postgres_tables():
    """Function to retrieve all table names in PostgreSQL"""
    with pg_conn.cursor() as cursor:
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        tables = cursor.fetchall()
    return [table[0] for table in tables]

def setup_postgres_trigger_for_table(table_name):
    """Set up PostgreSQL trigger for a given table"""
    with pg_conn.cursor() as cursor:
        trigger_name = f"{table_name}_update_trigger"
        function_name = f"notify_{table_name}_update"

        cursor.execute(f"""
        CREATE OR REPLACE FUNCTION {function_name}() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify('table_update', row_to_json(NEW)::text);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
        CREATE TRIGGER {trigger_name}
        AFTER INSERT OR UPDATE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION {function_name}();
        """)
        pg_conn.commit()

def setup_postgres_triggers():
    """Set up PostgreSQL triggers for all tables in the schema"""
    tables = get_postgres_tables()
    for table in tables:
        setup_postgres_trigger_for_table(table)
        print(f"Trigger set up for table: {table}")

def postgres_notify():
    """Function to notify Kafka of updates in PostgreSQL"""
    with pg_conn.cursor() as cursor:
        cursor.execute("LISTEN table_update;")
        print("Listening to PostgreSQL changes...")

        while True:
            pg_conn.poll()
            while pg_conn.notifies:
                notify = pg_conn.notifies.pop(0)
                data = json.loads(notify.payload)
                print(f"PostgreSQL Update: {data}")

                producer.send('postgres_updates', data)

def process_to_neo4j():
    """Function to process Kafka events and update Neo4j"""
    with neo4j_driver.session() as session:
        for message in consumer:
            data = message.value
            table_name = data.pop('table', None)
            print(f"Received Kafka message from {table_name}: {data}")

            # Dynamically create nodes/relationships based on table name
            if table_name == 'users':
                session.run("""
                    MERGE (u:User {id: $id})
                    SET u += $props
                """, id=data['id'], props=data)
            elif table_name == 'orders':
                session.run("""
                    MATCH (u:User {id: $user_id})
                    MATCH (i:Item {id: $item_id})
                    MERGE (o:Order {id: $id})
                    SET o += $props
                    MERGE (u)-[:PLACED]->(o)-[:CONTAINS]->(i)
                """, id=data['id'], user_id=data['user_id'], item_id=data['item_id'], props=data)
            elif table_name == 'inventory':
                session.run("""
                    MERGE (i:Item {id: $id})
                    SET i += $props
                """, id=data['id'], props=data)
            else:
                print(f"No specific handler for table: {table_name}")

def initial_sync():
    """Initial sync of all PostgreSQL data to Neo4j"""
    tables = get_postgres_tables() 
    for table_name in tables:
        with pg_conn.cursor() as cursor:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            columns = [row[0] for row in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            for row in rows:
                data = dict(zip(columns, row))
                
                with neo4j_driver.session() as session:
                    query = f"""
                    MERGE (n:{table_name.capitalize()} {{id: $id}})
                    SET n += $props
                    """
                    session.run(query, id=data.get('id'), props=data)
                    print(f"Synced data for table {table_name} with id {data.get('id')} to Neo4j")

    print("Initial sync complete.")



if __name__ == "__main__":
    initial_sync()

    setup_postgres_triggers()

    postgres_notify()

    process_to_neo4j()
