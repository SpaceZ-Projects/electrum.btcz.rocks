
import time
from threading import Event
import argparse
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


class WebServer:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port

        self.www_path = os.path.join(os.path.dirname(__file__), "www")
        self.static_path = os.path.join(self.www_path, "static")

        self.app = FastAPI()

        self._setup_static()


    def _setup_static(self):
        self.app.mount(
            "/static",
            StaticFiles(directory=self.static_path),
            name="static"
        )

        self.app.mount(
            "/static/wheels",
            StaticFiles(directory=os.path.join(self.static_path, "wheels")),
            name="wheels"
        )

        @self.app.get("/")
        async def index():
            return FileResponse(os.path.join(self.www_path, "index.html"))

        @self.app.get("/index.html")
        async def index_html():
            return FileResponse(os.path.join(self.www_path, "index.html"))
        
        @self.app.get("/{full_path:path}")
        async def catch_all(full_path: str):
            file_path = os.path.join(self.www_path, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(self.www_path, "index.html"))


    def start(self):
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )



if __name__ == "__main__":
    rpc = None
    app = None
    syncer = None
    event = Event()

    try:
        parser = argparse.ArgumentParser(description="Start the server")
        parser.add_argument("--host")
        parser.add_argument("--port", type=int)
        args = parser.parse_args()
        if args.host:
            host = args.host
        if args.port:
            port = args.port

        app = WebServer()

        app.start()

        while not event.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print("[INFO] Stopping application...")
        event.set()