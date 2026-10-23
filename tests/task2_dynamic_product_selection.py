
import pytest


# Search settings
SEARCH_KEYWORD = "Smartphone"
PRODUCT_TITLE_MATCH = "Apple"


@pytest.mark.asyncio
async def test_dynamic_product_selection(page):
    # Step 1: Open Amazon India
    await page.goto("https://www.amazon.in/")

    # Step 2: Search for a product
    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(SEARCH_KEYWORD)
    await search_box.press("Enter")

    # Step 3: Find all product cards
    product_cards = page.locator(
        "div[data-component-type='s-search-result']"
    )

    await product_cards.first.wait_for(
        state="visible",
        timeout=15000
    )

    print("Product cards found:", await product_cards.count())

    # Step 4: Find a card matching the required keyword
    matched_card = None
    matched_title = None

    for i in range(await product_cards.count()):
        card = product_cards.nth(i)
        title_locator = card.locator("h2")

        if await title_locator.count() == 0:
            continue

        title = (await title_locator.first.inner_text()).strip()

        if PRODUCT_TITLE_MATCH.casefold() in title.casefold():
            matched_card = card
            matched_title = title
            break

    # Step 5: Fail clearly if no product matches
    assert matched_card is not None, (
        f"No product containing '{PRODUCT_TITLE_MATCH}' "
        f"was found for search '{SEARCH_KEYWORD}'."
    )

    print("Matched product:", matched_title)

    # Step 6: Validate the title within the matched card
    assert PRODUCT_TITLE_MATCH.casefold() in matched_title.casefold()

    # Step 7: Find the link inside the matched card
    product_link = matched_card.locator("h2 a")

    if await product_link.count() == 0:
        product_link = matched_card.locator("a:has(h2)")

    assert await product_link.count() > 0, (
        "The matching product was found, but its title link "
        "was not found inside the product card."
    )

    # Step 8: Read the product link and navigate to it
    product_url = await product_link.first.get_attribute("href")

    assert product_url, "The matched product link has no URL."

    if product_url.startswith("/"):
        product_url = "https://www.amazon.in" + product_url

    await page.goto(product_url)

    # Step 9: Validate the product detail page
    detail_title = page.locator("span#productTitle")

    await detail_title.wait_for(
        state="visible",
        timeout=20000
    )

    detail_title_text = (await detail_title.inner_text()).strip()

    assert PRODUCT_TITLE_MATCH.casefold() in detail_title_text.casefold(), (
        f"Opened product title '{detail_title_text}' does not contain "
        f"'{PRODUCT_TITLE_MATCH}'."
    )

    print("Product selection passed:", detail_title_text)
    print("Product URL:", page.url)
