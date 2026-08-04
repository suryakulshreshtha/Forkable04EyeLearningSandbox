"""TOPIC 12 -- debugging, and reading what Playwright already tells you.

The escalation ladder:

  1. READ THE ERROR. Playwright's messages are unusually good: they name the
     locator, what it resolved to, and what it waited for.
  2. `--headed --slowmo 500`  -- watch it.
  3. `PWDEBUG=1`              -- Playwright Inspector: step, and pick locators
                                 off the page to check for ambiguity.
  4. Open the TRACE           -- especially for a CI failure you cannot
                                 reproduce locally.

A trace records a DOM snapshot before and after every action, plus network,
console and screenshots. We capture `retain-on-failure`, so passing runs cost
nothing:

    playwright show-trace reports/test-results/<test>/trace.zip
    make trace

Other tools:

    pytest -x            stop at the first failure
    pytest --lf          rerun only what failed last time
    pytest --sw          stepwise: stop, fix, continue from there
    pytest --durations=5 find your slowest tests
    playwright codegen https://the-internet.herokuapp.com/login
                         record clicks into Python -- treat it as a DRAFT; it
                         picks positional locators you would not choose
"""

import pytest
from playwright.sync_api import Page, expect

from utils.sites import internet


@pytest.mark.smoke
def test_a_good_failure_message_is_a_feature(page: Page, require_site) -> None:
    """We deliberately look for something that is not there, catch the error,
    and inspect it. This is the message you will read in CI -- learn its shape
    now rather than at 6pm on a Friday.
    """
    require_site("the-internet")
    page.goto(internet("/login"))

    missing = page.get_by_role("button", name="This Button Does Not Exist")

    with pytest.raises(AssertionError) as failure:
        expect(missing).to_be_visible(timeout=3000)

    message = str(failure.value)
    # The message names the locator and shows the wait log, which is exactly
    # what you need to tell "wrong locator" from "too slow" apart.
    assert "This Button Does Not Exist" in message
    assert "Locator expected to be visible" in message or "expect" in message.lower()


def test_pause_and_screenshot_helpers(page: Page, require_site, tmp_path) -> None:
    """A deliberate screenshot for documentation or a bug report. Failures are
    captured automatically -- see pytest.ini -- so use this only when you want
    a specific shot."""
    require_site("the-internet")
    page.goto(internet("/login"))

    shot = tmp_path / "login.png"
    page.screenshot(path=str(shot), full_page=True)
    assert shot.exists()
    assert shot.stat().st_size > 0

    # Uncomment to drop into the Inspector at exactly this point:
    # page.pause()


def test_console_and_network_are_observable(page: Page, require_site) -> None:
    """Half of "the test is flaky" turns out to be a JS error on the page."""
    require_site("the-internet")
    console_messages: list[str] = []
    requests: list[str] = []

    page.on("console", lambda msg: console_messages.append(msg.type))
    page.on("request", lambda req: requests.append(req.resource_type))

    page.goto(internet("/login"))
    expect(page.get_by_role("button", name="Login")).to_be_visible()

    assert "document" in requests
    assert "error" not in console_messages, f"page logged a JS error: {console_messages}"


# YOUR TURN
# Break a locator in topic 1 on purpose, run it, and read the failure. Then run
# `make trace` and find the moment it went wrong.
