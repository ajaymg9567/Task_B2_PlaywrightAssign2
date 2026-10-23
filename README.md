# Playwright_Assign2

Beginner-friendly async Playwright and Pytest assignment.

## Install

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Run Task 1 (visible browser)

```bash
python -m pytest tests/task1_product_discovery.py -v -s
```

The browser is visible because `conftest.py` launches Chromium with `headless=False`.

Edit `SEARCH_KEYWORD` and `PRODUCT_TITLE_MATCH` in `tests/task1_product_discovery.py` to match your trainer's instructions.

Amazon's page layout and available results can vary. No purchase is made by this test.
