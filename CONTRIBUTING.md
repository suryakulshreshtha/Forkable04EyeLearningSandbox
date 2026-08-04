# Contributing

This sandbox exists to be edited. A clearer comment is as welcome as a new
example — arguably more so.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
pre-commit install
```

## Before you open a pull request

```bash
make lint
make check
make smoke
```

`make check` imports every test without running it, which catches most mistakes
in about five seconds.

## How to add a new example

One topic per file. Keep it short enough to read in one sitting.

1. `tests/test_NN_topic.py`, numbered so the reading order is obvious
2. A module docstring that explains **why the topic matters**, not just what
   the API is. That is the whole value of this repo — anyone can read the
   Playwright docs.
3. Three to six focused tests. Resist adding a seventh.
4. Call `require_site("the-internet")` (or whichever host) so the test skips
   cleanly when the site is down.
5. End with a `YOUR TURN` exercise.
6. Add a row to the README topic table and tick it off in `TASKS.md`.

## The quality bar

1. **No `time.sleep()`.** Auto-waiting or `expect()`.
2. **Locators**: role → label → test-id → CSS. XPath needs a comment
   justifying it.
3. **Page objects never assert.** They expose actions and state; tests decide
   what is correct.
4. **No inter-test dependencies.** Each test creates its own preconditions and
   must pass under `-n 4`.
5. **Explain the reasoning.** `# click the button` is noise. `# expect_popup
   must wrap the click, not follow it` is the reason somebody forked this.
6. **Prove it works.** Break the thing, watch the test fail, fix it, watch it
   pass. A test you have never seen fail is a test you have not written.

## Working with sites we do not own

Everything here hits `the-internet.herokuapp.com`, `jsonplaceholder.typicode.com`
or `playwright.dev`. That shapes two rules:

- **A site being down is a SKIP, not a failure.** Use `require_site`. A suite
  that cries wolf about somebody else's outage gets ignored.
- **Assert loosely on their copy.** Their heading text is not your contract.
  Assert on structure and behaviour, not on prose you do not control.

If a site changes and breaks an example, that is a legitimate bug — open a
Flaky test or Bug report issue and, ideally, a PR.

## Commit messages

Conventional commits: `test:`, `feat:`, `fix:`, `ci:`, `docs:`, `chore:`.

```
test(alerts): cover the prompt dialog and the dismiss path
docs(locators): explain why password inputs have no textbox role
```

## Review

`CODEOWNERS` requests a review automatically. Expect comments about *why* a
comment says what it says — that is the point of the project, not pedantry.
