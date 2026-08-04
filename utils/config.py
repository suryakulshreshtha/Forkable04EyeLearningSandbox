"""Settings, read from the environment with sensible defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # Public-internet round trips from a shared CI runner are slow and jittery.
    # 20s is deliberately generous; against your own app on localhost, 5s would
    # be plenty and a shorter timeout gives faster feedback on real breakage.
    timeout_ms: int = field(default_factory=lambda: int(os.environ.get("TIMEOUT_MS", "20000")))
    headless: bool = field(default_factory=lambda: _bool("HEADLESS", True))
    slow_mo: int = field(default_factory=lambda: int(os.environ.get("SLOW_MO", "0")))
    skip_if_site_down: bool = field(default_factory=lambda: _bool("SKIP_IF_SITE_DOWN", True))

    @property
    def is_ci(self) -> bool:
        return os.environ.get("CI", "").lower() == "true"


settings = Settings()
