"""
A library to interface Arduino Servos through serial connection
"""
import serial

class Arduino():
    """
    Models an Arduino connection
    """

    def __init__(self, serial_port='COM3', baud_rate=9600,
            read_timeout=5):
        """
        Initializes the serial connection to the Arduino board
        """
        self.conn = serial.Serial(serial_port, baud_rate)
        self.conn.timeout = read_timeout # Timeout for readline()
        print("Connection initiated")
     
    def stepper_write(self, digital_value1, digital_value2, digital_value3, digital_value4, digital_value5, digital_value6):
        """
        Writes the digital_value on pin_number
        Internally sends b'WS{pin_number}:{digital_value}' over the serial
        connection 
        """
        command = "<{},{},{},{},{},{}>".format(str(digital_value1),str(digital_value2), str(digital_value3), str(digital_value4), str(digital_value5), str(digital_value6)).encode()
        self.conn.write(command)

    def close(self):
        """
        To ensure we are properly closing our connection to the
        Arduino device. 
        """
        self.conn.close()
        print("Connection to Arduino closed")