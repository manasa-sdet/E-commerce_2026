from data.test_data import PRODUCT_ADDED_ALERT
from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name = page.locator("#tbodyid .name")
        self.price = page.locator("#tbodyid .price-container")
        self.description = page.locator("#more-information p")
        self.add_to_cart_button = page.get_by_role("link", name="Add to cart")

    def add_to_cart(self):
        # wait for both the api call and the alert, if we navigate away too
        # early the item sometimes doesn't make it into the cart
        with self.page.expect_event("dialog") as dialog_info:
            with self.page.expect_response(lambda r: r.url.endswith("/addtocart") and r.ok):
                self.add_to_cart_button.click()
        dialog = dialog_info.value
        msg = dialog.message
        dialog.accept()
        assert msg == PRODUCT_ADDED_ALERT, f"unexpected alert: {msg!r}"
        return msg
