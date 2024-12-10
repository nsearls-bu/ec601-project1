# Database Synchronization System

A robust system for real-time synchronization between PostgreSQL and Neo4j databases using Kafka as a message broker. This project enables writing data to PostgreSQL while maintaining synchronized analytics capabilities in Neo4j.

## Overview

This system provides a containerized solution for maintaining consistent data across PostgreSQL and Neo4j databases. It leverages Kafka for event-driven synchronization, ensuring that analytics data remains up-to-date with the primary database.

### Key Features

- Real-time data synchronization between PostgreSQL and Neo4j
- ACID-compliant data writes in PostgreSQL
- Graph-based analytics capabilities in Neo4j
- Event-driven architecture using Kafka
- Fully containerized deployment
- Command-line configuration options

### Scalability

- Load testing and performance optimization
- Distributed deployment capabilities
- Resource utilization monitoring

### Error Handling

- Graceful failure recovery
- Data consistency preservation
- System health monitoring

## System Architecture

### Components

- **PostgreSQL**: Primary database for ACID-compliant data writes
- **Neo4j**: Graph database for real-time analytics
- **Apache Kafka**: Message broker for database synchronization
- **Docker**: Containerization platform for all components

### Data Flow

1. Data is written to PostgreSQL
2. Kafka captures the write events
3. Neo4j is updated in real-time based on Kafka events
4. Analytics are available immediately through Neo4j

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Command-line interface access
- Sufficient system resources for running multiple containers

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Run the deployment script:

```bash
docker-compose up -d
```

### Configuration

The system can be configured through command-line interfaces and manifest files. Detailed configuration options are available for:

- Database connections
- Kafka settings
- Synchronization parameters
- Performance tuning

## User Stories Implementation

### For Data Scientists

- Real-time access to analytics engine
- Synchronized data between PostgreSQL and Neo4j
- Graph-based query capabilities

### For Database Administrators

- Automated synchronization between databases
- Command-line configuration tools
- Monitoring and management capabilities

### For Cloud Administrators

- Optional Helm chart deployment
- Container orchestration support
- Scalability options

## Future plans

### Helm/kubernetes

- Implement manifests for easy kubernetes deployment
- Utilize Kind for single machine testing
- Create helm charts

### Custom schemas

- System for mapping customization yaml to hooks/debezium config

## Contributing

Please read our contribution guidelines before submitting pull requests.
