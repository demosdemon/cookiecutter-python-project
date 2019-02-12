import sys

import py
import pytest


def _clear_pyc_files():
    if sys.version_info[0] == 2:
        hooks = py.path.local().join("hooks")
        for child in hooks.listdir("*.pyc"):
            child.remove()


@pytest.fixture()
def default_baked_project(cookies, request):
    _clear_pyc_files()

    extra_context = {}
    for mark in request.node.iter_markers("cookie"):
        if mark.kwargs:
            extra_context.update(mark.kwargs)

    result = cookies.bake(extra_context)
    yield result
