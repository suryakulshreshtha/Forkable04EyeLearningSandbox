"""TOPIC 1 -- your first test.

    pytest tests/test_01_first_test.py -v
    pytest tests/test_01_first_test.py --headed --slowmo 800

Three things to notice:

1. `page` is a fixture from pytest-playwright. You never create or close a
   browser. Each test gets a fresh browser CONTEXT -- think a clean incognito
   profile -- so no test can leak cookies into another.
2. `expect(...)` is a WEB-FIRST assertion: it polls until the condition holds
   or the timeout expires. `assert locator.inner_text() == "x"` takes a single
   snapshot and is the number-one cause of flaky beginner tests.
3. `require_site` skips rather than fails when the site is down. A dependency
   being unavailable is not a defect in your automation.
"""

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.sites import internet


@pytest.mark.smoke
def test_the_page_loads(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    expect(page.get_by_role("heading", name="Login Page")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_enabled()


@pytest.mark.smoke
def test_a_successful_login(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("SuperSecretPassword!")
    page.get_by_role("button", name="Login").click()

    # No explicit wait for the navigation -- expect() handles it.
    expect(page.locator("#flash")).to_contain_text("You logged into a secure area!")
    expect(page.get_by_role("heading", name="Secure Area")).to_be_visible()


def test_a_failed_login(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("wrong-password")
    page.get_by_role("button", name="Login").click()

    expect(page.locator("#flash")).to_contain_text("Your password is invalid!")
    # Assert the negative too: we must NOT have got in.
    expect(page.get_by_role("heading", name="Secure Area")).to_have_count(0)


@pytest.mark.smoke
def test_the_same_thing_with_a_page_object(page: Page, require_site) -> None:
    """Compare this with the test above. Same coverage, no selectors in sight.

    See pages/login_page.py, and topic 6 for when POM starts to earn its keep.
    """
    require_site("the-internet")
    secure = LoginPage(page).open().login()

    expect(secure.heading).to_be_visible()
    expect(secure.logout).to_be_visible()


# YOUR TURN
# Log in, click Logout, and assert the flash says you logged out.
