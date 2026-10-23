
import pytest


# Search settings
SEARCH_KEYWORD = "Sony MDR-ZX310AP"
PRODUCT_IDENTIFIER = "MDR-ZX310AP"


@pytest.mark.asyncio
async def test_state_across_multiple_pages(page):
    # Step 1: Open Amazon India and search
    await page.goto("https://www.amazon.in/")

    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(SEARCH_KEYWORD)
    await search_box.press("Enter")

    # Step 2: Find the matching product card
    product_cards = page.locator(
        "div[data-component-type='s-search-result']"
    )

    await product_cards.first.wait_for(
        state="visible",
        timeout=15000
    )

    matched_card = None
    selected_title = None

    for i in range(await product_cards.count()):
        card = product_cards.nth(i)
        title_locator = card.locator("h2")

        if await title_locator.count() == 0:
            continue

        title = (await title_locator.first.inner_text()).strip()

        if PRODUCT_IDENTIFIER.casefold() in title.casefold():
            matched_card = card
            selected_title = title
            break

    assert matched_card is not None, (
        f"Product '{PRODUCT_IDENTIFIER}' was not found "
        f"for search '{SEARCH_KEYWORD}'."
    )

    # Step 3: Capture state before navigation
    selected_product_title = selected_title
    selected_product_identifier = PRODUCT_IDENTIFIER
    original_search_keyword = SEARCH_KEYWORD

    print("Saved product title:", selected_product_title)
    print("Saved product identifier:", selected_product_identifier)
    print("Saved search keyword:", original_search_keyword)

    # Step 4: Open the product detail page
    product_link = matched_card.locator("h2 a")

    if await product_link.count() == 0:
        product_link = matched_card.locator("a:has(h2)")

    assert await product_link.count() > 0, (
        "The selected product link was not found."
    )

    product_url = await product_link.first.get_attribute("href")

    assert product_url, "The selected product URL is missing."

    if product_url.startswith("/"):
        product_url = "https://www.amazon.in" + product_url

    await page.goto(product_url)

    # Step 5: Validate product detail page state
    detail_title = page.locator("span#productTitle")

    await detail_title.wait_for(
        state="visible",
        timeout=20000
    )

    detail_title_text = (await detail_title.inner_text()).strip()

    assert selected_product_identifier.casefold() in (
        detail_title_text.casefold()
    ), (
        "Product identifier was lost or the wrong detail page opened. "
        f"Expected identifier: {selected_product_identifier}; "
        f"Actual title: {detail_title_text}"
    )

    print("Product detail page validated:", detail_title_text)

    # Step 6: Add the selected product to the cart
    add_to_cart = page.locator("#add-to-cart-button")

    if await add_to_cart.count() == 0:
        pytest.skip("Add to Cart is unavailable on this page.")

    if not await add_to_cart.is_visible():
        pytest.skip("Add to Cart is not visible in this session.")

    if not await add_to_cart.is_enabled():
        pytest.skip("Add to Cart is disabled in this session.")

    await add_to_cart.click()

    # Step 7: Navigate to the cart
    await page.goto("https://www.amazon.in/gp/cart/view.html")

    cart_item = page.locator(
        "div.sc-list-item-content"
    ).filter(has_text=selected_product_identifier)

    try:
        await cart_item.first.wait_for(
            state="visible",
            timeout=15000
        )
    except Exception:
        pytest.fail(
            "State validation failed: the selected product "
            "was not found in the cart."
        )

    cart_text = (await cart_item.first.inner_text()).strip()

    assert selected_product_identifier.casefold() in (
        cart_text.casefold()
    ), (
        "Cart state mismatch. The selected product identifier "
        f"'{selected_product_identifier}' was not found in: {cart_text}"
    )

    assert selected_product_title.split()[0].casefold() in (
        cart_text.casefold()
    ), (
        "The cart item does not appear to match the selected product."
    )

    print("Cart state validated:", cart_text)

    # Step 8: Return to the original search results
    await page.goto("https://www.amazon.in/s?k=Sony+MDR-ZX310AP")

    await page.locator(
        "div[data-component-type='s-search-result']"
    ).first.wait_for(
        state="visible",
        timeout=15000
    )

    # Step 9: Verify search context and selected product are retained
    returned_search_box = page.locator("#twotabsearchtextbox")
    returned_search_value = await returned_search_box.input_value()

    assert original_search_keyword.casefold() in (
        returned_search_value.casefold()
    ), (
        "Search context was not retained. "
        f"Expected '{original_search_keyword}', "
        f"but found '{returned_search_value}'."
    )

    returned_product_titles = await page.locator(
        "div[data-component-type='s-search-result'] h2"
    ).all_inner_texts()

    product_found_again = any(
        selected_product_identifier.casefold() in title.casefold()
        for title in returned_product_titles
    )

    assert product_found_again, (
        "The previously selected product was not found "
        "after returning to search results."
    )

    print("Search context retained:", returned_search_value)
    print("Selected product found again in search results.")
    print("Task 6 state validation passed.")
