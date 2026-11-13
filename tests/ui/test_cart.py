import pytest
from playwright.sync_api import expect

from data.test_data import NOKIA_1520, SAMSUNG_S6, SONY_VAIO_I5

pytestmark = pytest.mark.ui


def test_add_one_product(add_to_cart, cart_page):
    add_to_cart(SAMSUNG_S6)
    cart_page.open()

    expect(cart_page.rows).to_have_count(1)
    expect(cart_page.row_for(SAMSUNG_S6.name)).to_contain_text(str(SAMSUNG_S6.price))
    expect(cart_page.total).to_have_text(str(SAMSUNG_S6.price))


def test_add_multiple_products(add_to_cart, cart_page):
    products = [SAMSUNG_S6, SONY_VAIO_I5]
    for p in products:
        add_to_cart(p)
    cart_page.open()

    expect(cart_page.rows).to_have_count(2)
    for p in products:
        expect(cart_page.row_for(p.name)).to_be_visible()
    expect(cart_page.total).to_have_text(str(SAMSUNG_S6.price + SONY_VAIO_I5.price))


def test_remove_products(add_to_cart, cart_page):
    add_to_cart(SAMSUNG_S6)
    add_to_cart(SONY_VAIO_I5)
    cart_page.open()
    expect(cart_page.rows).to_have_count(2)

    cart_page.remove(SAMSUNG_S6.name)
    expect(cart_page.titles).to_have_text([SONY_VAIO_I5.name])
    expect(cart_page.total).to_have_text(str(SONY_VAIO_I5.price))

    # remove the last one, cart should be empty now
    cart_page.remove(SONY_VAIO_I5.name)
    expect(cart_page.rows).to_have_count(0)
    expect(cart_page.total).to_be_empty()


def test_same_product_twice(add_to_cart, cart_page):
    # demoblaze doesn't merge them into a quantity, you get two rows
    add_to_cart(SAMSUNG_S6, times=2)
    cart_page.open()

    expect(cart_page.titles).to_have_text([SAMSUNG_S6.name, SAMSUNG_S6.name])
    expect(cart_page.total).to_have_text(str(SAMSUNG_S6.price * 2))


def test_cart_kept_after_refresh_and_navigation(page, add_to_cart, cart_page):
    add_to_cart(NOKIA_1520)
    cart_page.open()
    expect(cart_page.row_for(NOKIA_1520.name)).to_be_visible()

    page.reload()
    expect(cart_page.row_for(NOKIA_1520.name)).to_be_visible()

    cart_page.go_home()
    cart_page.open_cart()
    expect(cart_page.rows).to_have_count(1)
    expect(cart_page.row_for(NOKIA_1520.name)).to_be_visible()
