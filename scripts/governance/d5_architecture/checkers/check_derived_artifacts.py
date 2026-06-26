#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS | scripts/governance/d5_architecture/checkers/check_derived_artifacts.py | §derived-artifact-gate
# [MODULE] scripts.governance.d5_architecture.checkers.check_derived_artifacts
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] .pre-commit-config.yaml (GATE-DERIVED)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读校验；不修改任何派生产物；从 derived_artifact_registry.yaml 加载清单
# [MODIFY-GUARD] 本脚本由 OPS 任务卡驱动修改
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=一致; exit 1=发现漂移; exit 2=系统错误; warn-only 模式始终 exit 0
# [TESTS] tests/unit/test_check_derived_artifacts.py
"""GATE-DERIVED: 派生产物一致性校验器（OPS-2026062655 治本）。

从 derived_artifact_registry.yaml 加载派生产物清单，逐个运行 --check 命令，
检测 depgraph.db 变更后派生产物是否同步更新。

对标社区实践：
  - Bazel: `make check-generated` CI 阻断
  - OpenAPI Codegen: spec → 类型自动生成，CI --check 阻断漂移
  - Copilot Workspace: 任务完成检查清单含"重生成派生物"步骤

用法::

    # 只校验，不修改（pre-commit hook）
    python check_derived_artifacts.py --check

    # warn-only 模式（骨架阶段，只警告不阻断）
    python check_derived_artifacts.py --check --warn-only

exit codes: 0=一致/已应用, 1=发现漂移, 2=系统错误
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[4]
_REGISTRY_PATH = (
    _PROJECT_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "derived_artifact_registry.yaml"
)

# _shared.constants 统一路径引用
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()


def load_registry() -> dict:
    """加载派生产物清单注册表。"""
    if not _REGISTRY_PATH.exists():
        print(f"FATAL: 派生产物清单不存在: {_REGISTRY_PATH}")
        print("       请确认 OPS-2026062655 已完成（创建 derived_artifact_registry.yaml）")
        sys.exit(EXIT_ERROR)
    with open(_REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_single_artifact(artifact: dict, warn_only: bool) -> tuple[bool, str]:
    """校验单个派生产物。

    Returns:
        (passed, detail) — passed=True 表示一致，False 表示漂移。
    """
    artifact_path = artifact.get("artifact", "")
    check_command = artifact.get("check_command")
    has_check_mode = artifact.get("has_check_mode", False)
    archived = artifact.get("archived_generator", False)

    if not has_check_mode or not check_command:
        # 无 --check 模式的产物（如已归档生成器的孤儿产物）跳过
        return True, f"SKIP (无 --check 模式): {artifact_path}"

    if archived:
        return True, f"SKIP (生成器已归档): {artifact_path}"

    # 运行 --check 命令
    cmd_parts = check_command.split()
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT: {check_command} 超过 60s"
    except Exception as e:
        return False, f"ERROR: 运行 {check_command} 失败: {e}"

    if result.returncode == 0:
        return True, f"OK: {artifact_path}"
    else:
        stderr_snippet = result.stderr.strip()[:200] if result.stderr else ""
        stdout_snippet = result.stdout.strip()[:200] if result.stdout else ""
        return False, (
            f"DRIFT: {artifact_path}\n"
            f"  command: {check_command}\n"
            f"  exit={result.returncode}\n"
            f"  stdout: {stdout_snippet}\n"
            f"  stderr: {stderr_snippet}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GATE-DERIVED: 派生产物一致性校验（depgraph.db ↔ asset_index）"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="校验派生产物与真源一致性（只读，不修改文件）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="warn-only 模式：发现漂移仅警告，不阻断（exit 0）",
    )
    args = parser.parse_args()

    if not args.check:
        parser.print_help()
        return EXIT_PASS

    print("=" * 60)
    print("GATE-DERIVED: 派生产物一致性校验")
    print("=" * 60)

    registry = load_registry()
    artifacts = registry.get("derived_artifacts", [])
    if not artifacts:
        print("WARN: 派生产物清单为空")
        return EXIT_PASS

    print(f"注册表中派生产物数: {len(artifacts)}")
    print(f"模式: {'warn-only' if args.warn_only else 'hard-block'}")
    print()

    all_passed = True
    checked = 0
    skipped = 0
    drifted = 0

    for artifact in artifacts:
        artifact_path = artifact.get("artifact", "")
        passed, detail = check_single_artifact(artifact, args.warn_only)

        if "SKIP" in detail:
            skipped += 1
            print(f"  [SKIP] {detail}")
        elif passed:
            checked += 1
            print(f"  [PASS] {detail}")
        else:
            drifted += 1
            all_passed = False
            print(f"  [FAIL] {detail}")
            print(f"    → 修复命令: {artifact.get('write_command', 'N/A')}")
            print()

    print()
    print(f"总计: {checked} PASS, {drifted} DRIFT, {skipped} SKIP")

    if all_passed:
        print("结果: PASS — 所有派生产物与真源一致")
        return EXIT_PASS
    else:
        print("结果: FAIL — 发现漂移，请运行对应生成器 --write 更新派生产物")
        if args.warn_only:
            print("  (warn-only 模式，不阻断)")
            return EXIT_PASS
        return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
