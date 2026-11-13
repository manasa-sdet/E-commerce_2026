import pytest

from config.settings import settings
from data.test_data import (
    API_ORDER_COUNTRY,
    API_UPDATED_COUNTRY,
    INVALID_PASSWORD,
    INVALID_PRODUCT_ID,
)

pytestmark = pytest.mark.api


def test_login_valid_credentials(anonymous_api):
    res = anonymous_api.login()

    assert res.status == 200
    body = res.json()
    assert body["token"]
    assert body["userId"]
    assert body["message"] == "Login Successfully"


def test_login_invalid_password(anonymous_api):
    res = anonymous_api.login(settings.api_email, INVALID_PASSWORD)

    assert res.status == 400
    assert "token" not in res.json()


def test_get_products(api):
    res = api.get_products()

    assert res.status == 200
    products = res.json()["data"]
    assert len(products) > 0
    for p in products:
        assert p["_id"]
        assert p["productName"]
        assert p["productPrice"] > 0


def test_create_and_get_order(api, product, order_factory):
    order_id = order_factory(product["_id"], API_ORDER_COUNTRY)

    res = api.get_order(order_id)

    assert res.status == 200
    order = res.json()["data"]
    assert order["_id"] == order_id
    assert order["productOrderedId"] == product["_id"]
    assert order["productName"] == product["productName"]
    assert order["country"] == API_ORDER_COUNTRY


def test_update_order_not_supported(api, product, order_factory):
    # there's no update endpoint, make sure we get 404 and nothing changes
    order_id = order_factory(product["_id"], API_ORDER_COUNTRY)

    res = api.update_order(order_id, API_UPDATED_COUNTRY)
    assert res.status == 404

    order = api.get_order(order_id).json()["data"]
    assert order["country"] == API_ORDER_COUNTRY


def test_delete_order(api, product, order_factory):
    order_id = order_factory(product["_id"], API_ORDER_COUNTRY)

    res = api.delete_order(order_id)
    assert res.status == 200
    assert res.json()["message"] == "Orders Deleted Successfully"

    lookup = api.get_order(order_id)
    assert not lookup.ok
    assert lookup.status in (400, 404)


def test_create_order_without_token(anonymous_api):
    res = anonymous_api.create_order(INVALID_PRODUCT_ID, API_ORDER_COUNTRY)

    assert not res.ok
    assert res.status in (401, 403)
