import pytest

from api_client.ecommerce_api import EcommerceApi
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage


# UI fixtures
# every test gets a new browser context from pytest-playwright, so the
# demoblaze guest cookie is new and the cart always starts empty

@pytest.fixture
def home_page(page):
    home = HomePage(page)
    home.open()
    return home


@pytest.fixture
def product_page(page):
    return ProductPage(page)


@pytest.fixture
def cart_page(page):
    return CartPage(page)


@pytest.fixture
def add_to_cart(home_page, product_page):
    def _add(product, times=1):
        home_page.open()
        home_page.select_category(product.category)
        home_page.open_product(product.name)
        for _ in range(times):
            product_page.add_to_cart()

    return _add


# API fixtures

@pytest.fixture(scope="session")
def api_request_context(playwright):
    ctx = playwright.request.new_context()
    yield ctx
    ctx.dispose()


@pytest.fixture
def anonymous_api(api_request_context):
    return EcommerceApi(api_request_context)


@pytest.fixture(scope="session")
def auth_token(api_request_context):
    # login once and reuse the token for the whole run
    return EcommerceApi(api_request_context).authenticate()


@pytest.fixture
def api(api_request_context, auth_token):
    return EcommerceApi(api_request_context, token=auth_token)


@pytest.fixture
def product(api):
    res = api.get_products()
    assert res.status == 200
    products = res.json()["data"]
    assert products, "no products returned"
    return products[0]


@pytest.fixture
def order_factory(api):
    created = []

    def _create(product_id, country):
        res = api.create_order(product_id, country)
        assert res.status == 201, res.text()
        order_id = res.json()["orders"][0]
        created.append(order_id)
        return order_id

    yield _create

    # cleanup even if the test failed. ignore the result, the test may
    # have already deleted the order
    for order_id in created:
        api.delete_order(order_id)
