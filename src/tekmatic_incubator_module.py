"""
REST-based node for Tekmatic Single Plate Incubators that interfaces with WEI
"""

import time
import traceback
from typing import Optional

from starlette.datastructures import State
from typing_extensions import Annotated
from wei.modules.rest_module import RESTModule
from wei.types.module_types import (
    ModuleState,
)
from wei.types.step_types import (
    ActionRequest,
    StepResponse,
)

from tekmatic_incubator_interface import Interface

rest_module = RESTModule(
    name="tekmatic_incubator_module",
    version="0.0.1",
    description="A REST node to control Tekmatic Single Plate Incubators",
    model="tekmatic",
)

# add arguments
rest_module.arg_parser.add_argument(
    "--dll_path",
    type=str,
    help="path to incubator control dll (ComLib.dll)",
    default="C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll",
)
rest_module.arg_parser.add_argument(
    "--device_id",
    type=int,
    help="device ID of the Tekmatic Incubator device ",
    default=2,
)
rest_module.arg_parser.add_argument(
    "--stack_floor",
    type=int,
    help="stack floor of the Tekmatic Incubator device",
    default=0,
)
rest_module.arg_parser.add_argument(
    "--device",
    type=str,
    help="Serial port for communicating with the device",
    default="COM5",
)

# parse the arguments
args = rest_module.arg_parser.parse_args()


@rest_module.startup()
def tekmatic_startup(state: State):
    """Initializes the tekmatic interface and opens the COM connection"""
    state.tekmatic = None
    state.tekmatic = Interface()
    state.tekmatic.initialize_device()
    state.is_incubating_only = False
    state.incubation_seconds_remaining = 0


@rest_module.shutdown()
def tekmatic_shutdown(state: State):
    """Handles cleaning up the tekmatic object. This is also an admin action"""
    if state.tekmatic is not None:
        state.tekmatic.close_connection()
        del state.tekmatic


@rest_module.state_handler()
def tekmatic_state_handler(state: State) -> ModuleState:
    """Returns the state of the Tekmatic device and module"""
    tekmatic: Optional[Interface] = state.tekmatic

    if tekmatic is None:
        return ModuleState(
            status=state.status,
            error=state.error,
        )

    if not tekmatic.is_busy or (tekmatic.is_busy and state.is_incubating_only):
        # query for fresh state details and save to cache
        state.cached_current_shaker_active = tekmatic.is_shaker_active()
        state.cached_current_heater_active = tekmatic.is_heater_active()
        state.cached_current_actual_temperature = tekmatic.get_actual_temperature()
        state.cached_current_target_temperature = tekmatic.get_target_temperature()

    # if the shaker is actually busy, the previous cashed values will be returned
    return ModuleState.model_validate(
        {
            "status": state.status,
            "error": state.error,
            "target_temp": state.cached_current_target_temperature,
            "actual_temp": state.cached_current_actual_temperature,
            "shaker_active": state.cached_current_shaker_active,
            "heater_active": state.cached_current_heater_active,
            "incubation_seconds_remaining": state.incubation_seconds_remaining,
        }
    )


# OPEN TRAY ACTION
@rest_module.action(name="open", description="Open the plate tray")
def open(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Opens the Tekmatic incubator tray"""

    # disable the shaker if shaking
    if state.cached_current_shaker_active:
        state.tekmatic.disable_shaker()
    state.tekmatic.open_door()
    return StepResponse.step_succeeded()


# CLOSE TRAY ACTION
@rest_module.action(name="close", description="Close the plate tray")
def close(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Closes the Tekmatic incubator tray"""

    state.tekmatic.close_door()
    return StepResponse.step_succeeded()


# SET TEMP ACTION
@rest_module.action(
    name="set_temperature", description="Set target incubation temperature"
)
def set_temperature(
    state: State,
    action: ActionRequest,
    temperature: Annotated[
        float,
        "temperature in Celsius to one decimal point. 0.0 - 80.0 are valid inputs, 22.0 default",
    ] = 22.0,
    activate: Annotated[
        bool, "(optional) turn on heating/cooling element, on = True, off = False"
    ] = False,
) -> StepResponse:
    """TODO: Better description. Sets the temperature on the Tekmatic incubator, optionally turns on the heating element"""

    try:
        response = state.tekmatic.set_target_temperature(float(temperature))

        if activate:
            state.tekmatic.start_heater()
        else:
            state.tekmatic.stop_heater()

        if response == "":
            return StepResponse.step_succeeded()
        else:
            return StepResponse.step_failed(
                error="Set temperature action failed, unsuccessful response"
            )

    except Exception as e:
        print(f"Error in set_temperature action: {e}")
        return StepResponse.step_failed(error="Set temperature action failed")


# INCUBATE ACTION
@rest_module.action(
    name="incubate", description="Start incubation with optional shaking"
)
def incubate(
    state: State,
    action: ActionRequest,
    temperature: Annotated[
        float,
        "temperature in celsius to one decimal point. 0.0 - 80.0 are valid inputs, 22.0 default",
    ] = 22.0,
    shaker_frequency: Annotated[
        float,
        "shaker frequency in Hz (1Hz = 60rpm). 6.6-30.0 are valid inputs, default is 14.2 Hz",
    ] = 14.2,
    wait_for_incubation_time: Annotated[
        bool,
        "True if action should block until the specified incubation time has passed, False to continue immediately after starting the incubation",
    ] = False,
    incubation_time: Annotated[int, "Time to incubate in seconds"] = None,
) -> StepResponse:
    """Starts incubation at the specified temperature, optionally shakes, and optionally blocks all other actions until incubation complete"""

    # set the temperature and activate heating
    try:
        state.tekmatic.set_target_temperature(temperature)
        state.tekmatic.start_heater()
    except Exception as e:
        print(f"Error in incubate action: {e}")
        return StepResponse.step_failed(
            error="Failed to set temperature in incubate action"
        )

    try:
        state.tekmatic.set_shaker_parameters(frequency=shaker_frequency)
        state.tekmatic.start_shaker()
    except Exception as e:
        print(f"Error in incubate action: {e}")
        return StepResponse.step_failed(
            error=f"Failed to set shaker parameters or start shaking in incubate action: {traceback.format_exc()}"
        )

    if not wait_for_incubation_time:
        return StepResponse.step_succeeded()
    else:
        incubation_seconds_completed = 0
        total_incubation_seconds = None
        if incubation_time:
            total_incubation_seconds = incubation_time

        print(f"Incubation action: Starting incubation for {incubation_time} seconds")

        while incubation_seconds_completed < total_incubation_seconds:
            time.sleep(1)
            incubation_seconds_completed += 1
            state.incubation_seconds_remaining = (
                total_incubation_seconds - incubation_seconds_completed
            )

        # reset the incubation_time_remaining variable for next actions
        state.incubation_seconds_remaining = 0

        # stop shaking after incubation complete
        state.tekmatic.stop_shaker()

        print("Incubation action: Incubation complete")

        return StepResponse.step_succeeded()


# ****************#
# *Admin Commands*#
# ****************#

"""
To add support for custom admin actions, uncomment one or more of the
functions below.
By default, a module supports SHUTDOWN, RESET, LOCK, and UNLOCK modules. This can be overridden by using the decorators below, or setting a custom Set for python_rest_module.admin_commands
"""

# @tekmatic_incubator_module.pause    # TODO: implement
# def pause(state: State):
#     """Support pausing actions on this module"""
#     pass

# @tekmatic_incubator_module.resume    # TODO: implement
# def resume(state: State):
#     """Support resuming actions on this module"""
#     pass

# @rest_module.cancel   # TODO: implement
# def cancel(state: State):
#     """Support cancelling actions on this module"""
#     pass

# default LOCK and UNLOCK actions are sufficient


@rest_module.reset
def reset(state: State):
    """Support resetting the module.
    This should clear errors and reconnect to/reinitialize the device, if possible"""
    # TODO: test
    state.tekmatic.reset_device()
    state.tekmatic.initialize()


# *This runs the arg_parser, startup lifecycle method, and starts the REST server
if __name__ == "__main__":
    rest_module.start()
