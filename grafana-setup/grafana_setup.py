import requests
import json
import time
import os

# Configuration from environment variables
GRAFANA_HOST = os.environ.get("GRAFANA_HOST", "http://grafana:3000")
ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
ES_INDEX = os.environ.get("ELASTICSEARCH_INDEX", "logs")
ES_ANOMALY_INDEX = os.environ.get("ELASTICSEARCH_ANOMALY_INDEX", "anomalies")

# Grafana API credentials
GRAFANA_USER = os.environ.get("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.environ.get("GRAFANA_PASSWORD", "admin")


def wait_for_grafana():
    """Wait for Grafana to be available"""
    print("Waiting for Grafana to start...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{GRAFANA_HOST}/api/health", timeout=5)
            if response.status_code == 200:
                print("Grafana is up and running!")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"Waiting for Grafana... ({i+1}/{max_retries})")
        time.sleep(10)

    print("Timed out waiting for Grafana")
    return False


def create_elasticsearch_datasource():
    """Create Elasticsearch data source in Grafana"""
    print("Creating Elasticsearch data source...")

    datasource = {
        "name": "Elasticsearch Logs",
        "type": "elasticsearch",
        "url": ELASTICSEARCH_HOST,
        "access": "proxy",
        "basicAuth": False,
        "isDefault": True,
        "database": f"{ES_INDEX},*",
        "jsonData": {
            "timeField": "timestamp",
            "esVersion": "7.10.0",
            "maxConcurrentShardRequests": 5,
            "logMessageField": "message",
            "logLevelField": "level",
        },
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{GRAFANA_HOST}/api/datasources",
        headers=headers,
        json=datasource,
        auth=(GRAFANA_USER, GRAFANA_PASSWORD),
    )

    if response.status_code == 200:
        print("Elasticsearch data source created successfully")
        return response.json()
    else:
        print(f"Failed to create data source: {response.text}")
        # If it already exists, try to continue
        return None


def create_dashboard():
    """Create a basic log monitoring dashboard"""
    print("Creating log monitoring dashboard...")

    # Dashboard JSON model
    dashboard = {
        "dashboard": {
            "id": None,
            "title": "Log Monitoring Dashboard",
            "tags": ["logs", "monitoring"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "10s",
            "panels": [
                # Panel 1: Log Volume Over Time
                {
                    "id": 1,
                    "title": "Log Volume Over Time",
                    "type": "graph",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "timestamp",
                                    "id": "2",
                                    "settings": {
                                        "interval": "auto",
                                        "min_doc_count": 0,
                                        "trimEdges": 0,
                                    },
                                    "type": "date_histogram",
                                }
                            ],
                            "metrics": [{"id": "1", "type": "count"}],
                            "query": "",
                            "refId": "A",
                        }
                    ],
                    "xaxis": {"mode": "time", "show": True},
                    "yaxes": [
                        {
                            "format": "short",
                            "label": "Count",
                            "logBase": 1,
                            "show": True,
                        },
                        {"format": "short", "logBase": 1, "show": True},
                    ],
                },
                # Panel 2: Log Levels Distribution
                {
                    "id": 2,
                    "title": "Log Levels Distribution",
                    "type": "piechart",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 8},
                    "options": {
                        "legend": {
                            "displayMode": "list",
                            "placement": "right",
                            "values": ["value"],
                        }
                    },
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "level",
                                    "id": "2",
                                    "settings": {
                                        "min_doc_count": 0,
                                        "order": "desc",
                                        "orderBy": "_term",
                                        "size": "10",
                                    },
                                    "type": "terms",
                                }
                            ],
                            "metrics": [{"id": "1", "type": "count"}],
                            "query": "",
                            "refId": "A",
                        }
                    ],
                },
                # Panel 3: Log Types Distribution
                {
                    "id": 3,
                    "title": "Log Types Distribution",
                    "type": "piechart",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 9, "w": 12, "x": 12, "y": 8},
                    "options": {
                        "legend": {
                            "displayMode": "list",
                            "placement": "right",
                            "values": ["value"],
                        }
                    },
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "type",
                                    "id": "2",
                                    "settings": {
                                        "min_doc_count": 0,
                                        "order": "desc",
                                        "orderBy": "_term",
                                        "size": "10",
                                    },
                                    "type": "terms",
                                }
                            ],
                            "metrics": [{"id": "1", "type": "count"}],
                            "query": "",
                            "refId": "A",
                        }
                    ],
                },
                # Panel 4: Recent Error Logs
                {
                    "id": 4,
                    "title": "Recent Error Logs",
                    "type": "table",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 17},
                    "targets": [
                        {
                            "bucketAggs": [],
                            "metrics": [{"id": "1", "type": "logs"}],
                            "query": "level:ERROR",
                            "refId": "A",
                        }
                    ],
                    "options": {"showHeader": True},
                    "fieldConfig": {
                        "defaults": {
                            "custom": {"align": "auto", "displayMode": "auto"}
                        },
                        "overrides": [],
                    },
                },
                # Panel 5: Anomaly Count
                {
                    "id": 5,
                    "title": "Anomaly Count",
                    "type": "stat",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 5, "w": 8, "x": 0, "y": 25},
                    "targets": [
                        {
                            "bucketAggs": [],
                            "metrics": [{"id": "1", "type": "count"}],
                            "query": "is_anomaly:true",
                            "refId": "A",
                        }
                    ],
                    "options": {
                        "textMode": "value",
                        "colorMode": "value",
                        "graphMode": "area",
                        "justifyMode": "auto",
                        "orientation": "horizontal",
                        "reduceOptions": {
                            "calcs": ["sum"],
                            "fields": "",
                            "values": False,
                        },
                    },
                },
            ],
        },
        "folderId": 0,
        "overwrite": True,
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{GRAFANA_HOST}/api/dashboards/db",
        headers=headers,
        json=dashboard,
        auth=(GRAFANA_USER, GRAFANA_PASSWORD),
    )

    if response.status_code == 200:
        print("Dashboard created successfully:", response.json())
        return response.json()
    else:
        print(f"Failed to create dashboard: {response.text}")
        return None


def create_anomaly_dashboard():
    """Create a specialized anomaly monitoring dashboard"""
    print("Creating anomaly monitoring dashboard...")

    # Simplified for this example - in a real implementation,
    # this would contain a specialized dashboard for anomaly monitoring
    dashboard = {
        "dashboard": {
            "id": None,
            "title": "Anomaly Detection Dashboard",
            "tags": ["anomalies", "monitoring"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "10s",
            "panels": [
                # Panel 1: Anomaly Count Over Time
                {
                    "id": 1,
                    "title": "Anomalies Over Time",
                    "type": "graph",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "timestamp",
                                    "id": "2",
                                    "settings": {
                                        "interval": "auto",
                                        "min_doc_count": 0,
                                        "trimEdges": 0,
                                    },
                                    "type": "date_histogram",
                                }
                            ],
                            "metrics": [{"id": "1", "type": "count"}],
                            "query": "is_anomaly:true",
                            "refId": "A",
                        }
                    ],
                },
                # Panel 2: Anomaly Reasons
                {
                    "id": 2,
                    "title": "Anomaly Reasons",
                    "type": "piechart",
                    "datasource": "Elasticsearch Logs",
                    "gridPos": {"h": 9, "w": 12, "x": 0, "y": 8},
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "anomaly_reason",
                                    "id": "2",
                                    "settings": {
                                        "min_doc_count": 0,
                                        "order": "desc",
                                        "orderBy": "_term",
                                        "size": "10",
                                    },
                                    "type": "terms",
                                }
                            ],
                            "metrics": [{"id": "1", "type": "count"}],
                            "query": "is_anomaly:true",
                            "refId": "A",
                        }
                    ],
                },
            ],
        },
        "folderId": 0,
        "overwrite": True,
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{GRAFANA_HOST}/api/dashboards/db",
        headers=headers,
        json=dashboard,
        auth=(GRAFANA_USER, GRAFANA_PASSWORD),
    )

    if response.status_code == 200:
        print("Anomaly dashboard created successfully")
        return response.json()
    else:
        print(f"Failed to create anomaly dashboard: {response.text}")
        return None


def main():
    """Main function to set up Grafana"""
    if wait_for_grafana():
        time.sleep(5)  # Give Grafana a moment to fully initialize
        create_elasticsearch_datasource()
        create_dashboard()
        create_anomaly_dashboard()
        print("Grafana setup completed successfully!")
    else:
        print("Failed to connect to Grafana, setup aborted.")


if __name__ == "__main__":
    main()
