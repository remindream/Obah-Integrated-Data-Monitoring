import json
import os


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Environment variable {name} belum diisi")
    return value


ANTHROPIC_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
WA_ACCESS_TOKEN = _required("WA_ACCESS_TOKEN")
WA_APP_SECRET = _required("WA_APP_SECRET")
WA_PHONE_NUMBER_ID = _required("WA_PHONE_NUMBER_ID")
WA_VERIFY_TOKEN = _required("WA_VERIFY_TOKEN")
GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v23.0")
# The owner is the only number that may read or change the personal calendar.
OWNER_WA_NUMBER = _required("OWNER_WA_NUMBER")
# Admins get business data only, never the owner's personal agenda.
ADMIN_WA_NUMBERS = {
    n.strip() for n in os.environ.get("ADMIN_WA_NUMBERS", "").split(",") if n.strip()
} - {OWNER_WA_NUMBER}
GOOGLE_SERVICE_ACCOUNT_INFO = json.loads(_required("GOOGLE_SERVICE_ACCOUNT_JSON"))
GOOGLE_CALENDAR_ID = _required("GOOGLE_CALENDAR_ID")
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Jakarta")
