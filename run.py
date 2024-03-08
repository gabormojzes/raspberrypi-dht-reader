import sys
import time
from dht_reader.dht_reader import DHTReader

# Check if the correct number of arguments is provided
if len(sys.argv) != 5:
    print('Usage: python run.py <dht_type> <chip_path> <line_offset> <sensor_reading_delay>')
    sys.exit(1)

# DHT sensor type
dht_type = sys.argv[1].upper()
# Check if the provided DHT sensor type is supported
if dht_type not in ['DHT11', 'DHT22']:
    print('Error: Unsupported DHT sensor type. Please choose either DHT11 or DHT22')
    sys.exit(1)

# Path to the GPIO chip
chip_path = sys.argv[2]

# Offset of the GPIO line connected to the sensor
try:
    line_offset = int(sys.argv[3])
except ValueError:
    print('Error: Line offset must be an integer')
    sys.exit(1)

# Delay between sensor readings in seconds
try:
    sensor_reading_delay = float(sys.argv[4])
    if dht_type == 'DHT11' and sensor_reading_delay < 1:
        print('Error: Sensor reading delay cannot be less than 1 second')
        sys.exit(1)
    elif dht_type == 'DHT22' and sensor_reading_delay < 2:
        print('Error: Sensor reading delay cannot be less than 2 seconds')
        sys.exit(1)
except ValueError:
    print('Error: Sensor reading delay must be a float')
    sys.exit(1)

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
