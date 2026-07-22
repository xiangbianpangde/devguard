"""Installer bootstrap contract tests (#55).

Behavior tests drive ``scripts/install.sh`` through subprocess with fake repos,
fake Pythons, and a stub ``setup_scaffold.py`` so fail-closed paths and argument
pass-through are verified without touching the real network or Python installs.
``scripts/install.ps1`` cannot execute on this macOS runner, so it is covered by
static structure assertions only (evidence boundary documented in the worklog).
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO_ROOT / "scripts" / "install.sh"
INSTALL_PS1 = REPO_ROOT / "scripts" / "install.ps1"

STUB_SCAFFOLD = """#!/usr/bin/env python3
import os
import sys

record = os.environ["STUB_ARGV_FILE"]
with open(record, "w", encoding="utf-8") as fh:
    fh.write("\\n".join(sys.argv[1:]))
sys.exit(int(os.environ.get("STUB_EXIT", "0")))
"""

FAKE_OLD_PYTHON = """#!/usr/bin/env bash
# 伪装成 Python 3.9：只应答版本探测，其余直接失败
if [[ "$1" == "-c" ]]; then
    echo "3.9"
    exit 0
fi
exit 1
"""


def _make_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "fake-devguard"
    (repo / "scripts").mkdir(parents=True)
    stub = repo / "scripts" / "setup_scaffold.py"
    stub.write_text(STUB_SCAFFOLD, encoding="utf-8")
    return repo


def _neutral_installer(tmp_path: Path) -> Path:
    """把 install.sh 复制到中立目录，使脚本自定位失效，便于测试 cwd/env 探测。"""
    target_dir = tmp_path / "neutral" / "bin"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "install.sh"
    target.write_text(INSTALL_SH.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def _run_installer(args, *, env_extra=None, cwd=None, script: Path | None = None):
    env = os.environ.copy()
    env.update(env_extra or {})
    # PATH 被测试清空时 subprocess 自身也找不到 bash，退回到绝对路径
    bash = "/bin/bash" if "PATH" in (env_extra or {}) else "bash"
    return subprocess.run(
        [bash, str(script or INSTALL_SH), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=60,
        check=False,
    )


def _stub_env(tmp_path: Path, exit_code: str = "0"):
    argv_file = tmp_path / "argv.txt"
    return {
        "STUB_ARGV_FILE": str(argv_file),
        "STUB_EXIT": exit_code,
        "DEVGUARD_PYTHON": sys.executable,
    }, argv_file


class TestInstallShPassThrough:
    def test_repo_flag_and_args_passed_verbatim(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        env, argv_file = _stub_env(tmp_path)
        target = tmp_path / "my project"
        result = _run_installer(
            [
                "--repo",
                str(repo),
                str(target),
                "--profile",
                "core",
                "--project-name",
                "My Project",
                "--install",
                "--dry-run",
                "--force",
            ],
            env_extra=env,
        )
        assert result.returncode == 0, result.stderr
        recorded = argv_file.read_text(encoding="utf-8").splitlines()
        assert recorded == [
            str(target),
            "--profile",
            "core",
            "--project-name",
            "My Project",
            "--install",
            "--dry-run",
            "--force",
        ]
        assert str(repo) in result.stderr  # 诊断行打印实际使用的仓

    def test_repo_from_cwd(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        script = _neutral_installer(tmp_path)
        env, argv_file = _stub_env(tmp_path)
        result = _run_installer(
            ["/tmp/whatever-target", "--verify"],
            env_extra=env,
            cwd=repo,
            script=script,
        )
        assert result.returncode == 0, result.stderr
        assert argv_file.read_text(encoding="utf-8").splitlines() == [
            "/tmp/whatever-target",
            "--verify",
        ]

    def test_repo_from_env_var(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        script = _neutral_installer(tmp_path)
        env, argv_file = _stub_env(tmp_path)
        env["DEVGUARD_REPO"] = str(repo)
        result = _run_installer(
            ["/tmp/t", "--profile", "optional"],
            env_extra=env,
            cwd=tmp_path,
            script=script,
        )
        assert result.returncode == 0, result.stderr
        assert argv_file.read_text(encoding="utf-8").splitlines() == [
            "/tmp/t",
            "--profile",
            "optional",
        ]

    def test_setup_scaffold_exit_code_propagates(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        env, _argv_file = _stub_env(tmp_path, exit_code="3")
        result = _run_installer(["--repo", str(repo), "/tmp/t"], env_extra=env)
        assert result.returncode == 3


class TestInstallShFailClosed:
    def test_missing_repo_gives_clone_guidance(self, tmp_path):
        script = _neutral_installer(tmp_path)
        env, _ = _stub_env(tmp_path)
        env.pop("DEVGUARD_REPO", None)
        result = _run_installer(["/tmp/t"], env_extra=env, cwd=tmp_path, script=script)
        assert result.returncode == 1
        assert "git clone" in result.stderr
        assert "--repo" in result.stderr

    def test_invalid_devguard_python_fails(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        env, _ = _stub_env(tmp_path)
        env["DEVGUARD_PYTHON"] = str(tmp_path / "no-such-python")
        result = _run_installer(["--repo", str(repo), "/tmp/t"], env_extra=env)
        assert result.returncode == 1
        assert "DEVGUARD_PYTHON" in result.stderr

    def test_old_python_fails_closed(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        fake_py = tmp_path / "python39"
        fake_py.write_text(FAKE_OLD_PYTHON, encoding="utf-8")
        fake_py.chmod(fake_py.stat().st_mode | stat.S_IXUSR)
        env, _ = _stub_env(tmp_path)
        env["DEVGUARD_PYTHON"] = str(fake_py)
        result = _run_installer(["--repo", str(repo), "/tmp/t"], env_extra=env)
        assert result.returncode == 1
        assert "3.10" in result.stderr

    def test_no_python_on_path_fails_closed(self, tmp_path):
        repo = _make_fake_repo(tmp_path)
        empty_bin = tmp_path / "empty-bin"
        empty_bin.mkdir()
        env, _ = _stub_env(tmp_path)
        env.pop("DEVGUARD_PYTHON")
        env["PATH"] = str(empty_bin)
        result = _run_installer(["--repo", str(repo), "/tmp/t"], env_extra=env)
        assert result.returncode == 1
        assert "Python >= 3.10" in result.stderr
        assert "brew install" in result.stderr  # 分平台指引而非自动安装

    def test_help_describes_repo_and_passthrough(self, tmp_path):
        result = _run_installer(["--help"], env_extra={})
        assert result.returncode == 0
        assert "--repo" in result.stdout
        assert "--profile" in result.stdout


class TestInstallPs1StaticStructure:
    """install.ps1 本机无法执行（macOS runner），只做静态结构契约。"""

    def test_ps1_exists_and_detects_python(self):
        content = INSTALL_PS1.read_text(encoding="utf-8")
        assert "py" in content and "'-3'" in content  # py -3 启动器
        assert "python" in content
        assert "DEVGUARD_PYTHON" in content

    def test_ps1_enforces_min_version_3_10(self):
        content = INSTALL_PS1.read_text(encoding="utf-8")
        assert "$MinMajor = 3" in content
        assert "$MinMinor = 10" in content

    def test_ps1_fail_closed_no_auto_install(self):
        content = INSTALL_PS1.read_text(encoding="utf-8")
        # 指引中出现 winget，但绝不自动执行安装命令
        assert content.count("winget install") == 1  # 仅指引文本一处
        assert "Start-Process" not in content
        assert "Invoke-WebRequest" not in content
        assert "exit 1" in content

    def test_ps1_locates_repo_and_passes_through(self):
        content = INSTALL_PS1.read_text(encoding="utf-8")
        assert "ValueFromRemainingArguments" in content
        assert "DEVGUARD_REPO" in content
        assert "setup_scaffold.py" in content
        assert "exit $LASTEXITCODE" in content

    def test_ps1_mentions_guidance_for_clone(self):
        content = INSTALL_PS1.read_text(encoding="utf-8")
        assert "git clone" in content


class TestInstallerFiles:
    def test_install_sh_is_posix_bash_with_strict_mode(self):
        content = INSTALL_SH.read_text(encoding="utf-8")
        assert content.startswith("#!/usr/bin/env bash")
        assert "set -euo pipefail" in content

    def test_install_sh_has_no_auto_python_install(self):
        content = INSTALL_SH.read_text(encoding="utf-8")
        # 指引文本可出现安装命令，但脚本绝不执行 brew/apt/dnf/pacman
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith(("brew ", "sudo apt", "sudo dnf", "sudo pacman")):
                raise AssertionError(f"install.sh 疑似自动安装 Python: {line}")
