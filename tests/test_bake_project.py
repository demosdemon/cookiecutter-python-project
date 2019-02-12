import re
import subprocess

import pytest
import pytest_cookies

missing = object()


def _match_file(pattern, file_contents):
    match = re.search(pattern, file_contents, re.MULTILINE)
    assert match is not None, "%r did not match %r" % (pattern, file_contents)


@pytest.mark.parametrize(
    ("filename", "match_contents"),
    [
        pytest.param("README.md", None),
        pytest.param(
            "README.md",
            [
                re.escape("https://travis-ci.com/foobar_test/test-project.svg"),
                "^# Test Project$",
                "^A short description of the project$",
            ],
            marks=pytest.mark.cookie(
                github_username="foobar_test", project_name="Test Project"
            ),
        ),
        pytest.param(
            "Makefile",
            re.escape("PYTHON_VERSION ?= 3.6"),
            marks=pytest.mark.cookie(makefile_python_version="3.6"),
        ),
        pytest.param(
            "Makefile",
            re.escape("VIRTUAL_ENV ?= $(CURDIR)/.foobar"),
            marks=pytest.mark.cookie(makefile_virtualenv_name=".foobar"),
        ),
        pytest.param("Makefile", missing, marks=pytest.mark.cookie(use_makefile="no")),
    ],
)
def test_project_generated_file(default_baked_project, filename, match_contents):
    result = default_baked_project  # type: pytest_cookies.Result

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


@pytest.mark.cookie(project_slug="test_project")
def test_project_tree(default_baked_project):
    result = default_baked_project
    if result.exception is not None:
        raise result.exception
    assert result.exit_code == 0
    assert result.project.basename == "test_project"


def test_run_flake8(default_baked_project, monkeypatch):
    result = default_baked_project
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["flake8"])


@pytest.mark.skipif("sys.version_info < (3, 6)")
def test_run_black(default_baked_project, monkeypatch):
    result = default_baked_project
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["black", "--check", "--diff", "."])


def test_run_isort(default_baked_project, monkeypatch):
    result = default_baked_project
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["isort", "--check-only", "--diff", "--recursive", "."])
