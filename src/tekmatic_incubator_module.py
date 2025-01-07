"""
REST-based node for Tekmatic Single Plate Incubators that interfaces with WEI
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

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

# parse the arguments
args = rest_module.arg_parser.parse_args()


@rest_module.startup()
def custom_startup_handler(state: State):
    """
    Initializes the tekmatic interface and opens the COM connection
    """
    state.tekmatic_interface = tekmatic_incubator_interface.Interface()


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
    name="open", description="Open the tekmatic incubator plate tray"
)
def open(
    state: State,
    action: ActionRequest,
) -> StepResponse:
    """Opens the tekmatic incubator tray"""

    state.tekmatic.

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
