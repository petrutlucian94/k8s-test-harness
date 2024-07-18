#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import subprocess
from typing import List


def ensure_image_contains_paths(image, paths):
    """Ensures the given container image contains the provided paths
    within it by attempting to run the image and 'ls' all of them.
    """
    base_cmd = ["docker", "run", "--rm", "--entrypoint", "ls", image, "-l"]
    base_cmd.extend(paths)

    subprocess.run(base_cmd, check=True)


def list_files_under_container_image_dir(
        image: str, root_dir: str="/", exclude_hidden_files: bool=True) -> List[str]:
    """Lists all regular file paths under the given dir in the given image by
    attempting to run the image and executing `find -type f` within the dir.
    """
    cmd = [
        "docker",
        "run",
        "--rm",
        "--entrypoint",
        "find",
        image,
        root_dir.rstrip('/'),
        "-type",
        "f"
    ]

    if exclude_hidden_files:
        cmd.extend(
            ["-not", "-path", "'*/\\.*'", "(", "!", "-iname", ".*", ")"])

    proc = subprocess.run(cmd, check=True, capture_output=True)

    return [l.decode('utf8').strip() for l in proc.stdout.splitlines()]
