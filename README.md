# Raspberry Pi DHT22 Reader

Tested on a Raspberry Pi 5 running Ubuntu Server version 23.10.


### How to use
```
git clone https://github.com/gabormojzes/raspberrypi-dht22-reader.git
cd raspberrypi-dht22-reader
python3 -m venv venv
source venv/bin/activate

pip install gpiod
python run.py /dev/gpiochip4 4 2
```
python run.py <chip_path> <line_offset> <sensor_reading_delay>

### Example output
```
Humidity: 60.1% Temperature: 21.5°C
```
