from flask import Flask, request, jsonify
import openai
import pymysql
import os

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set!")


def get_db_connection():
    """
    Connect to the database in the Docker network.
    """
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),  # Docker service name for DB
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
        database=os.getenv('MYSQL_DB', 'airticketingsystem'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def query_to_sql(user_query):
    """
    Convert natural language queries into SQL queries using OpenAI.
    """
    schema_description = """
    The database schema is as follows:
    - airline (name)
    - airline_staff (username, name, password, first_name, last_name, date_of_birth)
    - flight (id, flight_number, name_depart, name_arrive, name_airline, depart_time, arrive_time, price, status, seats)
    - airport (name, city)
    - customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
    - ticket (ticket_id, name_airline, flight_number, depart_time, flight_id)
    - purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
    Relationships:
    - Flights reference airports (departure and arrival).
    - Tickets reference flights and airlines.
    - Purchases reference customers and tickets.

    Generate precise SQL queries based on this schema.
    """
    prompt = f"""
    You are an assistant that generates SQL queries from user queries based on the following database schema:
    {schema_description}
    
    User Query: "{user_query}"
    Write the corresponding SQL query without any explanation.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Generate SQL queries from natural language queries."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0
    )

    return response['choices'][0]['message']['content'].strip()


def execute_sql_query(sql_query):
    """
    Execute the SQL query and fetch results from the database.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results
    except Exception as e:
        return {"error": str(e)}
    finally:
        connection.close()

import sqlparse

def validate_sql_query(sql_query):
    """
    Validate SQL query for basic safety.
    """
    parsed = sqlparse.parse(sql_query)
    for token in parsed[0].tokens:
        if str(token).lower() in ["drop", "delete"]:
            raise ValueError("Unsafe SQL query detected.")
    return True


def generate_response(query, context):
    """
    Generate a response using OpenAI ChatCompletion.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"User Query: {query}\nContext: {context}\nProvide a detailed and helpful response:"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use "gpt-4" if you prefer GPT-4
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()


@app.route('/rag_query', methods=['POST'])
def rag_query():
    data = request.json
    user_query = data.get('query', '')
    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    # Generate SQL
    sql_query = query_to_sql(user_query)

    # Validate and execute SQL
    try:
        validate_sql_query(sql_query)
        results = execute_sql_query(sql_query)
        return jsonify({"query": user_query, "sql_query": sql_query, "results": results})
    except Exception as e:
        return jsonify({"error": str(e), "sql_query": sql_query}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
