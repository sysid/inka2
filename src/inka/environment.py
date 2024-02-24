import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).parent.parent.parent.absolute()

SKIP_WORDS = ("date", "datetime", "time", "timedelta", "list", "int")


class Environment(BaseSettings, extra="allow"):
    run_env: str = "local"
    log_level: str = "WARNING"

    def __init__(self, **values):
        super().__init__(**values)

    def log_config(self) -> dict:
        cfg = self.model_dump(mode="json")
        skip_keys = ()
        sanitized_cfg = {k: v for k, v in cfg.items() if k not in skip_keys}
        return sanitized_cfg


try:
    config = Environment()
except ValidationError as e:
    print(f"Error loading config: {e}")
    print("Make sure all required environment variables are set.")
    sys.exit(1)

if __name__ == "__main__":
    config = Environment()
