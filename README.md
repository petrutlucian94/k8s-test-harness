# k8s-test-harness

This project contains various pytest fixtures and helpers used in Rock
image testing.

## Fixtures

The ``module_instance`` fixture sets up a temporary Kubernetes environment
using the ``k8s`` snap and allows running commands in that context. It can use
a variety of substrates: lxd, juju, multipass or local (default).

As the name suggests, ``module_instance`` is module scoped, which means that
each **test module** will have its separate Kubernetes cluster.
This way, we can avoid conflicts when testing multiple versions of the same
chart, or any charts that may impact each other.

## Test utils

``k8s_test_harness.util`` provides various utilities that are expected to be
reused across tests:

* retry helpers
* k8s utils
* docker utils

Please add any helper that can be useful to other image tests.
