from __future__ import annotations
import logging, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s • %(levelname)s • %(name)s • %(message)s",
)

__version__ = "0.1.0"
