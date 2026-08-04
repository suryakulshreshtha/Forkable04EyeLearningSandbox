"""TOPIC 10 -- the things that live outside the page: dialogs, iframes, tabs.

These trip people up because the element is not in the page's DOM at all.
Playwright models each one explicitly rather than making you juggle handles.
"""

import pytest
from playwright.sync_api import Page, expect

from utils.sites import internet


def test_accept_a_javascript_alert(page: Page, require_site) -> None:
    """Playwright AUTO-DISMISSES dialogs unless you register a handler.

    That is the opposite of most tools and catches everyone once: without the
    `on("dialog")` line below, the alert is dismissed for you and the assertion
    still passes -- for the wrong reason.
    """
    require_site("the-internet")
    page.goto(internet("/javascript_alerts"))

    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Click for JS Alert").click()

    expect(page.locator("#result")).to_have_text("You successfully clicked an alert")


def test_dismiss_a_confirm(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/javascript_alerts"))

    page.on("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Click for JS Confirm").click()

    expect(page.locator("#result")).to_have_text("You clicked: Cancel")


def test_answer_a_prompt(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/javascript_alerts"))

    page.on("dialog", lambda dialog: dialog.accept("sandbox"))
    page.get_by_role("button", name="Click for JS Prompt").click()

    expect(page.locator("#result")).to_have_text("You entered: sandbox")


def test_work_inside_an_iframe(page: Page, require_site) -> None:
    """frame_locator() reads like a normal locator chain. No switch_to.frame,
    and no forgetting to switch back."""
    require_site("the-internet")
    page.goto(internet("/iframe"))

    editor = page.frame_locator("#mce_0_ifr").locator("body#tinymce")
    expect(editor).to_be_visible()
    expect(editor).to_contain_text("Your content goes here.")


def test_a_link_that_opens_a_new_tab(page: Page, require_site) -> None:
    """expect_popup() must WRAP the click -- start listening before the event,
    or you race the browser."""
    require_site("the-internet")
    page.goto(internet("/windows"))

    with page.expect_popup() as popup_info:
        page.get_by_role("link", name="Click Here").click()

    new_tab = popup_info.value
    expect(new_tab.get_by_text("New Window")).to_be_visible()
    assert page.url.endswith("/windows")  # the original tab is untouched
    new_tab.close()


@pytest.mark.parametrize("code", [200, 301, 404, 500])
def test_http_status_pages(page: Page, require_site, code: int) -> None:
    """page.goto() returns the Response, which is how you assert on status."""
    require_site("the-internet")
    response = page.goto(internet(f"/status_codes/{code}"))

    assert response is not None
    assert response.status == code


# YOUR TURN
# On /hovers, hover the first avatar and assert the caption appears.
