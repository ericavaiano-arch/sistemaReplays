import os
from dotenv import load_dotenv

load_dotenv()


def _int(key: str, default: int) -> int:
    return int(os.getenv(key, default))


CAMERA_INDEX: int | None = int(os.getenv("CAMERA_INDEX")) if os.getenv("CAMERA_INDEX") else None
BUFFER_SECONDS: int = _int("BUFFER_SECONDS", 30)
FPS: int = _int("FPS", 30)

R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
R2_ENDPOINT: str = os.getenv("R2_ENDPOINT", "")
R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "soccer-replay")
R2_PUBLIC_URL: str = os.getenv("R2_PUBLIC_URL", "")
