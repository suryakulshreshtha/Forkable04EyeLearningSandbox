"""TOPIC 6 -- the Page Object Model.

The problem it solves: twelve tests each containing `page.locator("#login")`.
A developer renames the id. Twelve failures, one cause, twelve edits. POM makes
that one edit.

The rules that keep it healthy:

  * A page object exposes ACTIONS and STATE. It never asserts. A page object
    with assertions can only be used one way, and `login()` is needed by tests
    that are not about login at all.
  * Return the DESTINATION page from an action. The test then reads as prose,
    and your IDE offers only the steps that are legal next.
  * Put locators in __init__. They are lazy, so that is safe before navigation.
  * Keep the base class boring. A bloated BasePage is how POM rots.

It is not free. Below roughly twenty tests, or for a page used once, plain
locators are clearer.
"""

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import VALID_PASSWORD, VALID_USER, LoginPage


@pytest.fixture
def login_page(page: Page, require_site) -> LoginPage:
    require_site("the-internet")
    return LoginPage(page).open()


@pytest.mark.smoke
def test_valid_login_reads_like_a_sentence(login_page: LoginPage) -> None:
    secure = login_page.login()

    expect(secure.heading).to_be_visible()
    expect(secure.flash()).to_contain_text("You logged into a secure area!")


@pytest.mark.parametrize(
    ("username", "password", "expected"),
    [
        ("wrong-user", VALID_PASSWORD, "Your username is invalid!"),
        (VALID_USER, "wrong-password", "Your password is invalid!"),
        ("", "", "Your username is invalid!"),
    ],
    ids=["bad-username", "bad-password", "both-empty"],
)
def test_invalid_logins(login_page: LoginPage, username, password, expected) -> None:
    """`ids=` is not cosmetic: it is the difference between a CI failure
    reading `[bad-password]` and `[case1]`."""
    result = login_page.login_expecting_failure(username, password)
    expect(result.flash()).to_contain_text(expected)


def test_logout_returns_to_login(login_page: LoginPage) -> None:
    secure = login_page.login()
    secure.logout.click()

    expect(login_page.page.get_by_role("heading", name="Login Page")).to_be_visible()


# YOUR TURN
# Add pages/upload_page.py for /upload and rewrite the upload test in topic 4
# to use it. See TASKS.md -- this one is on the board as a good first issue.
