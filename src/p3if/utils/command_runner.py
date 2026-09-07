"""
Shared subprocess command runner for P3IF orchestrator tooling.

Moved from scripts/run_all.py (2026-09 audit): the subprocess/timeout/result
plumbing is importable and testable from src/; orchestrator scripts delegate
to this module.

Usage:
    from p3if.utils.command_runner import run_command

    code, stdout, stderr = run_command("python -m pytest tests/ -q", timeout=600)
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def run_command(
    cmd: str,
    cwd: Optional[Path] = None,
    timeout: int = 300,
    project_root: Optional[Path] = None,
) -> Tuple[int, str, str]:
    """Run a shell command and capture output.

    Args:
        cmd: Command to run
        cwd: Working directory (defaults to project_root)
        timeout: Timeout in seconds
        project_root: Project root used for the PYTHONPATH bootstrap and as
            the default working directory

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    root = project_root or Path.cwd()
    try:
        # Set up environment with PYTHONPATH for p3if module
        env = os.environ.copy()
        src_path = str(root / 'src')
        existing_path = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = f"{src_path}:{root}:{existing_path}" if existing_path else f"{src_path}:{root}"

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or root,
            timeout=timeout,
            env=env
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, '', f'Command timed out after {timeout}s'
    except Exception as e:
        return -1, '', str(e)
