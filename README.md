# E-commerce QA Automation (Playwright + Python)

UI and API tests for:

- UI: DemoBlaze Product Store - https://www.demoblaze.com/
- API: Rahul Shetty Academy e-commerce API - https://rahulshettyacademy.com/api/ecom

Uses Playwright (sync API) with pytest. Page objects are in `pages/`, the API client is in `api_client/`,
test data is in `data/test_data.py` and URLs/credentials come from `.env` files.

There are 20 tests (13 UI, 7 API). Failed tests are retried 3 times.

## Prerequisites

- Python 3.11+ (I used 3.14)
- Access to demoblaze.com and rahulshettyacademy.com
- An account on https://rahulshettyacademy.com/client/#/auth/register (only needed for the API tests)

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

### Env config

Config is read from `.env.<TEST_ENV>` first (`TEST_ENV` defaults to `qa`), then `.env`, then `.env.example`.
Anything already set in your shell overrides the files.

```powershell
Copy-Item .env.example .env.qa
# then put your RSA_API_EMAIL / RSA_API_PASSWORD in .env.qa
```

| Variable | Required | What it is |
|---|---|---|
| `WEB_BASE_URL` | yes | DemoBlaze base URL |
| `API_BASE_URL` | yes | E-commerce API base URL |
| `RSA_API_EMAIL` | API tests | account email |
| `RSA_API_PASSWORD` | API tests | account password |

For another environment, make e.g. `.env.staging` and set `$env:TEST_ENV="staging"`.
If a required variable is missing, the tests stop with an error saying which one.
`.env.*` files (apart from `.env.example`) are git-ignored.

## Running

```powershell
pytest                                   # everything, chromium headless, 3 retries
pytest tests/ui                          # UI only
pytest tests/api                         # API only
pytest -m api                            # by marker (ui / api)
pytest -k "checkout"                     # by name
pytest tests/ui --headed --slowmo 300    # watch the browser
pytest --reruns 0                        # no retries, handy when debugging
```

The HTML report is written to `reports/report.html`. When a test fails, the trace and screenshot are saved in
`test-results/`. Open a trace with `python -m playwright show-trace test-results/<test>/trace.zip`.

## Structure

```text
api_client/ecommerce_api.py   API client (login, products, create/get/update/delete order)
config/settings.py            loads env files, checks required vars
data/test_data.py             products, categories, customer details, expected messages
pages/                        page objects: BasePage (navbar), HomePage, ProductPage, CartPage
tests/ui/                     test_navigation.py, test_cart.py, test_checkout.py
tests/api/                    test_order_api.py
conftest.py                   fixtures (page objects, api context, auth token, order cleanup)
pytest.ini                    browser, retries, tracing, report
```

## What's covered

### UI (13)

- Navigation: title, brand and categories; home > category > cart > home; each category filter only shows
  its own products; product page shows name, price, description and Add to cart
- Cart: add one product; add two products (rows + total); remove one of two, then remove the last one;
  same product added twice gives two rows; cart is still there after refresh and navigation
- Checkout: valid order shows the confirmation (id, amount, card, name), goes back home and the cart is empty
- Negative: purchase with all details / name / card missing shows the alert, the modal stays open and the
  cart is untouched
- Edge case: ordering with an empty cart

### API (7)

| Test | Expected |
|---|---|
| Login, valid credentials | 200 with token and userId |
| Login, wrong password | 400, no token |
| Get products | 200, list with id/name/price |
| Create + get order | 201 on create, order matches product and country |
| Update order | 404 (endpoint doesn't exist), order not changed |
| Delete order then get it | 200 on delete, get fails with 400/404 |
| Create order without token | 401/403 |

## Notes

- Each UI test gets a new browser context, so it starts with a new DemoBlaze guest cookie and an empty cart.
  API orders are created with the `order_factory` fixture, which deletes them after the test (even if it failed).
- No `sleep`s. The tests use `expect`, URL waits, and wait for the DemoBlaze XHR calls
  (`/bycat`, `/addtocart`, `/viewcart`, `/deleteitem`) before checking anything.
- "Product added" and the checkout validation messages are normal browser `alert()`s. They have to be accepted
  in a dialog handler. If you wait for the dialog after the click, it hangs, because the open alert blocks the page.
- The OK button on the purchase confirmation popup doesn't respond while the popup is still animating in.
  `confirm_purchase()` waits for the popup to get the `visible` class before clicking.
- The API logs in once per test session and reuses the token.
- Retries come from `pytest-rerunfailures` (`--reruns 3`). Use `--reruns 0` locally to see the first failure.

## Assumptions / limitations

- DemoBlaze has no written requirements, so for things like duplicates, empty-cart checkout and the cart after a
  refresh, the tests check what the site does now.
- Probably a bug: DemoBlaze lets you order an empty cart and shows `Amount: 0 USD`.
  `test_order_with_empty_cart` checks for this, so we'll notice if it gets fixed. In a real project I'd log it as
  a bug and change the test to expect the order to be rejected.
- DemoBlaze only validates Name and Credit card. Country, city, month and year are optional, and the card
  number format isn't checked.
- The API has no update-order endpoint, so the "update endpoint negative validation" test checks for `404` and
  that the order wasn't changed.
- Both sites are public demo sites, so products, prices and response times can change. Slow responses sometimes
  need a retry.
- Only Chromium is used. Add more browsers with `--browser firefox --browser webkit`.
- The shared training account from the reference repo doesn't work anymore (`400 Incorrect email or password`),
  so you need to put your own account in `.env.qa`.
- Some things still need manual testing: exploratory, usability, visual/responsive checks and unusual user actions.
