#!/usr/bin/env bash
# =============================================================================
# setup-git.sh -- build a readable commit history and optionally push.
# SAFE TO RE-RUN: every stage detects what is already done and skips it.
#
#   ./setup-git.sh                       commits only
#   ./setup-git.sh suryakulshreshtha     commits + remote + push
#   ./setup-git.sh --remote-only <user>  skip history, wire the remote
# =============================================================================
set -euo pipefail

REPO_NAME="Forkable04EyeLearningSandbox"
DEFAULT_USER="suryakulshreshtha"
REMOTE_ONLY=false
GH_USER=""

valid_username () { [[ "$1" =~ ^[A-Za-z0-9]([A-Za-z0-9-]{0,37}[A-Za-z0-9])?$ ]]; }

while [ $# -gt 0 ]; do
  case "$1" in
    --remote-only) REMOTE_ONLY=true; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $1"; exit 2 ;;
    *)
      # zsh does not strip '#' comments interactively, so a pasted
      #     ./setup-git.sh        # some comment
      # sends '#' here. Validate rather than build https://github.com/#/...
      if [ -n "$GH_USER" ] || ! valid_username "$1"; then
        echo "ERROR: '$1' is not a valid GitHub username."
        echo "If you pasted a trailing '# comment', run the command without it."
        exit 2
      fi
      GH_USER="$1"; shift ;;
  esac
done

say(){ printf '\n\033[1m==> %s\033[0m\n' "$1"; }
ok(){ printf '    ok   %s\n' "$1"; }
skip(){ printf '    skip %s\n' "$1"; }

say "Repository"
[ -d .git ] && skip "already a git repo" || { git init -q; ok "git init"; }
BRANCH="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo main)"
[ "$BRANCH" = "main" ] || { git branch -M main 2>/dev/null || git checkout -q -b main; }
ok "on branch main"

if ! git config user.email >/dev/null && ! git config --global user.email >/dev/null; then
  echo; echo "ERROR: git has no identity. Set one first:"
  echo '    git config --global user.name  "Your Name"'
  echo '    git config --global user.email "you@example.com"'; echo
  exit 1
fi

if [ "$REMOTE_ONLY" = true ] || git rev-parse --verify HEAD >/dev/null 2>&1; then
  say "Commit history"; skip "commits already exist or --remote-only given"
  if [ -n "$(git status --porcelain)" ]; then
    git add -A && git commit -q -m "chore: commit outstanding changes"
    ok "committed outstanding changes"
  fi
else
  say "Building commit history"
  rm -rf reports .pytest_cache .ruff_cache 2>/dev/null || true
  find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  commit(){ git commit -q -m "$1"; printf '    %s\n' "$1"; }

  git add .gitignore .gitattributes LICENSE
  commit "chore: initialise repo with license and gitignore"

  git add requirements.txt requirements-dev.txt pytest.ini pyproject.toml Makefile .pre-commit-config.yaml
  commit "chore: add dependencies, pytest config and lint config"

  git add utils/ conftest.py
  commit "feat(framework): site registry, settings and the reachability probe"

  git add pages/
  commit "feat(pom): base page and page objects for login and dynamic loading"

  git add tests/__init__.py tests/test_01_first_test.py tests/test_02_locators.py tests/test_03_assertions.py
  commit "test: topics 1-3 -- first test, locators, assertions"

  git add tests/test_04_forms.py tests/test_05_waiting.py tests/test_06_page_object.py
  commit "test: topics 4-6 -- forms, waiting, page object model"

  git add tests/test_07_fixtures.py tests/test_08_api.py tests/test_09_network_mocking.py
  commit "test: topics 7-9 -- fixtures, API testing, network mocking"

  git add tests/test_10_alerts_frames_windows.py tests/test_11_isolation.py tests/test_12_debugging.py
  commit "test: topics 10-12 -- dialogs and frames, isolation, debugging"

  git add .github/workflows/ .github/dependabot.yml
  commit "ci: single readable pipeline with caching, matrix and artifacts"

  git add .github/CODEOWNERS .github/ISSUE_TEMPLATE .github/pull_request_template.md
  commit "ci: add CODEOWNERS, issue templates and the PR checklist"

  git add README.md CONTRIBUTING.md TASKS.md
  commit "docs: README topic map, contributing guide and the task board"

  git add -A
  git diff --cached --quiet || commit "chore: add the git setup script"
  ok "$(git rev-list --count HEAD) commits built"
fi

if [ -z "$GH_USER" ]; then
  say "Remote"; skip "no username given"
  echo; echo "To publish:  ./setup-git.sh $DEFAULT_USER"; echo
  git --no-pager log --oneline; exit 0
fi

REMOTE_URL="https://github.com/${GH_USER}/${REPO_NAME}.git"
say "Remote"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"; ok "origin re-pointed"
else
  git remote add origin "$REMOTE_URL"; ok "origin added"
fi

say "Pushing"
if git push -u origin main; then
  ok "pushed to https://github.com/${GH_USER}/${REPO_NAME}"
  echo
  echo "Next:"
  echo "  1. Settings > General  -> tick 'Template repository'"
  echo "  2. Add topics via the gear beside 'About'"
  echo "  3. Let CI finish, then protect main requiring the 'Tests' checks"
  echo "  4. Settings > Features -> enable Discussions for collaborators"
else
  echo
  echo "Push failed. Common causes:"
  echo "  - repo does not exist yet   -> create it at https://github.com/new (no README)"
  echo "  - not authenticated        -> gh auth login, or use an SSH remote"
  echo "  - remote has its own commit -> git push --force-with-lease origin main"
  exit 1
fi
