from flask import Flask, request, jsonify
import openai
import pymysql
import os
import sqlparse

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set!")

# Database configuration
def get_db_connection():
    """
    Connect to the database in the Docker network.
    """
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
        database=os.getenv('MYSQL_DB', 'airticketingsystem'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# OpenAI query-to-SQL function
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
    Additional Notes:
    - Locations may be referred to by shorthand codes (e.g., "NYC" for "New York", "LAX" for "Los Angeles"). The data is stored as city's name for example New York. The flight table's data for example in name_depart is using airport codes e.g JFK. 
    - When search for a flight based on location of the airport you must match the user provided location to an Airport code. For example, NYC (New York) is JFK. You should do the same if the user provide any location, get the most relavent airport. 
    - If the user doesn't provide something which is relavent to your role as a customer support agent, just be nice and entertain them. 
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
        messages=[{"role": "system", "content": "Generate SQL queries from natural language queries."},
                  {"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0
    )
    return response['choices'][0]['message']['content'].strip()

# SQL execution and validation
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

def validate_sql_query(sql_query):
    """
    Validate SQL query for basic safety.
    """
    parsed = sqlparse.parse(sql_query)
    for token in parsed[0].tokens:
        if str(token).lower() in ["drop", "delete"]:
            raise ValueError("Unsafe SQL query detected.")
    return True

# Response generation
def generate_response(query, context):
    """
    Generate a response using OpenAI ChatCompletion.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"User Query: {query}\nContext: {context}\nProvide a detailed and helpful response:"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()

# Main route for RAG bot
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

        if not results:
            # Generate fallback response using LLM
            context = f"No data was found for the query: {user_query}. "
            context += (
                "You are unable to find the data as specified, please give the user a response to apologize for that. You are a customer service agent working for a booking agency."
            )
            fallback_response = generate_response(user_query, context)

            return jsonify({
                "query": user_query,
                "sql_query": sql_query,
                "results": results,
                "response": fallback_response
            }), 200

        # Format results for LLM
        formatted_results = "\n".join([
            f"Flight {r['flight_number']} ({r['name_airline']}) departs {r['name_depart']} at {r['depart_time']} and arrives at {r['name_arrive']} at {r['arrive_time']}. Price: ${r['price']}. Status: {r['status']}. Seats available: {r['seats'] or 'N/A'}."
            for r in results
        ])

        # Generate response using LLM
        context = f"The following flights were found based on the query: {user_query}.\n\n"
        context += formatted_results
        context += "\n\nSummarize this information for the customer in a professional tone. Do not include flight ID or seats or prices."

        llm_response = generate_response(user_query, context)

        return jsonify({
            "query": user_query,
            "sql_query": sql_query,
            "results": results,
            "response": llm_response
        }), 200

    except Exception as e:
        return jsonify({"error": str(e), "sql_query": sql_query}), 400

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
