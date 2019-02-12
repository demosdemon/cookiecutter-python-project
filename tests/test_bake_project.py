import re
import subprocess
import sys

import py
import pytest
import pytest_cookies

missing = object()


def _clear_pyc_files():
    if sys.version_info[0] == 2:
        hooks = py.path.local().join("hooks")
        for child in hooks.listdir("*.pyc"):
            child.remove()


def _match_file(pattern, file_contents):
    match = re.search(pattern, file_contents, re.MULTILINE)
    assert match is not None, "%r did not match %r" % (pattern, file_contents)


@pytest.mark.parametrize(
    ("filename", "match_contents", "extra_context"),
    [
        ("README.md", None, None),
        (
            "README.md",
            (
                re.escape("https://travis-ci.com/foobar_test/test-project.svg"),
                "^# Test Project$",
                "^A short description of the project$",
            ),
            {"github_username": "foobar_test", "project_name": "Test Project"},
        ),
        (
            "Makefile",
            re.escape("PYTHON_VERSION ?= 3.6"),
            {"makefile_python_version": "3.6"},
        ),
        (
            "Makefile",
            re.escape("VIRTUAL_ENV ?= $(CURDIR)/.foobar"),
            {"makefile_virtualenv_name": ".foobar"},
        ),
        ("Makefile", missing, {"use_makefile": "no"}),
    ],
)
def test_project_generated_file(cookies, filename, match_contents, extra_context):
    _clear_pyc_files()
    extra_context = extra_context or {}
    result = cookies.bake(extra_context)  # type: pytest_cookies.Result

    if result.exception is not None:
        raise result.exception

    assert result.exit_code == 0

    project = result.project
    if match_contents is missing:
        assert not project.join(filename).exists()
    else:
        assert project.join(filename).exists()

    if match_contents is not None and match_contents is not missing:
        with project.join(filename).open("r") as fp:
            file_contents = fp.read()

        if isinstance(match_contents, (list, tuple)):
            for pattern in match_contents:
                _match_file(pattern, file_contents)
        else:
            pattern = match_contents
            _match_file(pattern, file_contents)


def test_project_tree(cookies):
    _clear_pyc_files()
    result = cookies.bake(extra_context={"project_slug": "test_project"})
    if result.exception is not None:
        raise result.exception
    assert result.exit_code == 0
    assert result.project.basename == "test_project"


def test_run_flake8(cookies, monkeypatch):
    _clear_pyc_files()
    result = cookies.bake(extra_context={"project_slug": "flake8_compat"})
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["flake8"])


@pytest.mark.skipif("sys.version_info < (3, 6)")
def test_run_black(cookies, monkeypatch):
    _clear_pyc_files()
    result = cookies.bake()
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["black", "--check", "--diff", "."])


def test_run_isort(cookies, monkeypatch):
    _clear_pyc_files()
    result = cookies.bake()
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["isort", "--check-only", "--diff", "--recursive", "."])
