import logging
import cohere
import os
from flask import Flask, json, request, render_template, jsonify
from dotenv import load_dotenv
load_dotenv()
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram
from flask import Blueprint
from ai_routes import ai_bp

api = os.getenv("COHERE_API_KEY")
client = cohere.Client(api)

app = Flask(__name__)
app.register_blueprint(ai_bp)

swagger = Swagger(app)

# Enhanced metrics setup
metrics = PrometheusMetrics(app)

# Add custom metrics
api_calls_counter = Counter(
    "api_calls_total", "Total API calls", ["method", "endpoint"]
)
cohere_api_calls = Counter("cohere_api_calls_total", "Total Cohere API calls")
cohere_api_duration = Histogram(
    "cohere_api_duration_seconds", "Time spent calling Cohere API"
)

app.logger.info("Flask started")


@app.route("/")
def index():
    return render_template("index.html", project_name="BizBuddy")


@app.route("/faq")
def faq():
    return render_template("faq.html")


# Custom metric for tracking AI requests
@app.before_request
def before_request():
    if request.endpoint:
        api_calls_counter.labels(method=request.method, endpoint=request.endpoint).inc()


# Update your cohere_client function to include metrics:
def cohere_client(prompt):
    cohere_api_calls.inc()
    with cohere_api_duration.time():
        try:
            response = client.chat(
                model="command-light",
                message=prompt,
                max_tokens=50,
                temperature=0.7,
            )
            text = response.text.strip()
            logging.info(f"Cohere API is called with prompt: {prompt}")
            logging.info(f"Cohere response: {text}")
            return text
        except Exception as e:
            logging.error(f"Error calling Cohere API: {e}")
            return None


@app.route("/api/ask", methods=["POST"])
def ask():
    ai_bp.ask()

@app.route("/label-3d")
def label():
    return render_template("3d_asset.html")


@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"mssg": "Hello, founders!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)  # Allow container access