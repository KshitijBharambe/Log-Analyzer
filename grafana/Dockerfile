FROM grafana/grafana:latest

USER root
# Install the Elasticsearch plugin with the correct command and plugin ID
RUN grafana cli plugins install elasticsearch-datasource

USER grafana