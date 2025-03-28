import requests
import random
import threading
import json

URL = "http://localhost:5000/shorten"
OUTPUT_FILE = "responses.txt"
NUM_REQUESTS = 1000000  # Change this to control the number of requests
THREADS = 10        # Number of concurrent threads

lock = threading.Lock()  # Prevents file write conflicts

def make_request():
    long_url = f"https://example.com/page{random.randint(1, 1000000)}"
    payload = {"url": long_url}

    try:
        response = requests.post(URL, json=payload)
        response_data = response.json()

        # Write to file safely
        with lock:
            with open(OUTPUT_FILE, "a") as f:
                f.write(json.dumps({"request": payload, "response": response_data}) + "\n")

        print(f"Shortened: {long_url} -> {response_data}")

    except Exception as e:
        print(f"Error: {e}")

# Start multiple threads to simulate load
threads = []
for _ in range(NUM_REQUESTS // THREADS):
    t = threading.Thread(target=make_request)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"\n✅ Done! Check '{OUTPUT_FILE}' for results.")
