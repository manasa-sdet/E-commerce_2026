import re

import pytest
from playwright.sync_api import expect

from data.test_data import (
    MISSING_DETAILS_ALERT,
    PURCHASE_SUCCESS_TITLE,
    SONY_VAIO_I5,
    VALID_CUSTOMER,
)

pytestmark = pytest.mark.ui


def without(field):
    return {k: v for k, v in VALID_CUSTOMER.items() if k != field}


def test_place_order(page, add_to_cart, cart_page):
    add_to_cart(SONY_VAIO_I5)
    cart_page.open()
    expect(cart_page.rows).to_have_count(1)

    cart_page.open_order_form()
    expect(cart_page.order_modal).to_contain_text(f"Total: {SONY_VAIO_I5.price}")
    cart_page.fill_order_form(VALID_CUSTOMER)
    cart_page.purchase_button.click()

    expect(cart_page.confirmation_title).to_have_text(PURCHASE_SUCCESS_TITLE)
    details = cart_page.confirmation_details
    expect(details).to_contain_text(re.compile(r"Id: \d+"))
    expect(details).to_contain_text(f"Amount: {SONY_VAIO_I5.price} USD")
    expect(details).to_contain_text(f"Card Number: {VALID_CUSTOMER['card']}")
    expect(details).to_contain_text(f"Name: {VALID_CUSTOMER['name']}")

    cart_page.confirm_purchase()
    expect(page).to_have_url(re.compile(r"index\.html$"))

    # cart should be cleared after the order
    cart_page.open()
    expect(cart_page.rows).to_have_count(0)


@pytest.mark.parametrize(
    "customer",
    [
        pytest.param({}, id="all-details-missing"),
        pytest.param(without("name"), id="name-missing"),
        pytest.param(without("card"), id="card-missing"),
    ],
)
def test_order_missing_details(add_to_cart, cart_page, customer):
    add_to_cart(SONY_VAIO_I5)
    cart_page.open()
    cart_page.open_order_form()
    cart_page.fill_order_form(customer)

    assert cart_page.submit_order_expecting_alert() == MISSING_DETAILS_ALERT
    expect(cart_page.order_modal).to_be_visible()
    expect(cart_page.confirmation).to_be_hidden()
    # item should still be in the cart
    expect(cart_page.row_for(SONY_VAIO_I5.name)).to_be_visible()


def test_order_with_empty_cart(cart_page):
    # NOTE: demoblaze lets you order an empty cart and shows "Amount: 0 USD".
    # Looks like a bug (see README). Asserting current behaviour so we notice
    # if they ever add validation.
    cart_page.open()
    expect(cart_page.rows).to_have_count(0)

    cart_page.open_order_form()
    cart_page.fill_order_form(VALID_CUSTOMER)
    cart_page.purchase_button.click()

    expect(cart_page.confirmation_title).to_have_text(PURCHASE_SUCCESS_TITLE)
    expect(cart_page.confirmation_details).to_contain_text("Amount: 0 USD")
