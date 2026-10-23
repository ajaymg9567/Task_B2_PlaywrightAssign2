
import pytest


SEARCH_KEYWORD = "Laptop"
PRODUCT_TITLE_MATCH = "Apple"


@pytest.mark.asyncio
async def test_product_discovery(page):
    # Step 1: Open Amazon India
    await page.goto("https://www.amazon.in/")

    # Step 2: Search for a product
    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(SEARCH_KEYWORD)
    await search_box.press("Enter")

    # Step 3: Wait for search results
    results = page.locator(
        "div[data-component-type='s-search-result']"
    )

    await results.first.wait_for(state="visible", timeout=15000)


    # Step 4: Find a product by its visible title
    selected_title = None
    selected_link = None
    selected_price = None

    for i in range(await results.count()):
        product = results.nth(i)
        heading = product.locator("h2")

        if await heading.count() == 0:
            continue

        title = (await heading.inner_text()).strip()

        if not title:
            continue

        print("Checking product:", title)

        if PRODUCT_TITLE_MATCH.casefold() in title.casefold():
            # Find the link associated with this title
            title_link = heading.locator("xpath=ancestor::a[1]")

            if await title_link.count() == 0:
                title_link = product.locator("a:has(h2)")

            if await title_link.count() == 0:
                print("Matching title found, but product link is missing.")
                continue

            selected_title = title
            selected_link = await title_link.first.get_attribute("href")

            price_locator = product.locator(".a-price .a-offscreen")

            if await price_locator.count() > 0:
                selected_price = await price_locator.first.inner_text()

            break

    assert selected_title, (
        f"No product matched '{PRODUCT_TITLE_MATCH}' "
        "in the current search results."
    )

    assert selected_link, "Product link was not found"

    print("\nSelected product:", selected_title)


    # Step 5: Open the selected product detail page
    if selected_link.startswith("http"):
        product_url = selected_link
    else:
        product_url = "https://www.amazon.in" + selected_link

    await page.goto(product_url)

    # Step 6: Validate the product title
    detail_title_locator = page.locator("span#productTitle")

    await detail_title_locator.wait_for(
        state="visible",
        timeout=15000
    )

    detail_title = (await detail_title_locator.inner_text()).strip()

    # Compare the search result title with the product page title
    assert (
            " ".join(selected_title.split())
            == " ".join(detail_title.split())
    ), "Product title does not match between search results and product page"

    print("Product title validation passed:", detail_title)

    # Step 7: Record the price if available
    detail_price_locator = page.locator(
        "#corePriceDisplay_desktop_feature_div .a-offscreen, "
        "#corePrice_feature_div .a-offscreen, "
        ".apexPriceToPay .a-offscreen"
    )

    detail_price = selected_price or "Price not visible"

    for i in range(await detail_price_locator.count()):
        price = detail_price_locator.nth(i)

        if await price.is_visible():
            detail_price = (await price.inner_text()).strip()
            break

    # Step 8: Print product details
    print("\n--- Product Discovery Details ---")
    print("Product Title:", detail_title)
    print("Product Price:", detail_price)
    print("Product URL:", page.url)
