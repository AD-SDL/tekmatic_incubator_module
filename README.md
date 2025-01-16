# Tekmatic Incubator module

A WEI-powered module for controlling Tekmatic Single Plate Incubators.

Contains a tekmatic incubator interface (tekmatic_incubator_interface.py) and Tekmatic Incubator REST node (tekmatic_incubator_module.py).

### Installation

Tekmatic incubators run on Windows systems. See device documentation on system requirements for more details.

Before using the Tekmatic Incubator, you will need to clone the module GitHub repo and install the dependencies. Use the code below to complete this step. 

General install instructions: 

    git clone https://github.com/AD-SDL/tekmatic_incubator_module.git
    cd tekmatic_incubator_module 
    pip install -e .

### Running the driver

    cd tekmatic_incubator_module
    cd src
    python tekmatic_incubator_interface.py

This will print "Tekmatic device connected and initialized" if the interface is able to connect correctly to the Tekmatic device.

You can also use this python interface in other programs. See the below python program which uses the tekmatic interface to demonstrate all functions available in the interface. 

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


### Running the REST Node

The REST Node can be started with a command in the format below

    python your\\path\\to\\tekmatic_incubator_module.py --device <(optional) your COM port> --dll_path <(optional) path to incubator control dll (ComLib.dll)> --device_id <(optional) device ID of the Tekmatic Incubator device> --stack_floor <(optional) stack floor of the Tekmatic Incubator device>

--device will default to "COM5", --dll_path will default to "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll", --device_id will default to 2, and 
--stack_floor will default to 0 unless specified. 

Example usage with no optional arguments (assumes no changes needed to defaults): 

    python tekmatic_incubator_module.py


Example usage with all optional arguments: 

    python tekmatic_incubator_module.py --device "COM5" --dll_path "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll" --device_id 2 --stack_floor 0


### Example Usage in WEI Workflow YAML file

Below is an example of a YAML WEI Workflow file that could interact with the Tekmatic Single Plate Incubator module. 

    name: Tekmatic Example
    author: RPL 
    info: An example WEI workflow to show available Tekmatic Incubator actions
    version: '0.1'

    flowdef:
    - name: open tekmatic
      module: tekmatic
      action: open

    - name: close tekmatic
      module: tekmatic
      action: close

    - name: set temperature
      module: tekmatic
      action: set_temperature
      args:
        temperature: 30.0

    - name: start 60 second incubation, block until finished
      module: tekmatic
      action: incubate
      args: 
        temperature: 30.0
        shaker_frequency: 10
        wait_for_incubation_time: True
        incubation_time: 60

    - name: start continuous incubation, non-blocking
      module: tekmatic
      action: incubate
      args: 
        temperature: 30.0
        shaker_frequency: 10