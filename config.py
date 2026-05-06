from pathlib import Path
import os

APP_TITLE = "An Optimal Samples Selection System"
WINDOW_WIDTH = 1360
WINDOW_HEIGHT = 820

DB_PATH = "data/results.db"
DB_FILENAME = "results.db"

MIN_M = 45
MAX_M = 54
MIN_N = 7
MAX_N = 25
MIN_K = 4
MAX_K = 7
MIN_S = 3
MAX_S = 7

DEFAULT_M = 45
DEFAULT_N = 8
DEFAULT_K = 6
DEFAULT_J = 4
DEFAULT_S = 4


def get_default_params() -> dict[str, int]:
    return {
        "m": DEFAULT_M,
        "n": DEFAULT_N,
        "k": DEFAULT_K,
        "j": DEFAULT_J,
        "s": DEFAULT_S,
    }


def _resolve_android_data_directory() -> Path | None:
    try:
        from kivy.app import App  # type: ignore
    except Exception:
        App = None

    if App is not None:
        running_app = App.get_running_app()
        if running_app is not None:
            return Path(running_app.user_data_dir)

    android_argument = os.environ.get("ANDROID_ARGUMENT")
    if android_argument:
        return Path(android_argument)

    return None


def resolve_data_directory() -> Path:
    android_directory = _resolve_android_data_directory()
    if android_directory is not None:
        return android_directory
    return Path(__file__).resolve().parent


def get_db_path() -> str:
    data_directory = resolve_data_directory()
    if data_directory == Path(__file__).resolve().parent:
        return str(data_directory / DB_PATH)
    return str(data_directory / DB_FILENAME)
