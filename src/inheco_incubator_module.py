"""
REST-based node for Inheco Single Plate Incubators that interfaces with WEI
"""

import logging
from typing import Optional

import argparse # testing

from starlette.datastructures import State
from wei.modules.rest_module import RESTModule

from inheco_incubator_interface import Interface

import argparse
import time
import traceback
from typing import Any, List, Optional, Set

from fastapi import (
    APIRouter,
    FastAPI,
)
from fastapi.datastructures import State

from wei.types.module_types import (
    AdminCommands,
    ModuleAbout,
    ModuleAction,
    ModuleState,
)

import multiprocessing


################################################################################################################################
# CUSTOM WEI REST NODE CLASS INIT (need to allow multiple port entries from user for multiple devices)
class CustomRESTModule(RESTModule):
    """
    Custom implementation of the WEI REST Node __init__ funtion to allow parsing multiple ports
    """
    def __init__(
        self,
        arg_parser: Optional[argparse.ArgumentParser] = None,
        description: str = "",
        model: Optional[str] = None,
        interface: str = "wei_rest_node",
        actions: Optional[List[ModuleAction]] = None,
        resource_pools: Optional[List[Any]] = None,
        admin_commands: Optional[Set[AdminCommands]] = None,
        name: Optional[str] = None,
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 2000,
        about: Optional[ModuleAbout] = None,
        **kwargs,
    ):
        """Creates an instance of the RESTModule class"""

        # TESTING
        print("USING THE CUSTOM REST CLASS INIT")
        self.app = FastAPI(lifespan=RESTModule._lifespan, description=description)
        self.app.state = State(state={})
        self.state = self.app.state  # * Mirror the state object for easier access
        self.router = APIRouter()

        # * Set attributes from constructor arguments
        self.name = name
        self.about = about
        self.host = host
        self.port = port
        self.description = description
        self.model = model
        self.interface = interface
        self.actions = actions if actions else []
        self.resource_pools = resource_pools if resource_pools else []
        self.admin_commands = admin_commands if admin_commands else set()
        self.admin_commands.add(AdminCommands.SHUTDOWN)

        # * Set any additional keyword arguments as attributes as well
        # * These will then get added to the state object
        for key, value in kwargs.items():
            setattr(self, key, value)

        # * Set up the argument parser
        if arg_parser:
            self.arg_parser = arg_parser
        else:
            self.arg_parser = argparse.ArgumentParser(description=description)
            self.arg_parser.add_argument(
                "--host",
                type=str,
                default=self.host,
                help="Hostname or IP address to bind to (0.0.0.0 for all interfaces)",
            )
            self.arg_parser.add_argument(
                "--port",
                type=int,
                nargs="+",
                default=self.port,
                help="Hostname or IP address to bind to (0.0.0.0 for all interfaces)",
            )
            self.arg_parser.add_argument(
                "--alias",
                "--name",
                "--node_name",
                type=str,
                default=self.name,
                help="A unique name for this particular instance of this module",
            )
##############################################################################################################

def start_rest_node(device: int, port: int, device_id: int, stack_floor: int):
    rest_module = CustomRESTModule(
        name = f"inheco_incubator_module_devID{device_id}_stackFloor{stack_floor}",
        version="0.0.1", 
        description = f"A REST node to control Inheco incubator with device ID {device_id} and stack floor {stack_floor}", 
        model = "inheco",
        port=port,
        device=device,
    )

# create logger
logger = logging.getLogger(__name__)

# create rest module
rest_module = CustomRESTModule(
    name="inheco_incubator_module",
    version="0.0.1",
    description="A REST node to control Inheco Single Plate Incubators",
    model="inheco",
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
    help="device ID of the Inheco Incubator device ",
    default=2,
)
rest_module.arg_parser.add_argument(
    "--stack_floor",
    type=int,
    nargs="+",
    help="stack floor of the Inheco Incubator device",
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



# format logging file based on device id
# logging.basicConfig(
#     filename=f"inheco_deviceID{args.device_id}.log",
#     level=logging.DEBUG,
#     format='%(asctime)s %(levelname)s %(name)s %(message)s')



@rest_module.startup()
def inheco_startup(state: State):
    """Initializes the inheco interface and opens the COM connection"""
    logger.info("startup called")
    state.incubator = None
    state.stack_floor = current_device_stack_floor
    state.incubator = Interface()
    state.incubator.initialize_device()
    state.is_incubating_only = False
    state.incubation_seconds_remaining = 0
    logger.info("startup complete")

@rest_module.shutdown()
def inheco_shutdown(state: State):
    """Handles cleaning up the incubaotr object. This is also an admin action"""
    logger.info("shutdown called")
    if state.incubator is not None:
        state.incubator.close_connection()
        del state.incubator
    logger.info("shutdown complete")

@rest_module.state_handler()
def inheco_state_handler(state: State) -> ModuleState:
    """Returns the state of the Inheco device and module"""
    incubator: Optional[Interface] = state.incubator

    if incubator is None:
        return ModuleState(
            status=state.status,
            error=state.error,
        )

    if not incubator.is_busy or (incubator.is_busy and state.is_incubating_only):
        # query for fresh state details and save to cache
        logger.debug("querying fresh state")
        state.cached_current_shaker_active = incubator.is_shaker_active()
        state.cached_current_heater_active = incubator.is_heater_active()
        state.cached_current_actual_temperature = incubator.get_actual_temperature()
        state.cached_current_target_temperature = incubator.get_target_temperature()
    else:
        logger.debug("using cached state")

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


# # OPEN TRAY ACTION
# @rest_module.action(name="open", description="Open the plate tray")
# def open(
#     state: State,
#     action: ActionRequest,
# ) -> StepResponse:
#     """Opens the Inheco incubator tray"""

#     # disable the shaker if shaking
#     logger.info("open called")
#     if state.cached_current_shaker_active:
#         state.incubator.disable_shaker()
#     state.incubator.open_door()
#     logger.info("open complete")
#     return StepResponse.step_succeeded()


# # CLOSE TRAY ACTION
# @rest_module.action(name="close", description="Close the plate tray")
# def close(
#     state: State,
#     action: ActionRequest,
# ) -> StepResponse:
#     """Closes the Tekmatic incubator tray"""

#     logger.info("close called")
#     state.incubator.close_door()
#     logger.info("close complete")
#     return StepResponse.step_succeeded()


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

    # rest_module = RESTModule(
    #     name="inheco_incubator_module",
    #     version="0.0.1",
    #     description="A REST node to control Inheco Single Plate Incubators",
    #     model="inheco",
    # )

    # create a local argument parser that mimics the WEI REST Node argument parser but allows for multiple inputs for some arguments
    local_arg_parser = argparse.ArgumentParser()

    # add arguments to local argument parser
    local_arg_parser.add_argument(
        "--dll_path",
        type=str,
        help="path to incubator control dll (ComLib.dll)",
        default="C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll",
    )
    local_arg_parser.add_argument(
        "--device_id",
        type=int,
        help="device ID of the Inheco Incubator device ",
        default=2,
    )
    local_arg_parser.add_argument(
        "--stack_floor",
        nargs='+',
        type=int,
        help="Integer(s) representing the stack floor(s) of the Inheco Incubator devices in one tower (on one COM port). Multiple stack floor integers should be separated by a space.",
        default=0,
    )
    local_arg_parser.add_argument(
        "--device",
        type=str,
        help="Serial port for communicating with the device",
        default="COM5",
    )
    local_arg_parser.add_argument(
        "--port",
        nargs='+',
        type=int,
        help="Port(s) for the inheco device(s) in order of stack floor specified in stack floor argument. Multiple ports should be separated by a space."
    )

    # TESTING args passed in by user
    # python .\source\repos\inheco_incubator_module\src\inheco_incubator_module.py --device "COM5" --dll_path "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll" --device_id 2 --stack_floor 1 --port 3006

    # Collect the args from local and pass them to the REST Node arg parser
    args = local_arg_parser.parse_args()
    print(args.stack_floor)
    print(args.port)


    # loop through for each floor provided
    for i in range(len(args.stack_floor)):
        # pass

        # set rest node variables for each device
        # rest_module.arg_parser = local_arg_parser
        rest_module.port = args.port[i]
        rest_module.device = args.device
        current_device_stack_floor = args.stack_floor[i]

        print(f"Port: {rest_module.port}")
        print(f"Device: {rest_module.device}")
        print(f"Stack floor: {current_device_stack_floor}")

        rest_module.start()



        # TESTING
        # print(rest_module.arg_parser.args.stack_floor)


    # # testing (print out the stack floor arguments)
    # args = rest_module.arg_parser.parse_args()
    # print(args.stack_floor)
    # print(args.port)


    # rest_module.start()
