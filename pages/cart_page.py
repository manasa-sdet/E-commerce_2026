import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.rows = page.locator("#tbodyid tr")
        self.titles = page.locator("#tbodyid tr td:nth-child(2)")
        self.total = page.locator("#totalp")
        self.place_order_button = page.get_by_role("button", name="Place Order")

        # place order popup
        self.order_modal = page.locator("#orderModal")
        self.name_input = self.order_modal.locator("#name")
        self.country_input = self.order_modal.locator("#country")
        self.city_input = self.order_modal.locator("#city")
        self.card_input = self.order_modal.locator("#card")
        self.month_input = self.order_modal.locator("#month")
        self.year_input = self.order_modal.locator("#year")
        self.purchase_button = self.order_modal.get_by_role("button", name="Purchase")

        # "thank you" popup after purchase
        self.confirmation = page.locator(".sweet-alert")
        self.confirmation_title = self.confirmation.locator("h2")
        self.confirmation_details = self.confirmation.locator("p.lead")
        self.confirmation_ok = self.confirmation.get_by_role("button", name="OK")

    def open(self):
        # cart items load via ajax after the page loads, wait for that call
        with self.page.expect_response(lambda r: r.url.endswith("/viewcart") and r.ok):
            self.open_url("cart.html")

    def row_for(self, product_name):
        return self.rows.filter(has_text=product_name)

    def remove(self, product_name, index=0):
        count_after = self.rows.count() - 1
        with self.page.expect_response(lambda r: r.url.endswith("/deleteitem") and r.ok):
            self.row_for(product_name).nth(index).get_by_role("link", name="Delete").click()
        expect(self.rows).to_have_count(count_after)

    def open_order_form(self):
        self.place_order_button.click()
        expect(self.order_modal).to_be_visible()

    def fill_order_form(self, customer):
        inputs = {
            "name": self.name_input,
            "country": self.country_input,
            "city": self.city_input,
            "card": self.card_input,
            "month": self.month_input,
            "year": self.year_input,
        }
        for field, value in customer.items():
            inputs[field].fill(value)

    def confirm_purchase(self):
        # clicking OK while the popup is still animating does nothing.
        # it gets the "visible" class once it's actually ready
        expect(self.confirmation).to_have_class(re.compile(r"\bvisible\b"))
        self.confirmation_ok.click()
        self.page.wait_for_url("**/index.html")

    def submit_order_expecting_alert(self):
        """Click Purchase when we expect a validation alert, returns the alert text."""
        messages = []

        def on_dialog(dialog):
            messages.append(dialog.message)
            dialog.accept()

        # have to accept inside the handler, otherwise the alert blocks the
        # page and click() never returns
        self.page.once("dialog", on_dialog)
        self.purchase_button.click()
        assert messages, "expected a validation alert but got none"
        return messages[0]
