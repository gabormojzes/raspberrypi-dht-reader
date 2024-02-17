import time
import gpiod
from gpiod.line import Direction, Value


class DHT22Reader:
    """
    A class to read data from a DHT22 sensor using GPIO.

    Attributes:
        _PULSE_TIMEOUT_THRESHOLD (float): Timeout threshold for pulse reception (100 μs)
        _EXPECTED_PULSES (int): Expected number of pulses during data reception from DHT22 sensor
        _PULSE_DURATION_THRESHOLD (int): Threshold for pulse duration for binary conversion (50 μs)
    """

    _PULSE_TIMEOUT_THRESHOLD = 0.0001
    _EXPECTED_PULSES = 83
    _PULSE_DURATION_THRESHOLD = 50

    def __init__(self, chip_path: str, line_offset: int) -> None:
        """
        Initializes the DHT22Reader.

        Args:
            chip_path (str): The path to the GPIO chip.
            line_offset (int): The offset of the GPIO line.
        """
        self._chip_path = chip_path
        self._line_offset = line_offset

    def read_data(self) -> tuple[float, float, bool]:
        """
        Reads data from the DHT22 sensor.

        Returns:
            tuple: A tuple containing humidity, temperature, and a boolean indicating negative temperature.
        """
        with gpiod.request_lines(
            self._chip_path,
            consumer='DHT22',
            config={self._line_offset: gpiod.LineSettings(direction=Direction.OUTPUT)}
        ) as request:
            request.set_value(self._line_offset, Value.ACTIVE)
            time.sleep(0.5)  # Wait 500 ms

            # Send start signal to the sensor
            request.set_value(self._line_offset, Value.INACTIVE)
            time.sleep(0.02)  # Wait 20 ms

            request.set_value(self._line_offset, Value.ACTIVE)
            request.reconfigure_lines(
                config={self._line_offset: gpiod.LineSettings(direction=Direction.INPUT)}
            )
            # Delay to line up with the first ~80 μs low pulse from the DHT22 sensor
            time.sleep(0.000001)

            # Receive and process data
            data = self._receive_data(request)
            binary_data = self._convert_to_binary(data)
            self._validate_checksum(binary_data)

            humidity = self._get_humidity(binary_data)
            temperature, is_negative = self._get_temperature(binary_data)

            return humidity, temperature, is_negative

    def _receive_data(self, request: gpiod.LineRequest) -> list[float]:
        """
        Receives data from the DHT22 sensor.

        Args:
            request (gpiod.LineRequest): The GPIO line request object.

        Returns:
            list: A list containing pulse duration data.
        """
        data = [0] * self._EXPECTED_PULSES
        for i, _ in enumerate(data):
            pulse = [Value.INACTIVE, Value.ACTIVE][i % 2]
            start_time = time.monotonic()
            while request.get_value(self._line_offset) == pulse:
                if time.monotonic() - start_time > self._PULSE_TIMEOUT_THRESHOLD:
                    raise RuntimeError('Error: Pulse timeout')
            data[i] = time.monotonic() - start_time

        return data

    def _convert_to_binary(self, data: list[float]) -> list[int]:
        """
        Converts pulse duration data to binary.

        Args:
            data (list): A list containing pulse duration data.

        Returns:
            list: A list containing binary data.
        """
        # Convert high pulse durations to microseconds
        data = [duration * 10 ** 6 for duration in data[3::2]]
        # Translate time durations into binary representations
        # ~26-28 μs high pulse means "0" and ~70 μs high pulse means "1"
        return [1 if duration > self._PULSE_DURATION_THRESHOLD else 0 for duration in data]

    @staticmethod
    def _get_humidity(binary_data: list[int]) -> float:
        """
        Gets humidity from binary data.

        Args:
            data (list): A list containing binary data.

        Returns:
            float: The humidity value.
        """
        humidity_data = binary_data[0:16]  # Humidity is 2 bytes
        return int(''.join(map(str, humidity_data)), 2) / 10

    @staticmethod
    def _get_temperature(binary_data: list[int]) -> tuple[float, bool]:
        """
        Gets temperature from binary data.

        Args:
            binary_data (list): A list containing binary data.

        Returns:
            tuple: A tuple containing temperature and a boolean indicating negative temperature.
        """
        temperature_data = binary_data[16:32]  # Temperature is 2 bytes
        is_negative = temperature_data[0] == 1

        if is_negative:
            temperature_data[0] = 0

        temperature = int(''.join(map(str, temperature_data)), 2) / 10
        return temperature, is_negative

    @staticmethod
    def _validate_checksum(binary_data: list[int]) -> None:
        """
        Validates the checksum of the received data.

        Args:
            binary_data (list): A list containing binary data.

        Raises:
            RuntimeError: If the checksum is invalid.
        """
        received_checksum = ''.join(map(str, binary_data[32:40]))  # Checksum is 1 byte
        total_sum = sum(int(''.join(map(str, binary_data[i:i + 8])), 2) for i in range(0, 32, 8))
        calculated_checksum = format(total_sum & 0xFF, '08b')

        if calculated_checksum != received_checksum:
            raise RuntimeError('Error: Invalid checksum')
