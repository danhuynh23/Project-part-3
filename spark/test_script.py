from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("MongoDBIntegration") \
    .master("spark://spark-master:7077") \
    .config("spark.mongodb.read.connection.uri", "mongodb://root:rootpassword@mongo-container:27017") \
    .getOrCreate()

# Load data from MongoDB (update with your collection details)
mongo_df = spark.read.format("mongodb") \
    .option("uri", "mongodb://root:rootpassword@mongo-container:27017/flightdata.raw_flight_data") \
    .load()

mongo_df.show()

