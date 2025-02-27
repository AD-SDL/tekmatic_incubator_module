import tekmatic_incubator_interface
import time

tekmatic_device = tekmatic_incubator_interface.Interface()
# you can also specify dll path and Com port like this...
# tekmatic_device = tekmatic_incubator_interface.Interface(dll_path=r"C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll", port="COM5")

tekmatic_device.initialize_device()

print("Reporting any error flags")
print(tekmatic_device.report_error_flags())

print("Report actual temperature")
print(tekmatic_device.get_actual_temperature())

print("Report target temperature")
print(tekmatic_device.get_target_temperature())

print("Set the target temperature, deg C")
tekmatic_device.set_target_temperature(30.0)

print("Turn the heater on then off")
tekmatic_device.start_heater()
time.sleep(10)
tekmatic_device.stop_heater()

print("Is the heater active?")
print(tekmatic_device.is_heater_active())

print("Open then close the door")
tekmatic_device.open_door()
time.sleep(5)
tekmatic_device.close_door()

print("Is the door open?")
print(tekmatic_device.report_door_status())

print("Is any labware present in the incubator?")
print(tekmatic_device.report_labware())

print("Set the shaker parameters")
tekmatic_device.set_shaker_parameters(amplitude=2, frequency=14)

print("Start then stop the shaker")
tekmatic_device.start_shaker()
time.sleep(10)  # shake for 10 seconds
tekmatic_device.stop_shaker()

print("Is the shaker active?")
print(tekmatic_device.is_shaker_active())

print("Reset device settings")
tekmatic_device.reset_device()

print("Close the connection")
tekmatic_device.close_connection()