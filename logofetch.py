import os
import logging
import requests
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv('pass.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Directory to save the logos
LOGO_DIR = "wikipedia_airline_logos"
os.makedirs(LOGO_DIR, exist_ok=True)

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

# Fetch and save logo from Wikipedia
def fetch_and_save_logo(airline_name, airline_code):
    try:
        # Construct the Wikipedia search URL
        search_url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": airline_name,
            "prop": "images",
            "imlimit": "max",
        }
        headers = {
            "User-Agent": "MyAirlineLogoFetcher/1.0 (your_email@example.com)"
        }

        # Fetch the Wikipedia page
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        image_file = None

        for page in pages.values():
            images = page.get("images", [])
            for image in images:
                if "logo" in image.get("title", "").lower():
                    image_file = image["title"]
                    break
            if image_file:
                break

        if not image_file:
            logging.warning(f"No logo found on Wikipedia page for {airline_name}.")
            return None

        # Construct the file URL
        file_url = f"https://en.wikipedia.org/wiki/Special:FilePath/{image_file.replace(' ', '_')}"
        logging.info(f"Found 'File:' page for {airline_name}: {file_url}")

        # Download the logo file
        logo_response = requests.get(file_url, headers=headers)
        logo_response.raise_for_status()

        # Save the logo locally
        logo_path = os.path.join(LOGO_DIR, f"{airline_code.lower()}.svg")
        with open(logo_path, "wb") as f:
            f.write(logo_response.content)

        logging.info(f"Logo for airline {airline_name} saved locally at {logo_path}.")
        return logo_path
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error fetching or saving logo for {airline_name}: {e}")
        return None

# Update the airline table with the logo path
def update_airline_logos():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch all airlines from the database
            cursor.execute("SELECT name, airline_code FROM airline WHERE logo_path IS NULL")
            airlines = cursor.fetchall()

            if not airlines:
                logging.info("No airlines without logos found.")
                return

            for airline in airlines:
                airline_name = airline['name']
                airline_code = airline['airline_code']

                # Fetch the logo and save locally
                logo_path = fetch_and_save_logo(airline_name, airline_code)
                if logo_path:
                    # Update the database with the logo path
                    cursor.execute(
                        "UPDATE airline SET logo_path = %s WHERE airline_code = %s",
                        (logo_path, airline_code)
                    )
                    connection.commit()
                    logging.info(f"Updated logo path for airline {airline_code}.")
                else:
                    logging.warning(f"Logo fetch failed for airline {airline_code}.")
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        connection.close()

# Main testing function
if __name__ == "__main__":
    logging.info("Starting airline logo update process.")
    update_airline_logos()
    logging.info("Airline logo update process completed.")
