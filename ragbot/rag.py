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

# Initialize Flask
app = Flask(__name__)

# Logging config
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Conversation memory: each user/assistant message is stored for multi-turn context
memory = ConversationBufferMemory(return_messages=True)

# LLM: GPT-4 chat model
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
        database=os.getenv('MYSQL_DB', 'airticketingsystem'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(sql_query: str):
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

# Prompt templates for SQL generation, summarization, fallback
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

response_prompt = PromptTemplate(
    input_variables=["conversation_history", "query", "results"],
    template="""
{conversation_history}

User Query: "{query}"
SQL Results: "{results}"

Give a concise summary for the user.
"""
)

fallback_prompt = PromptTemplate(
    input_variables=["conversation_history", "query"],
    template="""
{conversation_history}

The user query is not DB-related:
"{query}"

Please respond helpfully:
"""
)

# Build chain from prompt + LLM
sql_chain = sql_prompt | llm
response_chain = response_prompt | llm
fallback_chain = fallback_prompt | llm

# Classification for DB-related queries
class UserQuery(BaseModel):
    query: str

def classify_query(query: str) -> bool:
    # Potential keywords
    target_keywords = ["flight", "ticket", "customer", "database", "query"]
    words_in_query = query.lower().split()

    # If any word in `words_in_query` is close to any of the `target_keywords`, return True
    for word in words_in_query:
        # e.g., look for words that have a close match with a ratio > 0.8
        matches = get_close_matches(word, target_keywords, n=1, cutoff=0.8)
        if matches:
            return True
    return False


# Helper to map HumanMessage, AIMessage, or SystemMessage to user/assistant/system
def get_message_role(msg):
    if isinstance(msg, HumanMessage):
        return "user"
    elif isinstance(msg, AIMessage):
        return "assistant"
    elif isinstance(msg, SystemMessage):
        return "system"
    return "unknown"

@app.route('/rag_query', methods=['POST'])
def rag_query():
    """
    Endpoint for multi-turn conversation with memory. 
    Database queries get SQL generation + summarization. 
    Non-database queries get a fallback response, but both see the entire conversation.
    """
    try:
        # 1) Parse input
        data = request.json
        logger.debug("Raw input data: %s", data)
        user_query = UserQuery(**data)
        logger.info("User query validated: %s", user_query.query)

        # 2) Add user message to memory
        memory.chat_memory.add_user_message(user_query.query)

        # 3) Build conversation text from all stored messages
        #    We check if each message is HumanMessage, AIMessage, etc.
        conversation_text = "\n".join(
            f"{get_message_role(msg)}: {msg.content}"
            for msg in memory.chat_memory.messages
        )

        # 4) Classification
        if classify_query(user_query.query):
            # a) Generate SQL, passing full conversation
            sql_result = sql_chain.invoke({
                "conversation_history": conversation_text,
                "query": user_query.query
            })

            # b) Extract SQL from chain result
            if isinstance(sql_result, AIMessage):
                sql_query = sql_result.content.strip()
            else:
                sql_query = str(sql_result).strip()
            logger.info("Generated SQL: %s", sql_query)

            # c) Execute SQL
            db_results = execute_query(sql_query)
            logger.info("Executed SQL successfully.")

            # d) Format for summarization
            db_results = execute_query(sql_query)  # returns a list of dictionaries

            if isinstance(db_results, list):
                formatted_results = "\n".join(
                    # Use r.get(...) with a default value 
                    # (e.g. 'Unknown Flight', 'Unknown Depart', or 'Unknown Time')
                    f"Flight {r.get('flight_number', 'Unknown Flight')} "
                    f"departs {r.get('name_depart', 'Unknown Depart')} at {r.get('depart_time', 'Unknown Time')}. "
                    f"Price: {r.get('price', 'N/A')}"
                    for r in db_results
                ) or "No flights found."
            else:
                formatted_results = db_results

            # e) Summarize with response_chain
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
            # Fallback path, also passing conversation history
            fallback_out = fallback_chain.invoke({
                "conversation_history": conversation_text,
                "query": user_query.query
            })

            if isinstance(fallback_out, AIMessage):
                fallback_response = fallback_out.content.strip()
            else:
                fallback_response = str(fallback_out).strip()

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
