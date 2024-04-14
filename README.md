# Raspberry Pi DHT11/DHT22 Reader

This project has been tested on a Raspberry Pi 5, with both Ubuntu Server version 23.10 (64-bit) and Raspberry Pi OS (64-bit) (Debian version: 12) operating systems.  

Python version used: 3.11.6  
gpiod version used: 2.1.3, available at https://pypi.org/project/gpiod/

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
