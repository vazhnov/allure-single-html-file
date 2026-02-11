import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def _copy_report(source_dir: Path, destination_dir: Path) -> Path:
    report_copy = destination_dir / "report_copy"
    shutil.copytree(source_dir, report_copy)
    return report_copy


@pytest.fixture(scope="session")
def generated_report(tmp_path_factory) -> Path:
    base_dir = tmp_path_factory.mktemp("source_allure")
    sample_tests = base_dir / "sample_tests"
    results_dir = base_dir / "results"
    report_dir = base_dir / "report"

    sample_tests.mkdir(parents=True, exist_ok=True)
    (sample_tests / "test_sample.py").write_text(
        "def test_sample_pass():\n"
        "    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )

    pytest_run = _run(
        [sys.executable, "-m", "pytest", "-q", str(sample_tests), "--alluredir", str(results_dir)]
    )
    assert pytest_run.returncode == 0, pytest_run.stdout + pytest_run.stderr

    allure_generate = _run(["allure", "generate", str(results_dir), "--clean", "-o", str(report_dir)])
    assert allure_generate.returncode == 0, allure_generate.stdout + allure_generate.stderr
    assert (report_dir / "index.html").exists()
    return report_dir


def test_cli_default_output_in_source_folder(generated_report, tmp_path):
    source_report = _copy_report(generated_report, tmp_path)
    cmd = _run(["allure-combine", str(source_report)])

    assert cmd.returncode == 0, cmd.stdout + cmd.stderr
    assert (source_report / "complete.html").exists()


def test_cli_dest_existing_folder(generated_report, tmp_path):
    source_report = _copy_report(generated_report, tmp_path / "src")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir(parents=True, exist_ok=True)

    cmd = _run(["allure-combine", str(source_report), "--dest", str(dest_dir)])

    assert cmd.returncode == 0, cmd.stdout + cmd.stderr
    assert (dest_dir / "complete.html").exists()


def test_cli_dest_missing_without_auto_create_fails(generated_report, tmp_path):
    source_report = _copy_report(generated_report, tmp_path / "src")
    missing_dest = tmp_path / "new" / "nested" / "dest"

    cmd = _run(["allure-combine", str(source_report), "--dest", str(missing_dest)])

    assert cmd.returncode != 0
    assert "Dest folder does not exists" in (cmd.stdout + cmd.stderr)


def test_cli_auto_create_folders(generated_report, tmp_path):
    source_report = _copy_report(generated_report, tmp_path / "src")
    missing_dest = tmp_path / "new" / "nested" / "dest"

    cmd = _run(
        ["allure-combine", str(source_report), "--dest", str(missing_dest), "--auto-create-folders"]
    )

    assert cmd.returncode == 0, cmd.stdout + cmd.stderr
    assert (missing_dest / "complete.html").exists()


def test_cli_remove_temp_files(generated_report, tmp_path):
    source_report = _copy_report(generated_report, tmp_path)

    cmd = _run(["allure-combine", str(source_report), "--remove-temp-files"])

    assert cmd.returncode == 0, cmd.stdout + cmd.stderr
    assert (source_report / "complete.html").exists()
    assert not (source_report / "server.js").exists()
    assert not (source_report / "sinon-9.2.4.js").exists()


def test_cli_ignore_utf8_errors(generated_report, tmp_path):
    source_without_flag = _copy_report(generated_report, tmp_path / "without_flag")
    source_with_flag = _copy_report(generated_report, tmp_path / "with_flag")

    bad_file_without_flag = source_without_flag / "extra_data" / "broken.json"
    bad_file_without_flag.parent.mkdir(parents=True, exist_ok=True)
    bad_file_without_flag.write_bytes(b"\xff\xfe\xfd")

    bad_file_with_flag = source_with_flag / "extra_data" / "broken.json"
    bad_file_with_flag.parent.mkdir(parents=True, exist_ok=True)
    bad_file_with_flag.write_bytes(b"\xff\xfe\xfd")

    cmd_without_flag = _run(["allure-combine", str(source_without_flag)])
    cmd_with_flag = _run(["allure-combine", str(source_with_flag), "--ignore-utf8-errors"])

    assert cmd_without_flag.returncode == 0, cmd_without_flag.stdout + cmd_without_flag.stderr
    assert "Error on reading file" in (cmd_without_flag.stdout + cmd_without_flag.stderr)
    assert (source_without_flag / "complete.html").exists()

    assert cmd_with_flag.returncode == 0, cmd_with_flag.stdout + cmd_with_flag.stderr
    assert "Error on reading file" not in (cmd_with_flag.stdout + cmd_with_flag.stderr)
    assert (source_with_flag / "complete.html").exists()
