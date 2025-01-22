from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
        .appName("UnifiedQueryEngine")
        # Optional: if you want a default connection string for all reads/writes:
        # .config("spark.mongodb.connection.uri", "mongodb://root:rootpassword@mongo-container:27017/?authSource=admin")
        .getOrCreate()
)

# Read from MongoDB
mongo_df = (
    spark.read
         .format("mongodb")
         .option("spark.mongodb.connection.uri", "mongodb://root:rootpassword@mongo-container:27017/?authSource=admin")
         .option("spark.mongodb.database", "flightdata")
         .option("spark.mongodb.collection", "raw_flight_data")
         .load()
)

# Read from MySQL (requires MySQL JDBC driver on classpath!)
mysql_df = (
    spark.read
         .format("jdbc")
         .option("url", "jdbc:mysql://mysql:3306/airticketingsystem")
         .option("driver", "com.mysql.cj.jdbc.Driver")  # Important
         .option("user", "root")
         .option("password", "my-secret-pw")
         .option("dbtable", "flight")
         .load()
)

# Combine data
combined_df = mongo_df.join(mysql_df, mongo_df["origin"] == mysql_df["name_depart"], "inner")
combined_df.show()
