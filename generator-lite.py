import json
import time
import random
from datetime import datetime
from websocket import create_connection

# Ganti alamat ini sesuai dengan endpoint WebSocket Django kamu
# Jika lokal: "ws://localhost:8000/ws/data/"
ws_url = "ws://localhost:8000/ws/data/"

def generate_dummy_data():
    return {
        "gx": random.randint(-15000, 15000),
        "gy": random.randint(-15000, 15000),
        "gz": random.randint(-15000, 15000),
        "ax": round(random.uniform(-12.0, 2.0), 6),
        "ay": round(random.uniform(0.0, 6.0), 6),
        "az": round(random.uniform(0.0, 10.0), 6),
        "mx": round(random.uniform(-1.0, 1.0), 6),
        "my": round(random.uniform(-1.0, 1.0), 6),
        "mz": round(random.uniform(-1.0, 1.0), 6),
        "timestamp": datetime.now().isoformat()
    }

def main():
    try:
        ws = create_connection(ws_url)
        print("Connected to Django WebSocket")

        while True:
            data = generate_dummy_data()
            json_data = json.dumps(data)
            ws.send(json_data)
            print("Sent:", json_data)
            time.sleep(1)  # kirim tiap 1 detik, 0.04=25data/detik

    except Exception as e:

        print("Error:", e)

    finally:
        ws.close()

if __name__ == "__main__":
    main()
