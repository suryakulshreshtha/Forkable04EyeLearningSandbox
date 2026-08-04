"""TOPIC 2 -- locators: finding things without writing brittle selectors.

Priority order used by professional teams:

    get_by_role        how a user or screen reader perceives the page. Best.
    get_by_label       form controls; also pressures the app into being accessible
    get_by_placeholder only when there is genuinely no label
    get_by_text        static content
    get_by_test_id     an explicit contract with the developers
    CSS                fine for structural hooks
    XPath              last resort; unreadable and breaks on any DOM reshuffle

A locator is LAZY and RE-RESOLVED on every use, which is why Playwright has no
stale-element exceptions.
"""

import re

import pytest
from playwright.sync_api import Page, expect

from utils.sites import internet


@pytest.fixture(autouse=True)
def _open_login(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))


def test_four_ways_to_find_one_field(page: Page) -> None:
    by_label = page.get_by_label("Username")
    by_css = page.locator("#username")
    by_name = page.locator("input[name='username']")
    by_xpath = page.locator("//input[@id='username']")  # shown for contrast only

    for locator in (by_label, by_css, by_name, by_xpath):
        expect(locator).to_be_visible()
    assert by_label.count() == 1


def test_roles_are_not_tag_names(page: Page) -> None:
    """A trap worth meeting early.

    <input type="password"> has NO implicit ARIA role, so get_by_role("textbox")
    finds the username field only. When a role locator surprises you, check the
    ARIA spec rather than guessing.
    """
    expect(page.get_by_role("textbox")).to_have_count(1)
    expect(page.get_by_label("Password")).to_have_count(1)


def test_text_matching_modes(page: Page) -> None:
    expect(page.get_by_text("This is where you can log into")).to_be_visible()
    expect(page.get_by_role("heading", name="Login Page", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(r"log ?in", re.IGNORECASE)).first).to_be_visible()


def test_strict_mode_is_protecting_you(page: Page) -> None:
    """Playwright refuses to act on an ambiguous locator instead of silently
    picking the first match. This is a feature: silent first-match is how
    false-green suites are born."""
    inputs = page.locator("#login input")
    assert inputs.count() >= 2

    with pytest.raises(Exception, match="strict mode violation"):
        inputs.fill("boom", timeout=3000)


def test_scoping_and_filtering_beat_clever_selectors(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/"))

    links = page.get_by_role("link")
    # filter() by text is readable; an XPath with contains() is not.
    expect(links.filter(has_text="Dynamic Loading")).to_have_count(1)
    # Scope to a container rather than reaching across the whole document.
    expect(
        page.locator("#content").get_by_role("heading", name="Available Examples")
    ).to_be_visible()


# YOUR TURN
# On /checkboxes, find both checkboxes three different ways and assert the
# second one starts checked.
