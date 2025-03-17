import requests
import time
import os

# Kibana configuration
KIBANA_HOST = os.environ.get("KIBANA_HOST", "http://kibana:5601")
ES_INDEX = os.environ.get("ELASTICSEARCH_INDEX", "logs")
ES_ANOMALY_INDEX = os.environ.get("ELASTICSEARCH_ANOMALY_INDEX", "anomalies")


def wait_for_kibana():
    """Wait for Kibana to be available"""
    print("Waiting for Kibana to start...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{KIBANA_HOST}/api/status", timeout=5)
            if response.status_code == 200:
                print("Kibana is up and running!")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"Waiting for Kibana... ({i+1}/{max_retries})")
        time.sleep(10)

    print("Timed out waiting for Kibana")
    return False


def create_index_patterns():
    """Create index patterns for logs and anomalies"""
    headers = {"Content-Type": "application/json", "kbn-xsrf": "true"}

    # Create logs index pattern
    logs_pattern = {"index_pattern": {"title": ES_INDEX, "timeFieldName": "timestamp"}}

    response = requests.post(
        f"{KIBANA_HOST}/api/index_patterns/index_pattern",
        headers=headers,
        json=logs_pattern,
    )

    if response.status_code in (200, 201):
        print(f"Created logs index pattern: {response.json()}")
    else:
        print(f"Failed to create logs index pattern: {response.text}")

    # Create anomalies index pattern
    anomalies_pattern = {
        "index_pattern": {"title": ES_ANOMALY_INDEX, "timeFieldName": "timestamp"}
    }

    response = requests.post(
        f"{KIBANA_HOST}/api/index_patterns/index_pattern",
        headers=headers,
        json=anomalies_pattern,
    )

    if response.status_code in (200, 201):
        print(f"Created anomalies index pattern: {response.json()}")
    else:
        print(f"Failed to create anomalies index pattern: {response.text}")


def create_visualizations():
    """Create basic visualizations for the dashboard"""
    # Note: In real implementation, this would create visualizations using the Kibana API
    # This is simplified for illustration purposes
    print("Creating visualizations...")

    # In a real implementation, we would create:
    # 1. Log Level Distribution (Pie Chart)
    # 2. Log Count Over Time (Line Chart)
    # 3. Top Anomaly Reasons (Bar Chart)
    # 4. Latest Anomalies (Data Table)

    print("Visualization setup would be completed here")
    print("For full implementation, use Kibana's saved objects API")


def main():
    """Main function to set up Kibana dashboards"""
    if wait_for_kibana():
        time.sleep(5)  # Give Kibana a moment to fully initialize
        create_index_patterns()
        create_visualizations()
        print("Kibana setup completed successfully!")
    else:
        print("Failed to connect to Kibana, setup aborted.")


if __name__ == "__main__":
    main()
