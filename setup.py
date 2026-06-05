"""py2app build script for MötesMochi."""

from setuptools import setup

APP = ["app.py"]

OPTIONS = {
    "argv_emulation": False,        # must be False for menubar apps
    "iconfile": None,               # add an .icns file path here if you have one
    "plist": {
        "CFBundleName": "MötesMochi",
        "CFBundleDisplayName": "MötesMochi",
        "CFBundleIdentifier": "com.motesmochi.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0",
        "LSUIElement": True,        # hide from Dock — menubar-only
        "NSUserNotificationAlertStyle": "alert",
        "NSCalendarsUsageDescription": "MötesMochi reads your Google Calendar.",
    },
    "packages": [
        "rumps",
        "google",
        "google.auth",
        "google.oauth2",
        "google.auth.transport",
        "google_auth_oauthlib",
        "googleapiclient",
    ],
}

setup(
    app=APP,
    name="MötesMochi",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
