# Raspberry Pi DHT11/DHT22 Reader

Tested on a Raspberry Pi 5 running Ubuntu Server version 23.10.

### How to use
```
git clone https://github.com/gabormojzes/raspberrypi-dht-reader.git
cd raspberrypi-dht-reader
python3 -m venv venv
source venv/bin/activate

pip install gpiod
python run.py DHT22 /dev/gpiochip4 4 2
```
python run.py <dht_type> <chip_path> <line_offset> <sensor_reading_delay>

### Example output
```
Humidity: 60.1% Temperature: 21.5°C
```
