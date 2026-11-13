from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.product_titles = page.locator("#tbodyid .card-title")
        self.category_links = page.locator("#itemc")

    def open(self):
        self.open_url("index.html")
        self.product_titles.first.wait_for()

    def select_category(self, category):
        # products get swapped out after the /bycat call returns
        with self.page.expect_response(lambda r: r.url.endswith("/bycat") and r.ok):
            self.page.get_by_role("link", name=category, exact=True).click()

    def product_link(self, name):
        return self.page.locator("#tbodyid .card-title a", has_text=name)

    def open_product(self, name):
        self.product_link(name).click()
        self.page.wait_for_url("**/prod.html?idp_=*")
