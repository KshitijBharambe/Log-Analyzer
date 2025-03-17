FROM python:3.9-slim

WORKDIR /app

COPY analyzer.py .

# Install required packages
RUN pip install elasticsearch kafka-python

CMD ["python", "analyzer.py"]