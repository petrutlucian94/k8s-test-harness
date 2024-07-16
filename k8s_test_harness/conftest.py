#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#
import logging
from typing import Generator

import pytest

from k8s_test_harness import config, harness
from k8s_test_harness.util import k8s_util

LOG = logging.getLogger(__name__)


def _harness_clean(h: harness.Harness):
    "Clean up created instances within the test harness."

    if config.SKIP_CLEANUP:
        LOG.warning(
            "Skipping harness cleanup. "
            "It is your job now to clean up cloud resources"
        )
    else:
        LOG.debug("Cleanup")
        h.cleanup()


@pytest.fixture(scope="module")
def h() -> harness.Harness:
    LOG.debug("Create harness for %s", config.SUBSTRATE)
    if config.SUBSTRATE == "local":
        h = harness.LocalHarness()
    elif config.SUBSTRATE == "lxd":
        h = harness.LXDHarness()
    elif config.SUBSTRATE == "multipass":
        h = harness.MultipassHarness()
    elif config.SUBSTRATE == "juju":
        h = harness.JujuHarness()
    else:
        raise harness.HarnessError(
            "TEST_SUBSTRATE must be one of: local, lxd, multipass, juju"
        )

    yield h

    _harness_clean(h)


@pytest.fixture(scope="module")
def module_instance(
    h: harness.Harness, tmp_path_factory: pytest.TempPathFactory, request
) -> Generator[harness.Instance, None, None]:
    """Constructs and bootstraps an instance that persists over a test session.

    Bootstraps the instance with all k8sd features enabled to reduce testing time.
    """
    LOG.info("Setup node and enable all features")

    instance = h.new_instance()
    k8s_util.setup_k8s_snap(instance)
    request.addfinalizer(lambda: k8s_util.purge_k8s_snap(instance))

    bootstrap_config_path = "/home/ubuntu/bootstrap-session.yaml"
    instance.send_file(
        (config.MANIFESTS_DIR / "bootstrap-session.yaml").as_posix(),
        bootstrap_config_path,
    )

    instance.exec(["k8s", "bootstrap", "--file", bootstrap_config_path])
    k8s_util.wait_until_k8s_ready(instance, [instance])
    k8s_util.wait_for_network(instance)
    k8s_util.wait_for_dns(instance)

    yield instance
