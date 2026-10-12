"""Tank Game launcher entrypoint."""

import sys
from pathlib import Path

# Add src to sys.path for direct launcher script execution
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from tank_game.__main__ import run_launcher

if __name__ == "__main__":
    run_launcher()
