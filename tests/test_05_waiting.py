"""TOPIC 5 -- waiting. The habit that separates stable suites from flaky ones.

THE RULE:  time.sleep() is never the answer.

A sleep is a bet that the app is slower than X and faster than X. On a cold,
shared, two-core CI runner you lose that bet. In order of preference:

  1. Do nothing -- actions and expect() auto-wait. Covers ~90% of cases.
  2. expect(...) with a larger timeout, for genuinely slow steps.
  3. wait_for_* / expect_* for events that are not DOM state: a network
     response, a popup, a download.
"""

import time

import pytest
from playwright.sync_api import Page, expect

from pages.dynamic_page import DynamicLoadingPage
from utils.sites import internet


@pytest.mark.smoke
def test_auto_waiting_needs_no_code(page: Page, require_site) -> None:
    require_site("the-internet")
    dynamic = DynamicLoadingPage(page, variant=2).open().begin()

    # The element does not exist when we ask for it. Zero waiting code.
    expect(dynamic.finish).to_have_text("Hello World!")


def test_hidden_then_revealed_behaves_identically(page: Page, require_site) -> None:
    """Variant 1 hides the element; variant 2 creates it. Your test cannot tell
    the difference, and does not need to."""
    require_site("the-internet")
    dynamic = DynamicLoadingPage(page, variant=1).open().begin()

    expect(dynamic.finish).to_be_visible()
    expect(dynamic.loading).to_be_hidden()


def test_custom_timeout_for_a_genuinely_slow_step(page: Page, require_site) -> None:
    """Raise the timeout on the ONE slow assertion, never globally -- a global
    bump hides regressions everywhere else."""
    require_site("the-internet")
    page.goto(internet("/dynamic_loading/2"))
    page.get_by_role("button", name="Start").click()

    expect(page.locator("#finish")).to_be_visible(timeout=30000)


def test_waiting_for_a_network_response(page: Page, require_site) -> None:
    """Sometimes the thing you care about never appears in the DOM."""
    require_site("the-internet")

    with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST") as info:
        page.goto(internet("/login"))
        page.get_by_label("Username").fill("tomsmith")
        page.get_by_label("Password").fill("SuperSecretPassword!")
        page.get_by_role("button", name="Login").click()

    assert info.value.status in (200, 302)


@pytest.mark.slow
def test_why_sleep_is_wrong(page: Page, require_site) -> None:
    """A demonstration, not a pattern to copy.

    Note the cost even when it "works": this test is always ~6s, whether the
    content arrives in 5s or 50ms. Multiply that by 300 tests.
    """
    require_site("the-internet")
    page.goto(internet("/dynamic_loading/2"))
    page.get_by_role("button", name="Start").click()

    started = time.time()
    time.sleep(6)
    assert time.time() - started >= 6
    expect(page.locator("#finish")).to_have_text("Hello World!")

    # The correct version of this whole test is one line, and finishes as soon
    # as the element appears:
    #     expect(page.locator("#finish")).to_have_text("Hello World!")


# YOUR TURN
# Delete the sleep above and measure the difference with `pytest --durations=5`.
