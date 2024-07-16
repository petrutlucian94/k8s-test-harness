#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import subprocess


def ensure_image_contains_paths(image, paths):
    for path in paths:
        subprocess.run(
            ["docker", "run", "--rm", image, "ls", "-l", path],
            check=True,
        )
