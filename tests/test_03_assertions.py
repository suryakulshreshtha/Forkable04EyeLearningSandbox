"""TOPIC 3 -- web-first assertions.

    expect(locator).to_have_text("x")    polls, retries, then fails with context
    assert locator.inner_text() == "x"   one snapshot, races the application

The first waits for the app to catch up. In a suite of any size, that
difference IS the flakiness.
"""

import pytest
from playwright.sync_api import Page, expect

from utils.sites import internet


def test_visibility_and_state(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/dynamic_loading/2"))

    expect(page.locator("#finish")).to_have_count(0)
    page.get_by_role("button", name="Start").click()
    # The element does not exist yet. We write no waiting code at all.
    expect(page.locator("#finish")).to_be_visible()
    expect(page.locator("#finish")).to_have_text("Hello World!")


def test_text_assertions(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    flash_free_heading = page.get_by_role("heading", name="Login Page")
    expect(flash_free_heading).to_have_text("Login Page")  # exact
    expect(page.locator("#content")).to_contain_text("tomsmith")  # substring


def test_list_assertions_cover_count_and_order(page: Page, require_site) -> None:
    """Passing a list asserts BOTH the number of elements and their order --
    which makes it a free regression test for sorting."""
    require_site("the-internet")
    page.goto(internet("/dropdown"))

    expect(page.locator("#dropdown option")).to_have_text(
        ["Please select an option", "Option 1", "Option 2"]
    )


def test_attribute_and_value(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    expect(page.locator("#username")).to_have_attribute("type", "text")
    page.locator("#username").fill("tomsmith")
    expect(page.locator("#username")).to_have_value("tomsmith")


def test_negative_assertions_and_timeouts(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    # not_to_* waits for the condition to BECOME true; it is not "check now".
    expect(page.locator("#flash")).not_to_be_visible()
    # Tighten the timeout on assertions you expect to pass instantly, so
    # failures are fast. Raise it only on the specific step that is slow.
    expect(page.get_by_role("button", name="Login")).to_be_visible(timeout=5000)


@pytest.mark.smoke
def test_soft_assertions_collect_several_failures(page: Page, require_site) -> None:
    """Useful for "check eight fields on this form" so one run reports all
    eight. Overuse hides real failures -- keep a hard assert for the thing the
    test is actually about."""
    require_site("the-internet")
    page.goto(internet("/login"))

    expect.soft(page.get_by_role("heading", name="Login Page")).to_be_visible()
    expect.soft(page.locator("#username")).to_be_editable()
    expect(page.get_by_role("button", name="Login")).to_be_enabled()


# YOUR TURN
# On /tables, assert the rows of table #table1 appear in a specific order using
# ONE expect() call.
