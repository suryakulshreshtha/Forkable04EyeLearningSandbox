"""TOPIC 8 -- API testing with Playwright's APIRequestContext.

No browser is launched here, so these run in milliseconds. Two reasons an SDET
cares:

  * If a rule can be verified at the API layer, verify it there. Reserve UI
    tests for what only exists in the UI -- rendering, navigation, client-side
    validation, accessibility.
  * API calls are the fastest way to SET UP a UI test. Creating a record over
    HTTP takes 30ms; creating it by driving a form takes four seconds.

JSONPlaceholder accepts writes and echoes them back WITHOUT storing them. That
is a useful lesson in itself: a 201 proves the endpoint answered, not that
anything was persisted. Assert on what you can actually observe.
"""

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from utils.sites import JSONPLACEHOLDER

# Everything in this file is browserless. Marked explicitly rather than
# inferred, so `pytest -m api` means exactly what it says.
pytestmark = pytest.mark.api


@pytest.fixture(scope="session")
def api(playwright: Playwright, site_status) -> APIRequestContext:
    if not site_status.get("jsonplaceholder"):
        pytest.skip("jsonplaceholder is unreachable from this machine")
    context = playwright.request.new_context(
        base_url=JSONPLACEHOLDER,
        extra_http_headers={"Accept": "application/json"},
        timeout=20000,
    )
    yield context
    context.dispose()


@pytest.mark.smoke
def test_get_a_collection(api: APIRequestContext) -> None:
    response = api.get("/posts")

    assert response.ok
    assert response.status == 200
    assert response.headers["content-type"].startswith("application/json")
    assert len(response.json()) == 100


def test_get_one_resource(api: APIRequestContext) -> None:
    post = api.get("/posts/1").json()

    assert post["id"] == 1
    assert set(post) == {"userId", "id", "title", "body"}


def test_query_parameters(api: APIRequestContext) -> None:
    posts = api.get("/posts", params={"userId": 1}).json()

    assert len(posts) == 10
    assert {p["userId"] for p in posts} == {1}


def test_404_for_something_that_is_not_there(api: APIRequestContext) -> None:
    response = api.get("/posts/999999")

    assert response.status == 404
    assert not response.ok


@pytest.mark.smoke
def test_create_update_delete(api: APIRequestContext) -> None:
    """A whole lifecycle in ONE test.

    Splitting CRUD into four tests that share an id is the classic ordering
    trap: it breaks the moment the suite runs in parallel or is sharded.
    """
    payload = {"title": "sandbox", "body": "written by a test", "userId": 1}

    created = api.post("/posts", data=payload)
    assert created.status == 201
    assert created.json()["title"] == payload["title"]
    new_id = created.json()["id"]

    updated = api.put(f"/posts/{new_id}", data={**payload, "id": new_id, "title": "edited"})
    assert updated.status == 200
    assert updated.json()["title"] == "edited"

    assert api.delete(f"/posts/{new_id}").status == 200


def test_nested_resources(api: APIRequestContext) -> None:
    comments = api.get("/posts/1/comments").json()

    assert len(comments) == 5
    assert all(c["postId"] == 1 for c in comments)


# YOUR TURN
# Add a test for /users/1 asserting the nested address.geo keys exist.
