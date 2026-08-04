"""Every external site this sandbox uses, in one place.

Why a module instead of literals in the tests
---------------------------------------------
We do not own any of these sites. When one of them moves, renames a page, or
dies, you want to change ONE line -- not grep 12 files. This is the same
discipline as never hard-coding a base URL at work; it just matters more here,
because the odds of an unannounced change are much higher.
"""

from __future__ import annotations

# the-internet.herokuapp.com is the long-standing practice site for automation.
# It is deliberately full of awkward widgets: delayed content, alerts, iframes,
# file inputs, dropdowns.
THE_INTERNET = "https://the-internet.herokuapp.com"

# JSONPlaceholder is a fake REST API. It accepts writes and echoes them back
# without persisting -- which is perfect for teaching request/response shape,
# and a useful reminder that a 201 does not prove anything was stored.
JSONPLACEHOLDER = "https://jsonplaceholder.typicode.com"

# Playwright's own documentation: a modern, JS-heavy site.
PLAYWRIGHT_DOCS = "https://playwright.dev"

#: Hosts we probe once per session. See the `require_site` fixture.
ALL = {
    "the-internet": THE_INTERNET,
    "jsonplaceholder": JSONPLACEHOLDER,
    "playwright-docs": PLAYWRIGHT_DOCS,
}


# Convenience page builders, so a typo is a NameError rather than a 404.
def internet(path: str = "/") -> str:
    return f"{THE_INTERNET}/{path.lstrip('/')}"


def api(path: str = "/") -> str:
    return f"{JSONPLACEHOLDER}/{path.lstrip('/')}"
