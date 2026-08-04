## What does this add or change?

<!-- One or two sentences. Link the issue: Closes #12 -->

## Type

- [ ] New example (a topic that was missing)
- [ ] Improves an existing example — clearer, shorter, better comments
- [ ] Fix for a broken or flaky test
- [ ] Framework / fixtures / CI
- [ ] Docs only

## Checklist

- [ ] `make lint` is clean
- [ ] `make check` passes (imports + collection)
- [ ] I ran the affected tests locally and they passed
- [ ] No `time.sleep()` — auto-waiting or `expect()` only
- [ ] Locators use role / label / test-id before CSS; any XPath has a comment justifying it
- [ ] The test calls `require_site(...)` if it touches an external site
- [ ] It passes with `-n 4` (no shared state, no ordering assumption)
- [ ] Comments explain **why**, not what — that is what makes this repo useful

## For a new example

- [ ] One topic per file, kept short enough to read in one sitting
- [ ] Ends with a `YOUR TURN` exercise
- [ ] Listed in the README topic table and ticked off in `TASKS.md`
