import argparse
import csv
import os
import serial
import sys
import time

def parse_cli_args():
    parser = argparse.ArgumentParser(description='od mini pro cli.')
    parser.add_argument('port', type=str, help='Serial port which is opened.')
    parser.add_argument('--baud_rate', '-b', type=int, choices=[9600, 19200, 38400, 57600, 115200, 230400, 312000, 460000, 500000, 625000, 833000, 920000, 1250000], default=9600, help='Baud rate usde for the serial conncetion.')
    parser.add_argument('--print_values', '-p', action='store_true', help='Print values the values on the console.')
    parser.add_argument('--store', '-s', type=str,nargs='?', default='',  help='File which the sensor values are stored in. If no file name is given sensor values are not stored.')

    return parser.parse_args(args=None if sys.argv[1:] else ["--help"])

# Constants
STX = b'\x02'   # STX marker (hex code 02)
ACK = b'\x06'   # ACK marker (hex code 06)
NAK = b'\x15'   # NAK marker (hex code 15)
ETX = b'\x03'   # ETX marker (hex code 03)
C = b'\x43'     # Command for reading out measurement value / output status
BCC_READ_SENSOR_VALUE = b'\xf2'
READ_SENSOR_VALUE = STX + C + b'\xb0' + b'\x01' + ETX + BCC_READ_SENSOR_VALUE

# Helper function to calculate BCC
# NOT WORKING carry over is missing!
# def calculate_bcc(ack, res1, res2, etx):
#     bcc = 0
#     print(f"bcc:={bcc}")
#     for bit in data:
#         bcc ^= bit
#         print(f"bcc:={bcc}")
#     print(f"full bcc:={bcc}")
#     return bcc.to_bytes(1, byteorder='big')

def send_read_sensor_value(ser):
    ser.setRTS(True)
    ser.write(READ_SENSOR_VALUE)
    ser.flush()
    ser.setRTS(False)

def calculate_value(package):
    ack = package[0:1]
    res1 = package[1:2]
    res2 = package[2:3]
    etx = package[3:4]
    bcc = package[4:5]
    if ack == ACK and etx == ETX:
        # SKIP BCC check for now
        # bcc_check = calculate_bcc(ack, res1, res2, etx)
        #

        # data is two bytes (signed two complement)
        # convert to int -> e.g. 1234 -> which represent 12.34 so divide
        # by 100 to get "correct" value
        return int.from_bytes(res1 + res2, byteorder='big', signed=True) / 100.0
    # no vali data received
    return foat('NaN')

def read_sensor_values(ser, file_to_store, print_values):
    file = None
    writer = None
    if file_to_store:
        if not file_to_store.endswith('.csv'):
            file_to_store += '.csv'
        if os.path.exists(file_to_store):
            print(f"Give file:{file_to_store} exists. Aborting.")
            ser.close()
            return
        file = open(file_to_store, 'a', newline='')
        try:
            writer = csv.writer(file)
            header = ["Time", "Value"]
            writer.writerow(header)
        except:
            file.close()
    try:
        while True:
            send_read_sensor_value(ser)
            # package is either:
            # STX|ACK|RES1|RES2|ETX|BCC <- actual data
            # or
            # STX|NAK|ERROR_CODE|OOH|ETX|BCC <- some error happend
            if ser.read(1) == STX:
                    # receive last 5 byte of package
                    package = ser.read(5)
                    current_time = time.time_ns()
                    value = calculate_value(package)
                    if file is not None:
                        data = [current_time, value]
                        writer.writerow(data)
                    if print_values:
                        print(f"{value} at time {current_time}")
    except KeyboardInterrupt:
        print("closing serial connection")
        ser.close()
        if file:
            print("closing file")
            file.close()

if __name__=="__main__":
    args = parse_cli_args()
    port = args.port
    baud_rate = args.baud_rate
    store = args.store
    print_values = args.print_values

    print(port)
    print(baud_rate)
    print(store)
    print(print_values)

    # Configure serial communication
    ser = serial.Serial(
        port=port,  # Replace with the appropriate serial port
        baudrate=baud_rate,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE,
        timeout=0 # don't know if should set to 0...
    )

    print(f"Starting to read sensor_values: {ser}")
    read_sensor_values(ser, store, print_values)
