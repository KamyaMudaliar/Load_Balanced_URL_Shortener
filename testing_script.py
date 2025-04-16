import requests
import random
import threading
import json

URL = "http://short.local/shorten"
OUTPUT_FILE = "responses.txt"
NUM_REQUESTS = 1000000  
THREADS = 10       

lock = threading.Lock()  

def make_request():
    long_url = f"https://example.com/page{random.randint(1, 1000000)}"
    payload = {"url": long_url}

    try:
        response = requests.post(URL, json=payload)
        response_data = response.json()

  
        with lock:
            with open(OUTPUT_FILE, "a") as f:
                f.write(json.dumps({"request": payload, "response": response_data}) + "\n")

        print(f"Shortened: {long_url} -> {response_data}")

    except Exception as e:
        print(f"Error: {e}")


threads = []
for _ in range(NUM_REQUESTS // THREADS):
    t = threading.Thread(target=make_request)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"\n✅ Done! Check '{OUTPUT_FILE}' for results.")
