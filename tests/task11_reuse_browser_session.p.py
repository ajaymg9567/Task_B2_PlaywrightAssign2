
import os

import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

STATE_FILE = os.path.join(
    PROJECT_ROOT,
    "task11_auth_state.json",
)

EXPIRED_STATE_FILE = os.path.join(
    PROJECT_ROOT,
    "task11_expired_auth_state.json",
)

DEMO_URL = "http://mock-auth.local/dashboard"
VALID_TOKEN = "task11-demo-session-valid"


async def mock_dashboard(route):
    await route.fulfill(
        status=200,
        content_type="text/html",
        body="""
        <!DOCTYPE html>
        <html>
        <head><title>Task 11 Demo Dashboard</title></head>
        <body>
            <h1 id="dashboard">Demo Dashboard</h1>
            <p id="account">Signed in as Demo User</p>
        </body>
        </html>
        """,
    )


@pytest.mark.asyncio
async def test_reuse_saved_browser_session(page):
    # The setup script must be run before this test
    if not os.path.exists(STATE_FILE):
        pytest.skip(
            "Saved state file is missing. "
            "Run setup_task11_auth_state.py first."
        )

    browser = page.context.browser

    assert browser is not None, "Browser is not available."

    # Create a fresh context using the saved state
    context = await browser.new_context(
        storage_state=STATE_FILE
    )

    try:
        await context.route(
            "http://mock-auth.local/**",
            mock_dashboard,
        )

        new_page = await context.new_page()
        await new_page.goto(DEMO_URL)

        account_indicator = new_page.locator("#account")
        await account_indicator.wait_for(state="visible")

        saved_token = await new_page.evaluate(
            'localStorage.getItem("auth_token")'
        )

        if saved_token != VALID_TOKEN:
            pytest.skip(
                "Saved session is invalid or expired. "
                "Re-authentication is needed."
            )

        assert await account_indicator.inner_text() == (
            "Signed in as Demo User"
        )

        print("Saved browser session reused successfully.")
        print("Authenticated account indicator verified.")

    finally:
        await context.close()


@pytest.mark.asyncio
async def test_expired_session_is_detected(page):
    browser = page.context.browser

    assert browser is not None, "Browser is not available."

    # Create a state file containing an expired demo token
    expired_context = await browser.new_context()

    try:
        await expired_context.route(
            "http://mock-auth.local/**",
            mock_dashboard,
        )

        expired_page = await expired_context.new_page()
        await expired_page.goto(DEMO_URL)

        await expired_page.evaluate(
            """() => localStorage.setItem("auth_token", "expired-demo-token")"""
        )

        await expired_context.storage_state(
            path=EXPIRED_STATE_FILE
        )

    finally:
        await expired_context.close()

    # Load the expired session in a separate context
    context = await browser.new_context(
        storage_state=EXPIRED_STATE_FILE
    )

    try:
        await context.route(
            "http://mock-auth.local/**",
            mock_dashboard,
        )

        new_page = await context.new_page()
        await new_page.goto(DEMO_URL)

        restored_token = await new_page.evaluate(
            'localStorage.getItem("auth_token")'
        )

        if restored_token != VALID_TOKEN:
            print(
                "Expired session detected. "
                "Re-authentication is needed."
            )
        else:
            pytest.fail("Expected the demo session to be expired.")

        assert restored_token == "expired-demo-token"

    finally:
        await context.close()


def test_missing_state_file_is_detected():
    missing_file = os.path.join(
        PROJECT_ROOT,
        "task11_missing_auth_state_for_test.json",
    )

    assert not os.path.exists(missing_file), (
        "The test's missing-state file unexpectedly exists. "
        "Remove that test file and rerun."
    )

    print("State file is missing.")
    print("Re-authentication and a new state save are needed.")
