# import serial
# import time

# try: 
#     # connect
#     ser = serial.Serial('COM5', 19200)
#     print('connected to the serial port')

#     # send a command
#     message = 'ping'.encode('utf-8').strip()
#     ser.write(message)

#     time.sleep(3)

#     response = ser.read(ser.in_waiting)
#     decoded = None
#     if response:
#         print(response.decode("ascii"))
#         decoded = response.decode('utf-16')
#         print(f"DECODED MESSAGE: {decoded}")
#     else:
#         print("no response")

# except Exception as e:
#     print(e)

# finally: 
#     if 'ser' in locals() and ser.is_open:
#         ser.close()
#         print("closing the connection")

# -------------------------------------------------------


def convertMsgToBytes(message: str):
    instruction_byte_array = bytes([ord(c) for c in message])
    return instruction_byte_array

# import clr form the pythonnet package
import clr
import time

# Add the dll as a clr reference so it can be accessed by python
clr.AddReference(r"C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll")

# Load the relevant namespace and class
from IncubatorCom import Com

# Create an instance of the com class
incubator_com = Com()

# OPEN COM
response = incubator_com.openCom("COM5")
print(f"Response (openCom): {response}")
# openCom returns 77 on success, 0xAA (170?) if not possible to open that port

# # CLOSE COM
# response = incubator_com.closeCom()
# print(f"Response (closeCom): {response}")
# # closeCom returns 99 is com is closed, otherwise what?  Seems to return 99 even if there was no port already open to close

#msg_string = "AOD"  # command to open the drawer
msg_string = "ACD"  # command to close the drawer
device_ID = 2
stack_floor = 0

msg_length = len(msg_string)
msg_len_bytes = msg_length & 0xFF
bytes_device_ID = device_ID & 0xFF
bytes_stack_floor = stack_floor & 0xFF

bytes_instruction = convertMsgToBytes(msg_string)
print(bytes_instruction)

time.sleep(3)
response = incubator_com.sendMsg(
    bytes_instruction,
    msg_len_bytes,
    bytes_device_ID,
    bytes_stack_floor
)

print(response)
#response = incubator_com.sendMsg(len(m)