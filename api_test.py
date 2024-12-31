from amadeus import Client, ResponseError
import logging
import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv('pass.env')

# Initialize the Amadeus client with your API credentials
amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("flight_sync.log"),
        logging.StreamHandler()
    ]
)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost')
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'airticketingsystem'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

import time

def fetch_airline_name_from_api(airline_code, retry=3):
    for attempt in range(retry):
        try:
            response = amadeus.reference_data.airlines.get(airlineCodes=airline_code)
            if response.status_code == 200 and response.data:
                airline_data = response.data[0]
                return airline_data.get('commonName') or airline_data.get('businessName') or airline_data.get('name')
            break
        except ResponseError as e:
            if e.response.status_code == 429 and attempt < retry - 1:
                logging.warning(f"Rate limit reached. Retrying in {2 ** attempt} seconds.")
                time.sleep(2 ** attempt)
            else:
                logging.error(f"Error fetching airline name for {airline_code}: {e}")
                return None

#

def resolve_airline_name(airline_code): 
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if the airline code exists
            cursor.execute("SELECT airline_code FROM airline WHERE airline_code = %s", (airline_code,))
            result = cursor.fetchone()
            if result:
                return result['airline_name']
            else:
                unformatted_airline_name=fetch_airline_name_from_api(airline_code)
                airline_name=format_airline_name(unformatted_airline_name)
                cursor.execute("""
                    INSERT INTO airline (name, airline_code)
                    VALUES (%s, %s)
                """, (airline_name, airline_code))
                connection.commit()
                logging.info(f"Airline code {airline_code} for {airline_name} inserted successfully.")
                return airline_name
    except Exception as e:
        logging.error(f"Database error while processing airline {airline_code}: {e}")
        return None
    finally:
        connection.close()


# Fetch flights using Amadeus API
def fetch_flights(origin, destination, departure_date):
    logging.debug(f"Fetching flights: origin={origin}, destination={destination}, departure_date={departure_date}")
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1
        )
        logging.info(f"Fetched {len(response.data)} flights from Amadeus API.")
        return response.data
    except ResponseError as error:
        logging.error(f"Error fetching flights: {error}")
        return []

# Prepare and log the SQL statement
def prepare_sql_statement(flight):
    sql_statement = f"""
    INSERT INTO flight (flight_number,name_airline, name_depart, name_arrive, depart_time, arrive_time, price)
    VALUES (
        '{flight['flight_number']}', 
        '{flight['name_airline']}',
        '{flight['origin']}', 
        '{flight['destination']}', 
        '{flight['departure_time'].strftime('%Y-%m-%d %H:%M:%S')}', 
        '{flight['arrival_time'].strftime('%Y-%m-%d %H:%M:%S')}', 
        {flight['price']}
    );
    """
    logging.debug(f"Prepared SQL statement: {sql_statement.strip()}")

# Get or create airline code
def get_or_create_airline_code(airline_name, airline_code):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if the airline code exists
            cursor.execute("SELECT airline_code FROM airline WHERE airline_code = %s", (airline_code,))
            result = cursor.fetchone()
            if result:
                return result['airline_code']
            else:
                # Insert the airline if not found
                logging.info(f"Airline code {airline_code} for {airline_name} not found. Inserting into database.")
                cursor.execute("""
                    INSERT INTO airline (name, airline_code)
                    VALUES (%s, %s)
                """, (airline_name, airline_code))
                connection.commit()
                logging.info(f"Airline code {airline_code} for {airline_name} inserted successfully.")
                return airline_code
    except Exception as e:
        logging.error(f"Database error while processing airline {airline_name}: {e}")
        return None
    finally:
        connection.close()

# Insert flight into the database with SQL statement logging
# Insert flight into the database
def insert_flight_into_db(flight,insert=False):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql_statement = f"""
            INSERT INTO flight (flight_number, name_airline, name_depart, name_arrive, depart_time, arrive_time, price, status)
            VALUES (
                '{flight['flight_number']}', 
                '{flight['name_airline']}', 
                '{flight['origin']}', 
                '{flight['destination']}', 
                '{flight['departure_time'].strftime('%Y-%m-%d %H:%M:%S')}', 
                '{flight['arrival_time'].strftime('%Y-%m-%d %H:%M:%S')}', 
                {flight['price']}, 
                'Scheduled'
            )
            """
            logging.debug(f"Prepared SQL statement: {sql_statement.strip()}")
            if insert: 
                cursor.execute(sql_statement)
                connection.commit()
                logging.info(f"Flight {flight['flight_number']} inserted successfully into the database.")

            else: 
                logging.info("Not inserting cause mode is FALSE")
    except Exception as e:
        logging.error(f"Error inserting flight into database: {e}")
    finally:
        connection.close()

def format_airline_name(name):
    # Convert to title case (handles cases like "JETBLUE AIRWAYS" -> "Jetblue Airways")
    return name.title() if name else "Unknown Airline"

# Sync flights and log SQL statements
def sync_flights_to_db(origin, destination, departure_date):
    flights = fetch_flights(origin, destination, departure_date)

    # Step 1: Resolve all airline names
    airline_name_map = {}
    for flight_data in flights:
        airline_code = flight_data.get('validatingAirlineCodes', [None])[0]
        if airline_code not in airline_name_map:
            airline_name = resolve_airline_name(airline_code)
            airline_name_map[airline_code] = format_airline_name(airline_name)

    # Step 2: Process flights with resolved and formatted airline names
    for flight_data in flights:
        try:
            airline_code = flight_data.get('validatingAirlineCodes', [None])[0]
            airline_name = airline_name_map.get(airline_code, "Unknown Airline")
            
            # Prepare flight details
            flight = {
                'flight_number': f"{airline_code}{flight_data['id'][-3:]}",
                'name_airline': airline_name,  # Add formatted airline name here
                'origin': flight_data['itineraries'][0]['segments'][0]['departure']['iataCode'],
                'destination': flight_data['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                'departure_time': datetime.fromisoformat(flight_data['itineraries'][0]['segments'][0]['departure']['at']),
                'arrival_time': datetime.fromisoformat(flight_data['itineraries'][0]['segments'][0]['arrival']['at']),
                'price': float(flight_data['price']['total'])
            }

            # Insert into the database
            insert_flight_into_db(flight,insert=True)

        except Exception as e:
            logging.error(f"Error processing flight data: {e}")
            logging.debug(f"Flight data: {flight_data}")




# Main testing function
if __name__ == "__main__":
    # Test parameters
    origin = "JFK"  # Replace with your test origin airport code
    destination = "LAX"  # Replace with your test destination airport code
    departure_date = "2024-12-30"  # Replace with your test departure date

    logging.info("Starting flight sync test.")  
    sync_flights_to_db(origin, destination, departure_date)
    logging.info("Flight sync test completed.")
