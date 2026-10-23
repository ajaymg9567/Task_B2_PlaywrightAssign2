
import pytest


@pytest.mark.asyncio
async def test_multistep_form_data_persistence(page):
    # Step 1: Create a local mock checkout form
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mock Checkout Form</title>
        </head>
        <body>
            <h1>Mock Checkout</h1>

            <section id="step1">
                <h2>Step 1: Address Details</h2>

                <label for="full_name">Name</label>
                <input id="full_name" type="text">

                <label for="address">Address</label>
                <input id="address" type="text">

                <label for="postal_code">Postal Code</label>
                <input id="postal_code" type="text">

                <button id="next_button" type="button"
                    onclick="
                        document.getElementById('step1').hidden = true;
                        document.getElementById('step2').hidden = false;
                    ">
                    Continue
                </button>
            </section>

            <section id="step2" hidden>
                <h2>Step 2: Delivery Preferences</h2>

                <label for="delivery">Delivery Option</label>
                <select id="delivery">
                    <option value="">Select delivery</option>
                    <option value="standard">Standard</option>
                    <option value="express">Express</option>
                </select>

                <button id="back_button" type="button"
                    onclick="
                        document.getElementById('step2').hidden = true;
                        document.getElementById('step1').hidden = false;
                    ">
                    Back
                </button>

                <button id="finish_button" type="button">
                    Finish Demo
                </button>
            </section>
        </body>
        </html>
    """)

    print("Local mock checkout form opened.")

    # Step 2: Enter fictional test data
    await page.locator("#full_name").fill("Test User")
    await page.locator("#address").fill("123 Test Street")
    await page.locator("#postal_code").fill("000000")

    # Validate data before moving forward
    assert await page.locator("#full_name").input_value() == "Test User"
    assert await page.locator("#address").input_value() == "123 Test Street"
    assert await page.locator("#postal_code").input_value() == "000000"

    print("Address fields populated with fictional test data.")

    # Step 3: Move to the next step
    await page.locator("#next_button").click()

    await page.locator("#step2").wait_for(state="visible")

    assert await page.locator("#step1").is_hidden()
    assert await page.locator("#step2").is_visible()

    # Enter delivery preference
    await page.locator("#delivery").select_option("express")

    assert await page.locator("#delivery").input_value() == "express"

    print("Moved to delivery preferences.")

    # Step 4: Go back to the address step
    await page.locator("#back_button").click()

    await page.locator("#step1").wait_for(state="visible")

    assert await page.locator("#step1").is_visible()
    assert await page.locator("#step2").is_hidden()

    # Step 5: Verify address data was retained
    assert await page.locator("#full_name").input_value() == "Test User", (
        "Name was lost after navigating back."
    )

    assert await page.locator("#address").input_value() == "123 Test Street", (
        "Address was lost after navigating back."
    )

    assert await page.locator("#postal_code").input_value() == "000000", (
        "Postal code was lost after navigating back."
    )

    print("Address data persisted after navigating back.")

    # Step 6: Move forward again
    await page.locator("#next_button").click()

    await page.locator("#step2").wait_for(state="visible")

    # Step 7: Verify delivery preference was also retained
    assert await page.locator("#delivery").input_value() == "express", (
        "Delivery preference was lost after navigating between steps."
    )

    print("Delivery preference persisted.")
    print("Task 8 form persistence validation passed.")
    print("Demo ended without submitting an order.")
