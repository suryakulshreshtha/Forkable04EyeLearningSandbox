"""What every page object shares -- and nothing more.

The commonest way the Page Object Model rots is a base class that grows until
it knows about every page. Keep this file boring.

Hard rule: page objects expose ACTIONS and STATE. They never assert. Tests
decide what is correct, because the same action is needed by tests with
completely different expectations.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page


class BasePage:
    #: Absolute URL. Subclasses set it.
    url: str = ""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> BasePage:
        self.page.goto(self.url, wait_until="domcontentloaded")
        return self

    @property
    def current_url(self) -> str:
        return self.page.url

    def flash(self) -> Locator:
        """the-internet shows results in a #flash banner on several pages."""
        return self.page.locator("#flash")
