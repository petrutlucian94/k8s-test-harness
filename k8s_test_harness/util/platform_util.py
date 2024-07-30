#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

"""Module containing utilities for querying platform parameters
for ROCK testing."""

import platform

ROCKCRAFT_PLATFORM_AMD64 = "amd64"
ROCKCRAFT_PLATFORM_I386 = "i386"
ROCKCRAFT_PLATFORM_ARM64 = "arm64"


_PYTHON_MACHINE_TO_ROCKCRAFT_PLATFORM_ARCHITECTURE_MAP = {
    "x86": ROCKCRAFT_PLATFORM_I386,
    "x86_64": ROCKCRAFT_PLATFORM_AMD64,
    "arm64": ROCKCRAFT_PLATFORM_ARM64,
}


def get_current_rockcraft_platform_architecture() -> str:
    """Returns a string containing the rockcraft-specific platform
    architecture label of the currently running process.

    https://documentation.ubuntu.com/rockcraft/en/latest/reference/rockcraft.yaml/#platforms

    :raises OSError: if `platform.machine()` does not return anything.
    :raises ValueError: if `platform.machine()` returns unrecognized value.
    """

    machine = platform.machine()
    if not machine:
        raise OSError("Failed to get current platform through `platform.machine()`.")

    if machine not in _PYTHON_MACHINE_TO_ROCKCRAFT_PLATFORM_ARCHITECTURE_MAP:
        raise ValueError(
            f"Unknown platform machine type '{machine}'. Known values are: "
            f"{list(_PYTHON_MACHINE_TO_ROCKCRAFT_PLATFORM_ARCHITECTURE_MAP)}"
        )

    return _PYTHON_MACHINE_TO_ROCKCRAFT_PLATFORM_ARCHITECTURE_MAP[machine]
