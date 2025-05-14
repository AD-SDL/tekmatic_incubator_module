"""
REST-based node for Inheco Single Plate Incubators that interfaces with WEI
"""

import logging
import time
import traceback
from typing import Optional
import requests

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

from inheco_incubator_interface import Interface

# create logger
logger = logging.getLogger(__name__)

# create rest module
rest_module = RESTModule(
    name="inheco_incubator_module",
    version="0.0.1",
    description="A REST node to control Inheco Single Plate Incubators",
    model="inheco",
)

rest_module.arg_parser.add_argument(
    "--device_id",
    type=int,
    help="device ID of the Inheco Incubator device ",
    default=2,
)
rest_module.arg_parser.add_argument(
    "--stack_floor",
    type=int,
    help="stack floor of the Inheco Incubator device",
    default=0,
)
rest_module.arg_parser.add_argument(
    "--interface_host",
    type=str,
    help="Inheco Interface FastAPI server host",
    default = "127.0.0.0",
)
rest_module.arg_parser.add_argument(
    "--interface_port",
    type=int,
    help="Inheco Interface FastAPI server port",
    default=7000, # TODO:  pick a better default
)

# parse the arguments
args = rest_module.arg_parser.parse_args()


# configure urls for connection to Interface API
# base_url = f"https://{args.host}:{args.port}"


# format logging file based on device id
logging.basicConfig(
    filename=f"inheco_deviceID{args.device_id}_stackFloor{args.stack_floor}.log",
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s')

@rest_module.startup()
def inheco_startup(state: State):
    """Initializes the inheco interface and opens the COM connection"""
    state.is_incubating_only = False
    state.incubation_seconds_remaining = 0
    state.stack_floor = args.stack_floor

    logger.info("startup called")

    # configure urls for connection to Interface API
    state.base_url = f"http://{args.interface_host}:{args.interface_port}"   # NOTE: does not work with https???
    print(f"base_url: {state.base_url}")

    response = send_request(
        base_url=state.base_url,
        action_string="initialize",
        stack_floor=state.stack_floor)

    print(response) # TESTING

    logger.info("startup complete")


   


def send_request(base_url, action_string, stack_floor, arguments=None):
    "Send the http requests"
    response = None
    try:
        endpoint = f"/{action_string}?stack_floor={args.stack_floor}"
        request_url = f"{base_url}{endpoint}"
        print("request url")
        print(request_url)
        response = requests.get(request_url)
        response.raise_for_status()
    except Exception as e:
        raise e
    return response


# TODO: COM port connection should be shut down separately from the node now
# @rest_module.shutdown()
# def inheco_shutdown(state: State):
#     """Handles cleaning up the incubaotr object. This is also an admin action"""
#     logger.info("shutdown called")
#     if state.incubator is not None:
#         state.incubator.close_connection()
#         del state.incubator
#     logger.info("shutdown complete")

# @rest_module.state_handler()   # TODO: How do I check if the COM connection is busy now
# def inheco_state_handler(state: State) -> ModuleState:
#     """Returns the state of the Inheco device and module"""
#     incubator: Optional[Interface] = state.incubator

#     if incubator is None:
#         return ModuleState(
#             status=state.status,
#             error=state.error,
#         )

#     if not incubator.is_busy or (incubator.is_busy and state.is_incubating_only):
#         # query for fresh state details and save to cache
#         logger.debug("querying fresh state")
#         state.cached_current_shaker_active = incubator.is_shaker_active()
#         state.cached_current_heater_active = incubator.is_heater_active()
#         state.cached_current_actual_temperature = incubator.get_actual_temperature()
#         state.cached_current_target_temperature = incubator.get_target_temperature()
#     else:
#         logger.debug("using cached state")

#     # if the shaker is actually busy, the previous cashed values will be returned
#     return ModuleState.model_validate(
#         {
#             "status": state.status,
#             "error": state.error,
#             "target_temp": state.cached_current_target_temperature,
#             "actual_temp": state.cached_current_actual_temperature,
#             "shaker_active": state.cached_current_shaker_active,
#             "heater_active": state.cached_current_heater_active,
#             "incubation_seconds_remaining": state.incubation_seconds_remaining,
#         }
#     )


# OPEN TRAY ACTION
@rest_module.action(name="open", description="Open the plate tray")
def open(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Opens the Inheco incubator tray"""

    # disable the shaker if shaking
    # logger.info("open called")
    # if state.cached_current_shaker_active:
    #     state.incubator.disable_shaker()
    # state.incubator.open_door()
    # logger.info("open complete")
    print("open door called")
    logger.info("open called")
    # TODO: disable the shaker if shaking
    response = send_request(state.base_url, action_string="open_door", stack_floor=state.stack_floor)
    print(response)  # TESTING
    logger.debug(response)
    logger.info("open complete")

    return StepResponse.step_succeeded()


# CLOSE TRAY ACTION
@rest_module.action(name="close", description="Close the plate tray")
def close(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Closes the Tekmatic incubator tray"""

    logger.info("close called")
    # state.incubator.close_door()
    response = send_request(state.base_url, action_string="close_door", stack_floor=state.stack_floor)
    print(response)  # TESTING
    logger.debug(response)
    logger.info("close complete")

    return StepResponse.step_succeeded()


# # SET TEMP ACTION
# @rest_module.action(
#     name="set_temperature", description="Set target incubation temperature"
# )
# def set_temperature(
#     state: State,
#     action: ActionRequest,
#     temperature: Annotated[
#         float,
#         "temperature in Celsius to one decimal point. 0.0 - 80.0 are valid inputs, 22.0 default",
#     ] = 22.0,
#     activate: Annotated[
#         bool, "(optional) turn on heating/cooling element, on = True (default), off = False"
#     ] = True,
# ) -> StepResponse:
#     """Sets the temperature in Celsius on the Tekmatic incubator. If activate is set to False, heating element will turn off """

#     logger.info("set temperature called")
#     try:
#         response = state.incubator.set_target_temperature(float(temperature))

#         if activate:
#             state.incubator.start_heater()
#         else:
#             state.incubator.stop_heater()

#         if response == "":
#             logger.info("set temperature complete")
#             return StepResponse.step_succeeded()
#         else:
#             logger.error(f"Set temperature action failed, unsuccessful response: {response}")
#             return StepResponse.step_failed(
#                 error=f"Set temperature action failed, unsuccessful response: {response}"
#             )

#     except Exception as e:
#         logger.error(f"Error in set_temperature action: {e}")
#         logger.error(traceback.format_exc())
#         print(f"Error in set_temperature action: {e}")
#         return StepResponse.step_failed(error="Set temperature action failed")


# # INCUBATE ACTION
# @rest_module.action(
#     name="incubate", description="Start incubation with optional shaking"
# )
# def incubate(
#     state: State,
#     action: ActionRequest,
#     temperature: Annotated[
#         float,
#         "temperature in celsius to one decimal point. 0.0 - 80.0 are valid inputs, 22.0 default",
#     ] = 22.0,
#     shaker_frequency: Annotated[
#         float,
#         "shaker frequency in Hz (1Hz = 60rpm). 0 (no shaking) and 6.6-30.0 are valid inputs, default is 14.2 Hz",
#     ] = 14.2,
#     wait_for_incubation_time: Annotated[
#         bool,
#         "True if action should block until the specified incubation time has passed, False to continue immediately after starting the incubation",
#     ] = False,
#     incubation_time: Annotated[int, "Time to incubate in seconds"] = None,
# ) -> StepResponse:
#     """Starts incubation at the specified temperature, optionally shakes, and optionally blocks all other actions until incubation complete"""

#     logger.info("incubate called")
#     # set the temperature and activate heating
#     try:
#         state.incubator.set_target_temperature(temperature)
#         state.incubator.start_heater()
#         logger.info("heater set and started")
#     except Exception as e:
#         logger.error(f"Error starting heater in incubate action: {e}")
#         logger.error(traceback.format_exc())
#         print(f"Error starting heater in incubate action: {e}")
#         return StepResponse.step_failed(
#             error="Failed to set temperature in incubate action"
#         )

#     try:
#         if not shaker_frequency == 0:   # don't start the shaker if user sets shaker frequency to 0
#             state.incubator.set_shaker_parameters(frequency=shaker_frequency)
#             state.incubator.start_shaker()
#             logger.info("shaker set and started")
#     except Exception as e:
#         logger.error(f"Error starting shaker in incubate action: {e}")
#         logger.error(traceback.format_exc())
#         print(f"Error starting shaker in incubate action: {e}")
#         return StepResponse.step_failed(
#             error=f"Failed to set shaker parameters or start shaking in incubate action: {traceback.format_exc()}"
#         )

#     if not wait_for_incubation_time:
#         logger.info("incubate call complete - not waiting for incubation time")
#         return StepResponse.step_succeeded()
#     else:
#         logger.info("incubation call - waiting for incubation time to finish")
#         incubation_seconds_completed = 0
#         total_incubation_seconds = None
#         if incubation_time:
#             total_incubation_seconds = incubation_time

#         print(f"Incubation action: Starting incubation for {incubation_time} seconds")

#         while incubation_seconds_completed < total_incubation_seconds:
#             time.sleep(1)
#             incubation_seconds_completed += 1
#             state.incubation_seconds_remaining = (
#                 total_incubation_seconds - incubation_seconds_completed
#             )
#         logger.info("incubation time complete")

#         # reset the incubation_time_remaining variable for next actions
#         state.incubation_seconds_remaining = 0

#         # stop shaking after incubation complete
#         state.incubator.stop_shaker()

#         print("Incubation action: Incubation complete")

#         logger.info("incubation completes")
#         return StepResponse.step_succeeded()


# ****************#
# *Admin Commands*#
# ****************#

"""
To add support for custom admin actions, uncomment one or more of the
functions below.
By default, a module supports SHUTDOWN, RESET, LOCK, and UNLOCK modules. This can be overridden by using the decorators below, or setting a custom Set for python_rest_module.admin_commands
"""

# @rest_module.pause    # TODO: implement
# def pause(state: State):
#     """Support pausing actions on this module"""
#     pass

# @rest_module.resume    # TODO: implement
# def resume(state: State):
#     """Support resuming actions on this module"""
#     pass

# @rest_module.cancel   # TODO: implement
# def cancel(state: State):
#     """Support cancelling actions on this module"""
#     pass

# @rest_module.reset    # TODO: implement
# def reset(state: State):
#     """Support resetting the module.
#     This should clear errors and reconnect to/reinitialize the device, if possible"""
#     state.tekmatic.reset_device()
#     state.tekmatic.initialize()

# default LOCK and UNLOCK actions are sufficient






# *This runs the arg_parser, startup lifecycle method, and starts the REST server
if __name__ == "__main__":
    rest_module.start()