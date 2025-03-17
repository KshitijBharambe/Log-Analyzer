import os
import time
import json
import threading
from datetime import datetime
from elasticsearch import Elasticsearch

# Kafka imports
from kafka import KafkaConsumer

# Get configuration from environment variables
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "/logs/application.log")
ANOMALY_FILE_PATH = os.environ.get("ANOMALY_FILE_PATH", "/logs/anomalies.json")
ES_HOST = os.environ.get("ELASTICSEARCH_HOST", "elasticsearch")
ES_PORT = int(os.environ.get("ELASTICSEARCH_PORT", "9200"))
ES_INDEX = os.environ.get("ELASTICSEARCH_INDEX", "logs")
ES_ANOMALY_INDEX = os.environ.get("ELASTICSEARCH_ANOMALY_INDEX", "anomalies")

# Kafka configuration
KAFKA_ENABLED = os.environ.get("KAFKA_ENABLED", "false").lower() == "true"
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "logs")
KAFKA_CONSUMER_GROUP = os.environ.get("KAFKA_CONSUMER_GROUP", "log-analyzer")


# Initialize Elasticsearch client
def init_elasticsearch():
    """Initialize and configure Elasticsearch client"""
    print(f"Connecting to Elasticsearch at {ES_HOST}:{ES_PORT}")

    es = Elasticsearch([{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}])

    # Create indices if they don't exist
    if not es.indices.exists(index=ES_INDEX):
        print(f"Creating index: {ES_INDEX}")
        es.indices.create(
            index=ES_INDEX,
            body={
                "mappings": {
                    "properties": {
                        "timestamp": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss.SSS",
                        },
                        "level": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "message": {"type": "text"},
                        "errorId": {"type": "keyword"},
                        "is_anomaly": {"type": "boolean"},
                    }
                }
            },
        )

    if not es.indices.exists(index=ES_ANOMALY_INDEX):
        print(f"Creating index: {ES_ANOMALY_INDEX}")
        es.indices.create(
            index=ES_ANOMALY_INDEX,
            body={
                "mappings": {
                    "properties": {
                        "timestamp": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss.SSS",
                        },
                        "level": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "message": {"type": "text"},
                        "errorId": {"type": "keyword"},
                        "anomaly_reason": {"type": "text"},
                        "detected_at": {"type": "date"},
                    }
                }
            },
        )

    return es


def analyze_log(log_line, es):
    """Analyze a single log line and index it to Elasticsearch"""
    try:
        # Parse the JSON-like log entry
        log_entry = json.loads(log_line)

        # Basic anomaly detection
        is_anomaly = False
        anomaly_reason = ""

        # Check for ERROR level logs
        if log_entry.get("level") == "ERROR":
            is_anomaly = True
            anomaly_reason = "Error log detected"

        # Check for errorId which indicates an anomaly pattern
        if "errorId" in log_entry:
            is_anomaly = True
            anomaly_reason = f"Part of error pattern {log_entry['errorId']}"

        # Check for slow responses in warning logs
        if log_entry.get("level") == "WARN" and "slow response" in log_entry.get(
            "message", ""
        ):
            is_anomaly = True
            anomaly_reason = "Slow response detected"

        # Add the analysis results to the log entry
        log_entry["is_anomaly"] = is_anomaly
        if is_anomaly:
            log_entry["anomaly_reason"] = anomaly_reason

            # Create a separate anomaly document with detection timestamp
            anomaly_doc = log_entry.copy()

            # Use ISO format for the timestamp which Elasticsearch can parse
            anomaly_doc["detected_at"] = datetime.now().isoformat()

            # Index the anomaly
            try:
                es.index(index=ES_ANOMALY_INDEX, body=anomaly_doc)
                print(f"Indexed anomaly to {ES_ANOMALY_INDEX}: {anomaly_reason}")
            except Exception as e:
                print(f"Error indexing anomaly to Elasticsearch: {str(e)}")

        # Index the log entry
        try:
            es.index(index=ES_INDEX, body=log_entry)
        except Exception as e:
            print(f"Error indexing log to Elasticsearch: {str(e)}")

        return log_entry

    except json.JSONDecodeError:
        print(f"Error parsing log line: {log_line}")
        return None
    except Exception as e:
        print(f"Error analyzing log: {str(e)}")
        return None


def monitor_log_file(es):
    """Monitor the log file for new entries and index them to Elasticsearch"""
    print(f"Starting file-based log analyzer")
    print(f"Watching file: {LOG_FILE_PATH}")

    # Keep track of the file position
    file_position = 0
    anomalies = []

    try:
        # Create the log directory if it doesn't exist
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(ANOMALY_FILE_PATH), exist_ok=True)

        # Wait for the log file to be created if it doesn't exist
        while not os.path.exists(LOG_FILE_PATH):
            print("Waiting for log file to be created...")
            time.sleep(1)

        while True:
            # Open the file and seek to the last position
            with open(LOG_FILE_PATH, "r") as f:
                f.seek(file_position)

                # Read new lines
                new_lines = f.readlines()

                if new_lines:
                    print(f"Processing {len(new_lines)} new log entries from file")

                    # Process each new line
                    for line in new_lines:
                        result = analyze_log(line.strip(), es)

                        if result and result.get("is_anomaly"):
                            print(
                                f"ANOMALY DETECTED: {result.get('anomaly_reason')} - {result.get('message')}"
                            )
                            anomalies.append(result)

                    # Save anomalies to file (keeping this for backward compatibility)
                    if anomalies:
                        with open(ANOMALY_FILE_PATH, "w") as anomaly_file:
                            json.dump(anomalies, anomaly_file, indent=2)
                        print(
                            f"Saved {len(anomalies)} anomalies to {ANOMALY_FILE_PATH}"
                        )

                # Update file position
                file_position = f.tell()

            # Sleep for a bit before checking again
            time.sleep(1)

    except Exception as e:
        print(f"Error monitoring log file: {str(e)}")


def consume_kafka_logs(es):
    """Consume logs from Kafka topic and analyze them"""
    print(f"Starting Kafka consumer for topic {KAFKA_TOPIC}")

    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            group_id=KAFKA_CONSUMER_GROUP,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode("utf-8"),
        )

        # Start consuming messages
        for message in consumer:
            try:
                log_line = message.value
                print(f"Received log from Kafka: {log_line[:100]}...")

                # Analyze and index the log
                result = analyze_log(log_line, es)

                if result and result.get("is_anomaly"):
                    print(
                        f"KAFKA ANOMALY DETECTED: {result.get('anomaly_reason')} - {result.get('message')}"
                    )

            except Exception as e:
                print(f"Error processing Kafka message: {str(e)}")

    except Exception as e:
        print(f"Error setting up Kafka consumer: {str(e)}")


def main():
    """Main function to start log analysis"""
    print("Starting log analyzer with Elasticsearch integration")

    if KAFKA_ENABLED:
        print("Kafka integration enabled")
        print(f"Kafka broker: {KAFKA_BROKER}")
        print(f"Kafka topic: {KAFKA_TOPIC}")
        print(f"Kafka consumer group: {KAFKA_CONSUMER_GROUP}")

    # Initialize Elasticsearch
    retries = 5
    es = None

    while retries > 0 and es is None:
        try:
            es = init_elasticsearch()
            print("Successfully connected to Elasticsearch")
        except Exception as e:
            print(f"Failed to connect to Elasticsearch: {str(e)}")
            print(f"Retrying in 5 seconds... ({retries} attempts left)")
            time.sleep(5)
            retries -= 1

    if es is None:
        print("Could not connect to Elasticsearch after multiple attempts. Exiting.")
        return

    # Start file monitoring thread
    file_thread = threading.Thread(target=monitor_log_file, args=(es,))
    file_thread.daemon = True
    file_thread.start()

    # Start Kafka consumer if enabled
    if KAFKA_ENABLED:
        kafka_thread = threading.Thread(target=consume_kafka_logs, args=(es,))
        kafka_thread.daemon = True
        kafka_thread.start()

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down log analyzer...")


if __name__ == "__main__":
    main()
