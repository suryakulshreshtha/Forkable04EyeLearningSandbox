"""TOPIC 9 -- intercepting the network with page.route().

Why an SDET cares: some states are impossible or expensive to produce for real
-- a 500 from a payment provider, a ten-thousand-row response, a field that is
null only for accounts created before 2019. Mocking gives you those states in
milliseconds, deterministically, without asking the backend team for anything.

The honest trade-off: a mocked test proves your UI handles a response SHAPE. It
does NOT prove the backend still produces that shape. Pair every mocked test
with a real contract test (topic 8), or you will ship a green suite against a
changed API.

Bonus: the first test here needs no network at all, because route() intercepts
before the request leaves the browser.
"""

from playwright.sync_api import Page, Route, expect

from utils.sites import api, internet


def test_fulfil_a_whole_page_without_a_server(page: Page) -> None:
    """route() fires before the request goes out, so this passes even if the
    site is down. Handy for testing rendering in isolation."""
    page.route(
        "**/mocked-page",
        lambda route: route.fulfill(
            status=200,
            content_type="text/html",
            body="<h1>Served entirely by the test</h1><p id='who'>no server involved</p>",
        ),
    )
    page.goto("https://example.invalid/mocked-page")

    expect(page.get_by_role("heading", name="Served entirely by the test")).to_be_visible()
    expect(page.locator("#who")).to_have_text("no server involved")


def test_stub_a_json_response(page: Page, require_site) -> None:
    """Navigating to a JSON endpoint renders it as the document, which makes
    the stub easy to see."""
    require_site("jsonplaceholder")
    page.route(
        "**/posts/1",
        lambda route: route.fulfill(json={"id": 1, "title": "stubbed title", "userId": 99}),
    )
    page.goto(api("/posts/1"))

    expect(page.locator("body")).to_contain_text("stubbed title")


def test_modify_a_real_response(page: Page, require_site) -> None:
    """Let the request reach the server, then tamper with the reply.

    Ideal for "what if this optional field is missing" without hand-writing the
    entire payload.
    """
    require_site("jsonplaceholder")

    def shout(route: Route) -> None:
        response = route.fetch()
        body = response.json()
        body["title"] = body["title"].upper()
        route.fulfill(response=response, json=body)

    page.route("**/posts/1", shout)
    page.goto(api("/posts/1"))

    text = page.locator("body").inner_text()
    assert text == text.upper() or "TITLE" in text.upper()


def test_abort_requests_to_speed_up_and_isolate(page: Page, require_site) -> None:
    """Blocking images, fonts, ads and analytics is the cheapest speed-up
    available to a UI suite, and removes a class of third-party flakiness."""
    require_site("the-internet")
    blocked: list[str] = []

    def block_media(route: Route) -> None:
        blocked.append(route.request.resource_type)
        route.abort()

    page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", block_media)
    page.goto(internet("/"))

    expect(page.get_by_role("heading", name="Welcome to the-internet")).to_be_visible()


def test_assert_on_the_outgoing_request(page: Page, require_site) -> None:
    """Sometimes the interesting thing is what the client SENT."""
    require_site("jsonplaceholder")
    seen: dict[str, str] = {}

    def capture(route: Route) -> None:
        seen["method"] = route.request.method
        seen["url"] = route.request.url
        route.continue_()

    page.route("**/posts/2", capture)
    page.goto(api("/posts/2"))

    assert seen["method"] == "GET"
    assert seen["url"].endswith("/posts/2")


# YOUR TURN
# Stub /posts to return an EMPTY list and confirm the page renders `[]`.
