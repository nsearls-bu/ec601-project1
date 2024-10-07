# Sprint 2 Definitions:

The goal of Sprint 2 is to integrate PostgreSQL and Neo4j databases into a functional system, synchronized via Kafka, running on a single machine using containerized images. PostgreSQL will handle data writes, while Neo4j will provide real-time analytics. 
The focus is to package the stack together and ensure smooth data flow between the two databases.

## System Description:
### Database Endpoints:
PostgreSQL for data writing (ACID compliance).
Neo4j for real-time data analytics (graph data read).
### Data Synchronization:
Kafka will handle event-based synchronization between PostgreSQL and Neo4j.
When data is posted to PostgreSQL, Kafka triggers an update in Neo4j.
### MVP Goal:
The stack should be fully operational locally with container images, synchronizing data between the two databases when written in PostgreSQL.

## Objectives

Implement PostgreSQL and Neo4j in a Docker-based environment.
Use Kafka to facilitate real-time updates from PostgreSQL to Neo4j.
Ensure ACID compliance for SQL data and evaluate if we can use an ACID-compliant GraphDB for Neo4j.
Run the entire system on a single machine as a prototype.

## User Stories

    Real-time Data Access:
        As a data scientist, I should be able to access the Neo4j analytics engine in real-time as the PostgreSQL database is updated.

    Database Synchronization:
        As a database admin, I should be able to automatically synchronize Neo4j and PostgreSQL whenever new data is written.

    Command Line Configuration:
        As an admin, I want to use the command line and manifest files to configure the connection between PostgreSQL and Neo4j.

    Helm Chart Deployment (Optional):
        As a cloud administrator, I want to be able to install this stack using a Helm chart for easier deployment and management.

## Sprint 3 Plans

### Scalability and Performance:
    As a network engineer, I want to ensure the system performs without significant impact under load, and it can scale efficiently when deployed in larger environments.

### Error Handling and Recovery:
    As an end user, I want the system to handle failures gracefully, ensuring that data is not lost even if part of the system becomes unavailable.

### Security and Compliance:
    As a system that may gather personal identifiable information (PII), I want to ensure that the data management adheres to GDPR and similar privacy regulations, with mechanisms for data removal on request.

## Expected Results for Sprint 2

A fully containerized system running on a single machine that allows real-time updates from PostgreSQL to Neo4j.
Successful synchronization via Kafka between both databases.
Basic command-line configuration and potentially optional Helm chart installation.
Performance tested for basic scalability and error handling to ensure data integrity.
Demo that shows insertion of data into Postgres and live-reflection in graph database.
