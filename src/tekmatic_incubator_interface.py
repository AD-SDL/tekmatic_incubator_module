"""Interface for controlling the Tekmatic Single Plate Incubator device."""

import clr
from pathlib import Path
import time
from starlette.datastructures import State

"""
TODOs: 
- test all driver funtions
- add docstrings to all functions
- how to handle errors, where should that happen?

- FORMAT ALL RESPONSES

"""


class Interface:
    """
    The skeleton for a device interface.
    TODO: Replace with your device-specific interface implementation
    """

    def __init__(self, dll_path=r"C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll", port="COM5"):
        """Initializes and opens the connection to the incubator"""

        # TODO: make this a command line argument
        clr.AddReference(dll_path)
        from IncubatorCom import Com
        self.incubator_com = Com()
        self.open_connection(port)

    # def __del__(self):
    #     """Disconnect/cleanup interface"""
    #     self.close_connection()

    # DEVICE CONTROL -------------------------------------------------------------------------------------------------------
    def open_connection(self, port):
        """Opens the connection to the incubator over the specified COM port"""

        response = self.incubator_com.openCom(port)
        if response == 77:
            print("Com connection opened sucessfully")
        else: # response 170 means failed
            print("Com open connection failed")
        return response

    def close_connection(self):
        """Closes any existing open connection, no response expected on success or fail"""

        self.incubator_com.closeCom()
        print("Com connection closed")


    def initialize_device(self):   # WORKING
        """Initializes the Tekmatic Single Plate Incubator Device through the open connection. """
        # TODO: what is the response if initialization fails?
        self.send_message("AID",read_delay=3)
        print("Tekmatic incubator initialized")


    def reset_device(self):
        """Resets the Tekmatic Single Plate Incubator Device
        Note: seems to respond 88 regardless of success or failure
        """
        response = self.send_message("SRS", read_delay=5)  # wait 5 seconds for device to reset before reading response
        print("device reset")
        return response

    def report_error_flags(self):
        """Reports any error flags present on device
        Responses:
            0 = no errors
            """
        # TODO: interpret the error codes!
        response = self.send_message("REF")
        return response


    # TEMPERATURE CONTROL -------------------------------------------------------------------------------------------------------
    def get_actual_temperature(self):
        "Returns the actual temperature as measured by main sensor on incubator (sensor 1)"
        # RAT Selector (selector = 1,2,or 3, default 1 (main))

        # TODO: Should we report the temperature of all sensors or just the main one? RAT, RAT2, RAT3
        # TODO: Format temperature response
        response = self.send_message("RAT")
        return response

    def get_target_temperature(self):
        """Returns the set target temperature of the incubator"""
        # TODO: format temperature response
        response = self.send_message("RTT")
        return response

    def set_target_temperature(self, temperature=None):
        """Sets the target temperature, if no temperature specified, defaults to 22 deg C"""
        # TODO: check that any temperature inputs are valid (int between 0 and 800 after x10)
        # TODO: format temperature response
        message = "STT" + str(int(temperature*10)) if temperature else "STT"
        response = self.send_message(message)
        return response

    def enable_heater(self):  # WORKING
        """Enables the device heating element.
        Note: can read the set value with self.send_message("RHE"). 0 = off, 1 = on.
        """
        self.send_message("SHE1")

    def disable_heater(self):  # WORKING
        """Disable the device heating element.
        Note: can read the set value with self.send_message("RHE"). 0 = off, 1 = on.
        """
        self.send_message("SHE")


    # DOOR ACTIONS -------------------------------------------------------------------------------------------------------
    def open_dooor(self):  # WORKING
        """Opens the door"""
        self.send_message("AOD", read_delay=5) # wait 5 seconds for door to open before reading com response


    def close_door(self):  # WORKING
        """Closes the door"""
        self.send_message("ACD", read_delay=5) # wait 5 seconds for door to close before reading com response

    def report_door_status(self):  # WORKING
        """Returns 1 if door open, 0 if door closed"""
        response = self.send_message("RDS")
        return response

    def report_labware(self):
        """Returns 0 if no labware present, 1 if labware detected, error 8 if door is open, and error 7 if reset and door closed"""
        response = self.send_message("RLW")
        return response

    # SHAKER COMMANDS -------------------------------------------------------------------------------------------------------
    def enable_shaker(self, status=1):
        """Enables the device shaking element
        Status:
            1 = on
            ND = on without labware detection
        """
        if status in [1,"ND"]:
            self.send_message("ASE" + str(status), read_delay=2)
        else:
            print("Error: invalid status in enable_shaker method")

    def disable_shaker(self):
        """Disables the device shaking element"""
        self.send_message("ASE0", read_delay=5)

    def set_shaker_parameters(self, amplitude:int=20, frquency:int=142):  # WORKING
        """Sets the shaking parameters

        Amplitude: shaking distance in 1/10 mm, 0-30 valid, 20 default
        Frequency: speed of shaking revolutions in Hzx10 (1Hz = 60 rpm), 66-300 valid (6.6-30Hz), 142 default (14.2 Hz)

        Notes:
        - Through the dll there is support for controlling amplitude and frequency on x and y axes.
            That level of control is not supported here as it was deemed not necessary

        - Phase shift is also controllable through dll, we will keep it at 0 deg.

        - Read set values with: "RFX" (frequency x), "RFY" (frequency y), "RAX" (amplitude x), "RAY" (amplitude y), and "RPS" (phase shift)
        - Read actual values with: "RFX1", "RFY1", "RAX(1(actual) or 2(static measure))", "RAY(1(actual) or 2(static measure))", and "RPS1"
        """
        phase_shift = "000"

        if 0 <= amplitude <= 30 and 66 <= frquency <= 300:
            # SSP + str(amplitude_x) + srt(amplitude_y) + str(frequency_x) + str(frequency_y) + str(phase_shift)
            self.send_message(
                "SSP" + str(amplitude) + "," + str(amplitude) + "," + str(frquency) + "," + str(frquency) + "," + str(phase_shift))
        else:
            print("Error: invalid amplitude or frequency input values in set_shaker_parameters method")


    # HELPER COMMANDS -------------------------------------------------------------------------------------------------------
    def send_message(self, message_string, device_id=2, stack_floor=0, read_delay=.5):
        """Formats and sends message to Tekmatic Device, then collects device response"""

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

        time.sleep(read_delay)

        # Read COM port response
        response = self.incubator_com.readCom()
        formatted_response = self.format_response(response)
        print(f"Message: {message_string}, com response: {formatted_response}")

        # return response
        return formatted_response  # returned response will be 88 if mesage sent correctly


    def format_response(self, response:str):
        """Extracts important message details from longer com response message"""
        formatted_response = response.replace("`", "")
        formatted_response = formatted_response.replace("²", "")
        formatted_response = formatted_response.strip()
        return formatted_response


if __name__ == "__main__":
    com = Interface()
    com.initialize_device()
    # com.reset_device()
    # com.report_error_flags()

    # # Door testing -------------------
    com.open_dooor()
    com.close_door()
    com.report_door_status()
    print(com.format_response(com.report_labware()))

    # # Temperature testing --------------
    com.get_target_temperature()
    com.get_actual_temperature()

    # com.set_target_temperature(30.0)
    
    # com.set_target_temperature()

    # # Shaker testing --------------
    com.enable_shaker("ND")
    com.send_message("RSE")

    time.sleep(5)

    com.disable_shaker()
    com.send_message("RSE")

    # read shaker settings
    # print("FX")
    # com.send_message("RFX")

    # print("FY")
    # com.send_message("RFY")

    # print("AX")
    # com.send_message("RAX")

    # print("FX")
    # com.send_message("RAX")

    # com.set_shaker_parameters(amplitude=22, frquency=143)

    # # print("FX")
    # com.send_message("RFX")

    # print("FY")
    # com.send_message("RFY")

    # print("AX")
    # com.send_message("RAX")

    # print("FX")
    # com.send_message("RAX")


    # # Heater testign -----------------
    # com.enable_heater()
    # com.send_message("RHE")

    # time.sleep(5)

    # com.disable_heater()
    # com.send_message("RHE")

    com.close_connection()

