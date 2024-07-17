#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

from k8s_test_harness.util import harness


def get_default_cidr(instance: harness.Instance, instance_default_ip: str):
    # ----
    # 1:  lo    inet 127.0.0.1/8 scope host lo .....
    # 28: eth0  inet 10.42.254.197/24 metric 100 brd 10.42.254.255 scope global dynamic eth0 ....
    # ----
    # Fetching the cidr for the default interface by matching with instance ip from the output
    p = instance.exec(["ip", "-o", "-f", "inet", "addr", "show"], capture_output=True)
    out = p.stdout.decode().split(" ")
    return [i for i in out if instance_default_ip in i][0]


def get_default_ip(instance: harness.Instance):
    # ---
    # default via 10.42.254.1 dev eth0 proto dhcp src 10.42.254.197 metric 100
    # ---
    # Fetching the default IP address from the output, e.g. 10.42.254.197
    p = instance.exec(
        ["ip", "-o", "-4", "route", "show", "to", "default"], capture_output=True
    )
    return p.stdout.decode().split(" ")[8]
