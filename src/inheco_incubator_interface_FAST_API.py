from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import threading
import argparse
import uvicorn

from inheco_incubator_interface import Interface


# from fastapi import FastAPI

# Singleton Interface instance
device_lock = threading.Lock()   # Q: do I need to do this here if it's in the driver?
device = None

app = FastAPI()

# Global or shared config
config = {}
# com_port = None

@app.get("/")
def read_root():
    return {"message": f"Running with device(s) on COM port {config['device']}"}

@app.on_event("startup")
async def startup_event():
    "Called on start up of the FAST API"
    global device
    with device_lock:
        try:
            device = Interface(config["device"])
            # TODO: intitialization should be called by each node on startup
        except Exception as e:
            raise(e)

@app.get("/initialize", summary="initializes incubator at specified stack_floor")
def initialize(stack_floor: int = Query(..., description="Stack floor number")):
    """Opens the door"""
    device.initialize_device(stack_floor=stack_floor)


# # DOOR ACTIONS  (Q: Why can't these be post actions?)
@app.get("/open_door", summary="opens the incubator door at specified stack_floor")
def open_door(stack_floor: int = Query(..., description="Stack floor number")):
    """Opens the door"""
    device.open_door(stack_floor=stack_floor)

@app.get("/close_door", summary="closes the incubator door at specified stack_floor")
def close_door(stack_floor: int = Query(..., description="Stack floor number")):
    """Closes the door"""
    device.close_door(stack_floor=stack_floor)















# from fastapi import FastAPI
# import argparse

# app = FastAPI()





def create_app(device: int):
    """Created the app and opens connection to the specified COM port"""
    global config
    config["device"] = device
    return app
    
    
    # com_port
    # com_port = device
    # return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host computer IP for the interface API")
    parser.add_argument("--device", type=str, default="COM5", help="COM Port for the incubator device(s)")
    parser.add_argument("--port", type=int, default=7000, help="Port to run FastAPI on")

    args = parser.parse_args()

    app = create_app(args.device)
    uvicorn.run(app, host=args.host, port=args.port)














# HEATER ACTIONS
# @app.get("/get_actual_temperature/{stack_floor}", summary = "Return the actual temperature of the incubator")



# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}





# @app.on_event("startup")
# def startup_event():
#     "Called on start up of the FAST API"
#     global device
#     with device_lock:
#         try:
#             device = Interface()
#             device.initialize_device()
#         except Exception as e:
#             raise(e)
#             # raise RuntimeError(f"Failed to initialize device: {e}")


