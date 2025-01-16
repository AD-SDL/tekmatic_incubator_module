# Tekmatic Incubator module

A WEI-powered module for controlling Tekmatic Single Plate Incubators.

Contains a tekmatic incubator interface (tekmatic_incubator_interface.py) and Tekmatic Incubator REST node (tekmatic_incubator_module.py).

### Installation

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

You can also use this python interface in other programs. See the below python program which uses the tekmatic interface to demonstrate all functions available in the interface

    import tekmatic_incubator_interface

    tekmatic_device = tekmatic_incubator_interface.Interface()
    # you can also specify dll path and Com port like this...
    # tekmatic_device = tekmatic_incubator_interface.Interface(dll_path=r"C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll", port="COM5")

    tekmatic_device.initialize_device()
    tekmatic_device.reset_device()

    # report any errors on the device
    print(tekmatic_device.report_error_flags())

    # report actual temperature
    print(tekmatic_device.get_actual_temperature())

    # report the target temperature
    print(tekmatic_device.get_target_temperature())

    # set the target temperature, deg c
    tekmatic_device.set_target_temperature(30.0)

    # turn the heater on, then off
    tekmatic_device.start_heater()
    tekmatic_device.stop_heater()

    # check if heater is active
    print(tekmatic_device.is_heater_active)

    # open/close the door 
    tekmatic_device.open_door()
    tekmatic_device.close_door()

    # check if the door is open
    print(tekmatic_device.report_door_status())

    # check if labware is present
    print(tekmatic_device.report_labware())

    # start/stop the shaker
    tekmatic_device.start_shaker()
    tekmatic_device.stop_shaker()

    # check if shaker is active
    print(tekmatic_device.is_shaker_active())

    # set shaker parameters (amplitude in mm, frequency in Hz)
    tekmatic_device.set_shaker_parameters(amplitude=2, frequency=10)

    # close the connection
    tekmatic_device.close_connection()


### Running the REST Node

The REST Node can be started with a command in the format below

    python tekmatic_incubator_module.py --device <(optional) your COM port> --dll_path <(optional) path to incubator control dll (ComLib.dll)> --device_id <(optional) device ID of the Tekmatic Incubator device> --stack_floor <(optional) stack floor of the Tekmatic Incubator device>

--device will default to "COM5", \ --dll_path will default to "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll" \ --device_id will default to 2, \ and 
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


        
        









## Using This Template

[Creating a Repository From a Template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)


## Renaming

To automatically replace `tekmatic_incubator` with the name of your instrument, run the "Rename Module Repo" GitHub Actions Workflow in your repository: [Manually Running a Workflow](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/manually-running-a-workflow)

N.B. this assumes your repository is named using the `<instrument_name>_module` format.

Alternatively, you can run `.github/rename.sh tekmatic_incubator <new_name>` locally and commit the results.

## TODO's

Throughout this module template, there are a number of comments marked `TODO`. You can use search/find and replace to help ensure you're taking full advantage of the module template and don't have any residual template artifacts hanging around.

## Guide to Writing Your Own Module

For more details on how to write your own module (either using this template or from scratch), see [How-To: Modules (WEI Docs)](https://rpl-wei.readthedocs.io/en/latest/pages/how-to/module.html)
