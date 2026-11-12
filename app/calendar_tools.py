"""Google Calendar tools the assistant can call.

Event titles follow the dashboard convention "[Unit] Judul", with a trailing
"!" marking high priority, e.g. "[Neksa] Rapat direksi !".
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from anthropic import beta_tool
from google.oauth2 import service_account
from googleapiclient.discovery import build

from app import config

_SCOPES = ["https://www.googleapis.com/auth/calendar"]
_service = None


def _calendar():
    global _service
    if _service is None:
        creds = service_account.Credentials.from_service_account_info(
            config.GOOGLE_SERVICE_ACCOUNT_INFO, scopes=_SCOPES
        )
        _service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return _service


@beta_tool
def list_events(start_date: str, days: int = 1) -> str:
    """List calendar events starting on a date.

    Args:
        start_date: First day to list, in YYYY-MM-DD (Asia/Jakarta).
        days: Number of days to include, 1 to 31.
    """
    tz = ZoneInfo(config.TIMEZONE)
    start = datetime.fromisoformat(start_date).replace(tzinfo=tz)
    end = start + timedelta(days=max(1, min(days, 31)))
    result = (
        _calendar()
        .events()
        .list(
            calendarId=config.GOOGLE_CALENDAR_ID,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=100,
        )
        .execute()
    )
    lines = []
    for event in result.get("items", []):
        when = event["start"].get("dateTime", event["start"].get("date"))
        lines.append(f"{when} | {event.get('summary', '(tanpa judul)')} | id={event['id']}")
    return "\n".join(lines) or "Tidak ada agenda."


@beta_tool
def create_event(title: str, start: str, end: str, description: str = "") -> str:
    """Create a calendar event.

    Args:
        title: Title in the form "[Unit] Judul", ending with " !" if high priority.
        start: Start time, ISO 8601 local time, e.g. 2026-11-16T10:00:00.
        end: End time, ISO 8601 local time.
        description: Optional notes.
    """
    body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start, "timeZone": config.TIMEZONE},
        "end": {"dateTime": end, "timeZone": config.TIMEZONE},
    }
    event = _calendar().events().insert(calendarId=config.GOOGLE_CALENDAR_ID, body=body).execute()
    return f"Dibuat: {event.get('summary')} ({start} - {end}), id={event['id']}"


TOOLS = [list_events, create_event]
