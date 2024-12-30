import openai

import os 

openai.api_key = ""

if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set!")

completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
            {"role": "system", "content": "You are a helpful assistant for generating SQL queries."},
            {
                "role": "user",
                "content": """
                    You are an advanced SQL query generator. You generate SQL queries for a predefined database schema based on user requests.

                    Database Schema:
                    - airline (name)
                    - airline_staff (username, name, password, first_name, last_name, date_of_birth)
                    - flight (id, flight_number, name_depart, name_arrive, name_airline, depart_time, arrive_time, price, status, seats)
                    - airport (name, city)
                    - customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
                    - ticket (ticket_id, name_airline, flight_number, depart_time, flight_id)
                    - purchases (ticket_id, customer_email, booking_agent_id, purchase_date)

                    User Query: "Find flights from JFK to LAX"

                    ### Instructions:
                    - Only generate a valid SQL query based on the user query.
                    - Do not include explanations, apologies, or unrelated content.
                    - Ensure the SQL query adheres to the database schema.
                    - Response must only contain the SQL query.

                    ### Response:
                """
            }
        ]
    )


print(completion.choices[0].message)