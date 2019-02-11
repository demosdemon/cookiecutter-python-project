import subprocess


def test_project_tree(cookies):
    result = cookies.bake(extra_context={"project_slug": "test_project"})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == "test_project"


def test_run_flake8(cookies, monkeypatch):
    result = cookies.bake(extra_context={"project_slug": "flake8_compat"})
    monkeypatch.chdir(str(result.project))
    subprocess.check_call(["flake8"])
