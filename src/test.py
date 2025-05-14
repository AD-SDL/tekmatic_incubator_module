from inheco_incubator_interface import Interface
from time import sleep

device = Interface(port="COM5")
# device.initialize_device(0)  # this closes the first door
# print("i 0")


# sleep(5)

device.initialize_device(1)  # this also closes the door
# print("i 1")

# device.close_door(0)
# print("cd 0")
# device.close_door(1)
# print("cd 1")

# device.open_door(1)
# device.open_door(0)







