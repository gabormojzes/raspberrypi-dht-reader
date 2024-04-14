import sys
import time
from dht_reader.dht_reader import DHTReader

# Check if the correct number of arguments is provided
if len(sys.argv) != 5:
    print('Usage: python run.py <dht_type> <chip_path> <line_offset> <sensor_reading_delay>')
    sys.exit(1)

# DHT sensor type
dht_type = sys.argv[1]
# Path to the GPIO chip
chip_path = sys.argv[2]
# Offset of the GPIO line
line_offset = int(sys.argv[3])
# Delay between sensor readings in seconds
sensor_reading_delay = float(sys.argv[4])

dht_reader = DHTReader(dht_type, chip_path, line_offset)

while True:
    try:
        # Read sensor data
        humidity, temperature, is_negative = dht_reader.read_data()
        temperature_sign = '-' if is_negative else ''

        print(f'Humidity: {humidity}% Temperature: {temperature_sign}{temperature}°C')

    except Exception as e:
        print(str(e))
    finally:
        time.sleep(sensor_reading_delay)
