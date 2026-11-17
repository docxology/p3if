"""Process-level regression checks for visualization discovery failures."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests/visualization/run_all_tests.py"


def _finish(process: subprocess.Popen[str]) -> subprocess.CompletedProcess[str]:
    """Wait for one started process and return its completed result."""
    stdout, stderr = process.communicate()
    return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)


def test_import_failure_changes_exit_status(tmp_path):
    """Real unittest import errors must survive the runner's process boundary."""
    env = os.environ | {"PYTHONPATH": str(ROOT / "src"), "MPLBACKEND": "Agg"}
    command = [sys.executable, str(RUNNER), "--pattern", "test_base.py"]
    (tmp_path / "pytest.py").write_text('raise RuntimeError("WF01 import sentinel")\n')
    shadow = env | {"PYTHONPATH": os.pathsep.join([str(tmp_path), str(ROOT / "src")])}
    direct_command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(RUNNER.parent),
        "-p",
        "test_base.py",
    ]
    # The control and both shadowed runs are independent processes, so they start
    # together; each would otherwise pay interpreter and import startup in sequence.
    # The restored run still starts only after every shadowed process has exited.
    started = [
        subprocess.Popen(
            argv, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for argv, environment in ((command, env), (command, shadow), (direct_command, shadow))
    ]
    control, failed, direct = (_finish(process) for process in started)
    assert control.returncode == 0, control.stderr
    assert failed.returncode != 0
    assert "WF01 import sentinel" in failed.stderr
    assert direct.returncode != 0
    assert "WF01 import sentinel" in direct.stderr
    restored = subprocess.run(command, env=env, capture_output=True, text=True)
    assert restored.returncode == control.returncode


def test_discovery_exception_fails_suite(tmp_path):
    """An invalid discovery directory must produce a failed suite result."""
    code = (
        "import runpy; from pathlib import Path; "
        f"ns=runpy.run_path({str(RUNNER)!r}); "
        "run=ns['run_all_tests']; "
        f"run.__globals__['current_dir']=Path({str(tmp_path / 'missing')!r}); "
        "raise SystemExit(0 if run(pattern='test_base.py') else 1)"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Error loading test_base.py" in result.stderr
