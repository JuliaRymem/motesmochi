#!/usr/bin/env python3
"""MötesMochi — Google Calendar menubar app for macOS."""

import os
import sys
import json
import datetime
import threading
import webbrowser

import rumps
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

CREDENTIALS_FILE = os.path.expanduser("~/.motesmochi/credentials.json")
TOKEN_FILE = os.path.expanduser("~/.motesmochi/token.json")
PREFS_FILE = os.path.expanduser("~/.motesmochi/prefs.json")
ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

CHARACTERS = [
    ("vanilla",  "Vanilla"),
    ("sakura",   "Sakura"),
    ("matcha",   "Matcha"),
    ("sushi",    "Sushi"),
    ("cloud",    "Cloud"),
    ("kinoko",   "Kinoko"),
    ("shiro",    "Shiro"),
    ("neko",     "Neko"),
    ("fuusen",   "Fuusen"),
    ("yoru",     "Yoru"),
]

POLL_INTERVAL = 60          # seconds between calendar checks
NOTIFY_AHEAD_MINUTES = 5    # minutes before meeting to send notification
SHOW_UPCOMING_MINUTES = 10  # window for "upcoming" meetings


def ensure_config_dir():
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)


def load_prefs():
    try:
        with open(PREFS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_prefs(prefs):
    ensure_config_dir()
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f)


def icon_path(name):
    return os.path.join(ICONS_DIR, f"{name}.png")


def get_credentials():
    """Return valid OAuth2 credentials, refreshing or re-authorizing as needed."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except Exception:
            pass  # fall through to re-auth

    if not os.path.exists(CREDENTIALS_FILE):
        return None

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    return creds


def _save_token(creds):
    ensure_config_dir()
    with open(TOKEN_FILE, "w") as fh:
        fh.write(creds.to_json())


def fetch_upcoming_events(creds):
    """Return a list of calendar events starting in the next SHOW_UPCOMING_MINUTES."""
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    now = datetime.datetime.utcnow()
    window_end = now + datetime.timedelta(minutes=SHOW_UPCOMING_MINUTES)

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat() + "Z",
            timeMax=window_end.isoformat() + "Z",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return result.get("items", [])


def event_start_dt(event):
    """Return a timezone-aware datetime for the event start."""
    start = event["start"]
    raw = start.get("dateTime") or start.get("date")
    if "T" in raw:
        # dateTime — may or may not have timezone offset
        dt = datetime.datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    # all-day event — treat as midnight UTC
    date = datetime.date.fromisoformat(raw)
    return datetime.datetime(date.year, date.month, date.day,
                             tzinfo=datetime.timezone.utc)


def meet_link(event):
    """Extract a Google Meet URL from the event if present."""
    # Check conferenceData
    conf = event.get("conferenceData", {})
    for ep in conf.get("entryPoints", []):
        if ep.get("entryPointType") == "video":
            return ep.get("uri")
    # Fallback: scan description and location for meet.google.com links
    for field in (event.get("description", ""), event.get("location", "")):
        if field and "meet.google.com" in field:
            for token in field.split():
                if "meet.google.com" in token:
                    return token.strip()
    return None


class MötesMochi(rumps.App):
    def __init__(self):
        prefs = load_prefs()
        self._character = prefs.get("character", "vanilla")
        initial_icon = icon_path(self._character)
        super().__init__("", icon=initial_icon, quit_button=None)
        self.title = ""  # icon only, no text
        self._creds = None
        self._notified = set()
        self._next_event = None

        self.next_meeting_item = rumps.MenuItem(
            "No upcoming meetings", callback=self._open_meet
        )
        self.refresh_item = rumps.MenuItem("Refresh", callback=self._refresh)

        # Character picker submenu
        character_menu = rumps.MenuItem("Välj karaktär")
        for key, label in CHARACTERS:
            item = rumps.MenuItem(label, callback=self._pick_character)
            item._character_key = key
            character_menu.add(item)

        self.quit_item = rumps.MenuItem("Quit MötesMochi", callback=rumps.quit_application)

        self.menu = [
            self.next_meeting_item,
            None,
            self.refresh_item,
            character_menu,
            None,
            self.quit_item,
        ]

        threading.Thread(target=self._init_auth, daemon=True).start()

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _init_auth(self):
        ensure_config_dir()
        if not os.path.exists(CREDENTIALS_FILE):
            rumps.notification(
                "MötesMochi",
                "Setup required",
                "Place your credentials.json in ~/.motesmochi/ and restart.",
                sound=False,
            )
            self._set_menu_title("⚙️ Setup needed")
            return

        self._creds = get_credentials()
        if self._creds:
            self._do_refresh()
        else:
            self._set_menu_title("❌ Auth failed")

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    @rumps.timer(POLL_INTERVAL)
    def _poll(self, _sender):
        if self._creds:
            threading.Thread(target=self._do_refresh, daemon=True).start()

    def _do_refresh(self):
        try:
            # Refresh creds if needed
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
                _save_token(self._creds)

            events = fetch_upcoming_events(self._creds)
            self._process_events(events)
        except HttpError as exc:
            self._set_menu_title("⚠️ Calendar error")
            print(f"[MötesMochi] Calendar API error: {exc}", file=sys.stderr)
        except Exception as exc:
            print(f"[MötesMochi] Unexpected error: {exc}", file=sys.stderr)

    def _process_events(self, events):
        now = datetime.datetime.now(datetime.timezone.utc)

        if not events:
            self._next_event = None
            self._set_menu_title("No meetings soon")
            return

        # Pick soonest event
        next_ev = events[0]
        self._next_event = next_ev
        start = event_start_dt(next_ev)
        minutes_away = (start - now).total_seconds() / 60
        title = next_ev.get("summary", "Untitled meeting")
        local_start = start.astimezone().strftime("%H:%M")

        label = f"{title} @ {local_start}"
        self._set_menu_title(f"🍡 {label}")

        # Send notification once per event when within NOTIFY_AHEAD_MINUTES
        event_id = next_ev.get("id", "")
        if (
            0 <= minutes_away <= NOTIFY_AHEAD_MINUTES
            and event_id not in self._notified
        ):
            self._notified.add(event_id)
            link_hint = " — Meet link in menu" if meet_link(next_ev) else ""
            rumps.notification(
                "MötesMochi 🍡",
                f"Meeting in {int(minutes_away)} min",
                f"{title} starts at {local_start}{link_hint}",
            )

        # Prune old notification IDs to avoid unbounded growth
        if len(self._notified) > 200:
            self._notified = set(list(self._notified)[-100:])

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _set_menu_title(self, text):
        """Update the dropdown label (first menu item) on the main thread."""
        self.next_meeting_item.title = text

    def _open_meet(self, _sender):
        if self._next_event:
            url = meet_link(self._next_event)
            if url:
                webbrowser.open(url)
            else:
                rumps.alert("No Meet link", "This event has no Google Meet link.")
        else:
            rumps.alert("No upcoming meetings", "Nothing scheduled in the next 10 minutes.")

    def _refresh(self, _sender):
        if not self._creds:
            threading.Thread(target=self._init_auth, daemon=True).start()
        else:
            threading.Thread(target=self._do_refresh, daemon=True).start()

    def _pick_character(self, sender):
        self._character = sender._character_key
        self.icon = icon_path(self._character)
        self.title = ""
        prefs = load_prefs()
        prefs["character"] = self._character
        save_prefs(prefs)


if __name__ == "__main__":
    MötesMochi().run()
