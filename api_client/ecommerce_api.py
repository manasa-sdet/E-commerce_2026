from playwright.sync_api import APIRequestContext, APIResponse

from config.settings import settings


class EcommerceApi:
    LOGIN = "auth/login"
    PRODUCTS = "product/get-all-products"
    CREATE_ORDER = "order/create-order"
    ORDER_DETAILS = "order/get-orders-details?id={}"
    UPDATE_ORDER = "order/update-order/{}"
    DELETE_ORDER = "order/delete-order/{}"

    def __init__(self, request: APIRequestContext, token=None):
        self.request = request
        self.token = token

    def _url(self, path):
        return f"{settings.api_base_url}/{path}"

    def _headers(self):
        if self.token:
            return {"Authorization": self.token}
        return {}

    def login(self, email=None, password=None) -> APIResponse:
        if email is None:
            email = settings.api_email
        if password is None:
            password = settings.api_password
        return self.request.post(
            self._url(self.LOGIN),
            data={"userEmail": email, "userPassword": password},
        )

    def authenticate(self):
        res = self.login()
        assert res.status == 200, f"login failed: {res.status} {res.text()}"
        self.token = res.json()["token"]
        return self.token

    def get_products(self) -> APIResponse:
        return self.request.post(self._url(self.PRODUCTS), headers=self._headers(), data={})

    def create_order(self, product_id, country) -> APIResponse:
        payload = {"orders": [{"country": country, "productOrderedId": product_id}]}
        return self.request.post(self._url(self.CREATE_ORDER), headers=self._headers(), data=payload)

    def get_order(self, order_id) -> APIResponse:
        url = self._url(self.ORDER_DETAILS.format(order_id))
        return self.request.get(url, headers=self._headers())

    def update_order(self, order_id, country) -> APIResponse:
        url = self._url(self.UPDATE_ORDER.format(order_id))
        return self.request.put(url, headers=self._headers(), data={"country": country})

    def delete_order(self, order_id) -> APIResponse:
        url = self._url(self.DELETE_ORDER.format(order_id))
        return self.request.delete(url, headers=self._headers())
