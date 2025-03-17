
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Properties;
import java.util.Random;
import java.util.concurrent.TimeUnit;

// Kafka imports
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public class LogGenerator {

    private static final Random random = new Random();
    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");

    private static final String[] LOG_TYPES = {
        "API_REQUEST", "DATABASE_QUERY", "AUTHENTICATION", "SERVICE_HEALTH"
    };
    

    private static final String[] LOG_MESSAGES = {
        "User login successful",
        "Database query executed in 45ms",
        "API request processed",
        "File download completed",
        "Email notification sent"
    };

    private static final String[] ERROR_MESSAGES = {
        "Connection timeout after 30 seconds",
        "Database query failed: syntax error",
        "Invalid user credentials for user admin",
        "File not found: config.json",
        "Service unavailable: payment processor"
    };

    public static void main(String[] args) {
        System.out.println("Log Generator starting...");

        // Get configuration from environment variables
        String logFilePath = System.getenv("LOG_FILE_PATH");
        if (logFilePath == null || logFilePath.isEmpty()) {
            logFilePath = "/logs/application.log";
        }

        String kafkaEnabled = System.getenv("KAFKA_ENABLED");
        boolean useKafka = "true".equalsIgnoreCase(kafkaEnabled);

        String kafkaBroker = System.getenv("KAFKA_BROKER");
        if (kafkaBroker == null || kafkaBroker.isEmpty()) {
            kafkaBroker = "kafka:9092";
        }

        String kafkaTopic = System.getenv("KAFKA_TOPIC");
        if (kafkaTopic == null || kafkaTopic.isEmpty()) {
            kafkaTopic = "logs";
        }

        System.out.println("Writing logs to file: " + logFilePath);
        if (useKafka) {
            System.out.println("Kafka integration enabled");
            System.out.println("Kafka broker: " + kafkaBroker);
            System.out.println("Kafka topic: " + kafkaTopic);
        }

        // Initialize Kafka producer if enabled
        Producer<String, String> producer = null;
        if (useKafka) {
            producer = createKafkaProducer(kafkaBroker);
        }

        try (FileWriter writer = new FileWriter(logFilePath, true)) {
            while (true) {
                try {
                    // Generate a timestamp
                    String timestamp = dateFormat.format(new Date());

                    // Select a random log type
                    String logType = LOG_TYPES[random.nextInt(LOG_TYPES.length)];

                    // Generate a log entry
                    String logLevel;
                    String message;

                    int randomVal = random.nextInt(100);
                    if (randomVal < 80) {
                        // 80% INFO logs
                        logLevel = "INFO";
                        message = LOG_MESSAGES[random.nextInt(LOG_MESSAGES.length)];
                    } else if (randomVal < 95) {
                        // 15% WARNING logs
                        logLevel = "WARN";
                        message = LOG_MESSAGES[random.nextInt(LOG_MESSAGES.length)] + " (slow response)";
                    } else {
                        // 5% ERROR logs
                        logLevel = "ERROR";
                        message = ERROR_MESSAGES[random.nextInt(ERROR_MESSAGES.length)];
                    }

                    // Create a structured log entry in JSON-like format
                    String logEntry = String.format("{\"timestamp\":\"%s\",\"level\":\"%s\",\"type\":\"%s\",\"message\":\"%s\"}\n",
                            timestamp, logLevel, logType, message);

                    // Write to file
                    writer.write(logEntry);
                    writer.flush();

                    // Send to Kafka if enabled
                    if (useKafka && producer != null) {
                        ProducerRecord<String, String> record = new ProducerRecord<>(kafkaTopic, logEntry.trim());
                        producer.send(record, (metadata, exception) -> {
                            if (exception != null) {
                                System.err.println("Error sending to Kafka: " + exception.getMessage());
                            }
                        });
                    }

                    // Also print to stdout for debugging
                    System.out.print(logEntry);

                    // Occasionally generate a burst of error logs to simulate an anomaly (1% chance)
                    if (random.nextInt(100) < 1) {
                        System.out.println("Generating anomaly pattern...");
                        String errorId = "ERR-" + random.nextInt(10000);

                        for (int i = 0; i < 5; i++) {
                            String anomalyEntry = String.format(
                                    "{\"timestamp\":\"%s\",\"level\":\"ERROR\",\"type\":\"%s\",\"errorId\":\"%s\",\"message\":\"ANOMALY: System failure detected, attempt %d\"}\n",
                                    dateFormat.format(new Date()), logType, errorId, i + 1);
                            writer.write(anomalyEntry);
                            writer.flush();

                            // Send to Kafka if enabled
                            if (useKafka && producer != null) {
                                ProducerRecord<String, String> record = new ProducerRecord<>(kafkaTopic, anomalyEntry.trim());
                                producer.send(record);
                            }

                            System.out.print(anomalyEntry);
                            TimeUnit.MILLISECONDS.sleep(100);
                        }
                    }

                    // Sleep for a random time between 200ms and 1000ms
                    TimeUnit.MILLISECONDS.sleep(200 + random.nextInt(800));

                } catch (InterruptedException e) {
                    System.err.println("Log generation interrupted: " + e.getMessage());
                    break;
                }
            }
        } catch (IOException e) {
            System.err.println("Error writing to log file: " + e.getMessage());
        } finally {
            // Close Kafka producer if it was created
            if (producer != null) {
                producer.close();
            }
        }
    }

    private static Producer<String, String> createKafkaProducer(String bootstrapServers) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.CLIENT_ID_CONFIG, "log-generator");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // Add retry and resilience configurations
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.ACKS_CONFIG, "1");

        // Create the producer
        return new KafkaProducer<>(props);
    }
}
