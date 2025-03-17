# Log Monitoring System

A comprehensive log monitoring and analysis system built with Docker Compose, featuring real-time log generation, anomaly detection, and visualization using Elasticsearch, Kibana, and Grafana.

## Overview

This system provides end-to-end log management capabilities:

- **Log Generation**: Simulates application logs with various levels (INFO, WARN, ERROR)
- **Log Analysis**: Processes logs in real-time to detect anomalies
- **Storage & Indexing**: Uses Elasticsearch for efficient log storage and querying
- **Visualization**: Multiple dashboards with Kibana and Grafana
- **Streaming**: Optional Kafka integration for high-throughput log processing

## Architecture

![Architecture Diagram](https://via.placeholder.com/800x400?text=Log+Monitoring+System+Architecture)

The system consists of the following components:

- **Log Generator**: Java application that produces simulated logs
- **Log Analyzer**: Python service that processes logs and detects anomalies
- **Elasticsearch**: Search and analytics engine for log storage
- **Kibana**: Data visualization dashboard for Elasticsearch
- **Grafana**: Advanced metrics visualization platform
- **Kafka** (optional): Message broker for log streaming

## Prerequisites

- Docker Engine (20.10+)
- Docker Compose (2.0+)
- At least 4GB of RAM available for containers

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/log-monitoring-system.git
   cd log-monitoring-system
   ```

2. Create required directories:
   ```bash
   mkdir -p log-files
   ```

3. Start the system:
   ```bash
   docker-compose up -d
   ```

4. Verify all services are running:
   ```bash
   docker-compose ps
   ```

## Accessing the Dashboards

Once the system is up and running, you can access the following interfaces:

- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601
- **Grafana**: http://localhost:3001 (default credentials: admin/admin)
- **Kafka UI**: http://localhost:8080

## Configuration

The system can be configured through environment variables in the docker-compose.yml file:

### Log Generator Configuration
- `LOG_FILE_PATH`: Path to write logs (default: /logs/application.log)
- `KAFKA_ENABLED`: Enable Kafka integration (default: true)
- `KAFKA_BROKER`: Kafka broker address (default: kafka:9092)
- `KAFKA_TOPIC`: Kafka topic for logs (default: logs)

### Log Analyzer Configuration
- `LOG_FILE_PATH`: Path to read logs from (default: /logs/application.log)
- `ANOMALY_FILE_PATH`: Path to write detected anomalies (default: /logs/anomalies.json)
- `ELASTICSEARCH_HOST`: Elasticsearch host (default: elasticsearch)
- `ELASTICSEARCH_PORT`: Elasticsearch port (default: 9200)
- `ELASTICSEARCH_INDEX`: Index for logs (default: logs)
- `ELASTICSEARCH_ANOMALY_INDEX`: Index for anomalies (default: anomalies)
- `KAFKA_ENABLED`: Enable Kafka integration (default: true)
- `KAFKA_BROKER`: Kafka broker address (default: kafka:9092)
- `KAFKA_TOPIC`: Kafka topic for logs (default: logs)
- `KAFKA_CONSUMER_GROUP`: Consumer group ID (default: log-analyzer)

## Usage

### Viewing Logs

1. In Kibana:
   - Go to http://localhost:5601
   - Navigate to "Discover"
   - Select the "logs" index pattern
   - Filter and explore logs

2. In Grafana:
   - Go to http://localhost:3001
   - Log in with admin/admin
   - Navigate to the "Log Monitoring Dashboard"

### Analyzing Anomalies

1. View the "Anomaly Detection Dashboard" in Grafana
2. Check the "Recent Error Logs" panel for error details
3. Monitor the "Anomaly Count" for sudden increases

## Development

### Project Structure

```
log-monitoring-system/
├── log-generator/
│   ├── Dockerfile
│   └── LogGenerator.java
├── log-analyzer/
│   ├── Dockerfile
│   └── analyzer.py
├── kibana-setup/
│   ├── Dockerfile
│   └── kibana_setup.py
├── grafana-setup/
│   ├── Dockerfile
│   └── grafana_setup.py
├── grafana/
│   └── Dockerfile
└── docker-compose.yml
```

### Extending the System

#### Adding Custom Log Sources

To add your own log sources:

1. Create a new service in docker-compose.yml
2. Configure it to write logs in JSON format
3. Update log-analyzer to process your specific log format

#### Creating Custom Dashboards

1. Use the Kibana or Grafana UI to create custom visualizations
2. Export dashboard configurations to make them part of the setup scripts

## Troubleshooting

### Common Issues

1. **Elasticsearch fails to start**: 
   - Increase the vm.max_map_count on your host system:
   ```bash
   sudo sysctl -w vm.max_map_count=262144
   ```

2. **Log analyzer can't connect to Elasticsearch**:
   - Check if Elasticsearch is running: `docker-compose ps elasticsearch`
   - Verify connectivity: `docker-compose exec log-analyzer curl elasticsearch:9200`

3. **Kafka connectivity issues**:
   - Check Zookeeper status: `docker-compose logs zookeeper`
   - Verify Kafka is running: `docker-compose logs kafka`

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
