"""TOPIC 4 -- interacting: fill, check, select, upload.

Every action runs an ACTIONABILITY check first: the element must be attached,
visible, stable, able to receive events and enabled. Playwright retries until
all of those hold. That is why you almost never need a wait before a click.
"""

import pytest
from playwright.sync_api import Page, expect

from utils.sites import internet


def test_fill_versus_typing(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))
    username = page.get_by_label("Username")

    # fill() clears and sets in one operation and fires the input event, so
    # React/Vue see it. Use this by default.
    username.fill("tomsmith")
    expect(username).to_have_value("tomsmith")

    # press_sequentially() emulates real keystrokes. Only needed when the app
    # reacts per key: autocomplete, input masks, character counters.
    username.clear()
    username.press_sequentially("tom", delay=40)
    expect(username).to_have_value("tom")


def test_checkboxes(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/checkboxes"))
    boxes = page.locator("#checkboxes input[type=checkbox]")

    expect(boxes).to_have_count(2)
    expect(boxes.nth(0)).not_to_be_checked()
    expect(boxes.nth(1)).to_be_checked()

    boxes.nth(0).check()  # idempotent: a no-op if already checked
    boxes.nth(1).uncheck()
    expect(boxes.nth(0)).to_be_checked()
    expect(boxes.nth(1)).not_to_be_checked()


@pytest.mark.parametrize(("value", "label"), [("1", "Option 1"), ("2", "Option 2")])
def test_dropdown(page: Page, require_site, value: str, label: str) -> None:
    """Data-driven: one function, two independent results in the report."""
    require_site("the-internet")
    page.goto(internet("/dropdown"))

    page.locator("#dropdown").select_option(value)
    expect(page.locator("#dropdown")).to_have_value(value)
    expect(page.locator("#dropdown option:checked")).to_have_text(label)


def test_keyboard_submit(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/login"))

    page.get_by_label("Username").fill("tomsmith")
    page.get_by_label("Password").fill("SuperSecretPassword!")
    page.get_by_label("Password").press("Enter")

    expect(page.locator("#flash")).to_contain_text("You logged into a secure area!")


def test_file_upload_from_memory(page: Page, require_site) -> None:
    """No temp file on disk: nothing to create, nothing to clean up, nothing to
    collide under `-n auto`. Prefer this in CI."""
    require_site("the-internet")
    page.goto(internet("/upload"))

    page.locator("#file-upload").set_input_files(
        files=[{"name": "sandbox.txt", "mimeType": "text/plain", "buffer": b"hello sandbox\n"}]
    )
    page.locator("#file-submit").click()

    expect(page.get_by_role("heading", name="File Uploaded!")).to_be_visible()
    expect(page.locator("#uploaded-files")).to_have_text("sandbox.txt")


def test_adding_and_removing_elements(page: Page, require_site) -> None:
    require_site("the-internet")
    page.goto(internet("/add_remove_elements/"))

    add = page.get_by_role("button", name="Add Element")
    for _ in range(3):
        add.click()
    expect(page.locator(".added-manually")).to_have_count(3)

    page.locator(".added-manually").first.click()
    expect(page.locator(".added-manually")).to_have_count(2)


# YOUR TURN
# On /inputs, type a number, press ArrowUp twice, and assert the value.
