
import pytest


# Amazon search settings
SEARCH_KEYWORD = "Sony MDR-ZX310AP"
PRODUCT_IDENTIFIER = "MDR-ZX310AP"

# Reference source for this exercise:
# Trainer-approved mock product fixture, not a live Amazon API.
MOCK_API_ENDPOINT = "mock://trainer-approved/products/sony-zx310ap"


@pytest.fixture
def api_product_reference():
    # Mock API response for UI/API validation
    return {
        "product_identifier": "MDR-ZX310AP",
        "product_title": (
            "Sony ZX Series MDR-ZX310AP Wired Headband "
            "Stereo On Ear Headset -Black"
        ),
    }


def normalize_text(value):
    # Remove extra spaces and normalize case
    return " ".join(value.split()).casefold()


@pytest.mark.asyncio
async def test_ui_api_product_title_validation(
    page, api_product_reference
):
    # Step 1: Read the reference data from the mock API fixture
    api_title = api_product_reference["product_title"]
    api_identifier = api_product_reference["product_identifier"]

    print("API source endpoint:", MOCK_API_ENDPOINT)
    print("API field: product_identifier =", api_identifier)
    print("API field: product_title =", api_title)

    # Step 2: Open Amazon India and search for the product
    await page.goto("https://www.amazon.in/")

    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(SEARCH_KEYWORD)
    await search_box.press("Enter")

    # Step 3: Find the product using its identifier
    product_cards = page.locator(
        "div[data-component-type='s-search-result']"
    )

    await product_cards.first.wait_for(
        state="visible",
        timeout=15000
    )

    matched_card = None
    ui_search_title = None

    for i in range(await product_cards.count()):
        card = product_cards.nth(i)
        title_locator = card.locator("h2")

        if await title_locator.count() == 0:
            continue

        title = (await title_locator.first.inner_text()).strip()

        if PRODUCT_IDENTIFIER.casefold() in title.casefold():
            matched_card = card
            ui_search_title = title
            break

    assert matched_card is not None, (
        f"Product '{PRODUCT_IDENTIFIER}' was not found "
        f"in Amazon search results for '{SEARCH_KEYWORD}'."
    )

    print("UI search field: product title =", ui_search_title)

    # Step 4: Open the matching product detail page
    product_link = matched_card.locator("h2 a")

    if await product_link.count() == 0:
        product_link = matched_card.locator("a:has(h2)")

    assert await product_link.count() > 0, (
        "Product title link was not found inside the matched card."
    )

    product_url = await product_link.first.get_attribute("href")

    assert product_url, "The product link has no URL."

    if product_url.startswith("/"):
        product_url = "https://www.amazon.in" + product_url

    await page.goto(product_url)

    # Step 5: Read the visible title on the product detail page
    detail_title = page.locator("span#productTitle")

    await detail_title.wait_for(
        state="visible",
        timeout=20000
    )

    ui_title = (await detail_title.inner_text()).strip()

    print("UI field: product title =", ui_title)
    print("Product URL:", page.url)

    # Step 6: Validate the identifier against the reference data
    assert api_identifier.casefold() in api_title.casefold(), (
        f"Mock API data mismatch: field 'product_identifier' "
        f"('{api_identifier}') is not present in field "
        f"'product_title' ('{api_title}'). "
        f"Source: {MOCK_API_ENDPOINT}"
    )

    # Step 7: Compare normalized UI title and API title
    normalized_api_title = normalize_text(api_title)
    normalized_ui_title = normalize_text(ui_title)

    assert normalized_ui_title == normalized_api_title, (
        "UI/API product title mismatch.\n"
        f"API endpoint: {MOCK_API_ENDPOINT}\n"
        "API field: product_title\n"
        "UI field: span#productTitle\n"
        f"API value: '{api_title}'\n"
        f"UI value: '{ui_title}'"
    )

    print("UI/API validation passed.")
    print("Compared fields: API product_title vs UI span#productTitle")
