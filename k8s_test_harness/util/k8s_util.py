#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#
import json
import logging
from typing import Any, List

from k8s_test_harness import config, harness
from k8s_test_harness.util import exec_util

LOG = logging.getLogger(__name__)


# Installs and setups the k8s snap on the given instance and connects the interfaces.
def setup_k8s_snap(instance: harness.Instance):
    LOG.info("Install k8s snap")
    instance.exec(
        ["snap", "install", "k8s", "--classic", "--channel", config.SNAP_CHANNEL]
    )


def purge_k8s_snap(instance: harness.Instance):
    LOG.info("Purge k8s snap")
    instance.exec(["sudo", "snap", "remove", "k8s", "--purge"])


# Validates that the K8s node is in Ready state.
def wait_until_k8s_ready(
    control_node: harness.Instance, instances: List[harness.Instance]
):
    for instance in instances:
        host = hostname(instance)
        result = (
            exec_util.stubbornly(retries=15, delay_s=5)
            .on(control_node)
            .until(lambda p: " Ready" in p.stdout.decode())
            .exec(["k8s", "kubectl", "get", "node", host, "--no-headers"])
        )
    LOG.info("Kubelet registered successfully!")
    LOG.info("%s", result.stdout.decode())


def wait_for_dns(instance: harness.Instance):
    LOG.info("Waiting for DNS to be ready")
    instance.exec(["k8s", "x-wait-for", "dns"])


def wait_for_network(instance: harness.Instance):
    LOG.info("Waiting for network to be ready")
    instance.exec(["k8s", "x-wait-for", "network"])


def hostname(instance: harness.Instance) -> str:
    """Return the hostname for a given instance."""
    resp = instance.exec(["hostname"], capture_output=True)
    return resp.stdout.decode().strip()


def get_local_node_status(instance: harness.Instance) -> str:
    resp = instance.exec(["k8s", "local-node-status"], capture_output=True)
    return resp.stdout.decode().strip()


def get_nodes(control_node: harness.Instance) -> List[Any]:
    """Get a list of existing nodes.

    Args:
        control_node: instance on which to execute check

    Returns:
        list of nodes
    """
    result = control_node.exec(
        ["k8s", "kubectl", "get", "nodes", "-o", "json"], capture_output=True
    )
    assert result.returncode == 0, "Failed to get nodes with kubectl"
    node_list = json.loads(result.stdout.decode())
    assert node_list["kind"] == "List", "Should have found a list of nodes"
    return [node for node in node_list["items"]]


def ready_nodes(control_node: harness.Instance) -> List[Any]:
    """Get a list of the ready nodes.

    Args:
        control_node: instance on which to execute check

    Returns:
        list of nodes
    """
    return [
        node
        for node in get_nodes(control_node)
        if all(
            condition["status"] == "False"
            for condition in node["status"]["conditions"]
            if condition["type"] != "Ready"
        )
    ]


# Create a token to join a node to an existing cluster
def get_join_token(
    initial_node: harness.Instance, joining_cplane_node: harness.Instance, *args: str
) -> str:
    out = initial_node.exec(
        ["k8s", "get-join-token", joining_cplane_node.id, *args],
        capture_output=True,
    )
    return out.stdout.decode().strip()


# Join an existing cluster.
def join_cluster(instance: harness.Instance, join_token: str):
    instance.exec(["k8s", "join-cluster", join_token])
