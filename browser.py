"""
Steel.dev cloud browser session handling, shared by every part of Verity that needs to
actually visit a page.
"""

import os
import sys
from contextlib import contextmanager

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from steel import Steel

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

STEEL_API_KEY = os.environ["STEEL_API_KEY"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]


@contextmanager
def steel_page(label="", quiet=False):
    """Opens one Steel cloud browser and yields a Playwright page for it, releasing the
    session on the way out no matter what happened inside."""
    client = Steel(steel_api_key=STEEL_API_KEY)
    session = client.sessions.create()
    if not quiet:
        suffix = f" [{label}]" if label else ""
        print(f"  Steel session{suffix}: {session.session_viewer_url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                f"wss://connect.steel.dev?apiKey={STEEL_API_KEY}&sessionId={session.id}"
            )
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            try:
                yield page
            finally:
                browser.close()
    finally:
        client.sessions.release(session.id)
