import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
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
        self.data_file = None
        self.save_to_file = False  # Tambahan flag baru
        self.update_callback = update_callback
        self.last_data = None
        self.start_time = None
        self.data_counter = 0

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
        if not self.save_to_file or not self.data_file:
            return
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
                self.data_counter += 1
                self.update_callback(self.last_data, data, self.get_time_lapse(), self.data_counter)
                self.last_data = data
            time.sleep(0.5)

    def start(self, save_to_file=False, file_path=None):
        self.save_to_file = save_to_file
        self.data_file = file_path
        self.start_time = time.time()
        self.data_counter = 0
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def pause(self):
        self.paused = True

    def continue_generate(self):
        self.paused = False

    def reset(self):
        self.running = False
        self.paused = False
        self.last_data = None
        self.data_file = None
        self.start_time = None
        self.data_counter = 0
        self.save_to_file = False
        if self.thread:
            self.thread.join()

    def get_time_lapse(self):
        if not self.start_time:
            return "0:00:00.000"
        elapsed = time.time() - self.start_time
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = int((elapsed % 1) * 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

class SensorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GY-91 Sensor Data Generator")

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        self.text_area = scrolledtext.ScrolledText(main_frame, width=60, height=15, state='disabled', wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.RIGHT)

        self.start_btn_text = tk.StringVar()
        self.start_btn_text.set("Generate")

        self.start_button = tk.Button(button_frame, textvariable=self.start_btn_text, width=20, command=self.toggle_start)
        self.start_button.pack(pady=10)

        self.reset_button = tk.Button(button_frame, text="Reset", width=20, command=self.reset)
        self.reset_button.pack(pady=5)

        self.timelapse_label = tk.Label(button_frame, text="Timelapse: 00:00:00.000", width=20)
        self.timelapse_label.pack(pady=5)

        self.data_generated_label = tk.Label(button_frame, text="Data Generated: 0", width=20)
        self.data_generated_label.pack(pady=5)

        # Label tambahan untuk "Saved"
        self.saved_label = tk.Label(button_frame, text="", width=20, fg="green")
        self.saved_label.pack(pady=5)

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

    def update_text_area(self, previous_data, new_data, timelapse, data_count):
        output_lines = []

        output_lines.append("")
        output_lines += self.format_sensor_output(previous_data)
        output_lines += self.format_sensor_output(new_data)
        output_lines.append("Generating data...")

        text_to_display = "\n".join(output_lines[-7:])

        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, text_to_display + "\n\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

        self.timelapse_label.config(text=f"Timelapse: {timelapse}")
        self.data_generated_label.config(text=f"Data Generated: {data_count}")

    def toggle_start(self):
        text = self.start_btn_text.get()
        if text == "Generate":
            answer = messagebox.askyesno("Save JSON?", "Simpan data JSON?")
            if answer:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")],
                    title="Save sensor data as..."
                )
                if file_path:
                    self.simulator.start(save_to_file=True, file_path=file_path)
                    self.saved_label.config(text="Saved")  # Munculkan label Saved
                    self.start_btn_text.set("Pause")
            else:
                self.simulator.start(save_to_file=False)
                self.saved_label.config(text="")  # Kosongkan label Saved
                self.start_btn_text.set("Pause")
        elif text == "Pause":
            self.simulator.pause()
            self.start_btn_text.set("Continue")
        elif text == "Continue":
            self.simulator.continue_generate()
            self.start_btn_text.set("Pause")

    def reset(self):
        self.simulator.reset()
        self.text_area.config(state='normal')
        self.text_area.delete('1.0', tk.END)
        self.text_area.config(state='disabled')
        self.start_btn_text.set("Generate")
        self.timelapse_label.config(text="Timelapse: 00:00:00.000")
        self.data_generated_label.config(text="Data Generated: 0")
        self.saved_label.config(text="")  # Reset label Saved juga

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.mainloop()
