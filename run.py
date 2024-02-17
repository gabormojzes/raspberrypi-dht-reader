import sys
import time
from dht22_reader.dht22_reader import DHT22Reader

# Check if the correct number of arguments is provided
if len(sys.argv) != 4:
    print('Usage: python start.py <chip_path> <line_offset> <sensor_reading_delay>')
    sys.exit(1)

# Path to the GPIO chip
chip_path = sys.argv[1]

# Offset of the GPIO line connected to the sensor
try:
    line_offset = int(sys.argv[2])
except ValueError:
    print('Error: Line offset must be an integer')
    sys.exit(1)

# Delay between sensor readings in seconds (2 seconds per read according to datasheet)
try:
    sensor_reading_delay = float(sys.argv[3])
    if sensor_reading_delay < 2:
        print('Error: Sensor reading delay cannot be less than 2 seconds')
        sys.exit(1)
except ValueError:
    print('Error: Sensor reading delay must be a float')
    sys.exit(1)

dht22_reader = DHT22Reader(chip_path, line_offset)

while True:
    try:
        # Read sensor data
        humidity, temperature, is_negative = dht22_reader.read_data()
        temperature_prefix = '-' if is_negative else ''

        print(f'Humidity: {humidity}% Temperature: {temperature_prefix}{temperature}°C')

    except Exception as e:
        print(str(e))
    finally:
        time.sleep(sensor_reading_delay)
