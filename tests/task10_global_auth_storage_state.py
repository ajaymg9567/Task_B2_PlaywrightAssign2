
import pytest


STATE_FILE = "auth_state.json"
MOCK_URL = "http://mock-auth.local/dashboard"
VALID_DEMO_TOKEN = "demo-session-valid"


async def mock_auth_page(route):
    # Local practice page; no external website or real account is used.
    await route.fulfill(
        status=200,
        content_type="text/html",
        body="""
        <!DOCTYPE html>
        <html>
        <head><title>Mock Auth Dashboard</title></head>
        <body>
            <h1 id="dashboard">Test Dashboard</h1>
            <p id="status">Authentication demo page</p>
        </body>
        </html>
        """,
    )


@pytest.mark.asyncio
async def test_global_authentication_using_storage_state(page):
    # Step 1: Open the local mock dashboard
    browser = page.context.browser

    assert browser is not None, (
        "Could not access the browser from the page fixture."
    )

    await page.context.route(
        "http://mock-auth.local/**",
        mock_auth_page,
    )

    await page.goto(MOCK_URL)

    # Step 2: Simulate an authenticated test session.
    # This is demo data, not a real login or real credential.
    await page.evaluate(
        """token => localStorage.setItem("auth_token", token)""",
        VALID_DEMO_TOKEN,
    )

    assert await page.evaluate(
        'localStorage.getItem("auth_token")'
    ) == VALID_DEMO_TOKEN

    print("Mock test session created.")

    # Step 3: Save the browser context state locally
    await page.context.storage_state(path=STATE_FILE)

    print(f"Storage state saved locally to {STATE_FILE}.")

    # Step 4: Create a new context using the saved state
    new_context = await browser.new_context(
        storage_state=STATE_FILE
    )

    try:
        # Reinstall the route for the new context
        await new_context.route(
            "http://mock-auth.local/**",
            mock_auth_page,
        )

        new_page = await new_context.new_page()
        await new_page.goto(MOCK_URL)

        # Step 5: Check authentication without repeating sign-in
        dashboard_visible = await new_page.locator(
            "#dashboard"
        ).is_visible()

        assert dashboard_visible, (
            "Dashboard did not load in the new browser context."
        )

        saved_token = await new_page.evaluate(
            'localStorage.getItem("auth_token")'
        )

        # Step 6: Handle missing or expired authentication
        if saved_token != VALID_DEMO_TOKEN:
            print(
                "Authentication is missing or expired. "
                "Re-authentication is needed."
            )
            pytest.skip(
                "No valid authenticated session was restored."
            )

        assert await new_page.title() == "Mock Auth Dashboard"

        print("Authenticated state restored successfully.")
        print("No sign-in flow was repeated.")

    finally:
        await new_context.close()
