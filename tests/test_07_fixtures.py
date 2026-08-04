"""TOPIC 7 -- fixtures and markers.

A fixture is dependency injection with a lifecycle:

    @pytest.fixture
    def thing():
        setup()
        yield value     # the test runs here
        teardown()      # runs even if the test failed

Scope it as widely as is SAFE. Session-scoped state that tests mutate is how a
suite passes serially and fails under `-n 4`.

    function (default)  per test     anything the test mutates
    module              per file     expensive read-only setup
    session             once         browser, API client, probes

Markers select subsets: `pytest -m smoke`, `pytest -m "api and not slow"`.
Every marker is registered in pytest.ini, and --strict-markers turns a typo
into an error instead of a silently empty run.
"""

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.sites import internet


@pytest.fixture
def logged_in_page(page: Page, require_site) -> Page:
    """Composable setup. Ask for it and you are already authenticated."""
    require_site("the-internet")
    LoginPage(page).open().login()
    expect(page.get_by_role("heading", name="Secure Area")).to_be_visible()
    return page


@pytest.fixture
def counted() -> list[str]:
    """Demonstrates teardown running even when the test fails."""
    events = ["setup"]
    yield events
    events.append("teardown")


@pytest.mark.smoke
def test_a_fixture_removes_setup_noise(logged_in_page: Page) -> None:
    expect(logged_in_page.get_by_role("link", name="Logout")).to_be_visible()


def test_fixtures_compose(logged_in_page: Page, counted: list[str]) -> None:
    assert counted == ["setup"]
    logged_in_page.goto(internet("/dropdown"))
    expect(logged_in_page.locator("#dropdown")).to_be_visible()


@pytest.mark.slow
def test_markers_let_you_slice_the_suite() -> None:
    """Marked `slow`, so `pytest -m "not slow"` skips it.

    Marker discipline that matters in real life: `smoke` gates every pull
    request, so it must stay small and fast. If everything is smoke, nothing
    is -- and the team starts merging on red.
    """
    assert True


def test_builtin_fixtures(tmp_path, request) -> None:
    """`tmp_path` is unique per test AND per xdist worker, so it can never
    collide. `request` exposes the running test's metadata."""
    target = tmp_path / "note.txt"
    target.write_text("per-test directory", encoding="utf-8")

    assert target.exists()
    # pytest derives the directory from the test name but TRUNCATES it to 30
    # characters, so asserting the full name breaks the moment someone renames
    # the test to something longer. Compare a prefix. (Found by running it --
    # the original version of this line failed at 34 characters.)
    assert request.node.name[:20] in str(tmp_path)


# YOUR TURN
# Run `pytest --fixtures | head -40` and find where `page` comes from.
