
import asyncio
import os

from playwright.async_api import async_playwright


STATE_FILE = os.path.join(
    os.path.dirname(__file__),
    "task11_auth_state.json",
)

DEMO_TOKEN = "task11-demo-session-valid"
DEMO_URL = "http://mock-auth.local/dashboard"


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


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)

        context = await browser.new_context()

        await context.route(
            "http://mock-auth.local/**",
            mock_dashboard,
        )

        page = await context.new_page()
        await page.goto(DEMO_URL)

        # Simulate an authorized demo session without real credentials
        await page.evaluate(
            """token => localStorage.setItem("auth_token", token)""",
            DEMO_TOKEN,
        )

        await context.storage_state(path=STATE_FILE)

        print("Demo browser state saved successfully.")
        print(f"State file: {STATE_FILE}")

        await browser.close()


asyncio.run(main())
