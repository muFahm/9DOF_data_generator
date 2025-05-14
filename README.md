# GY-91 Sensor Data Generator

This project is a **sensor data generator** designed for use in a **welder monitoring system**. It simulates data from a **9-DOF (Degrees of Freedom) sensor** and generates random accelerometer, gyroscope, and magnetometer data. The data is saved in a **JSON** format, which can be used for further processing in applications like **welder activity monitoring** and analysis.

## Features

- **9-DOF Sensor Simulation**: Generates random sensor data for accelerometer, gyroscope, and magnetometer readings.
- **JSON Data Output**: The generated sensor data is saved in a JSON file format, which can be easily updated and read.
- **Start, Pause, and Continue**: You can start generating data, pause it, and resume data generation at any time.
- **Time Lapse**: Tracks the elapsed time since data generation started (in hours, minutes, seconds, and milliseconds).
- **Data Counter**: Keeps track of how many data entries have been generated.
- **Reset**: Resets both the time lapse and data counter to zero, clearing the generated data.

## Requirements

To run this program, you will need the following dependencies:

- Python 3.x
- Tkinter (Python GUI library)
- JSON (for data handling)

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/muFahm/9DOF_data_generator.git
cd sensor-data-generator
```

Make sure Python 3.x is installed on your system.

Note: `Tkinter` comes pre-installed with Python, so no extra installation is required for the GUI.

## Usage

To run the program:

1. **Run the Script**:

```bash
python sensor_data_generator.py
```

2. **Generate Data**: 
   - Click on the "Generate" button to start generating data. 
   - A file dialog will open, prompting you to save the JSON file where data will be stored.
   
3. **Pause/Continue**: 
   - Click "Pause" to stop generating data temporarily.
   - Click "Continue" to resume generating data from where it left off.

4. **Reset**:
   - Clicking "Reset" will reset the time lapse and data counter to 0 and clear the displayed data.

5. **View Time Lapse**: 
   - The time lapse will update continuously to reflect how long the data generation has been running.

6. **Data Generated Counter**: 
   - The number of generated data entries is displayed and updated as new data is created.

## Data Format

Each sensor data entry includes the following fields:

```json
{
  "timestamp": "2025-04-21T12:34:56.789Z",
  "accelerometer": {
    "x": 1.234,
    "y": -0.456,
    "z": 0.789
  },
  "gyroscope": {
    "x": -100.5,
    "y": 200.3,
    "z": -150.2
  },
  "magnetometer": {
    "x": 3200.5,
    "y": -3100.1,
    "z": 3300.7
  }
}
```

- **Timestamp**: The time when the data was generated.
- **Accelerometer**: Simulated accelerometer data (x, y, z).
- **Gyroscope**: Simulated gyroscope data (x, y, z).
- **Magnetometer**: Simulated magnetometer data (x, y, z).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to fork this project, submit issues, or send pull requests. Contributions are welcome!

For more information or questions, please open an issue or contact the repository maintainer.
