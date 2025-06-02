from flask import Blueprint, request, jsonify
import cohere
import os
import sqlite3
from dotenv import load_dotenv
from faq_embed import search_similiar_faq, build_faq_index

load_dotenv()
ai_bp = Blueprint("ai", __name__)
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def init_db():
    conn = sqlite3.connect("cache.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS cache(
        prompt TEXT primary key,
        answer TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


init_db()


def get_cached_answer(prompt):
    conn = sqlite3.connect("cache.db")
    c = conn.cursor()
    c.execute("SELECT answer FROM cache WHERE prompt=?", (prompt,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def cache_answer(prompt, answer):
    conn = sqlite3.connect("cache.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO cache (prompt, answer) VALUES (?, ?)", (prompt, answer)
    )
    conn.commit()
    conn.close()


@ai_bp.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    cached = get_cached_answer(prompt)
    if cached:
        return jsonify({"answer": cached, "cached": True})
    print("not cached")
    try:
        response = co.generate(model="command", prompt=prompt, max_tokens=200)
        answer = response.generations[0].text.strip()
        cache_answer(prompt, answer)
        return jsonify({"answer": answer, "cached": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# FAQ question
faq_data, faq_vectors = build_faq_index()


@ai_bp.route("/api/support", methods=["POST"])
def support():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        similar_faqs = search_similiar_faq(faq_data, faq_vectors, question)
        context = "\n".join(
            [f"Q: {f['question']}\nA: {f['answer']}" for f in similar_faqs]
        )
        prompt = f"""Answer the user's question using ONLY the information provided in the FAQ context below. Stay as close as possible to the original FAQ answer.
        Do not elaborate or add extra information unless the user's question specifically asks for more details. FAQ Context: {context}
        User Question: {question} Answer (stay close to the FAQ answer):"""
        response = co.generate(model="command", prompt=prompt, max_tokens=100)
        answer = response.generations[0].text.strip()
        return jsonify({"answer": answer, "context_used": context})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# SQL Database
DB_PATH = "mydb.sqlite"

SCHEMA = """
Table users:
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- signup_data (TEXT)
- email (TEXT)
"""


def generate_sql_query(question, schema):
    prompt = f"""You are an AI that converts natural language questions into valid SQLite SQL queries.
Return only the SQL query with no explanation or extra text.

SCHEMA:
{schema}

Question: {question}
SQL:"""
    response = co.generate(
        model="command",
        prompt=prompt,
        temperature=0,
        stop_sequences=["\n\n"],
    )
    query = response.generations[0].text.strip()
    return query


def execute_sql(sql_query):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        columns = [desc[0] for desc in c.description]
        results = [dict(zip(columns, row)) for row in rows]
        return results
    except Exception as e:
        return {"error": str(e)}
