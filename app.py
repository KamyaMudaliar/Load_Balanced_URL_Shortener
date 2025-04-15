from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import redis
import hashlib
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers="*", supports_credentials=True)



# Connect to Redis service in Kubernetes
r = redis.Redis(host='redis-service', port=6379, decode_responses=True)

# # Prometheus Metrics (optional)
# URL_SHORTENED = Counter("url_shortened_total", "Total number of URLs shortened")
# URL_REDIRECTED = Counter("url_redirected_total", "Total number of redirects")
# REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])

def shorten_url(long_url):
    hash_object = hashlib.md5(long_url.encode())
    short_code = hash_object.hexdigest()[:6]
    r.set(short_code, long_url)
    # URL_SHORTENED.inc()
    return short_code

@app.route('/shorten', methods=['POST'])
def shorten():
    start_time = time.time()
    data = request.get_json()
    long_url = data.get('url')
    if not long_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = shorten_url(long_url)

    # Use host + port from the request (works with Minikube's forwarded port)
    short_url = request.host_url.rstrip('/') + '/' + short_code

    # REQUEST_LATENCY.labels("/shorten").observe(time.time() - start_time)
    return jsonify({"short_url": short_url})

@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    start_time = time.time()
    long_url = r.get(short_code)
    if not long_url:
        return jsonify({"error": "Short URL not found"}), 404

    # URL_REDIRECTED.inc()
    # REQUEST_LATENCY.labels("/<short_code>").observe(time.time() - start_time)
    return redirect(long_url)

# @app.route('/metrics', methods=['GET'])
# def metrics():
#     return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
