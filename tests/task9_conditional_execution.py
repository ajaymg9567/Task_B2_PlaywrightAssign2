
import pytest


@pytest.mark.asyncio
async def test_conditional_execution_based_on_ui_state(page):
    # Step 1: Open Amazon India and search for a product
    await page.goto("https://www.amazon.in/")

    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill("Sony headphones")
    await page.locator("#nav-search-submit-button").click()

    await page.locator(
        "div[data-component-type='s-search-result']"
    ).first.wait_for(state="visible")


    # Step 2: Select a product by its visible title, not its position
    product_cards = page.locator(
        "div[data-component-type='s-search-result']"
    )

    selected_product_url = None

    for index in range(await product_cards.count()):
        card = product_cards.nth(index)
        title_locator = card.locator("h2")

        if await title_locator.count() == 0:
            continue

        product_title = (
            await title_locator.first.inner_text()
        ).strip()

        title_lower = product_title.lower()

        if (
            "sony" in title_lower
            and (
                "headphone" in title_lower
                or "headset" in title_lower
            )
        ):
            # Inspect links inside this matching product card
            links = card.locator("a[href]")

            for link_index in range(await links.count()):
                link = links.nth(link_index)

                href = await link.get_attribute("href")

                if not href:
                    continue

                # Accept Amazon product-detail links
                if "/dp/" in href or "/gp/product/" in href:
                    selected_product_url = href
                    print(f"Matching product: {product_title}")
                    print(f"Product link: {selected_product_url}")
                    break

            if selected_product_url:
                break

    assert selected_product_url, (
        "No matching Sony headphones product with an Amazon "
        "product-detail link was found. Check the current search "
        "results and their link structure."
    )

    if selected_product_url.startswith("/"):
        selected_product_url = (
            "https://www.amazon.in" + selected_product_url
        )

    elif selected_product_url.startswith("//"):
        selected_product_url = "https:" + selected_product_url

    # Step 3: Open the selected product details page
    await page.goto(selected_product_url)

    product_title_locator = page.locator("span#productTitle")
    await product_title_locator.wait_for(state="visible")

    selected_title = (
        await product_title_locator.inner_text()
    ).strip()

    print(f"Selected product: {selected_title}")
    print(f"Product URL: {page.url}")

    # Step 4: Check the current stock status
    availability = page.locator("#availability")
    stock_text = ""

    if (
        await availability.count() > 0
        and await availability.first.is_visible()
    ):
        stock_text = (
            await availability.first.inner_text()
        ).strip()

    print(f"Stock status shown by Amazon: {stock_text or 'Not displayed'}")

    stock_lower = stock_text.lower()

    unavailable_messages = [
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "unavailable",
    ]

    if any(message in stock_lower for message in unavailable_messages):
        reason = (
            f"Product unavailable according to the page: {stock_text}"
        )
        print(reason)
        pytest.skip(reason)

    # Step 5: Check whether Add to Cart exists, is visible, and is enabled
    add_to_cart = page.locator("#add-to-cart-button")

    if await add_to_cart.count() == 0:
        reason = "Add to Cart control is missing; cart validation cannot continue."
        print(reason)
        pytest.skip(reason)

    if not await add_to_cart.first.is_visible():
        reason = "Add to Cart control is not visible; cart validation cannot continue."
        print(reason)
        pytest.skip(reason)

    if not await add_to_cart.first.is_enabled():
        reason = "Add to Cart control is disabled; product cannot be added to the cart."
        print(reason)
        pytest.skip(reason)

    print("Add to Cart is visible and enabled.")

    # Step 6: Continue only when the UI allows adding the product
    await add_to_cart.first.click()

    # Step 7: Open the cart and validate the selected product
    await page.goto("https://www.amazon.in/gp/cart/view.html")

    cart_text = (await page.locator("body").inner_text()).lower()

    # Check that meaningful words from the selected title appear in the cart.
    title_words = [
        word.lower()
        for word in selected_title.split()
        if len(word) >= 4
    ]

    matching_words = [
        word for word in title_words
        if word in cart_text
    ]

    assert matching_words, (
        "The selected product could not be identified in the cart. "
        f"Selected product: {selected_title}"
    )

    print("Cart validation passed.")
    print(f"Matched product-title words: {matching_words}")
