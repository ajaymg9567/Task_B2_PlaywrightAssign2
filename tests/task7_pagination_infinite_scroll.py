
import pytest


SEARCH_KEYWORD = "Smartphone"

PRODUCT_CARDS = "div[data-component-type='s-search-result']"


@pytest.mark.asyncio
async def test_pagination_and_infinite_scroll(page):
    # Step 1: Open Amazon India and search for smartphones
    await page.goto("https://www.amazon.in/")

    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(SEARCH_KEYWORD)
    await search_box.press("Enter")

    product_cards = page.locator(PRODUCT_CARDS)

    await product_cards.first.wait_for(
        state="visible",
        timeout=15000
    )

    initial_count = await product_cards.count()
    initial_titles = await page.locator(
        f"{PRODUCT_CARDS} h2"
    ).all_inner_texts()

    initial_url = page.url

    print("Search keyword:", SEARCH_KEYWORD)
    print("Initial product card count:", initial_count)
    print("Initial results URL:", initial_url)

    # Step 2: Check for a Next-page control
    next_page = page.locator("a.s-pagination-next")

    if await next_page.count() > 0 and await next_page.first.is_visible():
        is_disabled = await next_page.first.get_attribute(
            "aria-disabled"
        )
        css_class = await next_page.first.get_attribute("class") or ""

        if is_disabled != "true" and "s-pagination-disabled" not in css_class:
            next_url = await next_page.first.get_attribute("href")

            print("Observed pattern: Pagination")

            await next_page.first.click()

            await page.wait_for_url(
                lambda url: str(url) != initial_url,
                timeout=15000
            )

            await product_cards.first.wait_for(
                state="visible",
                timeout=15000
            )

            next_titles = await page.locator(
                f"{PRODUCT_CARDS} h2"
            ).all_inner_texts()

            assert next_titles, (
                "The next page opened but no product titles were found."
            )

            assert next_titles != initial_titles, (
                "The next page loaded, but the product result set "
                "did not change."
            )

            print("Next-page link:", next_url)
            print("Next-page URL:", page.url)
            print("Next-page product card count:", await product_cards.count())
            print("Pagination validation passed.")
            return

    # Step 3: Check for a Load More control
    load_more = page.get_by_role(
        "button",
        name="Load more",
        exact=False
    )

    if await load_more.count() == 0:
        load_more = page.locator(
            "a:has-text('Load more'), button:has-text('Load more')"
        )

    if await load_more.count() > 0 and await load_more.first.is_visible():
        print("Observed pattern: Load More control")

        await load_more.first.click()

        await page.wait_for_function(
            """args => document.querySelectorAll(args.selector).length > args.count""",
            arg={
                "selector": PRODUCT_CARDS,
                "count": initial_count
            },
            timeout=15000
        )

        updated_count = await product_cards.count()

        assert updated_count > initial_count, (
            "Load More was clicked, but no new product cards appeared."
        )

        print("Initial count:", initial_count)
        print("Updated count:", updated_count)
        print("Load More validation passed.")
        return

    # Step 4: Check for products loaded by scrolling
    print("No usable Next-page or Load More control was found.")
    print("Checking whether scrolling loads additional products.")

    await page.evaluate(
        "window.scrollTo(0, document.body.scrollHeight)"
    )

    try:
        await page.wait_for_function(
            """args => document.querySelectorAll(args.selector).length > args.count""",
            arg={
                "selector": PRODUCT_CARDS,
                "count": initial_count
            },
            timeout=10000
        )

        updated_count = await product_cards.count()

        assert updated_count > initial_count, (
            "Scrolling did not increase the number of product cards."
        )

        print("Observed pattern: Scroll-triggered loading")
        print("Initial count:", initial_count)
        print("Updated count:", updated_count)
        print("Infinite-scroll validation passed.")

    except Exception:
        pytest.skip(
            "Amazon did not expose a usable Next-page or Load More "
            "control, and scrolling did not reveal additional product "
            "cards in this session. Use a trainer-approved test page "
            "to demonstrate the missing pagination or lazy-loading behavior."
        )
