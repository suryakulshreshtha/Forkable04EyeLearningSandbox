# Forkable04EyeLearningSandbox

[![CI](https://github.com/suryakulshreshtha/Forkable04EyeLearningSandbox/actions/workflows/ci.yml/badge.svg)](https://github.com/suryakulshreshtha/Forkable04EyeLearningSandbox/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-1.47%2B-green)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![good first issues](https://img.shields.io/github/issues/suryakulshreshtha/Forkable04EyeLearningSandbox/good%20first%20issue)](https://github.com/suryakulshreshtha/Forkable04EyeLearningSandbox/labels/good%20first%20issue)

> **One short, heavily-commented example per topic.** Python + Playwright + a
> CI pipeline you can read on one screen. Built to be forked, argued with, and
> contributed to.

No app to install and no accounts to create — every example runs against public
practice sites. Clone it, `make install`, `make smoke`, and you are testing.

Looking for the deep version? The sibling repo
**[Forkable04EyePythonPlaywrightLearning](https://github.com/suryakulshreshtha/Forkable04EyePythonPlaywrightLearning)**
has a bundled app, 86 tests, a 16-job sharded matrix and a 7-day course. Start
here; graduate there.

---

## 60-second start

```bash
git clone https://github.com/suryakulshreshtha/Forkable04EyeLearningSandbox.git
cd Forkable04EyeLearningSandbox

python3 -m venv .venv
source .venv/bin/activate
make install

make smoke
```

Watch it drive the browser:

```bash
make headed
```

---

## The twelve topics

Read them in order. Each file stands alone and ends with a `YOUR TURN`.

| # | File | Topic | What you take away |
| --- | --- | --- | --- |
| 1 | `test_01_first_test.py` | First test | Contexts, `expect()` vs `assert`, why a down site should skip |
| 2 | `test_02_locators.py` | Locators | The priority order; roles are not tag names; strict mode is a feature |
| 3 | `test_03_assertions.py` | Assertions | Web-first assertions, list assertions, soft assertions, timeouts |
| 4 | `test_04_forms.py` | Forms | `fill` vs typing, checkboxes, selects, in-memory uploads |
| 5 | `test_05_waiting.py` | Waiting | Auto-waiting; the real cost of `time.sleep()` |
| 6 | `test_06_page_object.py` | Page objects | Actions and state, returning the next page, when POM is not worth it |
| 7 | `test_07_fixtures.py` | Fixtures & markers | Scopes, composition, teardown, slicing the suite |
| 8 | `test_08_api.py` | API testing | `APIRequestContext`, lifecycle in one test, what a 201 does not prove |
| 9 | `test_09_network_mocking.py` | Network mocking | Fulfil, modify, abort — and the honest limits of mocking |
| 10 | `test_10_alerts_frames_windows.py` | Dialogs, iframes, tabs | Auto-dismissal, `frame_locator`, `expect_popup` |
| 11 | `test_11_isolation.py` | Isolation | Surviving `-n auto`; unique data; context isolation |
| 12 | `test_12_debugging.py` | Debugging | Reading failure messages, traces, Inspector, codegen |

Supporting cast: `pages/` (3 page objects), `utils/sites.py` (every external URL
in one place), `conftest.py` (the reachability probe and shared fixtures).

---

## CI/CD, in one file

`.github/workflows/ci.yml` is ~140 lines including comments, and every concept
is visible at once:

| Concept | Where |
| --- | --- |
| Triggers: push, PR, manual, scheduled | `on:` |
| Least-privilege token | `permissions: contents: read` |
| Auto-cancel superseded runs | `concurrency:` |
| Fail fast and cheap | `lint` → `needs: lint` |
| Matrix across browsers | `strategy.matrix.browser` |
| `fail-fast: false` | one engine's failure does not cancel the others |
| Dependency + browser caching | `setup-python cache: pip`, `actions/cache` keyed on the Playwright version |
| The cache-hit trap | `install-deps` still runs — OS libs are not in the cache |
| Two-tier suites | PRs run `smoke`, main runs everything |
| Artifacts you can debug from | `upload-artifact` with `if: always()` |
| Job summaries | `$GITHUB_STEP_SUMMARY` |
| Timeouts on every job | `timeout-minutes` |
| Automated dependency PRs | `.github/dependabot.yml` |

---

## Running tests

```bash
make test        # everything
make smoke       # the stable subset CI gates on
make api         # no browser, milliseconds
make ui          # browser only
make parallel    # -n auto
make headed      # watch it
make debug       # Playwright Inspector
make trace       # open the newest trace
make lint        # exactly what CI runs
make check       # lint + import every test

pytest -m "api and not slow"
pytest tests/test_06_page_object.py::test_valid_login_reads_like_a_sentence
pytest -k "dropdown or checkbox"
pytest --browser webkit
```

---

## Why retries are on by default

`pytest.ini` sets `--reruns 2`. In a repo that tests **your own** application
that would be a bad idea — retries hide real race conditions and train the team
to ignore red.

Here, every test crosses the public internet to a site nobody in this project
controls. A retry is the correct response to somebody else's transient 502.

The same reasoning drives the reachability probe in `conftest.py`: if a site is
unreachable, its tests **skip** rather than fail. Distinguishing *broken* from
*unavailable* is the single most transferable idea in this repo, and it applies
directly to third-party sandboxes and shared staging at work.

---

## Contributing

This repo is meant to be added to. **[TASKS.md](TASKS.md)** is a board of
scoped gaps tagged 🟢🟡🔴, and **[CONTRIBUTING.md](CONTRIBUTING.md)** covers the
quality bar and how to add an example.

Good first issues: a page object for `/upload`, a hovers example, a tables
example, adding webkit to the matrix.

The house rule: comments explain **why**, not what. Anyone can read the
Playwright docs; the reasoning is what makes this worth forking.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Everything skipped | The demo sites are unreachable from your network. Check `the-internet.herokuapp.com` in a browser |
| `Executable doesn't exist at .../chrome` | `python -m playwright install --with-deps` |
| `strict mode violation: resolved to N elements` | Your locator is ambiguous — scope or `.filter()` it. This is Playwright helping |
| A test passes alone, fails in the suite | Shared state or an ordering assumption — see topic 11 |
| `Marker not registered` | Add it to `pytest.ini`; `--strict-markers` is on deliberately |
| Tests are slow | They cross the public internet. `make api` is instant; `make parallel` helps the rest |

## License

MIT — see [LICENSE](LICENSE). Use it for workshops, study groups, or interview prep.
