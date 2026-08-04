"""Root conftest -- read this first.

The whole sandbox tests sites we do not control, which forces one design
decision that shapes everything else:

    a site being down is NOT a test failure.

If `the-internet.herokuapp.com` 502s, nothing about your automation is wrong,
and a red build teaches the team to ignore red. So we probe each host once per
session and SKIP its tests if it is unreachable. Skips are visible in the
report; false failures are noise.

That distinction -- broken versus unavailable -- is the single most useful idea
in this repo, and it applies directly to third-party sandboxes and shared
staging environments at work.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from utils.config import settings
from utils.sites import ALL

ROOT = Path(__file__).resolve().parent

#: Probed once, then reused. {host_key: reachable?}
_REACHABILITY: dict[str, bool] = {}


def _reachable(url: str, timeout: float = 10.0) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": "Forkable04Eye-Sandbox"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status < 500
    except urllib.error.HTTPError as exc:
        # 4xx still means the server is alive and answering.
        return exc.code < 500
    except (urllib.error.URLError, OSError):
        return False


@pytest.fixture(scope="session")
def site_status() -> dict[str, bool]:
    """Probe every site once, and print a summary at the top of the run."""
    if not _REACHABILITY:
        for key, url in ALL.items():
            _REACHABILITY[key] = _reachable(url)
    print("\n  external site reachability:")
    for key, ok in _REACHABILITY.items():
        print(f"    {'UP  ' if ok else 'DOWN'}  {key:16} {ALL[key]}")
    return _REACHABILITY


@pytest.fixture
def require_site(site_status: dict[str, bool]):
    """Ask for this, then call it with a host key, to skip cleanly when down.

        def test_login(page, require_site):
            require_site("the-internet")

    Set SKIP_IF_SITE_DOWN=false to force the failure instead -- useful when you
    actually want CI to shout that a dependency has gone away.
    """

    def _require(key: str) -> None:
        if key not in ALL:
            raise KeyError(f"unknown site {key!r}; known: {sorted(ALL)}")
        if not site_status.get(key, False) and settings.skip_if_site_down:
            pytest.skip(f"{key} ({ALL[key]}) is unreachable from this machine")

    return _require


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Applies to every browser context in the suite."""
    return {
        **browser_context_args,
        "viewport": {"width": 1366, "height": 900},
        "locale": "en-GB",
        "ignore_https_errors": True,
        # Instant animations: removes a whole class of timing flakiness.
        "reduced_motion": "reduce",
    }


@pytest.fixture(autouse=True)
def configure_timeouts(request):
    """Set generous timeouts, but only when a browser is actually in play.

    The `fixturenames` guard matters: taking `page` as an argument here would
    force a browser launch for every API test too, turning a 200ms test into a
    2-second one.
    """
    if "page" not in request.fixturenames:
        yield
        return
    page = request.getfixturevalue("page")
    page.set_default_timeout(settings.timeout_ms)
    page.set_default_navigation_timeout(settings.timeout_ms * 2)
    yield


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Tag anything that drives a browser as `ui`.

    Note what this does NOT do: it does not label everything else `api`. An
    earlier version did, which meant `pytest -m api` also ran pure-Python tests
    that touch no API at all. Mark what a test IS, not what it is not --
    `api` is applied explicitly at the top of tests/test_08_api.py.
    """
    for item in items:
        names = set(getattr(item, "fixturenames", ()))
        already = {m.name for m in item.iter_markers()}
        if already & {"ui", "api"}:
            continue
        if names & {"page", "browser", "context"}:
            item.add_marker(pytest.mark.ui)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def annotate_failures(request):
    """Turn a failure into an inline annotation on the PR's Files-changed tab."""
    yield
    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed and os.environ.get("GITHUB_ACTIONS") == "true":
        rel = Path(str(request.node.fspath)).relative_to(ROOT)
        print(
            f"::error file={rel},line={request.node.location[1] + 1},"
            f"title=Failed: {request.node.name}::{report.longreprtext[:500]}"
        )
