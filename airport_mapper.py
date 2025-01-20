import os
import csv
import logging
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv('pass.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Database connection
# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'airticketingsystem'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# Update airport data
def update_airports_from_file(file_path):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Read airports.dat file
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                name = row[4]  # IATA code as name
                city = row[2]
                country = row[3]
                icao_code = row[5]
                latitude = row[6]
                longitude = row[7]
                altitude = row[8]
                timezone = row[9]
                dst = row[10]
                tz_database_time_zone = row[11]

                if name and len(name) == 3 and name != '\\N':
                    # Update the airport data
                    sql = """
                    UPDATE airport
                    SET
                        city = %s,
                        country = %s,
                        icao_code = %s,
                        latitude = %s,
                        longitude = %s,
                        altitude = %s,
                        timezone = %s,
                        dst = %s,
                        tz_database_time_zone = %s
                    WHERE name = %s
                    """
                    cursor.execute(
                        sql, (city, country, icao_code, latitude, longitude, altitude, timezone, dst, tz_database_time_zone, name)
                    )

        # Commit changes
        connection.commit()
        logging.info("Airport data updated successfully.")

    except Exception as e:
        logging.error(f"Error updating airport data: {e}")
    finally:
        if connection.open:
            cursor.close()
            connection.close()

# Insert airport data from airports.dat
def insert_airports_from_file(file_path):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Read airports.dat file
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                name = row[4]  # IATA code as name
                city = row[2]
                country = row[3]
                icao_code = row[5]
                latitude = row[6]
                longitude = row[7]
                altitude = row[8]
                timezone = row[9]
                dst = row[10]
                tz_database_time_zone = row[11]

                if name and len(name) == 3 and name != '\\N':
                    # Insert the airport data
                    sql = """
                    INSERT IGNORE INTO airport (name, city, country, icao_code, latitude, longitude, altitude, timezone, dst, tz_database_time_zone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        sql, (name, city, country, icao_code, latitude, longitude, altitude, timezone, dst, tz_database_time_zone)
                    )

        # Commit changes
        connection.commit()
        logging.info("Airport data inserted successfully.")

    except Exception as e:
        logging.error(f"Error inserting airport data: {e}")
    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

# Main function
if __name__ == "__main__":
    file_path = "airports.dat"  # Path to airports.dat file
    if os.path.exists(file_path):
        logging.info("Starting airport data update process.")
        update_airports_from_file(file_path)
        insert_airports_from_file(file_path)
        logging.info("Airport data update process completed.")
    else:
        logging.error(f"File {file_path} not found.")
