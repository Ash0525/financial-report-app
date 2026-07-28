import unittest
from unittest.mock import MagicMock, patch

from backend import desktop


class DesktopLauncherTests(unittest.TestCase):
    def test_find_available_port_returns_bindable_port(self) -> None:
        """Port selection should request and return an OS-assigned port."""

        mock_socket = MagicMock()
        mock_socket.__enter__.return_value.getsockname.return_value = (
            desktop.HOST,
            54321,
        )

        with patch(
            "backend.desktop.socket.socket",
            return_value=mock_socket,
        ):
            port = desktop.find_available_port()

        mock_socket.__enter__.return_value.bind.assert_called_once_with(
            (desktop.HOST, 0)
        )
        self.assertEqual(port, 54321)

    def test_wait_for_server_returns_after_successful_health_check(
        self,
    ) -> None:
        """A successful health response should finish the wait."""

        response = MagicMock()
        response.status = 200

        response_context = MagicMock()
        response_context.__enter__.return_value = response

        with patch(
            "backend.desktop.urllib.request.urlopen",
            return_value=response_context,
        ) as mock_urlopen:
            desktop.wait_for_server(
                "http://127.0.0.1:54321",
                timeout_seconds=1.0,
            )

        mock_urlopen.assert_called_once_with(
            "http://127.0.0.1:54321/health",
            timeout=0.5,
        )

    def test_wait_for_server_retries_then_times_out(self) -> None:
        """An unavailable server should produce a clear timeout error."""

        with (
            patch(
                "backend.desktop.time.monotonic",
                side_effect=[0.0, 0.05, 0.2],
            ),
            patch(
                "backend.desktop.urllib.request.urlopen",
                side_effect=OSError("Server unavailable"),
            ) as mock_urlopen,
            patch("backend.desktop.time.sleep") as mock_sleep,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "The local server did not start in time",
            ):
                desktop.wait_for_server(
                    "http://127.0.0.1:54321",
                    timeout_seconds=0.1,
                )

        mock_urlopen.assert_called_once()
        mock_sleep.assert_called_once_with(0.1)

    def test_stop_server_requests_graceful_shutdown(self) -> None:
        """Stopping the desktop app should signal the Uvicorn server."""

        server = MagicMock()
        server.should_exit = False

        desktop.stop_server(server)

        self.assertTrue(server.should_exit)

    def test_configure_webview_enables_downloads(self) -> None:
        """The desktop window should allow attachment downloads."""

        original_setting = desktop.webview.settings.get("ALLOW_DOWNLOADS")
        desktop.webview.settings["ALLOW_DOWNLOADS"] = False
        try:
            desktop.configure_webview()

            self.assertTrue(
                desktop.webview.settings["ALLOW_DOWNLOADS"]
            )
        finally:
            desktop.webview.settings["ALLOW_DOWNLOADS"] = original_setting


if __name__ == "__main__":
    unittest.main()
