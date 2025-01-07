"""Interface for controlling the Tekmatic Single Plate Incubator device."""

import clr
from pathlib import Path

from starlette.datastructures import State

"""
TODOs: 
- test all driver funtions
- add docstrings to all functions
- how to handle errors, where should that happen?

"""


class Interface:
    """
    The skeleton for a device interface.
    TODO: Replace with your device-specific interface implementation
    """

    def __init__(self, dll_path):
        """Initializes and opens the connection to the incubator"""

        # TODO: make this a command line argument
        clr.AddReference(repr(dll_path))
        from IncubatorCom import Com
        self.incubator_com = Com()
        self.open_connection()

    def __del__(self):
        """Disconnect/cleanup interface"""
        response = self.incubator_com.closeCom()
    
    # DEVICE CONTROL 
    def open_connection(self, port): 
        """Opens the connection to the incubator over the specified COM port"""

        response = self.incubator_com.openCom(port)
        print(f"Response (openCom): {response}")  
        return response  

    def close_connection(self): 
        """Closes any existing open connection"""

        response = self.incubator_com.closeCom()
        return response

    def initialize_device(self): 
        response= self.send_message("AID")
        # TODO: if response == 1, initialization failed
        # what is the response if succeded?
        return response 

    def reset_device(self): 
        self.send_message("SRS") 
        # TODO: is there no response here?
    
    def report_error_flags(self): 
        response = self.send_message("REF")
        return response
    

    # TEMPERATURE CONTROL
    def get_actual_temperature(self): 
        # RAT Selector (selector = 1,2,or 3, default 1 (main))

        # TODO: report the temperature of all sensors? do we care about all of them? 
        # TODO: what is the error code for invalid operand
        # reports the actual temperature of the main sensor on the device 
        response = self.send_message("RAT")

        if response == 3: # if there is an error... # what is the error response here???
            return response
            
        else: # If no error ...
            # if response id 345, this means 34.5 deg C
            temperature = float(response/10)  # do I need to round this to 1 decimal
            return temperature

    def get_target_temperature(self): 
        response = self.send_message("RTT")
        temperature = float(response/10)  
        return temperature

    def set_target_temperature(self, temperature: float): 
        # make sure the temperature input is valid (one decimal, between 0 and 800)
        # default = 220, which is 22.0
        temperature = temperature * 10
        response = self.send_message("SFF" + str(temperature))
        return response
        

    



    def send_message(self, message_string, device_id=2, stack_floor=0):

        # convert message length, device ID, and stack floor to bytes
        bytes_message_length = len(message_string) & 0xFF
        bytes_device_ID = device_id & 0xFF
        bytes_stack_floor = stack_floor & 0xFF

        # convert them message to byte array
        bytes_message = bytes([ord(c) for c in message_string])
        
        # format the message, send over com port and collect response
        response = self.incubator_com.sendMsg(
            bytes_message,
            bytes_message_length,
            bytes_device_ID,
            bytes_stack_floor
        )

        # return response 
        return response 

