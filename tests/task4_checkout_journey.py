
import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


# Search settings
SEARCH_KEYWORD = "Sony headphones"
PRODUCT_TITLE_MATCH = "Sony"


@pytest.mark.asyncio
async def test_checkout_journey_stop_before_purchase(page):
    # Step 1: Open Amazon India and search
    await page.goto("https://www.amazon.in/")

    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(SEARCH_KEYWORD)
    await search_box.press("Enter")

    # Step 2: Find product cards
    product_cards = page.locator(
        "div[data-component-type='s-search-result']"
    )

    await product_cards.first.wait_for(
        state="visible",
        timeout=15000
    )

    # Step 3: Select a Sony headphone dynamically
    matched_card = None
    matched_title = None

    for i in range(await product_cards.count()):
        card = product_cards.nth(i)
        title_locator = card.locator("h2")

        if await title_locator.count() == 0:
            continue

        title = (await title_locator.first.inner_text()).strip()
        title_lower = title.casefold()

        is_sony = "sony" in title_lower
        looks_like_headphones = (
            "headphone" in title_lower
            or "headset" in title_lower
            or "wh-" in title_lower
        )

        if is_sony and looks_like_headphones:
            matched_card = card
            matched_title = title
            break

    assert matched_card is not None, (
        f"No Sony headphone was found for search '{SEARCH_KEYWORD}'."
    )

    print("Selected product:", matched_title)

    # Step 4: Open the selected product
    product_link = matched_card.locator("h2 a")

    if await product_link.count() == 0:
        product_link = matched_card.locator("a:has(h2)")

    assert await product_link.count() > 0, (
        "The matching product link was not found."
    )

    product_url = await product_link.first.get_attribute("href")

    assert product_url, "The product link has no URL."

    if product_url.startswith("/"):
        product_url = "https://www.amazon.in" + product_url

    await page.goto(product_url)

    # Step 5: Validate the product detail page
    detail_title = page.locator("span#productTitle")

    await detail_title.wait_for(
        state="visible",
        timeout=20000
    )

    detail_title_text = (await detail_title.inner_text()).strip()

    assert "sony" in detail_title_text.casefold(), (
        "The opened product is not a Sony product."
    )

    print("Product detail title:", detail_title_text)

    # Step 6: Check Add to Cart availability
    add_to_cart = page.locator("#add-to-cart-button")

    if await add_to_cart.count() == 0:
        pytest.skip(
            "Add to Cart is unavailable on this product page/session."
        )

    if not await add_to_cart.is_visible():
        pytest.skip("Add to Cart is not visible in this session.")

    if not await add_to_cart.is_enabled():
        pytest.skip("Add to Cart is disabled for this product.")

    # Step 7: Add the product to the cart
    await add_to_cart.click()

    print("Add to Cart was clicked.")

    # Step 8: Open the cart
    await page.goto("https://www.amazon.in/gp/cart/view.html")

    cart_item = page.locator(
        "div.sc-list-item-content"
    ).filter(has_text="Sony")

    try:
        await cart_item.first.wait_for(
            state="visible",
            timeout=15000
        )
    except PlaywrightTimeoutError:
        pytest.fail(
            "The Sony product was not found in the cart. "
            "Amazon may require sign-in or may not have added the item."
        )

    print("Sony product found in the cart.")


    # Step 9: Validate the cart item and quantity
    cart_text = (await cart_item.first.inner_text()).strip()

    assert "sony" in cart_text.casefold(), (
        "The cart item does not contain the expected Sony product."
    )

    # Amazon may display quantity in different ways
    quantity = cart_item.first.locator(
        "select[name='quantity'], "
        "select[id*='quantity'], "
        "span.a-dropdown-prompt"
    )

    if await quantity.count() > 0:
        quantity_value = (
            await quantity.first.input_value()
            if await quantity.first.evaluate(
                "(element) => element.tagName === 'SELECT'"
            )
            else (await quantity.first.inner_text()).strip()
        )

        assert quantity_value == "1", (
            f"Expected cart quantity 1, but found '{quantity_value}'."
        )

        print("Cart quantity:", quantity_value)

    else:
        # Check other quantity-related controls within this cart item
        quantity_controls = cart_item.first.locator(
            "[aria-label*='quantity' i], "
            "[aria-label*='Qty' i], "
            "input[name*='quantity' i]"
        )

        if await quantity_controls.count() > 0:
            quantity_value = await quantity_controls.first.get_attribute(
                "aria-label"
            )

            print(
                "Quantity control found. "
                f"Accessible label: {quantity_value}"
            )
        else:
            print(
                "Sony item is in the cart, but the quantity control "
                "is not exposed by the current Amazon page layout."
            )

    print("Cart item:", cart_text)

    # Step 10: Proceed to checkout if the control is available
    checkout_button = page.locator(
        "input[name='proceedToRetailCheckout'], "
        "#sc-buy-box-ptc-button"
    )

    if await checkout_button.count() == 0:
        print(
            "Checkout control is unavailable. "
            "Stopping after cart validation."
        )
        return

    if not await checkout_button.first.is_visible():
        print(
            "Checkout control is not visible. "
            "Stopping after cart validation."
        )
        return

    await checkout_button.first.click()
    print("Proceed to Checkout was clicked.")

    # Step 11: Stop at the final review stage, if reached.
    # Never click Place Order or submit payment.
    place_order_control = page.locator(
        "#placeYourOrder, "
        "input[name='placeYourOrder1'], "
        "#submitOrderButtonId"
    )

    try:
        await place_order_control.first.wait_for(
            state="visible",
            timeout=10000
        )

        print(
            "Final order-review control is visible. "
            "Stopping here without placing the order."
        )

    except PlaywrightTimeoutError:
        print(
            "The final review stage was not detected. "
            "Amazon may require sign-in or another permitted checkout step."
        )

    print("Current checkout URL:", page.url)
    print("Test stopped before purchase.")
