import os
from dotenv import load_dotenv

load_dotenv()

def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    return int(v) if v and v.isdigit() else default

CREW_VERBOSE = env_int("CREW_VERBOSE", 0)