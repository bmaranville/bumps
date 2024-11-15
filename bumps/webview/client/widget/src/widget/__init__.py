import asyncio
import importlib.metadata
import pathlib
from concurrent.futures import ThreadPoolExecutor


import anywidget
import traitlets

try:
    __version__ = importlib.metadata.version("widget")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class Widget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "style.css"
    _server = None
    value = traitlets.Int(0).tag(sync=True)

    def __init__(self, server=None, **kwargs):
        super().__init__(**kwargs)
        self._server = server
        self._server.connect(self)

    @anywidget.experimental.command
    def _asyncEmit(self, msg, buffers):
        return self._server.handle_async_emit(msg, buffers), buffers
    
    def emit(self, topic, message):
        # print("Emitting", dict(topic=topic, message=message))
        self.send({"type": "emit", "topic": topic, "message": message})


