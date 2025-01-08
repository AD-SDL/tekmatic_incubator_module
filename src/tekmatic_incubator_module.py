"""
REST-based node for Tekmatic Single Plate Incubators that interfaces with WEI
"""

from pathlib import Path
from tempfile import NamedTemporaryFile
import time

from fastapi.datastructures import UploadFile
from starlette.datastructures import State
from typing_extensions import Annotated
from wei.modules.rest_module import RESTModule
from wei.types.module_types import (
    LocalFileModuleActionResult,
    ModuleAction,
    ModuleActionArg,
    ModuleState,
    ValueModuleActionResult,
)
from wei.types.step_types import (
    ActionRequest,
    StepFileResponse,
    StepResponse,
    StepStatus,
)
from wei.utils import extract_version

import tekmatic_incubator_interface 

rest_module = RESTModule(
    name="tekmatic_incubator_module",
    version="0.0.1",
    description="A REST node to control Tekmatic Single Plate Incubators",
    model="tekmatic",
)

# add arguments
rest_module.arg_parser.add_argument(
    "--dll_path", type=str, help="path to incubator control dll (ComLib.dll)", default="C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll"
)
rest_module.arg_parser.add_argument(
    "--device_id", type=int, help="device ID of the Tekmatic Incubator device ", default=2
)
rest_module.arg_parser.add_argument(
    "--stack_floor", type=int, help="stack floor of the Tekmatic Incubator device", default=0
)
rest_module.arg_parser.add_argument(
    "--device", type=str, help="Serial port for communicating with the device", default="COM5"
)

# parse the arguments
args = rest_module.arg_parser.parse_args()


@rest_module.startup()
def custom_startup_handler(state: State):
    """
    Initializes the tekmatic interface and opens the COM connection
    """
    state.tekmatic = tekmatic_incubator_interface.Interface()
    state.tekmatic.initialize_device()  # TODO: is this necessary?


# @rest_module.shutdown()
# def custom_shutdown_handler(state: State):
#     """
#     Custom shutdown handler that is called whenever the module is shutdown.

#     If this isn't provided, the default shutdown handler will be used, which will do nothing.
#     """

#     # del state.interface  # *Close device connection or do other cleanup, if needed


# @rest_module.state_handler()
# def custom_state_handler(state: State) -> ModuleState:
#     """
#     Custom state handler that is called whenever the modules state is requested via the REST API.

#     If this isn't provided, the default state handler will be used, which will return the following:

#     ModuleState(status=state.status, error=state.error)
#     """

#     # if state.interface:
#         # state.interface.query_state(state)  # *Query the state of the device, if supported

#     return ModuleState.model_validate(
#         {
#             "status": state.status,  # *Required, Dict[ModuleStatus, bool]
#             "error": state.error, # * Optional, str
#             # *Custom state fields
#             "sum": state.sum,
#             "difference": state.difference,
#         }
#     )


# OPEN TRAY ACTION
@rest_module.action(
    name="open", description="Open the plate tray"
)
def open(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Opens the Tekmatic incubator tray"""

    state.tekmatic.disable_shaker()  # TODO: maybe check if the shaker is active before doing this action to save 5 seconds. 
    state.tekmatic.open_door()
    return StepResponse.step_succeeded()

# CLOSE TRAY ACTION
@rest_module.action(
    name="close", description="Close the plate tray"
)
def close(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Opens the Tekmatic incubator tray"""

    state.tekmatic.close_door()
    return StepResponse.step_succeeded()


# SET TEMP ACTION
@rest_module.action(
    name="set_temp", descriptionn="Set target incubation temperature"
)
def set_temp(
    state: State,
    action: ActionRequest,
    temperature: Annotated[float, "temperature in Celsius to one decimal point. 0.0 - 80.0 are valid inputs, 22.0 default"] = 22.0, # TODO: What happens if a user enters an integer
    activate: Annotated[bool, "(optional) turn on heating/cooling element, on = True, off = False"] = False,
) -> StepResponse:
    """Sets the temperature on the tekmatic incubator, optionally turns on the heating element"""

    # TODO: Check that this actualy sets the temp after adding temp and other information into the state

    try:
        response = state.tekmatic.set_target_temperature(float(temperature))  # TODO: validate that the float has one decimal place? Necessary?

        if activate:
            state.tekmatic.start_heater()  # TODO": should I be checking these too for a successful response?
        else:
            state.tekmatic.stop_heater()

        if response == "":
            return StepResponse.step_succeeded()
        else:
            return StepResponse.step_failed(error="Set temp action failed, unsucessful response")

    except Exception as e:
        print(f"Error in set_temp action: {e}")
        return StepResponse.step_failed(error="Set temp action failed")

# INCUBATE ACTION
@rest_module.action(
    name="incubate", description="Start incubation with optional shaking"
)
def incubate(
    state:State,
    action: ActionRequest,
    temperature: Annotated[float, "temperature in celsius to one decimal point. 0.0 - 80.0 are valid inputs, 22.0 default"] = 22.0, # TODO: What happens if a user enters an integer
    shaker_frequency: Annotated[float, "shaker frequency in Hz (1Hz = 60rpm). 6.6-30.0 are valid inputs, default is 14.2 Hz"] = 14.2,
    wait_for_incubation_time: Annotated[bool, "True if action should block until the specified incubation time has passes, False to continue immediately after starting the incubation"] = False,
    incubation_time: Annotated[int, "Time to incubate in seconds"] = None,
) -> StepResponse:
    """Starts incubation at the specified temperature, optionally shakes, and optionally blocks all other actions until incubation complete"""

    # format inputs
    shaker_frequency_formatted = int(shaker_frequency * 10)  # TODO, either put all unit conversions in module or driver, not both like you have now.

    # set the temperature and activate heating
    if 0 <= int(temperature*10) <= 800:
        try:
            state.tekmatic.set_target_temperature(temperature)
            state.tekmatic.start_heater()
            print(f"Incubation action: Temperature set to {temperature} deg C")

        except Exception as e:
            print(f"Error in incuabte action: {e}")
            return StepResponse.step_failed(error="Failed to set temerature in incubate action")

    if 66 <= shaker_frequency <= 300:
        try:
            state.tekmatic.set_shaker_parameters(frquency=shaker_frequency_formatted)
            state.tekmatic.start_shaker()

            # TODO: wait a second then check that the shaker actually started? Add method ot check shaker status to interface
            print(f"Incubate action: Shaker started at {shaker_frequency} Hz")

        except Exception as e:
            print(f"Error in incuabte action: {e}")
            return StepResponse.step_failed(error="Failed to set shaker parameters or start shaking in incubate action")

    if not wait_for_incubation_time:
        return StepResponse.step_succeeded()
    else:
        print(f"Incubation action: Starting incubation for {incubation_time} seconds")
        time.sleep(incubation_time)  # block until incubation time is complete
        # TODO: print time left or time that incubation will stop somewhere? in the status?

        # stop shaking after incubation time complete?
        state.tekmatic.stop_shaker()
        print("Incubation action: Incubation complete")

        return StepResponse.step_succeeded()


#****************#
#*Admin Commands*#
#****************#

# TODO: Add support for admin commands, if desired

"""
To add support for custom admin actions, uncomment one or more of the
functions below.
By default, a module supports SHUTDOWN, RESET, LOCK, and UNLOCK modules. This can be overridden by using the decorators below, or setting a custom Set for python_rest_module.admin_commands
"""

# @tekmatic_incubator_module.pause
# def pause(state: State):
#     """Support pausing actions on this module"""
#     pass

# @tekmatic_incubator_module.resume
# def resume(state: State):
#     """Support resuming actions on this module"""
#     pass

# @tekmatic_incubator_module.cancel
# def cancel(state: State):
#     """Support cancelling actions on this module"""
#     pass

# @tekmatic_incubator_module.lock
# def lock(state: State):
#     """Support locking the module to prevent new actions from being accepted"""
#     pass

# @tekmatic_incubator_module.unlock
# def unlock(state: State):
#     """Support unlocking the module to allow new actions to be accepted"""
#     pass

# @tekmatic_incubator_module.reset
# def reset(state: State):
#     """Support resetting the module.
#     This should clear errors and reconnect to/reinitialize the device, if possible"""
#     pass

# @tekmatic_incubator_module.shutdown
# def shutdown(state: State):
#     """Support shutting down the module"""
#     pass


# *This runs the arg_parser, startup lifecycle method, and starts the REST server
if __name__ == "__main__":
    rest_module.start()
