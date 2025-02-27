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

TODO: Add link to example file and usage of example file details


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

TODO: insert link for example wei usage file