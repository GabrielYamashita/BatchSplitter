from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_test_files(tests_dir: Path) -> list[Path]:
    return sorted(
        file for file in tests_dir.glob("test_*.py") if file.name != "run_all.py"
    )


def run_test(test_file: Path, project_root: Path) -> bool:
    env = os.environ.copy()

    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(project_root)
        if not current_pythonpath
        else f"{project_root}{os.pathsep}{current_pythonpath}"
    )

    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"✅ PASS {test_file.name}")
        return True

    print(f"\n❌ FAIL {test_file.name}")
    print("-" * 80)

    if result.stdout.strip():
        print("\nSTDOUT:")
        print(result.stdout)

    if result.stderr.strip():
        print("\nSTDERR:")
        print(result.stderr)

    print("-" * 80)
    return False


def main() -> None:
    project_root = get_project_root()
    tests_dir = Path(__file__).resolve().parent

    test_files = get_test_files(tests_dir)

    if not test_files:
        print("No manual test files found.")
        return

    print(f"Running {len(test_files)} manual tests...\n")

    passed = 0
    failed = 0

    for test_file in test_files:
        success = run_test(test_file, project_root)

        if success:
            passed += 1
        else:
            failed += 1
            break

    print("\nSummary")
    print("-" * 80)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
