import re
import subprocess

import py
import pytest
import pytest_cookies


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
    ],
)
def test_project_generated_file(cookies, filename, match_contents, extra_context):
    extra_context = extra_context or {}
    result = cookies.bake(extra_context)  # type: pytest_cookies.Result

    assert result.exit_code == 0
    assert result.exception is None

    project = result.project
    assert project.join(filename).exists()

    if match_contents:
        with project.join(filename).open("r") as fp:
            file_contents = fp.read()

        if isinstance(match_contents, (list, tuple)):
            for pattern in match_contents:
                _match_file(pattern, file_contents)
        else:
            pattern = match_contents
            _match_file(pattern, file_contents)


def _match_file(pattern, file_contents):
    match = re.search(pattern, file_contents, re.MULTILINE)
    assert match is not None, "%r did not match %r" % (pattern, file_contents)


def test_project_tree(cookies):
    result = cookies.bake(extra_context={"project_slug": "test_project"})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == "test_project"


def test_run_flake8(cookies, monkeypatch):
    result = cookies.bake(extra_context={"project_slug": "flake8_compat"})
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["flake8"])
