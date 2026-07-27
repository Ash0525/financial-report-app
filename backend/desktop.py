import threading
import time
import urllib.request
import socket
import uvicorn
import webview

from backend.main import app

# Make a flexible port
def find_available_port() -> int:
    # Ask macOS to select an available local network port

    # Create temporary local network socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as port_socket:

        # Port zero tells macOS to select an available port
        port_socket.bind((HOST, 0))

        # Selected port is second item in address
        return port_socket.getsockname()[1]

# Restrict server to this computer
HOST = "127.0.0.1"

# Identifies where the local server listens
PORT = find_available_port()

# Address displayed inside the desktop window
APP_URL = f"http://{HOST}:{PORT}"

# Configure a controllable Uvicorn server
SERVER = uvicorn.Server(
    uvicorn.Config(
        app=app,
        host=HOST,
        port=PORT,
        log_level="info",
    )
)


# Run FastAPI
def run_server() -> None:
    # Run FastAPI in the background

    SERVER.run()

# Stop server
def stop_server() -> None:
    # Request graceful shutdown

    SERVER.should_exit = True

# Wait for server, 10 second deadline, default
def wait_for_server(
    timeout_seconds: float = 10.0,
) -> None:
    # Wait until FastAPI is ready to receive requests.

    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            # Require the /health endpoint
            with urllib.request.urlopen(
                f"{APP_URL}/health",
                timeout=0.5,
            ) as response:
                # Returns when FastAPI responds
                if response.status == 200:
                    return

        except OSError:
            time.sleep(0.1)

    # Raise an error only after the complete waiting period expires.
    raise RuntimeError("The local server did not start in time")


def main() -> None:
    # Start the local server and open the desktop window

    # Create background thread for FastAPI
    server_thread = threading.Thread(
        target=run_server,
        daemon=True,
        name="fastapi-server",
    )

    # Start server
    server_thread.start()

    try:
        # Wait for server
        wait_for_server()

        # Create native desktop window
        window = webview.create_window(
            title="Financial Report App",
            url=APP_URL,
            width=1200,
            height=800,
            min_size=(900, 600),
        )

        # Ask Uvicorn to shutdown when window closes
        window.events.closed += stop_server

        # Start the native macOS window loop
        webview.start()

    finally:
        # Always runs even if startup raises an error
        stop_server()

        # Wait to finish shutdown
        server_thread.join(timeout=5.0)


if __name__ == "__main__":
    # Run desktop launcher when this file is executed
    main()
