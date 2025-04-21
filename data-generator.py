import tkinter as tk
from tkinter import scrolledtext
import json
import os
import random
import threading
import time
from datetime import datetime

class SensorSimulator:
    def __init__(self, update_callback):
        self.running = False
        self.paused = False
        self.thread = None
        self.data_file = "sensor_data.json"
        self.update_callback = update_callback
        self.last_data = None

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
                self.update_callback(self.last_data, data)
                self.last_data = data
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
        self.root = root
        self.root.title("GY-91 Sensor Data Generator")

        # Frame utama horizontal
        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        # Area teks kiri
        self.text_area = scrolledtext.ScrolledText(main_frame, width=60, height=15, state='disabled', wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, padx=10)

        # Frame kanan untuk tombol
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.RIGHT)

        self.start_btn_text = tk.StringVar()
        self.start_btn_text.set("Generate")

        self.start_button = tk.Button(button_frame, textvariable=self.start_btn_text, width=20, command=self.toggle_start)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(button_frame, text="Stop", width=20, command=self.stop)
        self.stop_button.pack(pady=5)

        self.simulator = SensorSimulator(self.update_text_area)

    def format_sensor_output(self, data):
        if not data:
            return ["No previous data."]
        return [
            f"Timestamp: {data['timestamp']}",
            f"Accelerometer: x={data['accelerometer']['x']} y={data['accelerometer']['y']} z={data['accelerometer']['z']}",
            f"Gyroscope:     x={data['gyroscope']['x']} y={data['gyroscope']['y']} z={data['gyroscope']['z']}",
            f"Magnetometer:  x={data['magnetometer']['x']} y={data['magnetometer']['y']} z={data['magnetometer']['z']}"
        ]

    def update_text_area(self, previous_data, new_data):
        output_lines = []

        output_lines.append("")  # Line kosong
        output_lines += self.format_sensor_output(previous_data)
        output_lines += self.format_sensor_output(new_data)
        output_lines.append("Generating data...")

        text_to_display = "\n".join(output_lines[-7:])  # Hanya ambil 7 baris terakhir

        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, text_to_display + "\n\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

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
