#!/usr/bin/env python3
"""Run the harness test suite and enforce per-file line coverage.

Coverage is measured with the stdlib `trace` module, so the suite has the same
zero-dependency guarantee as the skills it tests: system `python3` and nothing
else.

Usage:
    python3 tests/run_tests.py                 # tests + coverage gate (100%)
    python3 tests/run_tests.py --min 95        # lower the threshold for one run
    python3 tests/run_tests.py --no-coverage   # tests only, much faster

Exit codes: 0 = pass, 1 = test failure or a file below the threshold.
"""

from __future__ import annotations

import argparse
import dis
import re
import sys
import trace
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent

# The files the gate applies to: every script bundled inside a skill.
TARGETS = sorted(REPO_ROOT.glob("skills/*/scripts/*.py"))

# Full coverage is the standing requirement — it never goes down.
DEFAULT_MIN_COVERAGE = 100.0

MAIN_GUARD_RE = re.compile(r"^if\s+__name__\s*==")


def main_guard_lines(source_lines: list[str]) -> set[int]:
    """Line numbers of `if __name__ == "__main__":` blocks.

    The guard only runs when the script is invoked as a command, and the tests
    call `main()` in-process on purpose, so those lines are excluded from the
    gate instead of being faked with a subprocess.
    """
    excluded: set[int] = set()
    for index, line in enumerate(source_lines, start=1):
        if not MAIN_GUARD_RE.match(line):
            continue
        excluded.add(index)
        for offset, following in enumerate(source_lines[index:], start=index + 1):
            if following.strip() and not following.startswith((" ", "\t")):
                break
            excluded.add(offset)
    return excluded


def executable_lines(path: Path) -> set[int]:
    """Line numbers that can actually run, including nested functions."""
    source = path.read_text(encoding="utf-8")
    code = compile(source, str(path), "exec")
    lines: set[int] = set()
    stack = [code]
    while stack:
        current = stack.pop()
        lines.update(lineno for _, lineno in dis.findlinestarts(current) if lineno)
        stack.extend(const for const in current.co_consts if hasattr(const, "co_consts"))
    return lines - main_guard_lines(source.splitlines())


def build_suite() -> unittest.TestSuite:
    return unittest.defaultTestLoader.discover(
        start_dir=str(TESTS_DIR), pattern="test_*.py", top_level_dir=str(TESTS_DIR)
    )


def run_suite() -> bool:
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    return runner.run(build_suite()).wasSuccessful()


def report_coverage(counts: dict, minimum: float) -> bool:
    """Print per-file coverage and return whether every target meets `minimum`."""
    hit_by_file: dict[str, set[int]] = {}
    for filename, lineno in counts:
        hit_by_file.setdefault(str(Path(filename).resolve()), set()).add(lineno)

    print(f"\nPer-file line coverage (minimum {minimum:.0f}%)\n")
    below: list[str] = []

    for target in TARGETS:
        executable = executable_lines(target)
        hit = hit_by_file.get(str(target.resolve()), set()) & executable
        percent = (len(hit) / len(executable) * 100) if executable else 100.0
        rel = target.relative_to(REPO_ROOT)
        mark = "✓" if percent >= minimum else "✗"
        print(f"  {mark} {percent:6.2f}%  {rel}  ({len(hit)}/{len(executable)} lines)")
        if percent < minimum:
            missing = sorted(executable - hit)
            preview = ", ".join(str(line) for line in missing[:20])
            suffix = ", ..." if len(missing) > 20 else ""
            print(f"      uncovered lines: {preview}{suffix}")
            below.append(str(rel))

    if below:
        print(f"\n✗ Below {minimum:.0f}% line coverage: {', '.join(below)}")
        return False

    print(f"\n✓ Every file is at or above {minimum:.0f}% line coverage.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--min", type=float, default=DEFAULT_MIN_COVERAGE, help="minimum per-file line coverage"
    )
    parser.add_argument("--no-coverage", action="store_true", help="run the tests without the coverage gate")
    args = parser.parse_args()

    if not TARGETS:
        print("error: no scripts found under skills/*/scripts/", file=sys.stderr)
        return 1

    if args.no_coverage:
        return 0 if run_suite() else 1

    # `trace` only needs to watch the repository itself; ignoring the interpreter
    # directories keeps the run fast enough to sit in a pre-push hook.
    tracer = trace.Trace(count=1, trace=0, ignoredirs=[sys.prefix, sys.exec_prefix])
    passed = tracer.runfunc(run_suite)

    covered = report_coverage(tracer.results().counts, args.min)
    return 0 if passed and covered else 1


if __name__ == "__main__":
    sys.exit(main())
