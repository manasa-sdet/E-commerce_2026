import re

import pytest
from playwright.sync_api import expect

from data.test_data import APPLE_MONITOR, CATEGORIES, SONY_VAIO_I5, STORE_TITLE

pytestmark = pytest.mark.ui


def test_home_page_and_navigation(page, home_page):
    expect(page).to_have_title(STORE_TITLE)
    expect(home_page.brand).to_contain_text("PRODUCT STORE")
    expect(home_page.category_links).to_have_text(["Phones", "Laptops", "Monitors"])
    expect(home_page.product_titles.first).to_be_visible()

    home_page.select_category(APPLE_MONITOR.category)
    expect(home_page.product_link(APPLE_MONITOR.name)).to_be_visible()

    home_page.open_cart()
    expect(page).to_have_url(re.compile(r"cart\.html$"))
    expect(page.get_by_role("heading", name="Products")).to_be_visible()

    home_page.go_home()
    expect(page).to_have_url(re.compile(r"index\.html$"))
    expect(home_page.product_titles.first).to_be_visible()


def test_category_filter(home_page):
    for category, product in CATEGORIES.items():
        home_page.select_category(category)
        expect(home_page.product_link(product.name)).to_be_visible()

        # products from the other categories shouldn't show up
        for other in CATEGORIES.values():
            if other.category != category:
                expect(home_page.product_link(other.name)).to_have_count(0)


def test_product_details(page, home_page, product_page):
    home_page.select_category(SONY_VAIO_I5.category)
    home_page.open_product(SONY_VAIO_I5.name)

    expect(page).to_have_url(re.compile(r"prod\.html\?idp_=\d+"))
    expect(product_page.name).to_have_text(SONY_VAIO_I5.name)
    expect(product_page.price).to_contain_text(f"${SONY_VAIO_I5.price}")
    expect(product_page.description).not_to_be_empty()
    expect(product_page.add_to_cart_button).to_be_visible()
