
import pytest


# Search settings
PARTIAL_PRODUCT_NAME = "iph"
EXPECTED_SUGGESTION = "iphone"


@pytest.mark.asyncio
async def test_autosuggest_dropdown(page):
    # Step 1: Open Amazon India
    await page.goto("https://www.amazon.in/")

    # Step 2: Enter a partial product name
    search_box = page.locator("#twotabsearchtextbox")
    await search_box.fill(PARTIAL_PRODUCT_NAME)

    # Step 3: Check whether suggestions appear
    suggestion_list = page.locator(
        "div.s-suggestion-container"
    )

    suggestions_found = False

    try:
        await suggestion_list.first.wait_for(
            state="visible",
            timeout=5000
        )
        suggestions_found = True
    except Exception:
        print(
            "Autocomplete suggestions were not displayed "
            "within the waiting period."
        )

    # Step 4: Handle suggestions if they are displayed
    if suggestions_found:
        print("Autocomplete suggestions are displayed.")

        # Find a suggestion matching the expected keyword
        matching_suggestion = suggestion_list.get_by_text(
            EXPECTED_SUGGESTION,
            exact=False
        )

        try:
            await matching_suggestion.first.wait_for(
                state="visible",
                timeout=5000
            )

            suggestion_text = (
                await matching_suggestion.first.inner_text()
            ).strip()

            print("Matching suggestion:", suggestion_text)

            # Select the matching suggestion
            await matching_suggestion.first.click()

            # Validate that Amazon navigated or updated the search
            await page.wait_for_url(
                "**/s?**",
                timeout=10000
            )

            search_value = await search_box.input_value()

            assert (
                EXPECTED_SUGGESTION.casefold()
                in search_value.casefold()
                or EXPECTED_SUGGESTION.casefold()
                in page.url.casefold()
            ), (
                "A suggestion was selected, but the resulting "
                "search term or URL did not contain the expected keyword."
            )

            print("Selected suggestion successfully.")
            print("Search value:", search_value)
            print("Result URL:", page.url)

        except Exception as error:
            pytest.fail(
                "Suggestions appeared, but the expected matching "
                f"suggestion could not be selected or validated: {error}"
            )

    # Step 5: If suggestions are absent, use Search
    else:
        print(
            "Fallback: submitting the partial product name "
            "using the Search button."
        )

        search_button = page.locator("#nav-search-submit-button")
        await search_button.click()

        # Validate that Amazon opened a search results URL
        await page.wait_for_url(
            "**/s?**",
            timeout=15000
        )

        assert "/s?" in page.url, (
            "Amazon did not navigate to the search results page."
        )

        print("Fallback search completed.")
        print("Search value:", await search_box.input_value())
        print("Result URL:", page.url)
