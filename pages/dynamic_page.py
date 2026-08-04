"""Page object for the dynamic-loading pages.

/dynamic_loading/1 -- the element exists but is hidden, then is revealed
/dynamic_loading/2 -- the element does not exist at all until it is created

Those two cases behave identically as far as your test is concerned, which is
the point: Playwright's auto-waiting covers both without you choosing a
strategy. In older tools this distinction cost people hours.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.sites import internet


class DynamicLoadingPage(BasePage):
    def __init__(self, page: Page, variant: int = 2) -> None:
        super().__init__(page)
        self.url = internet(f"/dynamic_loading/{variant}")
        self.start: Locator = page.get_by_role("button", name="Start")
        self.loading: Locator = page.locator("#loading")
        self.finish: Locator = page.locator("#finish")

    def begin(self) -> DynamicLoadingPage:
        self.start.click()
        return self

    def result_text(self) -> str:
        return self.finish.inner_text()
