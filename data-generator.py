import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import random
import json
import socket
import ssl
from datetime import datetime
import websocket

class SensorSimulator:
    def __init__(self, update_callback, send_ws_callback):
        self.running = False
        self.paused = False
        self.thread = None
        self.update_callback = update_callback
        self.send_ws_callback = send_ws_callback
        self.last_data = None
        self.start_time = None
        self.data_counter = 0

    def _generate_sensor_data(self):
        return {
            "timestamp": datetime.utcnow().isoformat(),
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

    def _run(self):
        while self.running:
            if not self.paused:
                data = self._generate_sensor_data()
                self.update_callback(self.last_data, data, self.get_time_lapse(), self.data_counter)
                self.send_ws_callback(data)
                self.last_data = data
                self.data_counter += 1
            time.sleep(0.5)

    def start(self):
        self.start_time = time.time()
        self.data_counter = 0
        if not self.running:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def pause(self):
        self.paused = True

    def reset(self):
        self.running = False
        self.paused = False
        self.last_data = None
        self.start_time = None
        self.data_counter = 0
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
        self.root.title("GY-91 ESP WiFi & WebSocket Simulator")

        self.ws = None
        self.ws_connected = False

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        # === Bagian Teks Output
        self.text_area = scrolledtext.ScrolledText(main_frame, width=70, height=20, state='disabled', wrap=tk.WORD)
        self.text_area.pack()

        # === Status
        self.network_status = tk.Label(root, text="Checking network...", fg="blue")
        self.network_status.pack()

        self.ws_status = tk.Label(root, text="WebSocket: Disconnected", fg="red")
        self.ws_status.pack()

        # === Input WebSocket
        input_frame = tk.Frame(root)
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Host:").grid(row=0, column=0)
        self.host_entry = tk.Entry(input_frame, width=30)
        self.host_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="Port:").grid(row=0, column=2)
        self.port_entry = tk.Entry(input_frame, width=5)
        self.port_entry.grid(row=0, column=3)

        tk.Label(input_frame, text="Path:").grid(row=0, column=4)
        self.path_entry = tk.Entry(input_frame, width=20)
        self.path_entry.grid(row=0, column=5)

        self.use_ssl = tk.BooleanVar()
        tk.Radiobutton(input_frame, text="SSL", variable=self.use_ssl, value=True).grid(row=1, column=1)
        tk.Radiobutton(input_frame, text="Non-SSL", variable=self.use_ssl, value=False).grid(row=1, column=2)

        self.connect_btn = tk.Button(input_frame, text="Connect WebSocket", command=self.connect_websocket)
        self.connect_btn.grid(row=1, column=4, columnspan=2)

        # === Tombol utama
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        self.generate_btn = tk.Button(control_frame, text="Generate", width=20, command=self.toggle_generate)
        self.generate_btn.grid(row=0, column=0, padx=10)

        self.reset_btn = tk.Button(control_frame, text="Reset", width=20, command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=10)

        self.timelapse_label = tk.Label(control_frame, text="Timelapse: 00:00:00.000")
        self.timelapse_label.grid(row=1, column=0, columnspan=2)

        self.data_generated_label = tk.Label(control_frame, text="Data Generated: 0")
        self.data_generated_label.grid(row=2, column=0, columnspan=2)

        # === Inisialisasi Simulator
        self.simulator = SensorSimulator(self.update_output, self.send_to_websocket)
        self.check_network_status()

    def check_network_status(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            ssid = self.get_ssid() or "Unknown"
            self.network_status.config(text=f"Connected to network: {ssid}, IP: {local_ip}", fg="green")
        except:
            self.network_status.config(text="Disconnected from network", fg="red")

    def get_ssid(self):
        try:
            import subprocess
            result = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            for line in result.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
        except:
            return None

    def connect_websocket(self):
        host = self.host_entry.get()
        port = self.port_entry.get()
        path = self.path_entry.get()
        use_ssl = self.use_ssl.get()

        def _connect():
            scheme = "wss" if use_ssl else "ws"
            try:
                ip = socket.gethostbyname(host)
                url = f"{scheme}://{ip}:{port}{path}"

                self.ws = websocket.WebSocket()
                if use_ssl:
                    self.ws.connect(url, sslopt={"cert_reqs": ssl.CERT_NONE})
                else:
                    self.ws.connect(url)

                self.ws_connected = True
                self.ws_status.config(text="WebSocket: Connected", fg="green")
            except Exception as e:
                self.ws_connected = False
                self.ws_status.config(text=f"WebSocket: Disconnected", fg="red")
                messagebox.showerror("Connection Failed", f"Error: {e}")

        threading.Thread(target=_connect).start()

    def send_to_websocket(self, data):
        if self.ws_connected and self.ws:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                print("Send error:", e)
                self.ws_connected = False
                self.ws_status.config(text="WebSocket: Disconnected", fg="red")

    def update_output(self, prev_data, new_data, timelapse, data_count):
        output = f"""\
Timestamp: {new_data['timestamp']}
Accelerometer: x={new_data['accelerometer']['x']} y={new_data['accelerometer']['y']} z={new_data['accelerometer']['z']}
Gyroscope:     x={new_data['gyroscope']['x']} y={new_data['gyroscope']['y']} z={new_data['gyroscope']['z']}
Magnetometer:  x={new_data['magnetometer']['x']} y={new_data['magnetometer']['y']} z={new_data['magnetometer']['z']}
---"""
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, output + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

        self.timelapse_label.config(text=f"Timelapse: {timelapse}")
        self.data_generated_label.config(text=f"Data Generated: {data_count}")

    def toggle_generate(self):
        if not self.simulator.running:
            self.simulator.start()
            self.generate_btn.config(text="Pause")
        else:
            self.simulator.pause()
            self.simulator.running = False
            self.generate_btn.config(text="Generate")

    def reset(self):
        self.simulator.reset()
        self.generate_btn.config(text="Generate")
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state="disabled")
        self.data_generated_label.config(text="Data Generated: 0")
        self.timelapse_label.config(text="Timelapse: 00:00:00.000")


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.mainloop()
