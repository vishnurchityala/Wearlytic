import os
import platform

import pytest


def _detect_scraperkit_platform():
    system_name = platform.system().lower()
    machine_name = platform.machine().lower()

    if system_name == "darwin":
        if machine_name in {"arm64", "aarch64"}:
            return "macosarm64"
        return "macosamd64"
    if system_name == "windows":
        return "win64"
    if system_name == "linux":
        return "linux64"
    return None


@pytest.fixture(autouse=True)
def configure_platform_env(monkeypatch):
    if "PLATFORM" in os.environ:
        return

    platform_name = _detect_scraperkit_platform()
    if platform_name is not None:
        monkeypatch.setenv("PLATFORM", platform_name)
