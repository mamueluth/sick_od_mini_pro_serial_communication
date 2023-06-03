import serial
import sys

# Configure serial communication
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Replace with the appropriate serial port
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_NONE,
    timeout=1
    # Set an appropriate timeout value
)

# Constants
STX = b'\x02'  # STX marker (hex code 02)
ETX = b'\x03'  # ETX marker (hex code 03)

# Helper function to calculate BCC
def calculate_bcc(data):
    bcc = 0
    print(f"bcc:={bcc}")
    for bit in data:
        bcc ^= bit
        print(f"bcc:={bcc}")
    print(f"full bcc:={bcc}")
    return bcc.to_bytes(1, byteorder='big')


def send_read_sensor_value():
    packet = bytearray()
    packet.append(0x02)
    packet.append(0x43)
    packet.append(0xb0)
    packet.append(0x01)
    packet.append(0x03)
    packet.append(0xf2)
    command = bytes(packet)
    #binary_command = bin(int.from_bytes(command, 'big'))
    #print(command)
    ser.setRTS(True)
    # write and wait for data to be written
    #print(ser.write(command))
    ser.write(command)
    ser.flush()
    ser.setRTS(False)


# Function to send data
def send_data(command, data1, data2):
    # Assemble the transmission frame
    print(f"command:={command}, data1:={data1}, data2:={data2}")
    transmission_frame = STX + command + data1 + data2 + ETX
    print(f"frame:={transmission_frame}")
    # Calculate and append BCC
    bcc = calculate_bcc(transmission_frame)
    print(f"bcc:={bcc}")
    transmission_frame += bcc
    print(f"full_frame:={transmission_frame}")
    # Send the frame
    ser.write(transmission_frame)

# Function to receive data
def receive_data():
    # Wait for STX marker
    while True:
        send_read_sensor_value()

        if ser.read(1) == STX:
                frame = ser.read(5)
                print(f"received:{frame}")

    # Read the remaining frame
    frame = ser.read(6)  # 6 is the total length of the frame without BCC

    # Extract the fields
    ack = frame[0:3]
    response1 = frame[3:4]
    response2 = frame[4:5]
    etx = frame[5:6]

    # Verify the ETX marker
    if etx == ETX:
        # Calculate and verify the BCC
        bcc = calculate_bcc(STX + ack + response1 + response2 + ETX)
        if bcc == frame[6:7]:
            return ack, response1, response2
        else:
            return STX + b'NAK' + b'ERROR' + b'\x00' + ETX + bcc
    else:
        return STX + b'NAK' + b'ERROR' + b'\x01' + ETX + bcc

# Example usage
command = b'\x43'
data1 = b'\xb0'
data2 = b'\x01'
if not ser.is_open:
    ser.open()
receive_data()
print(f"serial open:{ser.is_open}")
print("send data")
# send_data(command, data1, data2)
send_read_sensor_value()
ack, response1, response2 = receive_data()

if ack == STX + b'ACK':
    print("Data received successfully.")
    print("Response 1:", response1)
    print("Response 2:", response2)
else:
    print("Error occurred while receiving data.")
    print("Error code:", response1)
