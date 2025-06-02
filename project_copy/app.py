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

# Enhanced metrics setup - Force enable metrics
metrics = PrometheusMetrics(app)

# Add custom metrics
api_calls_counter = Counter(
    "api_calls_total", "Total API calls", ["method", "endpoint"]
)
cohere_api_calls = Counter("cohere_api_calls_total", "Total Cohere API calls")
cohere_api_duration = Histogram(
    "cohere_api_duration_seconds", "Time spent calling Cohere API"
)

# Set up logging
logging.basicConfig(level=logging.INFO)
app.logger.info("Flask started")


@app.route("/")
def index():
    return render_template("index.html", project_name="BizBuddy")


# @app.route("/api/ask")
# def ask():
# ai_bp.ask()


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/label-3d")
def label():
    return render_template("3d_asset.html")


@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"mssg": "Hello, founders!"})


# Debug endpoint to check metrics
@app.route("/debug/metrics")
def debug_metrics():
    return jsonify(
        {
            "metrics_enabled": hasattr(app, "prometheus_metrics"),
            "debug_mode": app.debug,
            "flask_env": os.getenv("FLASK_ENV", "development"),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
