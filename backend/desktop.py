import threading
import time
import urllib.request

import uvicorn
import webview

from backend.main import app


# Restrict server to this computer
HOST = "127.0.0.1"

# Identifies where the local server listens
PORT = 8000

# Address displayed inside the desktop window
APP_URL = f"http://{HOST}:{PORT}"


# Run FastAPI
def run_server() -> None:
    # Run FastAPI locally for desktop application
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )

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

    # Wait for server
    wait_for_server()

    # Create native desktop window
    webview.create_window(
        title="Financial Report App",
        url=APP_URL,
        width=1200,
        height=800,
        min_size=(900, 600),
    )

    # Start the native macOS window loop
    webview.start()


if __name__ == "__main__":
    # Run desktop launcher when this file is executed
    main()
