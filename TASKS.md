# The board

Open, well-scoped work. Claim one by opening a **Good first issue** and saying
so, or comment on the existing issue. Tick the box in your PR.

Difficulty: 🟢 first contribution · 🟡 needs some Playwright · 🔴 design thinking

## Examples that are missing

- [ ] 🟢 **Hovers** — `/hovers`: hover an avatar, assert the caption appears
- [ ] 🟢 **Tables** — `/tables`: sort by a column, assert the new order with one `expect()`
- [ ] 🟢 **Key presses** — `/key_presses`: assert the page reports the key you sent
- [ ] 🟡 **Drag and drop** — `/drag_and_drop`: HTML5 DnD is genuinely awkward; document why
- [ ] 🟡 **Infinite scroll** — `/infinite_scroll`: scroll until a condition, without a sleep
- [ ] 🟡 **Basic auth** — `/basic_auth`: use `http_credentials` in the context
- [ ] 🟡 **Shadow DOM** — `/shadowdom`: show that Playwright pierces it by default
- [ ] 🔴 **Accessibility** — run `axe-core` via `page.evaluate` and fail on serious violations
- [ ] 🔴 **Visual regression** — `to_have_screenshot`, with an honest note on when it is worth the flakiness

## Framework

- [ ] 🟢 Page object for `/upload`, used by topic 4
- [ ] 🟢 Page object for `/dropdown`, used by topic 4
- [ ] 🟡 A `logged_in_page` fixture shared across files rather than redefined
- [ ] 🟡 Reuse authentication via `storage_state` so login runs once per session
- [ ] 🔴 A `--site` CLI option to point the suite at a mirror of the demo site

## CI/CD

- [ ] 🟢 Add webkit to the matrix and see what breaks
- [ ] 🟡 Publish the HTML report to GitHub Pages — see the sibling repo for a worked example
- [ ] 🟡 Add a `CI gate` aggregate job so branch protection needs only one check name
- [ ] 🔴 Shard the suite with `pytest-split` and measure the wall-clock difference

## Docs

- [ ] 🟢 A one-page cheat sheet of the locator priority order
- [ ] 🟡 A short guide on reading a trace, with screenshots
- [ ] 🟡 Translate the README topic table into a diagram

## Known rough edges

- [ ] 🟡 Every example hits the public internet, so the suite is slower and less
      deterministic than it would be against a local app. Consider adding a
      bundled Flask app as an alternative target (the sibling repo has one).
- [ ] 🟡 `test_09` asserts loosely on a modified response because the upstream
      title is not ours to depend on. A better assertion probably exists.
