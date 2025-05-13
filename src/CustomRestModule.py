
import argparse
import importlib.metadata
import inspect
import os
import signal
import sys
import time
import traceback
import warnings
from contextlib import asynccontextmanager
from threading import Thread
from typing import Any, List, Optional, Set, Union

from fastapi import (
    APIRouter,
    BackgroundTasks,
    FastAPI,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.datastructures import State
from typing_extensions import Annotated, get_type_hints

from wei.types import ModuleStatus
from wei.types.module_types import (
    AdminCommands,
    ModuleAbout,
    ModuleAction,
    ModuleActionArg,
    ModuleActionFile,
    ModuleState,
)
from wei.types.step_types import ActionRequest, StepFileResponse, StepResponse
from wei.utils import pretty_type_repr

from wei.modules.rest_module import RESTModule




class CustomRESTModule(RESTModule):

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

        # custom
        dll_path: Optional[str] = None,
        device_id: Optional[int] = None,
        stack_floor: Optional[int] = None, 
        device: Optional[str] = None,

        about: Optional[ModuleAbout] = None,
        **kwargs,
    ):
        """Creates an instance of the RESTModule class"""


        print("USING CUSTOM INIT FUNCTION")

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
        # for key, value in kwargs.items():
        #     setattr(self, key, value)

        # * Set up the argument parser
        # if arg_parser:
        #     self.arg_parser = arg_parser
        # else:
        #     self.arg_parser = argparse.ArgumentParser(description=description)
        #     self.arg_parser.add_argument(
        #         "--host",
        #         type=str,
        #         default=self.host,
        #         help="Hostname or IP address to bind to (0.0.0.0 for all interfaces)",
        #     )
        #     self.arg_parser.add_argument(   # altered
        #         "--port",
        #         type=List[int],
        #         nargs="+",
        #         default=self.port,
        #         help="Hostname or IP address to bind to (0.0.0.0 for all interfaces)",
        #     )
        #     self.arg_parser.add_argument(
        #         "--alias",
        #         "--name",
        #         "--node_name",
        #         type=str,
        #         default=self.name,
        #         help="A unique name for this particular instance of this module",
        #     )

        #     # add default arguments
        #     self.arg_parser.add_argument(
        #         "--dll_path",
        #         type=str,
        #         help="path to incubator control dll (ComLib.dll)",
        #         default="C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll",
        #     )
        #     self.arg_parser.add_argument(
        #         "--device_id",
        #         type=int,
        #         help="device ID of the Inheco Incubator device ",
        #         default=2,
        #     )
        #     self.arg_parser.add_argument(
        #         "--stack_floor",
        #         type=int,
        #         help="stack floor of the Inheco Incubator device",
        #         default=0,
        #     )
        #     self.arg_parser.add_argument(
        #         "--device",
        #         type=str,
        #         help="Serial port for communicating with the device",
        #         default="COM5",
        #     )

        # args = self.arg_parser.parse_args()
        # print("PORT")
        # print(args.port)


    def start(self):
        """Starts the REST server-based module"""
        import uvicorn

        print("CUSTOM REST START BEING USED")

        # * Initialize the state object with all non-private attributes
        for attr in dir(self):
            if attr in ["start", "state", "app", "router"]:
                # * Skip wrapper- or server-only methods/attributes
                continue
            self.state.__setattr__(attr, getattr(self, attr))

        # * If arguments are passed, set them as state variables
        # args = self.arg_parser.parse_args()
        # for arg_name in vars(args):
        #     if (
        #         getattr(args, arg_name) is not None
        #     ):  # * Don't override already set attributes with None's
        #         self.state.__setattr__(arg_name, getattr(args, arg_name))
        self._configure_routes()

        # * Enforce a name
        if not self.state.name:
            raise Exception("A unique --name is required")
        uvicorn.run(self.app, host=self.state.host, port=self.state.port)



