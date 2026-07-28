import socket
import threading
import time
import urllib.request

import uvicorn
import webview

from backend.main import app

# Restrict the server to this computer.
HOST = "127.0.0.1"


def find_available_port(host: str = HOST) -> int:
    """Ask the operating system to select an available local port."""

    # Create temporary local network socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as port_socket:
        # Port zero tells macOS to select an available port
        port_socket.bind((host, 0))

        # Selected port is second item in address
        return port_socket.getsockname()[1]


def run_server(server: uvicorn.Server) -> None:
    """Run FastAPI in the background."""

    server.run()


def stop_server(server: uvicorn.Server) -> None:
    """Request a graceful shutdown of the local server."""

    server.should_exit = True


def configure_webview() -> None:
    """Configure desktop-window behavior before creating the window."""

    # Allow attachment responses to use macOS file downloads.
    webview.settings["ALLOW_DOWNLOADS"] = True


def wait_for_server(
    app_url: str,
    timeout_seconds: float = 10.0,
) -> None:
    """Wait until FastAPI is ready to receive requests."""

    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                f"{app_url}/health",
                timeout=0.5,
            ) as response:
                if response.status == 200:
                    return

        except OSError:
            time.sleep(0.1)

    # Raise an error only after the complete waiting period expires.
    raise RuntimeError("The local server did not start in time")


def main() -> None:
    """Start the local server and open the desktop window."""

    # Resolve runtime resources only when the application is launched.
    port = find_available_port()
    app_url = f"http://{HOST}:{port}"
    configure_webview()
    server = uvicorn.Server(
        uvicorn.Config(
            app=app,
            host=HOST,
            port=port,
            log_level="info",
        )
    )

    # Create background thread for FastAPI
    server_thread = threading.Thread(
        target=run_server,
        args=(server,),
        daemon=True,
        name="fastapi-server",
    )

    # Start server
    server_thread.start()

    try:
        # Wait for server
        wait_for_server(app_url)

        # Create native desktop window
        window = webview.create_window(
            title="Financial Report App",
            url=app_url,
            width=1200,
            height=800,
            min_size=(900, 600),
        )

        # Ask Uvicorn to shutdown when window closes
        window.events.closed += lambda: stop_server(server)

        # Start the native macOS window loop
        webview.start()

    finally:
        # Always runs even if startup raises an error
        stop_server(server)

        # Wait to finish shutdown
        server_thread.join(timeout=5.0)


if __name__ == "__main__":
    # Run desktop launcher when this file is executed
    main()
