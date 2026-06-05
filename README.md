# MötesMochi 🍡

A Mac menubar app that watches your Google Calendar and nudges you before meetings.

- **🍡 icon** lives in the menubar — no Dock clutter
- Shows the next meeting title + time in the dropdown
- Sends a native macOS notification **5 minutes before** each meeting
- Clicking the meeting item opens its Google Meet link (if available)
- Polls Google Calendar every **60 seconds**

---

## Prerequisites

- macOS 12+
- Python 3.9+
- A Google account with Google Calendar

---

## 1 — Get Google Calendar API credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services → Library**, search for **Google Calendar API**, and click **Enable**.
4. Go to **APIs & Services → OAuth consent screen**:
   - Choose **External** (or Internal if you're in a Workspace org).
   - Fill in App name (`MötesMochi`), support email, and developer email.
   - Under **Scopes**, add `.../auth/calendar.readonly`.
   - Add your own Google account as a **Test user**.
   - Save and continue through all steps.
5. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**
   - Name: `MötesMochi`
   - Click **Create**.
6. Download the JSON file — click the ⬇ download icon next to the credential.
7. Move/rename it to:

```
~/.motesmochi/credentials.json
```

```sh
mkdir -p ~/.motesmochi
mv ~/Downloads/client_secret_*.json ~/.motesmochi/credentials.json
```

---

## 2 — Install & run

```sh
# Clone or cd into the project folder
cd motesmochi

# Create venv, install dependencies
make install

# Run the app (opens a browser for OAuth on first launch)
make run
```

On **first run**, a browser window will open asking you to sign in with Google and grant calendar read access. After approving, a `token.json` is saved to `~/.motesmochi/` and the app never asks again (unless the token is revoked).

---

## 3 — Build a standalone .app

```sh
make build
# → dist/MötesMochi.app
```

Drag `dist/MötesMochi.app` to `/Applications` and launch it like any other Mac app. It will start in the menubar with no Dock icon.

### Auto-launch on login (optional)

```
System Settings → General → Login Items → add MötesMochi.app
```

---

## File layout

```
motesmochi/
├── app.py            # main application
├── requirements.txt  # Python dependencies
├── setup.py          # py2app packaging config
├── Makefile          # install / run / build
└── README.md

~/.motesmochi/
├── credentials.json  # ← you place this here (never commit it)
└── token.json        # auto-generated after first OAuth flow
```

---

## Configuration

Edit the constants at the top of `app.py`:

| Constant | Default | Description |
|---|---|---|
| `POLL_INTERVAL` | `60` | Seconds between calendar checks |
| `NOTIFY_AHEAD_MINUTES` | `5` | Minutes before meeting to notify |
| `SHOW_UPCOMING_MINUTES` | `10` | Look-ahead window for "next meeting" |

---

## Troubleshooting

**"Setup required" notification on launch**
→ `~/.motesmochi/credentials.json` is missing. Follow step 1 above.

**"Calendar error" in menubar**
→ Check your internet connection. The token may have expired — delete `~/.motesmochi/token.json` and rerun `make run` to re-authenticate.

**No notifications appearing**
→ Go to System Settings → Notifications → MötesMochi and make sure notifications are allowed.

**py2app build fails with `ModuleNotFoundError`**
→ Add the missing module to the `packages` list in `setup.py` and rebuild.
