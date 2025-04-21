import tkinter as tk
import json
import os
import random
import threading
import time
from datetime import datetime

class SensorSimulator:
    def __init__(self):
        self.running = False
        self.paused = False
        self.thread = None
        self.data_file = "sensor_data.json"

    def _generate_sensor_data(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "accelerometer": {
                "x": round(random.uniform(-2.0, 2.0), 3),
                "y": round(random.uniform(-2.0, 2.0), 3),
                "z": round(random.uniform(-2.0, 2.0), 3)
            },
            "gyroscope": {
                "x": round(random.uniform(-250, 250), 3),
                "y": round(random.uniform(-250, 250), 3),
                "z": round(random.uniform(-250, 250), 3)
            },
            "magnetometer": {
                "x": round(random.uniform(-4800, 4800), 3),
                "y": round(random.uniform(-4800, 4800), 3),
                "z": round(random.uniform(-4800, 4800), 3)
            }
        }

    def _save_data_to_json(self, data):
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump([data], f, indent=4)
        else:
            with open(self.data_file, "r+") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
                existing_data.append(data)
                f.seek(0)
                json.dump(existing_data, f, indent=4)

    def _run(self):
        while self.running:
            if not self.paused:
                data = self._generate_sensor_data()
                self._save_data_to_json(data)
            time.sleep(0.5)

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def pause(self):
        self.paused = True

    def continue_generate(self):
        self.paused = False

    def stop(self):
        self.running = False
        self.paused = False
        if self.thread:
            self.thread.join()

class SensorGUI:
    def __init__(self, root):
        self.simulator = SensorSimulator()
        self.root = root
        self.root.title("GY-91 Sensor Data Generator")

        self.start_btn_text = tk.StringVar()
        self.start_btn_text.set("Generate")

        self.start_button = tk.Button(root, textvariable=self.start_btn_text, width=20, command=self.toggle_start)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", width=20, command=self.stop)
        self.stop_button.pack(pady=5)

    def toggle_start(self):
        text = self.start_btn_text.get()
        if text == "Generate":
            self.simulator.start()
            self.start_btn_text.set("Pause")
        elif text == "Pause":
            self.simulator.pause()
            self.start_btn_text.set("Continue")
        elif text == "Continue":
            self.simulator.continue_generate()
            self.start_btn_text.set("Pause")

    def stop(self):
        self.simulator.stop()
        self.start_btn_text.set("Generate")

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.mainloop()
