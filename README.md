# Raspberry Pi DHT11/DHT22 Reader

A Python class for reading temperature and humidity data from DHT11/DHT22 sensors via GPIO.

This project has been tested on a Raspberry Pi 5 running Ubuntu Server 24.04.3 LTS (64-bit).  
Python version used: 3.12.3  
gpiod version used: 2.4.0, available at https://pypi.org/project/gpiod/

### How to use
```
git clone https://github.com/gabormojzes/raspberrypi-dht-reader.git
cd raspberrypi-dht-reader
python3 -m venv venv
source venv/bin/activate

pip install gpiod
python run.py DHT22 /dev/gpiochip4 4 2
```
#### Command format
```
python run.py <dht_type> <chip_path> <line_offset> <sensor_reading_delay>
```

### Sample output
```
Humidity: 60.1% Temperature: 22.4°C 72.3°F
```
