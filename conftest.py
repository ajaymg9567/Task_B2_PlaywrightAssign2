import pytest_asyncio
from playwright.async_api import async_playwright


@pytest_asyncio.fixture
async def page():
    async with async_playwright() as p:
        # headless=False makes the browser window visible
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        yield page

        await browser.close()
