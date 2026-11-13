from config.settings import settings


class BasePage:
    # navbar is the same on every page so it lives here

    def __init__(self, page):
        self.page = page
        self.brand = page.locator("#nava")
        self.home_link = page.get_by_role("link", name="Home")
        self.cart_link = page.get_by_role("link", name="Cart", exact=True)

    def open_url(self, path=""):
        self.page.goto(f"{settings.web_base_url}/{path}")

    def go_home(self):
        self.home_link.click()
        self.page.wait_for_url("**/index.html")

    def open_cart(self):
        self.cart_link.click()
        self.page.wait_for_url("**/cart.html")
