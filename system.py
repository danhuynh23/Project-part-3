from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail,Message
import pymysql
import hashlib
import secrets
import requests
import pandas as pd
import math
from datetime import datetime,timedelta
import os 

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong, secret value in production

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True  # Use HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'squirrelboat@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'jiqh vnoy rrfi xdux'    # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'squirrelboat@gmail.com'
mail = Mail(app)

airport_data = pd.read_csv('airports.dat', header=None, names=[
    "Airport ID", "Name", "City", "Country", "IATA/FAA", "ICAO",
    "Latitude", "Longitude", "Altitude", "Timezone", "DST",
    "Tz Database Timezone", "Type", "Source"
])

# Function to calculate the Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Function to find the nearest airport (ignoring heliports and airbases, returning airport codes)
def find_nearest_airport(lat, lon):
    # Exclude heliports and airbases by filtering based on 'Name'
    filtered_data = airport_data[
        ~airport_data['Name'].str.contains("Heliport|Air Base", case=False, na=False)
    ].copy()
    
    # Calculate distances to all remaining airports
    filtered_data['Distance'] = filtered_data.apply(
        lambda row: haversine(lat, lon, row['Latitude'], row['Longitude']), axis=1
    )
    
    # Find the nearest airport
    nearest_row = filtered_data.loc[filtered_data['Distance'].idxmin()]
    return nearest_row['IATA/FAA'], nearest_row['Distance']

# Function to get default origin based on user's location
def get_default_origin():
    """
    Determine the default origin based on the user's location.
    """
    try:
        # Use an external service to get the user's approximate location
        response = requests.get("http://ip-api.com/json")
        response.raise_for_status()
        data = response.json()

        if data["status"] == "success":
            latitude = data["lat"]
            longitude = data["lon"]
            print(f"Lat: {latitude} \nLong: {longitude}")
            # Find the nearest airport using the user's location
            airport_code, distance = find_nearest_airport(latitude, longitude)
            print(f"The nearest airport is {airport_code} at {distance:.2f} km.")
            return airport_code
        
        # Default to JFK if location cannot be determined
        print("Could not determine location. Defaulting to JFK.")
        return "JFK"

    except Exception as e:
        print(f"Error fetching location: {e}")
        return "JFK"  # Fallback to default JFK

# Database connection
def get_db_connection_local():
    return pymysql.connect(
        host='34.173.201.121',  # Replace with your Cloud SQL instance's public IP
        user='root',            # Replace with your Cloud SQL username
        password='Daniscool123!',  # Replace with your Cloud SQL password
        database='airticketingsystem',  # Replace with your database name
        cursorclass=pymysql.cursors.DictCursor
    )

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),  # Default to 'localhost' if MYSQL_HOST is not set
        user=os.getenv('MYSQL_USER', 'root'),       # Default to 'root'
        password=os.getenv('MYSQL_PASSWORD', ''),  # Default to empty password
        database=os.getenv('MYSQL_DB', 'airticketingsystem'),  # Default to 'airticketingsystem'
        port=int(os.getenv('MYSQL_PORT', 3306)),   # Default to 3306
        cursorclass=pymysql.cursors.DictCursor     # Optional: Use dictionary-style rows
    )
def check_permission(required_permission):
    if 'user' not in session or session['user_type'] != 'airline_staff':
        flash('Access denied', 'error')
        return False

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if the user has the required permission
            cursor.execute("""
                SELECT permission 
                FROM permissions 
                WHERE username = %s AND permission = %s
            """, (session['user'], required_permission))
            result = cursor.fetchone()
            
            if not result:
                flash('Insufficient permissions', 'error')
                return False

        return True

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
        return False

    finally:
        connection.close()


@app.route('/manage_flights', methods=['GET', 'POST'])
def manage_flights():
    if not check_permission('manage_flights'):
        return redirect(url_for('dashboard'))
    
    # Flight management logic here
    return render_template('manage_flights.html')

@app.route('/')
def home():
    logged_in = 'user' in session 
    user_type = session.get('user_type')  # Optional: pass user type if you need it in the header
    user=session.get('user')
    name=session.get('name')
    if user_type=="booking_agent":
        return render_template('index.html', logged_in=logged_in, user_type=user_type, user=user,name=user)
    else: 
        return render_template('index.html', logged_in=logged_in, user_type=user_type, user=user,name=name)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next')  # Capture the next URL

    if request.method == 'POST':
        user_type = request.form['user_type']
        login_field = request.form['login_field']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Determine table based on user type
        table_name = {
            'customer': 'customer',
            'booking_agent': 'booking_agent',
            'airline_staff': 'airline_staff'
        }.get(user_type)

        if not table_name:
            flash('Invalid user type', 'error')
            return redirect(url_for('login', next=next_url))

        # Execute the query based on user type (database logic omitted for brevity)
        connection = get_db_connection()
        with connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM {table_name} WHERE password=%s AND "
            query += "username=%s" if user_type == 'airline_staff' else "email=%s"
            cursor.execute(query, (hashed_password, login_field))
            user = cursor.fetchone()

        if user:
            session.clear()
            print(user['name'])
            if user_type=="booking_agent":
                session['name']=user['booking_agent_id']
            else:
                session['name']=user['name']
            session['user'] = login_field
            session['user_type'] = user_type
            session['session_id'] = secrets.token_hex(16)
            session.permanent = True
            flash('Login successful', 'success')

            # Redirect to the user-specific dashboard or the next URL if provided
            dashboard_route = {
                'customer': 'customer_dashboard',
                'booking_agent': 'booking_agent_dashboard',
                'airline_staff': 'airline_dashboard'
            }.get(user_type, 'home')  # Default to 'home' if no match
            default_origin = get_default_origin()
            print(default_origin)
            session['default_origin'] = default_origin
            return redirect(next_url or url_for(dashboard_route))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login', next=next_url))

    return render_template('login.html', next=next_url)

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    # Check if user is logged in
    if 'user' not in session:
        flash("Please log in to update your profile.")
        return redirect(url_for('login'))

    connection = get_db_connection()
    user_email = session['user']

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Validate inputs (you can add more validation here)
        if not name or not email or not phone:
            flash("All fields are required.", "error")
            return redirect(url_for('update_profile'))

        # Update the user's profile in the database
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE customer 
                    SET name = %s, email = %s, phone_number = %s 
                    WHERE email = %s
                """, (name, email, phone, user_email))
                connection.commit()

            # Update session data and flash success message
            session['user'] = email
            flash("Profile updated successfully.", "success")
            return redirect(url_for('customer_dashboard'))  # Redirect to dashboard or another page
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            connection.close()

    # Render the update profile form with current user details
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE email = %s", (user_email,))
            user = cursor.fetchone()
    finally:
        connection.close()

    return render_template('update_profile.html', user=user)


@app.route('/airline_dashboard')
def airline_dashboard():
    user_name = session.get('user', 'Guest')
    return render_template('airline_staff_dashboard.html', user=user_name)

@app.route('/customer_dashboard')
def customer_dashboard():
    user_name = session.get('user', 'Guest')
    return render_template('customer_dashboard.html', user=session['name'])

@app.route('/booking_agent_dashboard')
def booking_agent_dashboard():
    user_name = session.get('user', 'Guest')
    return render_template('booking_agent_dashboard.html', user=user_name)

@app.template_filter('strftime')
def format_datetime(value, format="%a, %d %b %Y"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value


from flask import render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3


from random import randint

@app.route('/show_flights', methods=['GET'])
def show_flights():
    # Get parameters
    customer_details={}
    logged_in = 'user' in session
    user = session['user'] if logged_in else None
    if logged_in:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE email = %s", (user,))
            customer_details = cursor.fetchone()
    print(customer_details)

    origin = request.args.get('from', session.get('default_origin'))
    print( session.get('default_origin'))

    destination = request.args.get('to')
    depart_date = request.args.get('depart', datetime.today().strftime('%Y-%m-%d'))
    passengers = request.args.get('passengers', 1, type=int)

    # Validate and parse `depart_date`
    try:
        depart_date_obj = datetime.strptime(depart_date, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format. Defaulting to today.", "warning")
        depart_date_obj = datetime.today()

    # Generate ±3 days of date options
    date_options = [depart_date_obj + timedelta(days=i) for i in range(-3, 4)]

    # Check if `origin` is provided
    if not origin:
        flash(f"Departure location is required, defaulting to { session.get('default_origin')} .", "error")
        return redirect(url_for('home'))

    # Connect to the database
    connection = get_db_connection()
    with connection:
        cursor = connection.cursor()

        # Fetch flights and date prices
        flights = []
        date_prices = {}
        for date in date_options:
            date_str = date.strftime('%Y-%m-%d')
            if destination:
                query = """
                SELECT f.*, dep_airport.city AS origin_city, arr_airport.city AS destination_city
                FROM flight f
                JOIN airport dep_airport ON f.name_depart = dep_airport.name
                JOIN airport arr_airport ON f.name_arrive = arr_airport.name
                WHERE f.name_depart = %s AND f.name_arrive = %s AND DATE(f.depart_time) = %s
                """
                cursor.execute(query, [origin, destination, date_str])
            else:
                query = """
                SELECT f.*, dep_airport.city AS origin_city, arr_airport.city AS destination_city
                FROM flight f
                JOIN airport dep_airport ON f.name_depart = dep_airport.name
                JOIN airport arr_airport ON f.name_arrive = arr_airport.name
                WHERE f.name_depart = %s AND DATE(f.depart_time) = %s
                """
                cursor.execute(query, [origin, date_str])

            flights_on_date = cursor.fetchall()
            if flights_on_date:
                # Generate random business prices
                for flight in flights_on_date:
                    economy_price = flight['price']
                    business_price = economy_price + 200  # Add a random increment
                    flight['economy_price'] = economy_price
                    flight['business_price'] = business_price

                min_price = min(flight['price'] for flight in flights_on_date)
                date_prices[date] = min_price
                if date == depart_date_obj:
                    flights = flights_on_date
            else:
                date_prices[date] = None

    # Extract destinations for display
    destinations = set(flight['destination_city'] for flight in flights) if flights else []
    origin_city = flights[0]['origin_city'] if flights else "Unknown"
    destination_city = flights[0]['destination_city'] if flights else "Everywhere"

    return render_template(
        'show_flights.html',
        flights=flights,
        destinations=destinations,
        origin=origin,
        destination=destination,
        date_options=date_options,
        date_prices=date_prices,
        origin_city=origin_city,
        destination_city=destination_city,
        depart_date=depart_date_obj.strftime("%Y-%m-%d"),
        passengers=passengers, 
        logged_in=logged_in,
        user=user,
        customer_details=customer_details

    )






@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_type = request.form['user_type']  # Get the user type from the form
        
        # Hash the password
        if user_type == 'customer':
            email = request.form['customer-email']
            password = request.form['customer-password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

        elif user_type == 'booking_agent':
            email = request.form['agent-email']
            password = request.form['agent-password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

        elif user_type == 'airline_staff':
            airline = request.form['airline']
            username = request.form['username']
            password = request.form['staff-password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            date_of_birth = request.form['staff_date_of_birth']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Connect to the database
        connection = get_db_connection()
        with connection:
            cursor = connection.cursor()

            # Email uniqueness check for customers and booking agents only
            if user_type in ['customer', 'booking_agent']:
                cursor.execute(
                    """
                    SELECT email 
                    FROM customer 
                    WHERE email = %s 
                    UNION 
                    SELECT email 
                    FROM booking_agent 
                    WHERE email = %s
                    """, (email, email)
                )
                if cursor.fetchone():
                    flash('Email already exists', 'error')
                    return render_template('signup.html')

            # Insert data based on the user type
            if user_type == 'customer':
                customer_data = {
                    'email': email,
                    'password': hashed_password,
                    'name': request.form['name'],
                    'building_number': request.form.get('building_number', None),
                    'street': request.form['street'],
                    'city': request.form['city'],
                    'state': request.form['state'],
                    'phone_number': request.form['area_code'] + request.form['phone_number'],
                    'passport_number': request.form['passport_number'],
                    'passport_expiration': request.form['passport_expiration'],
                    'passport_country': request.form['passport_country'],
                    'date_of_birth': request.form['customer_date_of_birth']
                }
                cursor.execute("""
                    INSERT INTO customer (email, password, name, building_number, street, city, state, phone_number, 
                                          passport_number, passport_expiration, passport_country, date_of_birth) 
                    VALUES (%(email)s, %(password)s, %(name)s, %(building_number)s, %(street)s, %(city)s, %(state)s, 
                            %(phone_number)s, %(passport_number)s, %(passport_expiration)s, %(passport_country)s, %(date_of_birth)s)
                """, customer_data) 

                           # Handle signup for booking agents
                            # Handle signup for booking agents
            elif user_type == 'booking_agent':
                    email = request.form['agent-email']
                    booking_agent_id=request.form['agency_name']

              

                    # Check for email uniqueness
                    cursor.execute("""
                        SELECT email FROM customer WHERE email = %s
                        UNION
                        SELECT email FROM booking_agent WHERE email = %s
                    """, (email, email))
                    if cursor.fetchone():
                        flash('Email already exists', 'error')
                        return render_template('signup.html')

                    # Insert booking agent data
                    cursor.execute("""
                        INSERT INTO booking_agent (email, password, booking_agent_id)
                        VALUES (%s, %s, %s)
                    """, (email, hashed_password, booking_agent_id))

            elif user_type == 'airline_staff':
                cursor.execute("""
                    INSERT INTO airline_staff (name, username, password, first_name, last_name, date_of_birth) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (airline, username, hashed_password, first_name, last_name, date_of_birth))

            # Commit the transaction
            connection.commit()
            flash('Signup successful', 'success')
            return redirect(url_for('login'))
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM airline")  # Assuming the table is 'airline' and the column for airline names is 'name'
    airlines = cursor.fetchall()

    return render_template('signup.html', airlines=airlines)

user_types = ['customer', 'booking_agent', 'airline_staff']


@app.route('/booking', methods=['GET', 'POST'])
def booking_page():
    # Check if user is logged in
    if 'user' not in session:
        flash("Please log in to access the booking page.")
        return redirect(url_for('login', next=request.url))

    # Get flight details from query parameters
    flight_id = request.args.get('flight_id')
    fare_type = request.args.get('fare_type')

    # Fetch the flight details from the database using flight_id
    connection = get_db_connection()
    flight_details = None
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.flight_number, f.name_airline, f.depart_time, f.arrive_time, f.name_depart, 
                   f.name_arrive, f.price, f.seats
            FROM flight f
            WHERE f.id = %s
        """, (flight_id,))
        flight_details = cursor.fetchone()

    if not flight_details:
        flash("Flight not found.", "error")
        return redirect(url_for('show_flights'))

    # Fetch the total tickets booked for this flight
    with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS tickets_booked
                FROM ticket
                WHERE flight_id = %s
            """, (flight_id,))
            tickets_booked = cursor.fetchone()['tickets_booked']
    print(tickets_booked)
    if flight_details['seats']: 
        if tickets_booked >= flight_details['seats']:
                    flash("This flight is fully booked. Please choose another flight.", "error")
                    return redirect(url_for('show_flights'))
    else: 
        flash("This flight is fully booked. Please choose another flight.", "error")
        return redirect(url_for('show_flights'))
    
    print(flight_details)
    # Fetch user details
    user_details = None
    booking_agent_id = None

    if 'user' in session:
        with connection.cursor() as cursor:
            # Check if the user is a customer
            cursor.execute("SELECT * FROM customer WHERE email = %s", (session['user'],))
            user_details = cursor.fetchone()

            # Check if the logged-in user is a booking agent
            cursor.execute("SELECT booking_agent_id, name FROM booking_agent WHERE email = %s", (session['user'],))
            booking_agent = cursor.fetchone()

            if booking_agent:
                booking_agent_id = booking_agent['booking_agent_id']
                # Check if the booking agent has an assigned airline
                if not booking_agent['name']:
                    flash("Booking agent does not have an assigned airline. Please contact your administrator.", "error")
                    return redirect(url_for('home'))

    # Render the booking page
    return render_template(
        'booking_page.html',
        flight=flight_details,
        flight_id=flight_id,
        fare_type=fare_type,
        user_details=user_details,
        booking_agent_id=booking_agent_id  # Pass booking_agent_id to the template
    )






@app.route('/confirmed')
def comfirmed():
        return render_template('confirmation.html')

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    # Check if the user is logged in
    if 'user' not in session:
        flash("Please log in to confirm your booking.", "error")
        return redirect(url_for('login', next=request.url))

    # Retrieve data from the booking form
    flight_id = request.form.get('flight_id')
    fare_type = request.form.get('fare_type')
    passenger_name = request.form.get('name')
    passenger_email = request.form.get('email')
    passenger_phone = request.form.get('phone')
    passenger_count = int(request.form.get('passenger_count', 1))

    # Establish a database connection
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch flight details to ensure it exists
            cursor.execute("""
                SELECT name_airline, flight_number, depart_time, name_depart, 
                       name_arrive, price, seats
                FROM flight 
                WHERE id = %s
            """, (flight_id,))
            flight_data = cursor.fetchone()

            # Check if the flight exists
            if not flight_data:
                flash("Flight not found in the database. Please check your flight details.", "error")
                return redirect(url_for('show_flights'))

            # Retrieve the flight details
            name_airline = flight_data['name_airline']
            flight_number = flight_data['flight_number']
            depart_time = flight_data['depart_time']
            name_depart = flight_data['name_depart']
            name_arrive = flight_data['name_arrive']
            total_price = flight_data['price'] * passenger_count  # Total price for all passengers

            # Determine if the logged-in user is a booking agent
            booking_agent_id = None
            cursor.execute("SELECT booking_agent_id FROM booking_agent WHERE email = %s", (session['user'],))
            agent_data = cursor.fetchone()
            if agent_data:
                booking_agent_id = agent_data['booking_agent_id']

            # Debugging: Print booking agent ID
            print(f"Booking Agent ID: {booking_agent_id}")
            #Check if flight is over booked 
            cursor.execute("""
                SELECT COUNT(*) AS tickets_booked
                FROM ticket
                WHERE flight_id = %s
            """, (flight_id,))
            tickets_booked = cursor.fetchone()['tickets_booked']

            available_seats = flight_data['seats'] - tickets_booked
            if passenger_count > available_seats:
                flash(f"Only {available_seats} seat(s) are available. Please adjust your booking.", "error")
                return redirect(url_for('booking_page', flight_id=flight_id, fare_type=fare_type))

            # Insert into the ticket table (auto-increment ticket_id)
            cursor.execute("""
                INSERT INTO ticket (name_airline, flight_number, depart_time, flight_id)
                VALUES (%s, %s, %s, %s)
            """, (name_airline, flight_number, depart_time, flight_id))

            # Retrieve the auto-generated ticket_id
            ticket_id = cursor.lastrowid

            # Insert into the purchases table
            purchase_query = """
                INSERT INTO purchases (ticket_id, customer_email, purchase_date, booking_agent_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(purchase_query, (ticket_id, passenger_email, datetime.now(), booking_agent_id))

        # Commit the transaction after successful inserts
        connection.commit()

        # Send confirmation email
        send_confirmation_email(
            mail,  # Pass the Flask-Mail instance
            passenger_name,
            passenger_email,
            flight_data,
            fare_type,
            passenger_count,
            total_price
        )

        # Redirect to the confirmation page
        return render_template(
            'confirmation.html',
            ticket_id=ticket_id,
            flight_number=flight_number,
            name_airline=name_airline,
            name_depart=name_depart,
            name_arrive=name_arrive,
            depart_time=depart_time,
            fare_type=fare_type.capitalize(),
            passenger_name=passenger_name,
            passenger_email=passenger_email,
            passenger_phone=passenger_phone,
            passenger_count=passenger_count,
            total_price=total_price
        )

    except pymysql.MySQLError as e:
        # Roll back transaction in case of error
        connection.rollback()
        flash(f"Database error: {e}", "error")
        return redirect(url_for('booking_page', flight_id=flight_id, fare_type=fare_type))

    finally:
        # Ensure the database connection is closed
        connection.close()


def send_confirmation_email(mail, passenger_name, passenger_email, flight_data, fare_type, passenger_count, total_price):
    """
    Sends a booking confirmation email to the passenger.
    
    Parameters:
        mail (Mail): Flask-Mail instance.
        passenger_name (str): Name of the passenger.
        passenger_email (str): Email address of the passenger.
        flight_data (dict): Flight details including airline, flight number, etc.
        fare_type (str): Fare type selected by the passenger.
        passenger_count (int): Number of passengers booked.
        total_price (float): Total price of the booking.
    """
    try:
        msg = Message(
            subject="Booking Confirmation",
            recipients=[passenger_email],
            body=f"""Dear {passenger_name},

Your booking has been successfully confirmed!

Flight Details:
- Airline: {flight_data['name_airline']}
- Flight Number: {flight_data['flight_number']}
- Departure: {flight_data['name_depart']} on {flight_data['depart_time']}
- Arrival: {flight_data['name_arrive']}
- Fare Type: {fare_type.capitalize()}
- Passengers: {passenger_count}
- Total Price: ${total_price}

Thank you for booking with us!

Best regards,
Your Airline Team
"""
        )
        mail.send(msg)
        print(f"Confirmation email sent to {passenger_email}")
    except Exception as e:
        print(f"Failed to send email to {passenger_email}: {e}")

import geopy.distance

@app.route('/get_location', methods=['POST'])
def get_location():
    # Extract latitude and longitude from the frontend
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not latitude or not longitude:
        return jsonify({"success": False, "error": "Missing GPS coordinates"}), 400

    # Find the nearest airport code using the provided location
    airport_code, distance = find_nearest_airport(latitude, longitude)

    if not airport_code:
        return jsonify({"success": False, "error": "No nearby airport found"}), 404

    # Save the nearest airport code to the session or as a backend variable
    session['default_origin'] = airport_code
    return jsonify({
        "success": True,
        "nearest_airport": {
            "code": airport_code,
            "distance": distance
        }
    })





@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in first', 'info')
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/flights')
def flights():
    connection = get_db_connection()
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM flight")
        flights = cursor.fetchall()
    return render_template('flights.html', flights=flights)


@app.route('/view_flights', methods=['GET', 'POST'])
def view_flights():
    # Get the logged-in user's email and role from the session
    user_email = session.get('user')
    user_role = session.get('user_type')

    if not user_email or not user_role:
        flash("You must be logged in to view flights.", "warning")
        return redirect(url_for('login'))

    # Connect to the database
    connection = get_db_connection()

    try:
        if user_role == 'customer':
            # Query for customer: Fetch their booked flights
            query = """
                SELECT t.ticket_id, f.name_airline, f.flight_number, f.name_depart, f.name_arrive, 
                       f.depart_time, f.arrive_time, f.price, f.status, TIMEDIFF(f.arrive_time, f.depart_time) AS duration
                FROM ticket AS t
                JOIN flight AS f ON t.flight_number = f.flight_number
                JOIN purchases AS p ON t.ticket_id = p.ticket_id
                WHERE p.customer_email = %s
                AND t.depart_time=f.depart_time

            """
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, (user_email,))
                flights = cursor.fetchall()

            if not flights:
                flash("No flights found for this customer.", "info")
            return render_template('customer_flights.html', flights=flights)

        elif user_role == 'airline_staff':
            # Check if a flight status update has been submitted
            if request.method == 'POST' and 'update_status' in request.form:
                flight_number = request.form.get('flight_number')
                new_status = request.form.get('new_status')

                # Validate permissions for updating status
                if not check_permission('Operator'):
                    flash("You do not have permission to update flight statuses.", "error")
                else:
                    # Update flight status in the database
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE flight 
                            SET status = %s
                            WHERE flight_number = %s
                            AND name_airline = (SELECT name FROM airline_staff WHERE username = %s)
                        """, (new_status, flight_number, user_email))
                        connection.commit()
                        flash(f"Flight status updated successfully to {new_status}.", "success")

            # Default date range (next 30 days)
            today = datetime.now().date()
            default_start_date = today
            default_end_date = today + timedelta(days=30)

            # Get filter values from form (or use defaults)
            start_date = request.form.get('start_date', default_start_date)
            end_date = request.form.get('end_date', default_end_date)
            source = request.form.get('source', None)
            destination = request.form.get('destination', None)
            
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Base query
            query = """
                SELECT f.flight_number, f.name_airline, f.name_depart, f.name_arrive, 
                    f.depart_time, f.arrive_time, f.price, f.status, 
                    TIMEDIFF(f.arrive_time, f.depart_time) AS duration
                FROM flight f
                JOIN airport dep ON f.name_depart = dep.name
                JOIN airport arr ON f.name_arrive = arr.name
                WHERE f.name_airline = (SELECT name FROM airline_staff WHERE username = %s)
                AND f.depart_time BETWEEN %s AND %s
            """
            params = [user_email, start_date, end_date]

            # Add filters for source and destination only if they are provided
            if source and source.lower() != 'none':
                query += " AND (dep.city LIKE %s OR dep.name LIKE %s)"
                params.extend([f"%{source}%", f"%{source}%"])
            if destination and destination.lower() != 'none':
                query += " AND (arr.city LIKE %s OR arr.name LIKE %s)"
                params.extend([f"%{destination}%", f"%{destination}%"])

            # Execute the query
            print("Executing query:", query)
            print("With parameters:", params)
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                flights = cursor.fetchall()

            # Render the template with results and include update status feature
            return render_template(
                'staff_flights.html',
                flights=flights,
                start_date=start_date,
                end_date=end_date,
                source=source,
                destination=destination
            )

        elif user_role == 'booking_agent':
            # Get filter values from the form (if any)
            start_date = request.form.get('start_date', None)
            end_date = request.form.get('end_date', None)
            source = request.form.get('source', None)
            destination = request.form.get('destination', None)

            # Base query
            query = """
                SELECT t.ticket_id, f.name_airline, f.flight_number, f.name_depart, f.name_arrive, 
                    f.depart_time, f.arrive_time, f.price, f.status, 
                    p.customer_email, TIMEDIFF(f.arrive_time, f.depart_time) AS duration
                FROM ticket AS t
                JOIN flight AS f ON t.flight_number = f.flight_number
                JOIN purchases AS p ON t.ticket_id = p.ticket_id
                JOIN airport AS dep ON f.name_depart = dep.name
                JOIN airport AS arr ON f.name_arrive = arr.name
                WHERE p.booking_agent_id = (SELECT booking_agent_id FROM booking_agent WHERE email = %s)
                AND t.depart_time=f.depart_time
            """
            params = [user_email]

            # Add filters to the query
            if start_date:
                query += " AND f.depart_time >= %s"
                params.append(start_date)
            if end_date:
                query += " AND f.depart_time <= %s"
                params.append(end_date)
            # Add filters for source and destination only if they are provided
            if source and source.lower() != 'none':
                query += " AND (dep.city LIKE %s OR dep.name LIKE %s)"
                params.extend([f"%{source}%", f"%{source}%"])
            if destination and destination.lower() != 'none':
                query += " AND (arr.city LIKE %s OR arr.name LIKE %s)"
                params.extend([f"%{destination}%", f"%{destination}%"])

            # Execute the query
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                flights = cursor.fetchall()

            if not flights:
                flash("No flights found for the specified criteria.", "info")
            return render_template('agent_flights.html', flights=flights, filters={
                'start_date': start_date,
                'end_date': end_date,
                'source': source,
                'destination': destination
            })

        else:
            flash("Invalid user role.", "danger")
            return redirect(url_for('home'))

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('home'))

    finally:
        connection.close()



@app.route('/track_spending')
def track_spending():
    # Get the logged-in user's email from the session
    user_email = session.get('user')
    print(user_email)    
    if not user_email:
        flash("You must be logged in to view your bookings.", "warning")
        return redirect(url_for('login'))
    
    # Connect to the database
    connection = get_db_connection()
        # Query to calculate the total spending per date
    query = """
        SELECT DATE(p.purchase_date) AS purchase_date, SUM(f.price) AS total_spending
        FROM purchases AS p
        JOIN ticket AS t ON p.ticket_id = t.ticket_id
        JOIN flight AS f ON t.flight_number = f.flight_number
        WHERE p.customer_email = %s
        GROUP BY DATE(p.purchase_date)
        ORDER BY purchase_date
    """
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, (user_email,))
        spending_data = cursor.fetchall()
    
    connection.close()
    
    # Format data for the chart
    dates = [row['purchase_date'].strftime('%Y-%m-%d') for row in spending_data]
    spending = [row['total_spending'] for row in spending_data]
    
    return render_template('track_spending.html', dates=dates, spending=spending)


#<--------------------------------------------------Staff section>
@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    # Ensure the user is logged in and has the necessary permissions
    if not check_permission('Admin'):
        flash('Access denied: You do not have permission to create flights.', 'error')
        return redirect(url_for('airline_dashboard'))
    
    if request.method == 'POST':
        airline = request.form.get('airline')
        flight_number = request.form.get('flight_number')
        name_depart = request.form.get('name_depart')
        name_arrive = request.form.get('name_arrive')
        depart_time = request.form.get('depart_time')
        arrive_time = request.form.get('arrive_time')
        price = request.form.get('price')
        status = request.form.get('status', 'Scheduled')
        seats = request.form.get('seats',0)
        
        if not all([airline, flight_number, name_depart, name_arrive, depart_time, arrive_time, price]):
            flash("All fields are required.", "error")
            return render_template('create_flight.html')
        
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                query = """
                INSERT INTO flight (name_airline, flight_number, name_depart, name_arrive, 
                                    depart_time, arrive_time, price, status, seats)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (airline, flight_number, name_depart, name_arrive, 
                                       depart_time, arrive_time, price, status,seats))
                connection.commit()
            
            flash("Flight created successfully.", "success")
            return redirect(url_for('create_flight', success=True))
        
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}", "error")
        finally:
            connection.close()
    
    return render_template('create_flight.html')


@app.route('/update_flight_status', methods=['GET', 'POST'])
def update_flight_status():
    # Ensure the user is logged in and has the necessary permissions
    if not check_permission("Operator"):
        flash("You do not have the required permissions to update flight statuses.", "error")
        return redirect(url_for('view_flights'))

    connection = get_db_connection()

    try:
        if request.method == 'POST':
            # Get form data
            flight_number = request.form.get('flight_number')
            new_status = request.form.get('new_status')

            # Update flight status in the database
            query = "UPDATE flight SET status = %s WHERE flight_number = %s"
            with connection.cursor() as cursor:
                cursor.execute(query, (new_status, flight_number))
                connection.commit()

            flash(f"Flight status updated successfully to {new_status}.", "success")
            return redirect(url_for('view_flights'))

        # For GET requests, render the form
        else:
            # Fetch all flights for the dropdown
            query = """
                SELECT flight_number, name_depart, name_arrive, status, depart_time, arrive_time 
                FROM flight
                WHERE name_airline = (SELECT name FROM airline_staff WHERE username = %s)
            """
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, (session.get('user'),))
                flights = cursor.fetchall()

            return render_template('update_flight_status.html', flights=flights)

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('view_flights'))

    finally:
        connection.close()

@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    # Get the logged-in user's email
    user_email = session.get('user')

    if not user_email:
        flash("You must be logged in to add airplanes.", "warning")
        return redirect(url_for('login'))

    # Permission Check
    if not check_permission("Admin"):
        flash("You do not have permission to add airplanes.", "error")
        return redirect(url_for('airline_dashboard'))

    connection = get_db_connection()

    try:
        if request.method == 'POST':
            # Retrieve form data
            airplane_id = request.form.get('airplane_id')
            capacity = request.form.get('capacity')
            model = request.form.get('model')

            # Validate inputs
            if not airplane_id or not capacity or not model:
                flash("All fields are required.", "error")
                return redirect(url_for('add_airplane'))

            # Insert the new airplane into the database
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO airplane (id, name_airline, capacity, model)
                    VALUES (%s, (SELECT name FROM airline_staff WHERE username = %s), %s, %s)
                """
                cursor.execute(query, (airplane_id, user_email, capacity, model))
                connection.commit()
                flash(f"Airplane {airplane_id} added successfully.", "success")

        # Fetch all airplanes owned by the airline
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT id, capacity, model 
                FROM airplane 
                WHERE name_airline = (SELECT name FROM airline_staff WHERE username = %s)
            """
            cursor.execute(query, (user_email,))
            airplanes = cursor.fetchall()

        return render_template('add_airplane.html', airplanes=airplanes)

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('airline_dashboard'))

    finally:
        connection.close()

@app.route('/get_flight_details', methods=['GET'])
def get_flight_details():
    flight_number = request.args.get('flight_number')
    if not flight_number:
        return jsonify({"error": "Flight number is required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Query to get the airplane assigned to the flight
            query = """
                SELECT a.id, a.model, a.capacity
                FROM airplane a
                JOIN flight_airplane fa ON a.id = fa.airplane_id
                JOIN flight f ON fa.flight_id = f.id
                WHERE f.flight_number = %s
            """
            cursor.execute(query, (flight_number,))
            airplane = cursor.fetchone()

        return jsonify({"airplane": airplane})
    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/get_customers', methods=['GET'])
def get_customers():
    flight_number = request.args.get('flight_number')
    depart_time = request.args.get('depart_time')  # Expecting ISO format or matching database format

    if not flight_number or not depart_time:
        return jsonify({"error": "Both flight_number and depart_time are required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Fetch the flight_id using flight_number and depart_time
            flight_query = """
                SELECT id AS flight_id
                FROM flight
                WHERE flight_number = %s AND depart_time = %s
            """
            cursor.execute(flight_query, (flight_number, depart_time))
            print(f"The flight number is: {flight_number} and depart time is: {depart_time}")
            flight = cursor.fetchone()

            if not flight:
                return jsonify({"error": "Flight not found"}), 404

            flight_id = flight['flight_id']

            # Fetch customers associated with the retrieved flight_id
            customers_query = """
                SELECT c.name, c.email
                FROM customer c
                JOIN purchases p ON c.email = p.customer_email
                JOIN ticket t ON p.ticket_id = t.ticket_id
                WHERE t.flight_id = %s
            """
            cursor.execute(customers_query, (flight_id,))
            customers = cursor.fetchall()

        return jsonify({"customers": customers})
    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

@app.route('/customer_profile', methods=['GET'])
def customer_profile():
    # Check if the user is logged in and has admin permissions
    user_email = session.get('user')
    if not user_email:
        flash("You must be logged in to view customer profiles.", "warning")
        return redirect(url_for('login'))

    # Check permissions
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Query to check if the user has "Admin" permission
            query = """
                SELECT permission FROM permissions
                WHERE username = %s AND permission = 'Admin'
            """
            cursor.execute(query, (user_email,))
            permission = cursor.fetchone()

            if not permission:
                flash("You do not have the necessary permissions to view customer profiles.", "danger")
                return redirect(url_for('home'))  # Or redirect to a relevant page

            # Fetch customer details
            email = request.args.get('email')
            if not email:
                flash("Customer email is required to view the profile.", "warning")
                return redirect(url_for('home'))

            query = """
                SELECT name, email, building_number, street, city, state, phone_number, passport_number, passport_country
                FROM customer
                WHERE email = %s
            """
            cursor.execute(query, (email,))
            customer = cursor.fetchone()

        if not customer:
            flash("Customer not found.", "danger")
            return redirect(url_for('home'))  # Or another relevant page

        return render_template('customer_profile.html', customer=customer)
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "danger")
        return redirect(url_for('home'))
    finally:
        connection.close()


@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    # Check if the user has 'Admin' permission
    if not check_permission('Admin'):
        return redirect(url_for('airline_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')

        # Validate the form data
        if not name or not city:
            flash("Both name and city are required.", "error")
            return redirect(url_for('add_airport'))

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Insert the new airport into the database
                query = """
                    INSERT INTO airport (name, city)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (name, city))
                connection.commit()
                flash(f"Airport '{name}' in '{city}' added successfully.", "success")
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}", "error")
        finally:
            connection.close()

        return redirect(url_for('add_airport'))

    return render_template('add_airport.html')



@app.route('/view_all_bookings', methods=['GET'])
def view_all_bookings():
    # Ensure the user is logged in and has the necessary permissions
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can view all bookings.", "error")
        return redirect(url_for('home'))

    connection = get_db_connection()

    try:
        # Query to get all bookings for the airline
        query = """
            SELECT p.customer_email, t.ticket_id, f.name_airline, f.flight_number, 
                   f.name_depart, f.name_arrive, f.depart_time, f.arrive_time, 
                   p.purchase_date
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
            WHERE f.name_airline = (
                SELECT name FROM airline_staff WHERE username = %s
            )
            ORDER BY p.purchase_date DESC
        """
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, (session['user'],))
            bookings = cursor.fetchall()

        if not bookings:
            flash("No bookings found.", "info")
            return render_template('all_bookings.html', bookings=[], success=False)

        return render_template('all_bookings.html', bookings=bookings, success=True)

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('airline_dashboard'))

    finally:
        connection.close()


@app.route('/view_frequent_customers', methods=['GET'])
def view_frequent_customers():
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can view frequent customers.", "error")
        return redirect(url_for('home'))

    connection = get_db_connection()

    try:
        # Query for the top 5 frequent customers
        query = """
            SELECT p.customer_email, COUNT(p.ticket_id) AS ticket_count
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
            WHERE f.name_airline = (
                SELECT name FROM airline_staff WHERE username = %s
            )
            AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY p.customer_email
            ORDER BY ticket_count DESC
            LIMIT 5
        """
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, (session['user'],))
            frequent_customers = cursor.fetchall()

        # Prepare chart data
        chart_data = {
            "labels": [customer["customer_email"] for customer in frequent_customers],
            "values": [customer["ticket_count"] for customer in frequent_customers],
        }

        return render_template('frequent_customers.html', chart_data=chart_data)

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('airline_dashboard'))

    finally:
        connection.close()


@app.route('/view_reports', methods=['GET', 'POST'])
def view_reports():
    # Ensure the user is logged in and has the necessary permissions
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can view reports.", "error")
        return redirect(url_for('home'))

    # Initialize variables for the report
    total_tickets = 0
    ticket_sales = []
    chart_data = {"labels": [], "values": []}
    report_type = "last_year"
    start_date = None
    end_date = None

    try:
        # Handle date range and report type selection
        if request.method == 'POST':
            report_type = request.form.get('report_type', 'last_year')

            # Determine the date range based on the report type
            if report_type == 'custom':
                start_date = request.form.get('start_date')
                end_date = request.form.get('end_date')
                if not start_date or not end_date:
                    flash("Please provide both start and end dates for a custom report.", "warning")
                    return redirect(url_for('view_reports'))
            elif report_type == 'last_year':
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
            elif report_type == 'last_month':
                today = datetime.now()
                first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
                last_day_last_month = today.replace(day=1) - timedelta(days=1)
                start_date = first_day_last_month.strftime('%Y-%m-%d')
                end_date = last_day_last_month.strftime('%Y-%m-%d')

            # Debugging: Print the selected dates and report type
            print(f"Report Type: {report_type}, Start Date: {start_date}, End Date: {end_date}")

            # Connect to the database and execute queries
            connection = get_db_connection()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Query for total tickets
                query_total = """
                    SELECT COUNT(*) AS total_tickets
                    FROM purchases p
                    JOIN ticket t ON p.ticket_id = t.ticket_id
                    JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                    WHERE f.name_airline = (
                        SELECT name FROM airline_staff WHERE username = %s
                    )
                    AND p.purchase_date BETWEEN %s AND %s
                """
                cursor.execute(query_total, (session['user'], start_date, end_date))
                total_result = cursor.fetchone()
                print("Raw query result:", total_result)
                total_tickets = total_result['total_tickets'] if total_result else 0

                # Query for month-wise ticket sales
                query_monthly = """
                    SELECT DATE_FORMAT(p.purchase_date, '%%Y-%%m') AS month, COUNT(*) AS ticket_count
                    FROM purchases p
                    JOIN ticket t ON p.ticket_id = t.ticket_id
                    JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                    WHERE f.name_airline = (
                        SELECT name FROM airline_staff WHERE username = %s
                    )
                    AND p.purchase_date BETWEEN %s AND %s
                    GROUP BY month
                    ORDER BY month ASC
                """
                cursor.execute(query_monthly, (session['user'], start_date, end_date))
                ticket_sales = cursor.fetchall()

            # Prepare data for the bar chart
            chart_data["labels"] = [sale["month"] for sale in ticket_sales]
            chart_data["values"] = [sale["ticket_count"] for sale in ticket_sales]

        return render_template(
            'reports.html',
            total_tickets=total_tickets,
            chart_data=chart_data,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        flash("An error occurred while generating the report. Please try again later.", "error")
        return redirect(url_for('airline_dashboard'))

    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An unexpected error occurred. Please contact support.", "error")
        return redirect(url_for('airline_dashboard'))

    finally:
        if 'connection' in locals():
            connection.close()




@app.route('/compare_revenue', methods=['GET'])
def compare_revenue():
    # Ensure the user is logged in and has the necessary permissions
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can view revenue comparison.", "error")
        return redirect(url_for('home'))

    try:
        connection = get_db_connection()
        last_month_revenue = {"direct": 0, "indirect": 0}
        last_year_revenue = {"direct": 0, "indirect": 0}

        today = datetime.now()
        # Define date ranges
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
        last_day_last_month = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        one_year_ago = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        today_date = today.strftime('%Y-%m-%d')

        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Revenue for the last month
            query_last_month = """
                SELECT
                    SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) AS direct_revenue,
                    SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) AS indirect_revenue
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                WHERE f.name_airline = (
                    SELECT name FROM airline_staff WHERE username = %s
                )
                AND p.purchase_date BETWEEN %s AND %s
            """
            cursor.execute(query_last_month, (session['user'], first_day_last_month, last_day_last_month))
            result_last_month = cursor.fetchone()
            if result_last_month:
                last_month_revenue["direct"] = result_last_month["direct_revenue"] or 0
                last_month_revenue["indirect"] = result_last_month["indirect_revenue"] or 0

            # Revenue for the last year
            query_last_year = """
                SELECT
                    SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) AS direct_revenue,
                    SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) AS indirect_revenue
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                WHERE f.name_airline = (
                    SELECT name FROM airline_staff WHERE username = %s
                )
                AND p.purchase_date BETWEEN %s AND %s
            """
            cursor.execute(query_last_year, (session['user'], one_year_ago, today_date))
            result_last_year = cursor.fetchone()
            if result_last_year:
                last_year_revenue["direct"] = result_last_year["direct_revenue"] or 0
                last_year_revenue["indirect"] = result_last_year["indirect_revenue"] or 0

        return render_template(
            'compare_revenue.html',
            last_month_revenue=last_month_revenue,
            last_year_revenue=last_year_revenue
        )

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        flash("An error occurred while generating revenue comparison. Please try again later.", "error")
        return redirect(url_for('airline_dashboard'))

    finally:
        if 'connection' in locals():
            connection.close()


@app.route('/view_top_destinations', methods=['GET'])
def view_top_destinations():
    # Ensure the user is logged in and has the necessary permissions
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can view top destinations.", "error")
        return redirect(url_for('home'))

    try:
        connection = get_db_connection()
        top_destinations_3_months = []
        top_destinations_year = []

        today = datetime.now()
        three_months_ago = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        one_year_ago = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        today_date = today.strftime('%Y-%m-%d')

        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Top destinations for the last 3 months
            query_3_months = """
                SELECT f.name_arrive AS destination, COUNT(*) AS trip_count
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                WHERE f.name_airline = (
                    SELECT name FROM airline_staff WHERE username = %s
                )
                AND p.purchase_date BETWEEN %s AND %s
                GROUP BY f.name_arrive
                ORDER BY trip_count DESC
                LIMIT 3
            """
            cursor.execute(query_3_months, (session['user'], three_months_ago, today_date))
            top_destinations_3_months = cursor.fetchall()

            # Top destinations for the last year
            query_year = """
                SELECT f.name_arrive AS destination, COUNT(*) AS trip_count
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                WHERE f.name_airline = (
                    SELECT name FROM airline_staff WHERE username = %s
                )
                AND p.purchase_date BETWEEN %s AND %s
                GROUP BY f.name_arrive
                ORDER BY trip_count DESC
                LIMIT 3
            """
            cursor.execute(query_year, (session['user'], one_year_ago, today_date))
            top_destinations_year = cursor.fetchall()

        return render_template(
            'top_destinations.html',
            top_destinations_3_months=top_destinations_3_months,
            top_destinations_year=top_destinations_year
        )

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        flash("An error occurred while fetching top destinations. Please try again later.", "error")
        return redirect(url_for('airline_dashboard'))

    finally:
        if 'connection' in locals():
            connection.close()


@app.route('/grant_permissions', methods=['GET', 'POST'])
def grant_permissions():
    # Check if the user is logged in and has Admin permissions
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can manage permissions.", "error")
        return redirect(url_for('home'))

    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Check if the logged-in user has Admin permission
            cursor.execute("""
                SELECT permission
                FROM permissions
                WHERE username = %s AND permission = 'Admin'
            """, (session['user'],))
            has_admin_permission = cursor.fetchone()

            if not has_admin_permission:
                flash("Access denied: You do not have Admin permissions.", "error")
                return redirect(url_for('airline_dashboard'))

            # Fetch other staff members from the same airline
            cursor.execute("""
                SELECT username
                FROM airline_staff
                WHERE name = (
                    SELECT name
                    FROM airline_staff
                    WHERE username = %s
                )
                AND username != %s
            """, (session['user'], session['user']))
            staff_list = cursor.fetchall()

            if request.method == 'POST':
                staff_username = request.form.get('staff_username')
                new_permission = request.form.get('permission')

                # Validate staff selection
                cursor.execute("""
                    SELECT username
                    FROM airline_staff
                    WHERE username = %s AND name = (
                        SELECT name
                        FROM airline_staff
                        WHERE username = %s
                    )
                """, (staff_username, session['user']))
                valid_staff = cursor.fetchone()

                if not valid_staff:
                    flash("The selected staff member does not belong to your airline.", "error")
                    return redirect(url_for('grant_permissions'))

                # Grant the new permission
                cursor.execute("""
                    INSERT INTO permissions (username, permission)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE permission = VALUES(permission)
                """, (staff_username, new_permission))
                connection.commit()

                flash(f"Permission '{new_permission}' granted to {staff_username}.", "success")

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
    finally:
        connection.close()

    return render_template('grant_permissions.html', staff_list=staff_list)

@app.route('/update_booking_agent_airline', methods=['GET', 'POST'])
def update_booking_agent_airline():
    # Ensure the user is logged in and has Admin permissions
    if 'user' not in session or session.get('user_type') != 'airline_staff':
        flash("Access denied: Only airline staff can manage booking agents.", "error")
        return redirect(url_for('home'))

    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Check if the logged-in user has Admin permission
            cursor.execute("""
                SELECT permission
                FROM permissions
                WHERE username = %s AND permission = 'Admin'
            """, (session['user'],))
            has_admin_permission = cursor.fetchone()

            if not has_admin_permission:
                flash("Access denied: You do not have Admin permissions.", "error")
                return redirect(url_for('airline_dashboard'))

            # Fetch the airline name of the current admin
            cursor.execute("""
                SELECT name
                FROM airline_staff
                WHERE username = %s
            """, (session['user'],))
            airline = cursor.fetchone()

            if request.method == 'POST':
                agent_email = request.form.get('agent_email')

                # Validate the email
                if not agent_email:
                    flash("Please provide a valid booking agent email.", "error")
                    return redirect(url_for('update_booking_agent_airline'))

                # Check if the booking agent exists
                cursor.execute("SELECT * FROM booking_agent WHERE email = %s", (agent_email,))
                agent_exists = cursor.fetchone()

                if not agent_exists:
                    flash("Booking agent not found.", "warning")
                    return redirect(url_for('update_booking_agent_airline'))

                # Update the booking agent's airline
                cursor.execute("""
                    UPDATE booking_agent
                    SET name = %s
                    WHERE email = %s
                """, (airline['name'], agent_email))
                connection.commit()

                flash(f"Booking agent '{agent_email}' has been updated to airline '{airline['name']}'.", "success")
                return redirect(url_for('update_booking_agent_airline'))

    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "error")
    finally:
        connection.close()

    return render_template('update_booking_agent_airline.html')

#<--------------------------------------------------Staff section>
#<--------------------------------------------------Agent section>
@app.route('/view_my_flights', methods=['GET', 'POST'])
def view_my_flights():
    user_email = session.get('user')  # Get logged-in user's email
    connection = get_db_connection()
    
    query = """
        SELECT f.flight_number, f.name_airline, f.name_depart, f.name_arrive, f.depart_time, f.arrive_time
        FROM ticket t
        JOIN flight f ON t.flight_number = f.flight_number
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN booking_agent ba ON ba.booking_agent_id = p.booking_agent_id  -- Ensure we match booking agent ID
        WHERE ba.email = %s  -- Filter by the unique email of the booking agent
        AND f.depart_time >= NOW();  -- Only show upcoming flights
    """
    
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, (user_email,))  # Execute query using email from session
        flights = cursor.fetchall()  # Fetch all flights associated with the agent

    return render_template('booking_agent_dashboard.html', flights=flights)


@app.route('/purchase_ticket', methods=['POST'])
def purchase_ticket():
    flight_number = request.form['flight_number']
    customer_email = request.form['customer_email']
    booking_agent_email = session.get('user')
    query = """
        INSERT INTO purchases (booking_agent_id, customer_email, flight_number) 
        VALUES (%s, %s, %s, %s)
    """
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(query, (booking_agent_email, customer_email, flight_number))
        connection.commit()

    flash('Ticket Purchased Successfully', 'success')
    return redirect(url_for('view_my_flights'))

@app.route('/search_flights', methods=['POST'])
def search_flights():
    source = request.form['source']
    destination = request.form['destination']
    date = request.form['date']
    query = """
        SELECT * FROM flight f
        JOIN airport dep ON f.name_depart = dep.name
        JOIN airport arr ON f.name_arrive = arr.name
        WHERE dep.city LIKE %s AND arr.city LIKE %s AND f.depart_time >= %s;
    """
    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, (source, destination, date))
        flights = cursor.fetchall()

    return render_template('booking_agent_dashboard.html', flights=flights)

from collections import defaultdict

@app.route('/view_commission', methods=['GET'])
def view_commission():
    if 'user' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))

    connection = get_db_connection()
    booking_agent_id = None

    # Verify the user is a booking agent
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT booking_agent_id FROM booking_agent WHERE email = %s", (session['user'],))
            result = cursor.fetchone()
            if not result:
                flash("Access denied: Not a booking agent.", "error")
                return redirect(url_for('booking_agent_dashboard'))

            booking_agent_id = result['booking_agent_id']

    except Exception as e:
        flash(f"Error fetching agent details: {e}", "error")
        return redirect(url_for('booking_agent_dashboard'))

    # Calculate commissions and group by purchase date
    commission_percentage = 0.10  # 10%
    total_commission = 0
    total_tickets = 0
    commission_by_date = defaultdict(float)  # Dictionary to store commissions grouped by date

    try:
        with connection.cursor() as cursor:
            # Query to fetch price, purchase date, and other details
            query = """
                SELECT f.price AS flight_price, p.purchase_date
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                WHERE p.booking_agent_id = %s
            """
            cursor.execute(query, (booking_agent_id,))
            tickets = cursor.fetchall()

            # Calculate commission totals and group by date
            for ticket in tickets:
                total_commission += ticket['flight_price'] * commission_percentage
                total_tickets += 1

                # Group by date (e.g., YYYY-MM-DD)
                date_key = ticket['purchase_date'].strftime('%Y-%m-%d')
                commission_by_date[date_key] += ticket['flight_price'] * commission_percentage

    except Exception as e:
        flash(f"Error calculating commission: {e}", "error")
        return redirect(url_for('booking_agent_dashboard'))
    finally:
        connection.close()

    # Prepare data for the chart (sorted by date)
    chart_data = sorted(commission_by_date.items())  # [(date1, commission1), (date2, commission2), ...]

    return render_template(
        'view_commission.html',
        total_commission=total_commission,
        total_tickets=total_tickets,
        commission_percentage=commission_percentage * 100,
        chart_data=chart_data  # Pass chart data to the template
    )


@app.route('/view_top_customers', methods=['GET'])
def view_top_customers():
    if 'user' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))

    connection = get_db_connection()
    booking_agent_id = None

    # Verify the user is a booking agent
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT booking_agent_id FROM booking_agent WHERE email = %s", (session['user'],))
            result = cursor.fetchone()
            if not result:
                flash("Access denied: Not a booking agent.", "error")
                return redirect(url_for('booking_agent_dashboard'))  # Redirect to a safe fallback like `home`

            booking_agent_id = result['booking_agent_id']

    except Exception as e:
        flash(f"Error fetching agent details: {e}", "error")
        return redirect(url_for('home'))

    top_customers_tickets = []
    top_customers_commission = []

    try:
        with connection.cursor() as cursor:
            # Top 5 customers by tickets bought in the last 6 months
            query_tickets = """
                SELECT p.customer_email, COUNT(p.ticket_id) AS ticket_count
                FROM purchases p
                WHERE p.booking_agent_id = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY p.customer_email
                ORDER BY ticket_count DESC
                LIMIT 5
            """
            cursor.execute(query_tickets, (booking_agent_id,))
            top_customers_tickets = cursor.fetchall()

            # Top 5 customers by commission in the last year
            commission_percentage = 0.10  # 10% commission
            query_commission = """
                SELECT p.customer_email, SUM(f.price * %s) AS total_commission
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.flight_number = f.flight_number AND t.depart_time = f.depart_time
                WHERE p.booking_agent_id = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                GROUP BY p.customer_email
                ORDER BY total_commission DESC
                LIMIT 5
            """
            cursor.execute(query_commission, (commission_percentage, booking_agent_id))
            top_customers_commission = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching top customers: {e}", "error")
    finally:
        connection.close()

    # Prepare data for charts
    ticket_chart_data = {
        "labels": [customer["customer_email"] for customer in top_customers_tickets],
        "values": [customer["ticket_count"] for customer in top_customers_tickets]
    }
    commission_chart_data = {
        "labels": [customer["customer_email"] for customer in top_customers_commission],
        "values": [customer["total_commission"] for customer in top_customers_commission]
    }

    return render_template(
        'view_top_customers.html',
        ticket_chart_data=ticket_chart_data,
        commission_chart_data=commission_chart_data
    )



@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    
    # Optionally, use flash to show a message (as per your existing code)
    flash('You have been logged out', 'info')
    
    # Redirect the user to a "goodbye" page
    return render_template('goodbye.html')  # Render a goodbye page


if __name__ == '__main__':
    app.run(debug=True)
