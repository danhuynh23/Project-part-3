@app.route('/booking')
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
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.flight_number,f.name_airline, f.depart_time, f.arrive_time, f.name_depart, 
                   f.name_arrive, f.price
            FROM flight f
            WHERE f.id = %s
        """, (flight_id,))
        flight_details = cursor.fetchone()

    if not flight_details:
        flash("Flight not found.", "error")
        return redirect(url_for('show_flights'))

    # Fetch user details
    user_details = None
    if 'user' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE email = %s", (session['user'],))
            user_details = cursor.fetchone()

    # Render the booking page with flight details and user information
    return render_template(
        'booking_page.html',
        flight=flight_details,
        flight_id=flight_id,  # Pass flight_id explicitly
        fare_type=fare_type,
        name_airline=flight_details['name_airline'],
        flight_number=flight_details['flight_number'],
        user_details=user_details
    )
