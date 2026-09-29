import os
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH, override=True)
else:
    load_dotenv()

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key and os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH, override=True)
        key = os.getenv("GEMINI_API_KEY", "")
    return (key or "").strip()

def set_gemini_api_key(new_key: str) -> None:
    cleaned = (new_key or "").strip()
    os.environ["GEMINI_API_KEY"] = cleaned
    try:
        if not os.path.exists(ENV_PATH):
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.write(f"GEMINI_API_KEY={cleaned}\nPORT={PORT}\nHOST={HOST}\n")
        else:
            set_key(ENV_PATH, "GEMINI_API_KEY", cleaned)
    except Exception:
        # Fallback file rewrite
        lines = []
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
        found = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={cleaned}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"GEMINI_API_KEY={cleaned}\n")
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

# Module-level variable for backwards compatibility
class _ConfigProxy:
    @property
    def GEMINI_API_KEY(self) -> str:
        return get_gemini_api_key()

_proxy = _ConfigProxy()
GEMINI_API_KEY = get_gemini_api_key()

