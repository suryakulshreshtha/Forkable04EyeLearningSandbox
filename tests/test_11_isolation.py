"""TOPIC 11 -- tests that survive `pytest -n auto`.

Four rules:

1. No shared mutable state. Generate your own data; never assume record #3
   exists.
2. No ordering assumptions. If test B needs test A, they are one test.
3. Clean up what you create, or use a reset hook.
4. Unique file and directory names. `tmp_path` gives you one per test.

Browser CONTEXTS are the mechanism that makes this cheap: they are fully
isolated, cost about a millisecond, and pytest-playwright gives each test a
fresh one automatically.

Run this file four ways -- all must pass:
    pytest tests/test_11_isolation.py
    pytest tests/test_11_isolation.py -n 4
    pytest tests/test_11_isolation.py -p no:randomly
    pytest tests/test_11_isolation.py --count 3      (needs pytest-repeat)
"""

import os
import time

import pytest
from playwright.sync_api import Browser, expect

from pages.login_page import LoginPage
from utils.sites import internet


def unique_suffix() -> str:
    """Unique per worker AND per call.

    The counter matters. A timestamp alone is not unique: two calls inside the
    same millisecond collide, and modern machines do a lot in a millisecond.
    That is a real bug people ship, and it only ever shows up in CI.
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    unique_suffix.counter += 1
    return f"{worker}-{int(time.time() * 1000) % 1_000_000}-{unique_suffix.counter}"


unique_suffix.counter = 0


def test_suffixes_do_not_collide() -> None:
    values = {unique_suffix() for _ in range(50)}
    assert len(values) == 50


def test_two_contexts_are_isolated(browser: Browser, require_site) -> None:
    """Authenticated and anonymous side by side in one browser process. This is
    what makes parallel UI testing safe."""
    require_site("the-internet")

    authed_ctx = browser.new_context()
    anon_ctx = browser.new_context()
    authed, anon = authed_ctx.new_page(), anon_ctx.new_page()

    LoginPage(authed).open().login()
    expect(authed.get_by_role("heading", name="Secure Area")).to_be_visible()

    anon.goto(internet("/secure"))
    # No session in this context, so the site bounces us back.
    expect(anon.locator("#flash")).to_contain_text("must login")

    authed_ctx.close()
    anon_ctx.close()


@pytest.mark.parametrize("index", range(4))
def test_each_copy_is_independent(page, require_site, index: int) -> None:
    """Four parametrised runs that share nothing. Order is irrelevant, so a
    shard can split them across four machines safely."""
    require_site("the-internet")
    page.goto(internet("/login"))

    marker = f"user-{unique_suffix()}"
    page.get_by_label("Username").fill(marker)
    expect(page.get_by_label("Username")).to_have_value(marker)


def test_temp_files_are_per_test(tmp_path) -> None:
    target = tmp_path / "output.csv"
    target.write_text("id,name\n1,sandbox\n", encoding="utf-8")

    assert target.exists()
    # pytest names the directory after the test, so two tests -- and two
    # workers -- can never collide. Compare a PREFIX: pytest truncates the
    # name to 30 characters, so a longer test name would break a full match.
    assert "test_temp_files" in str(tmp_path)


# YOUR TURN
# Deliberately break isolation: make two tests share a module-level list and
# assert on its length. Run with -n 4 and watch it fail. Then fix it.
