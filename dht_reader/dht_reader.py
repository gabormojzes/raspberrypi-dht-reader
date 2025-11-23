import array
import time
import gpiod
from gpiod.line import Direction, Value


class DHTReader:
    """
    A class to read data from a DHT sensor using GPIO.

    Attributes:
        _PULSE_TIMEOUT_THRESHOLD (float): Timeout threshold for pulse reception (100 μs)
        _EXPECTED_PULSES (int): Expected number of pulses during data reception from DHT sensor
        _PULSE_DURATION_THRESHOLD (int): Threshold for pulse duration for binary conversion (50 μs)
        _SUPPORTED_SENSOR_TYPES (set[str]): List of supported DHT sensor types.
        _SENSOR_MIN_DELAY (dict[str, int]): Minimum required delay between readings (seconds).
    """
    _PULSE_TIMEOUT_THRESHOLD = 0.0001
    _EXPECTED_PULSES = 83
    _PULSE_DURATION_THRESHOLD = 50
    _SUPPORTED_SENSOR_TYPES = {'DHT11', 'DHT22'}
    _SENSOR_MIN_DELAY = {
        'DHT11': 1,
        'DHT22': 2,
    }

    def __init__(self, dht_type: str, chip_path: str, line_offset: int) -> None:
        """
        Initializes the DHTReader.

        Args:
            dht_type (str): The type of the DHT sensor.
            chip_path (str): The path to the GPIO chip.
            line_offset (int): The offset of the GPIO line.

        Raises:
            ValueError: If the DHT type is not supported.
        """
        dht_type = dht_type.upper()
        if dht_type not in self._SUPPORTED_SENSOR_TYPES:
            raise ValueError(f"Error: Unsupported DHT sensor type: {dht_type}. Supported: {', '.join(self._SUPPORTED_SENSOR_TYPES)}")

        self._dht_type = dht_type
        self._chip_path = chip_path
        self._line_offset = line_offset
        self._last_called = 0

    def read_data(self) -> tuple[float, float, float]:
        """
        Reads data from the DHT sensor.

        Returns:
            tuple[float, float, float]: A tuple containing humidity, temperature in Celsius
            and temperature in Fahrenheit.
        """
        self._check_elapsed_time_between_readings()

        with gpiod.request_lines(
            self._chip_path,
            consumer=self._dht_type,
            config={self._line_offset: gpiod.LineSettings(direction=Direction.OUTPUT)}
        ) as request:
            self._send_start_signal(request)
            pulses = self._receive_data(request)
            high_pulses = self._extract_high_pulses(pulses)
            binary_data = self._convert_to_binary(high_pulses)

            self._validate_checksum(binary_data)

            humidity = self._get_humidity(binary_data)
            temperature_c = self._get_temperature(binary_data)
            temperature_f = self._convert_celsius_to_fahrenheit(temperature_c)

            return humidity, temperature_c, temperature_f

    def _send_start_signal(self, request: gpiod.LineRequest) -> None:
        """
        Sends the start signal to the sensor.

        Args:
            request (gpiod.LineRequest): The GPIO line request object.
        """
        request.set_value(self._line_offset, Value.ACTIVE)
        time.sleep(0.5)  # Wait 500 ms

        # Send start signal to the sensor
        request.set_value(self._line_offset, Value.INACTIVE)
        if self._dht_type == 'DHT11':
            time.sleep(0.018)  # Wait 18 ms
        elif self._dht_type == 'DHT22':
            time.sleep(0.001)  # Wait 1 ms

        request.set_value(self._line_offset, Value.ACTIVE)
        # Configure the GPIO line for input mode
        request.reconfigure_lines(
            config={self._line_offset: gpiod.LineSettings(direction=Direction.INPUT)}
        )

    def _receive_data(self, request: gpiod.LineRequest) -> list[float]:
        """
        Receives data from the DHT sensor.

        Args:
            request (gpiod.LineRequest): The GPIO line request object.

        Returns:
            list[float]: A list containing pulse duration data.
        """
        pulses = [0.0] * self._EXPECTED_PULSES
        for i, _ in enumerate(pulses):
            pulse = [Value.INACTIVE, Value.ACTIVE][i % 2]
            start_time = time.monotonic()
            while request.get_value(self._line_offset) == pulse:
                if time.monotonic() - start_time > self._PULSE_TIMEOUT_THRESHOLD:
                    raise RuntimeError('Error: Pulse timeout.')
            pulses[i] = time.monotonic() - start_time

        return pulses

    @staticmethod
    def _extract_high_pulses(pulses: list[float]) -> list[float]:
        """
        Extracts the durations of high pulses from a list of pulse durations.

        Args:
            pulses (list[float]): A list of pulse durations in seconds.

        Returns:
            list[float]: A list of high pulse durations in microseconds.
        """
        return [duration * (10 ** 6) for duration in pulses[3::2]]

    def _convert_to_binary(self, pulses: list[float]) -> array.array:
        """
        Converts high pulse duration data to binary.

        Args:
            pulses (list[float]): A list containing high pulse duration data.

        Returns:
            array.array: A list containing binary data.
        """
        binary_data = array.array('B')
        for start in range(0, 40, 8):
            binary = 0
            for i in range(start, start + 8):
                # ~26-28 μs high pulse means "0" and a ~70 μs high pulse means "1".
                bit = 1 if pulses[i] > self._PULSE_DURATION_THRESHOLD else 0
                binary = binary << 1 | bit
            binary_data.append(binary)

        return binary_data

    def _get_humidity(self, binary_data: array.array) -> float:
        """
        Gets humidity from binary data.

        Args:
            binary_data (array.array): A list containing binary data.

        Returns:
            float: The humidity value.
        """
        # Humidity is 2 bytes
        if self._dht_type == 'DHT11':
            humidity = binary_data[0] + (binary_data[1] / 10)
        elif self._dht_type == 'DHT22':
            humidity = ((binary_data[0] << 8) | binary_data[1]) / 10

        return humidity

    def _get_temperature(self, binary_data: array.array) -> float:
        """
        Gets temperature from binary data.

        Args:
            binary_data (array.array): A list containing binary data.

        Returns:
            float: Temperature value in Celsius.
        """
        # Temperature is 2 bytes
        if self._dht_type == 'DHT11':
            temperature = binary_data[2] + (binary_data[3] / 10)
        elif self._dht_type == 'DHT22':
            temperature = (((binary_data[2] & 0x7F) << 8) | binary_data[3]) / 10
            is_negative = bool(binary_data[2] & 0x80)
            if is_negative:
                temperature = -temperature

        return temperature

    @staticmethod
    def _validate_checksum(binary_data: array.array) -> None:
        """
        Validates the checksum of the received data.

        Args:
            binary_data (array.array): A list containing binary data.

        Raises:
            RuntimeError: If the checksum is invalid.
        """
        # Checksum is 1 byte
        received_checksum = binary_data[4]
        calculated_checksum = sum(binary_data[:4]) & 0xFF

        if calculated_checksum != received_checksum:
            raise RuntimeError('Error: Invalid checksum.')

    def _check_elapsed_time_between_readings(self) -> None:
        """
        Checks elapsed time between readings.

        Raises:
            ValueError: If the elapsed time between readings is less
            than the required minimum for the specified sensor type.
                - For DHT11 sensor, the minimum elapsed time is 1 second.
                - For DHT22 sensor, the minimum elapsed time is 2 seconds.
        """
        elapsed_time = time.monotonic() - self._last_called
        min_time = self._SENSOR_MIN_DELAY[self._dht_type]

        if elapsed_time < min_time:
            raise ValueError(f"Error: Elapsed time between readings must be at least {min_time} seconds for {self._dht_type}.")

        self._last_called = time.monotonic()

    @staticmethod
    def _convert_celsius_to_fahrenheit(temperature_c: float) -> float:
        """
        Converts temperature from Celsius to Fahrenheit.

        Args:
            temperature_c (float): Temperature in Celsius to be converted.

        Returns:
            float: Temperature converted to Fahrenheit.
        """
        return (temperature_c * 1.8) + 32
