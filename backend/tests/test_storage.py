import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend import storage


class ApplicationDataDirectoryTests(unittest.TestCase):
    def test_environment_variable_overrides_default_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(
                "os.environ",
                {
                    storage.DATA_DIRECTORY_ENVIRONMENT_VARIABLE:
                        temporary_directory
                },
            ):
                data_directory = storage.get_application_data_directory()

        self.assertEqual(data_directory, Path(temporary_directory))

    def test_macos_uses_application_support(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("backend.storage.sys.platform", "darwin"),
            patch(
                "backend.storage.Path.home",
                return_value=Path("/Users/example"),
            ),
        ):
            data_directory = storage.get_application_data_directory()

        self.assertEqual(
            data_directory,
            Path(
                "/Users/example/Library/Application Support/"
                "Financial Report App"
            ),
        )


if __name__ == "__main__":
    unittest.main()
