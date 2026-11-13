from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    name: str
    price: int
    category: str


# demoblaze products
SAMSUNG_S6 = Product("Samsung galaxy s6", 360, "Phones")
NOKIA_1520 = Product("Nokia lumia 1520", 820, "Phones")
SONY_VAIO_I5 = Product("Sony vaio i5", 790, "Laptops")
APPLE_MONITOR = Product("Apple monitor 24", 400, "Monitors")

CATEGORIES = {
    "Phones": SAMSUNG_S6,
    "Laptops": SONY_VAIO_I5,
    "Monitors": APPLE_MONITOR,
}

STORE_TITLE = "STORE"

VALID_CUSTOMER = {
    "name": "QA Tester",
    "country": "India",
    "city": "Bengaluru",
    "card": "4111111111111111",
    "month": "11",
    "year": "2026",
}

MISSING_DETAILS_ALERT = "Please fill out Name and Creditcard."
PRODUCT_ADDED_ALERT = "Product added"
PURCHASE_SUCCESS_TITLE = "Thank you for your purchase!"

# api
API_ORDER_COUNTRY = "India"
API_UPDATED_COUNTRY = "Canada"
INVALID_PASSWORD = "definitely-wrong-password"
INVALID_PRODUCT_ID = "000000000000000000000000"
