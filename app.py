from flask import Flask, request, jsonify, redirect
from flask_cors import CORS  # Import CORS
import redis
import hashlib
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

r = redis.Redis(host='redis-service', port=6379, decode_responses=True)

BASE_URL = "http://127.0.0.1:5000/"

# Prometheus Metrics
URL_SHORTENED = Counter("url_shortened_total", "Total number of URLs shortened")
URL_REDIRECTED = Counter("url_redirected_total", "Total number of redirects")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])

def shorten_url(long_url):
    hash_object = hashlib.md5(long_url.encode())
    short_code = hash_object.hexdigest()[:6]  # First 6 characters of the hash
    r.set(short_code, long_url)
    URL_SHORTENED.inc()  # Increment the counter for shortened URLs
    return short_code

@app.route('/shorten', methods=['POST'])
def shorten():
    start_time = time.time()
    data = request.get_json()
    long_url = data.get('url')
    if not long_url:
        return jsonify({"error": "URL is required"}), 400
    short_code = shorten_url(long_url)
    REQUEST_LATENCY.labels("/shorten").observe(time.time() - start_time)  # Record request latency
    return jsonify({"short_url": BASE_URL + short_code})

@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    start_time = time.time()
    long_url = r.get(short_code)
    if not long_url:
        return jsonify({"error": "Short URL not found"}), 404
    URL_REDIRECTED.inc()  # Increment the counter for redirects
    REQUEST_LATENCY.labels("/<short_code>").observe(time.time() - start_time)  # Record latency
    return redirect(long_url)

@app.route('/metrics', methods=['GET'])
def metrics():
    """Expose Prometheus metrics"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    print("yoooooooo")