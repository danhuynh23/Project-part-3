import pymysql

# Database connection
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Replace with your actual password
        database='air_ticketing_system',
        cursorclass=pymysql.cursors.DictCursor
    )

# Test inserting into the customer table
def test_insert():
    connection = None
    try:
        connection = get_db_connection()
        print("Connection successful")

        with connection:
            cursor = connection.cursor()
            # Example data
            email = "test_insert@example.com"
            name = "Test User"
            password = "hashedpassword123"  # Example hashed password
            building_number = "123"
            street = "Main Street"
            city = "Sample City"
            state = "Sample State"
            phone_number = "1234567890"
            passport_number = "A1234567"
            passport_expiration = "2025-12-31"
            passport_country = "Sample Country"
            date_of_birth = "2000-01-01"

            # Insert query
            insert_query = """
                INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, 
                                      passport_number, passport_expiration, passport_country, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (email, name, password, building_number, street, city, state, phone_number,
                                          passport_number, passport_expiration, passport_country, date_of_birth))
            connection.commit()
            print("Insert successful")

    except pymysql.MySQLError as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    test_insert()
