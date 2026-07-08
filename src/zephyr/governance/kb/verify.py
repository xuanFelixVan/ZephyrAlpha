# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.verify
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.kb.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_verify | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""确定性事实核查 — 取代AI猜测
================================
蓝图: MOD-KB-001 §7.10.7
任务: KB-INF-0051

核心原则: 在存储事实之前，先验证事实。不做AI猜测。
  1. 文件系统 -> 检查文件是否存在、内容是否匹配
  2. 数据库   -> 检查记录是否存在、版本是否匹配
  3. Git       -> 检查commit hash是否存在
  4. 数字范围 -> 检查数字是否在合理范围内
  5. 路径引用 -> 检查路径是否可解析

用法:
    from zephyr.governance.kb.verify import FactChecker
    fc = FactChecker()
    fc.verify("file_exists", path="src/zephyr/data/knowledge_management/kb/__init__.py")
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


@dataclass
class FactResult:
    fact_type: str
    target: str
    verified: bool
    confidence: float
    actual_value: object = None
    expected_value: object = None
    error: str = ""


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


class FactChecker:
    _CONFIDENCE_THRESHOLD = 0.90

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    def verify(self, fact_type: str, **kwargs) -> FactResult:
        handlers = {
            "file_exists": self._verify_file_exists,
            "file_contains": self._verify_file_contains,
            "path_is_absolute": self._verify_path_absolute,
            "path_exists_relative": self._verify_path_relative,
            "count_in_range": self._verify_count_in_range,
            "module_has_attribute": self._verify_module_attribute,
            "version_matches": self._verify_version_match,
            "git_commit_exists": self._verify_git_commit,
        }
        handler = handlers.get(fact_type)
        if handler is None:
            return FactResult(
                fact_type=fact_type,
                target=str(kwargs),
                verified=False,
                confidence=0.0,
                error=f"Unknown fact type: {fact_type}",
            )
        return handler(**kwargs)

    def _verify_file_exists(self, path: str = "", **kwargs) -> FactResult:
        resolved = self._resolve_path(path)
        exists = resolved.exists()
        return FactResult(
            fact_type="file_exists",
            target=path,
            verified=exists,
            confidence=1.0 if exists else 0.0,
            actual_value=str(resolved) if exists else None,
        )

    def _verify_file_contains(self, path: str = "", needle: str = "", **kwargs) -> FactResult:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            return FactResult(
                fact_type="file_contains", target=path, verified=False, confidence=0.0, error=f"File not found: {path}"
            )
        try:
            content = resolved.read_text(encoding="utf-8", errors="replace")
            found = needle in content
            return FactResult(
                fact_type="file_contains",
                target=f"{path}[:{needle[:30]}]",
                verified=found,
                confidence=1.0 if found else 0.0,
            )
        except Exception as e:
            return FactResult(fact_type="file_contains", target=path, verified=False, confidence=0.0, error="internal error")

    def _verify_path_absolute(self, path: str = "", **kwargs) -> FactResult:
        is_abs = Path(path).is_absolute()
        return FactResult(
            fact_type="path_is_absolute",
            target=path,
            verified=is_abs,
            confidence=1.0,
            actual_value=is_abs,
        )

    def _verify_path_relative(self, path: str = "", **kwargs) -> FactResult:
        resolved = self._resolve_path(path)
        exists = resolved.exists()
        return FactResult(
            fact_type="path_exists_relative",
            target=path,
            verified=exists,
            confidence=1.0 if exists else 0.0,
            actual_value=str(resolved) if exists else None,
        )

    def _verify_count_in_range(self, count: int = 0, min_val: int = 0, max_val: int = 999999, **kwargs) -> FactResult:
        in_range = min_val <= count <= max_val
        confidence = 1.0 if in_range else (0.0 if count < min_val else 0.3)
        return FactResult(
            fact_type="count_in_range",
            target=f"{count} in [{min_val}, {max_val}]",
            verified=in_range,
            confidence=confidence,
            actual_value=count,
            expected_value=f"[{min_val}, {max_val}]",
        )

    def _verify_module_attribute(self, module_name: str = "", attr: str = "", **kwargs) -> FactResult:
        try:
            import importlib

            mod = importlib.import_module(module_name)
            has_attr = hasattr(mod, attr)
            return FactResult(
                fact_type="module_has_attribute",
                target=f"{module_name}.{attr}",
                verified=has_attr,
                confidence=1.0,
            )
        except Exception as e:
            return FactResult(
                fact_type="module_has_attribute",
                target=f"{module_name}.{attr}",
                verified=False,
                confidence=0.0,
                error="internal error",
            )

    def _verify_version_match(self, value: str = "", expected: str = "", **kwargs) -> FactResult:
        matched = value == expected
        return FactResult(
            fact_type="version_matches",
            target=f"{value} vs {expected}",
            verified=matched,
            confidence=1.0 if matched else 0.0,
            actual_value=value,
            expected_value=expected,
        )

    def _verify_git_commit(self, commit: str = "", **kwargs) -> FactResult:
        try:
            import subprocess

            result = subprocess.run(
                ["git", "cat-file", "-t", commit],
                capture_output=True,
                text=True,
                cwd=str(self._root),
                timeout=5,
            )
            exists = result.returncode == 0 and "commit" in result.stdout
            return FactResult(
                fact_type="git_commit_exists",
                target=commit,
                verified=exists,
                confidence=1.0 if exists else 0.0,
            )
        except Exception as e:
            return FactResult(
                fact_type="git_commit_exists", target=commit, verified=False, confidence=0.0, error=str(e)
            )

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        return (self._root / p).resolve()

    def batch_verify(self, facts: list[dict]) -> list[FactResult]:
        results: list[FactResult] = []
        for f in facts:
            fact_type = f.pop("type", "")
            results.append(self.verify(fact_type, **f))
        return results


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Deterministic Fact Verifier")
    sub = parser.add_subparsers(dest="cmd")

    fe = sub.add_parser("file-exists", help="Verify file exists")
    fe.add_argument("path", help="File path")

    fc = sub.add_parser("file-contains", help="Verify file contains string")
    fc.add_argument("path", help="File path")
    fc.add_argument("needle", help="String to search for")

    pr = sub.add_parser("path-relative", help="Verify relative path exists")
    pr.add_argument("path", help="Relative path")

    cr = sub.add_parser("count-range", help="Verify count in range")
    cr.add_argument("count", type=int)
    cr.add_argument("--min", type=int, default=0)
    cr.add_argument("--max", type=int, default=999999)

    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    checker = FactChecker()

    result = None
    if args.cmd == "file-exists":
        result = checker.verify("file_exists", path=args.path)
    elif args.cmd == "file-contains":
        result = checker.verify("file_contains", path=args.path, needle=args.needle)
    elif args.cmd == "path-relative":
        result = checker.verify("path_exists_relative", path=args.path)
    elif args.cmd == "count-range":
        result = checker.verify("count_in_range", count=args.count, min_val=args.min, max_val=args.max)
    else:
        parser.print_help()
        return

    if result:
        if args.json:
            print(
                json.dumps(
                    {
                        "fact_type": result.fact_type,
                        "target": result.target,
                        "verified": result.verified,
                        "confidence": result.confidence,
                        "actual": result.actual_value,
                        "expected": result.expected_value,
                        "error": result.error or None,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            verdict = "PASS" if result.verified else "FAIL"
            print(f"{verdict}  {result.fact_type}: {result.target}")
            if result.error:
                print(f"  Error: {result.error}")
        if not result.verified:
            sys.exit(1)


if __name__ == "__main__":
    main()
