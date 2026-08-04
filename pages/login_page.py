"""Page object for https://the-internet.herokuapp.com/login"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.sites import internet

#: The site publishes these on the page itself -- they are not a secret.
VALID_USER = "tomsmith"
VALID_PASSWORD = "SuperSecretPassword!"


class LoginPage(BasePage):
    url = internet("/login")

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Locators are lazy: nothing touches the DOM until an action or an
        # assertion runs, so defining them before navigation is fine.
        self.username: Locator = page.get_by_label("Username")
        self.password: Locator = page.get_by_label("Password")
        self.submit: Locator = page.get_by_role("button", name="Login")

    def login(self, username: str = VALID_USER, password: str = VALID_PASSWORD) -> SecureAreaPage:
        """Happy path returns the NEXT page object.

        That is the POM idiom that makes a test read as one sentence, and makes
        your IDE offer only the steps that are legal from here.
        """
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
        return SecureAreaPage(self.page)

    def login_expecting_failure(self, username: str, password: str) -> LoginPage:
        """The unhappy path stays here, so it returns self."""
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
        return self


class SecureAreaPage(BasePage):
    url = internet("/secure")

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading: Locator = page.get_by_role("heading", name="Secure Area")
        self.logout: Locator = page.get_by_role("link", name="Logout")
