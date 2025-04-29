# Inheco Single Plate Incubator Shaker Module

A WEI-powered module for controlling Inheco Single Plate Incubator Shakers.

Contains an Inheco incubator interface (inheco_incubator_interface.py) and Inheco incubator REST node (inheco_incubator_module.py).

### Installation

Inheco incubators run on Windows systems. See device documentation on system requirements for more details.

Before using the Inheco incubator, you will need to clone the module GitHub repo and install the dependencies. Use the code below to complete this step.

General install instructions:

    git clone https://github.com/AD-SDL/inheco_incubator_module.git
    cd inheco_incubator_module
    pip install -e .

### Running the driver

    cd inheco_incubator_module
    cd src
    python inheco_incubator_interface.py

This will print "Inheco incubator device connected and initialized" if the interface is able to connect correctly to the device.

You can also use this Python interface in other programs. The link below shows an example Python program which uses the Inheco interface to demonstrate all functions available in the interface.

[Example interface usage](https://github.com/AD-SDL/inheco_incubator_module/blob/main/examples/interface_usage_example.py)


### Running the REST Node

The REST Node can be started with a command in the format below

    python your\\path\\to\\inheco_incubator_module.py --device <(optional) your COM port> --dll_path <(optional) path to incubator control dll (ComLib.dll)> --device_id <(optional) device ID of the Inheco incubator device> --stack_floor <(optional) stack floor of the Inheco incubator device>

--device will default to "COM5", --dll_path will default to "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll", --device_id will default to 2, and
--stack_floor will default to 0 unless specified.

Example usage with no optional arguments (assumes no changes needed to defaults):

    python inheco_incubator_module.py


Example usage with all optional arguments:

    python inheco_incubator_module.py --device "COM5" --dll_path "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll" --device_id 2 --stack_floor 0


### Example Usage in WEI Workflow YAML file

The link below shows an example of a YAML WEI Workflow file that could interact with the Inheco Single Plate Incubator Shaker module.

[Example WEI usage](https://github.com/AD-SDL/inheco_incubator_module/blob/main/examples/wei_workflow_usage_example.yaml)
