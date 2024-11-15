# from .main import setup_bumps
import asyncio
import functools
import threading
from typing import Any, Callable, Dict, Optional
from typing import Union, List
from pathlib import Path
import uuid

import matplotlib
matplotlib.use("agg")

import mimetypes
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/html", ".html")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/svg+xml", ".svg")

from . import api
from .fit_thread import EVT_FIT_PROGRESS
from .state_hdf5_backed import SERIALIZERS, UNDEFINED
from .logger import logger, list_handler, console_handler
from . import persistent_settings

TRACE_MEMORY = False

# can get by name and not just by id
logger.addHandler(console_handler)

# app = web.Application()
APPLICATION_NAME = "bumps"

class SocketServer:
    LISTENERS: set
    id: str
    thread: threading.Thread
    loop: asyncio.AbstractEventLoop

    def __init__(self):
        self.LISTENERS = set()
        self.id = uuid.uuid4().hex
        self.loop = None
        self.thread = None

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.thread = threading.Thread(target=self.loop.run_forever)
        self.thread.start()

    def stop(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()
            self.loop = None

    def connect(self, listener):
        self.LISTENERS.add(listener)
        for topic, contents in api.state.topics.items():
            message = contents[-1] if len(contents) > 0 else None
            if message is not None:
                listener.emit(topic, message)
        logger.info(f"connect {listener}")
        api.EMITTERS[self.id] = self.emit

    def disconnect(self, sid):
        logger.info(f"disconnect {sid}")

    async def emit(
        self,
        event: str,
        data: Optional[Any] = None,
        to: Optional[str] = None,
        room: Optional[str] = None,
        skip_sid: Optional[str] = None,
        namespace: Optional[str] = None,
        callback: Optional[Callable] = None,
        ignore_queue: bool = False):

        for listener in self.LISTENERS:
            # print("emitting: ", event, data, listener)
            listener.emit(event, data)


    async def set_base_path(self, sid: str, pathlist: List[str]):
        path = str(Path(*pathlist))
        persistent_settings.set_value("base_path", path, application=APPLICATION_NAME)

    async def disconnect_all_clients(self):
        # disconnect all clients:
        for listener in self.LISTENERS:
            listener.disconnect()

        self.LISTENERS = set()

    def handle_async_emit(self, content, buffers):
        message: str = content.get("message", None)
        payload: List = content.get("payload", [])
        if message in api.REGISTRY:
            action = api.REGISTRY[message]
            logger.debug(f"calling: {message} {payload}, loop: {id(self.loop)}")
            future = asyncio.run_coroutine_threadsafe(action(*payload), self.loop)
            return future.result()
        else:
            return f"Unknown method {message}"
        
    def enable_convergence_kernel_heartbeat(self):
        from comm import create_comm
        comm = create_comm(target_name="heartbeat")

        async def send_heartbeat_on_convergence(event: str, *args, **kwargs):
            if event == "updated_convergence":
                comm.send({"status": "alive"})

        api.EMITTERS["convergence_heartbeat"] = send_heartbeat_on_convergence


