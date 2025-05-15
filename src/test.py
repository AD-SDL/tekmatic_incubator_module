from inheco_incubator_interface import Interface
from time import sleep

device = Interface(port="COM5")
device.initialize_device(0)  # this closes the first door
device.initialize_device(1)  # this also closes the door

print(device.get_actual_temperature(1))




# print("i 1")

# device.close_door(0)
# print("cd 0")
# device.close_door(1)
# print("cd 1")

# device.open_door(1)
# device.open_door(0)







