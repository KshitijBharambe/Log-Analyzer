FROM python:3.9-slim

WORKDIR /app

COPY grafana_setup.py .

RUN pip install requests

CMD ["python", "grafana_setup.py"]