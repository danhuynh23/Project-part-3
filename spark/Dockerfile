# Use the Bitnami Spark image as the base image
FROM bitnami/spark:3.4.0

# Add MySQL and MongoDB connectors\
ADD https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.26/mysql-connector-java-8.0.26.jar /opt/bitnami/spark/jars/
ADD https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.4.0/mongo-spark-connector_2.12-10.4.0.jar /opt/bitnami/spark/jars/
COPY pysparkscript.py /scripts/pysparkscript.py
