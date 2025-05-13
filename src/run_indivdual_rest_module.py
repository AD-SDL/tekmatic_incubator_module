"""
Callable REST node launcher for Inheco incubators.
This lets you start a REST node programmatically with custom configuration.
"""

import logging
import traceback
from starlette.datastructures import State
from typing import Optional
import time

from wei.modules.rest_module import RESTModule
from wei.types.module_types import ModuleState
from wei.types.step_types import ActionRequest, StepResponse

# Replace with actual Interface and CustomRESTModule in your code
from test_interface import Interface
from CustomRestModule import CustomRESTModule


def launch_rest_node(
    port: int,
    stack_floor: int,
    device_id: int,
    device: str = "COM5",
    dll_path: str = "C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll",
    host: str = "0.0.0.0",
):
    """
    Launch a REST node for the Inheco incubator using given parameters.

    :param port: Port to bind the REST server to
    :param stack_floor: Stack floor ID
    :param device_id: Device ID for the incubator
    :param device: COM port to use (e.g., COM5)
    :param dll_path: Path to the ComLib.dll
    :param host: Host address to bind to
    """

    # ------------------------
    # Logging Setup
    # ------------------------
    logging.basicConfig(
        filename=f"inheco_deviceID{device_id}_stackFloor{stack_floor}.log",
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logger = logging.getLogger(__name__)

    # ------------------------
    # Create the REST Module
    # ------------------------
    rest_module = CustomRESTModule(
        name=f"inheco_incubator_module_{stack_floor}",
        version="0.0.1",
        description="A REST node to control Inheco Single Plate Incubators",
        model="inheco",
        port=port,
        device=device,
        stack_floor=stack_floor,
        device_id=device_id,
        dll_path=dll_path,
        host=host,
    )

    @rest_module.startup()
    def inheco_startup(state: State):
        """Initializes the inheco interface and opens the COM connection"""
        logger.info("startup called")
        state.incubator = None
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





