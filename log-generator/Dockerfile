FROM openjdk:17-slim

WORKDIR /app

# Install Maven to handle dependencies
RUN apt-get update && \
    apt-get install -y maven && \
    apt-get clean

# Create a simple Maven project structure
RUN mkdir -p /app/src/main/java

# Copy the Java source file
COPY LogGenerator.java /app/src/main/java/

# Create a pom.xml file with Kafka dependencies
RUN echo '<?xml version="1.0" encoding="UTF-8"?>\
<project xmlns="http://maven.apache.org/POM/4.0.0"\
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">\
    <modelVersion>4.0.0</modelVersion>\
    <groupId>com.loganalyzer</groupId>\
    <artifactId>log-generator</artifactId>\
    <version>1.0-SNAPSHOT</version>\
    <properties>\
        <maven.compiler.source>17</maven.compiler.source>\
        <maven.compiler.target>17</maven.compiler.target>\
    </properties>\
    <dependencies>\
        <dependency>\
            <groupId>org.apache.kafka</groupId>\
            <artifactId>kafka-clients</artifactId>\
            <version>3.3.1</version>\
        </dependency>\
        <dependency>\
            <groupId>org.slf4j</groupId>\
            <artifactId>slf4j-api</artifactId>\
            <version>1.7.36</version>\
        </dependency>\
        <dependency>\
            <groupId>org.slf4j</groupId>\
            <artifactId>slf4j-simple</artifactId>\
            <version>1.7.36</version>\
        </dependency>\
    </dependencies>\
    <build>\
        <plugins>\
            <plugin>\
                <groupId>org.apache.maven.plugins</groupId>\
                <artifactId>maven-jar-plugin</artifactId>\
                <version>3.2.0</version>\
                <configuration>\
                    <archive>\
                        <manifest>\
                            <addClasspath>true</addClasspath>\
                            <classpathPrefix>lib/</classpathPrefix>\
                            <mainClass>LogGenerator</mainClass>\
                        </manifest>\
                    </archive>\
                </configuration>\
            </plugin>\
            <plugin>\
                <groupId>org.apache.maven.plugins</groupId>\
                <artifactId>maven-dependency-plugin</artifactId>\
                <version>3.2.0</version>\
                <executions>\
                    <execution>\
                        <id>copy-dependencies</id>\
                        <phase>package</phase>\
                        <goals>\
                            <goal>copy-dependencies</goal>\
                        </goals>\
                        <configuration>\
                            <outputDirectory>${project.build.directory}/lib</outputDirectory>\
                        </configuration>\
                    </execution>\
                </executions>\
            </plugin>\
        </plugins>\
    </build>\
</project>' > /app/pom.xml

# Build the project with Maven
RUN mvn package

# Set up the entry point
CMD ["java", "-cp", "target/log-generator-1.0-SNAPSHOT.jar:target/lib/*", "LogGenerator"]