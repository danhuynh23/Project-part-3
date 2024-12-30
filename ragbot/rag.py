from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from difflib import get_close_matches

import pymysql
import os
import logging

# ---------------------------
# 1) Flask App & Logging
# ---------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ---------------------------
# 2) Conversation Memory
# ---------------------------
# Stores multi-turn messages from user & assistant
memory = ConversationBufferMemory(return_messages=True)

# ---------------------------
# 3) GPT-4 Chat Model
# ---------------------------
llm = ChatOpenAI(model="gpt-4", temperature=0)

# ---------------------------
# 4) Database Connection
# ---------------------------
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "my-secret-pw"),
        database=os.getenv("MYSQL_DB", "airticketingsystem"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(sql_query: str):
    """
    Execute the given SQL query in MySQL and return results.
    """
    logger.info("Executing SQL query: %s", sql_query)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results if results else "No results found."
    except Exception as e:
        logger.error("Error executing SQL: %s", str(e))
        raise
    finally:
        conn.close()

# ---------------------------
# 5) Prompt Templates & Chains
# ---------------------------
sql_prompt = PromptTemplate(
    input_variables=["conversation_history", "query"],
    template="""
{conversation_history}

You are an advanced SQL generation assistant. Generate valid SQL queries for this database schema:

- airline(name)
- airline_staff(username, name, password, first_name, last_name, date_of_birth)
- flight(id, flight_number, name_depart, name_arrive, name_airline, depart_time, arrive_time, price, status, seats)
- airport(name, city)
- customer(email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
- ticket(ticket_id, name_airline, flight_number, depart_time, flight_id)
- purchases(ticket_id, customer_email, booking_agent_id, purchase_date)

When you join the same table multiple times (e.g., airport for depart and arrival),
use distinct aliases like a_depart and a_arrive. Avoid reusing `airport` as the same alias twice.
Avoid T-SQL or other dialect features like 'TOP'. Use `LIMIT` instead.

User Query: "{query}"
Only generate the SQL query. No explanations.
"""
)
sql_chain = sql_prompt | llm

response_prompt = PromptTemplate(
    input_variables=["conversation_history", "query", "results"],
    template="""
{conversation_history}

User Query: "{query}"
SQL Results: "{results}"

Give a concise summary for the user.
"""
)
response_chain = response_prompt | llm

fallback_prompt = PromptTemplate(
    input_variables=["conversation_history", "query"],
    template="""
{conversation_history}

The user query is not DB-related:
"{query}"

Please respond helpfully:
"""
)
fallback_chain = fallback_prompt | llm

# ---------------------------
# 6) Classification Logic
# ---------------------------
classification_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
User Query: "{query}"

Decide if the above query is about flights, tickets, customers, or any database operation. 
If yes, respond with exactly "true".
If no, respond with exactly "false".
"""
)

# Create a chain from the prompt and your LLM
classification_chain = classification_prompt | llm

class UserQuery(BaseModel):
    """Simple Pydantic model for the JSON payload."""
    query: str

def classify_query(query: str) -> bool:
    """
    Ask the LLM if the query is 'database-related' 
    (e.g. flights, tickets, customers).
    Returns True if LLM says "true", otherwise False.
    """
    # 1) Invoke the classification chain
    classification_result = classification_chain.invoke({"query": query})
    
    # 2) Extract the text from AIMessage or fallback to string
    if isinstance(classification_result, AIMessage):
        answer = classification_result.content.strip().lower()
    else:
        answer = str(classification_result).strip().lower()

    # 3) Return True if LLM answered "true", otherwise False
    return (answer == "true")

# Helper to map message classes (Human, AI, System) to role strings
def get_message_role(msg):
    if isinstance(msg, HumanMessage):
        return "user"
    elif isinstance(msg, AIMessage):
        return "assistant"
    elif isinstance(msg, SystemMessage):
        return "system"
    return "unknown"

# ---------------------------
# 7) Endpoint
# ---------------------------
@app.route("/rag_query", methods=["POST"])
def rag_query():
    """
    Endpoint for multi-turn conversation with memory. 
    - If classify_query() => True, it calls SQL chain & executes the query, then uses the response chain.
    - Else, it calls fallback chain.
    - Both see conversation_history for context (like 'My name is Dan').
    """
    try:
        # 1) Parse Input
        data = request.json
        logger.debug("Raw input data: %s", data)
        user_query = UserQuery(**data)
        logger.info("User query validated: %s", user_query.query)

        # 2) Add user message to memory
        memory.chat_memory.add_user_message(user_query.query)

        # 3) Build conversation text from stored messages
        conversation_text = "\n".join(
            f"{get_message_role(msg)}: {msg.content}"
            for msg in memory.chat_memory.messages
        )

        # 4) Classification
        if classify_query(user_query.query):
            # a) Generate SQL with conversation history
            sql_result = sql_chain.invoke({
                "conversation_history": conversation_text,
                "query": user_query.query
            })

            # b) Extract SQL
            if isinstance(sql_result, AIMessage):
                sql_query = sql_result.content.strip()
            else:
                sql_query = str(sql_result).strip()
            logger.info("Generated SQL: %s", sql_query)

            # c) Execute SQL
            db_results = execute_query(sql_query)
            logger.info("Executed SQL successfully.")

            # d) Format results with .get(...) to avoid KeyErrors
            # if isinstance(db_results, list):
            #     formatted_results = "\n".join(
            #         f"Flight {row.get('flight_number', 'Unknown Flight')} "
            #         f"departs {row.get('name_depart', 'Unknown Depart')} at {row.get('depart_time', 'Unknown Time')}. "
            #         f"Price: {row.get('price', 'N/A')}"
            #         for row in db_results
            #     ) or "No flights found."
            # else:
            #     formatted_results = db_results
            formatted_results = db_results
            # e) Summarize
            summary_out = response_chain.invoke({
                "conversation_history": conversation_text,
                "query": user_query.query,
                "results": formatted_results
            })

            if isinstance(summary_out, AIMessage):
                summary = summary_out.content.strip()
            else:
                summary = str(summary_out).strip()

            # f) Add summary to memory
            memory.chat_memory.add_ai_message(summary)

            return jsonify({
                "sql_query": sql_query,
                "results": formatted_results,
                "response": summary
            }), 200

        else:
            # Fallback path
            fallback_out = fallback_chain.invoke({
                "conversation_history": conversation_text,
                "query": user_query.query
            })

            if isinstance(fallback_out, AIMessage):
                fallback_response = fallback_out.content.strip()
            else:
                fallback_response = str(fallback_out).strip()

            # Add fallback response to memory
            memory.chat_memory.add_ai_message(fallback_response)

            return jsonify({
                "query": user_query.query,
                "response": fallback_response
            }), 200

    except ValidationError as e:
        logger.error("Validation Error: %s", str(e))
        return jsonify({"error": "Validation Error", "details": str(e)}), 400

    except Exception as e:
        logger.exception("Internal Server Error")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


# ---------------------------
# 8) Run Flask
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
