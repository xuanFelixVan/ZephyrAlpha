#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# [A_full] module_id=CFG-check-src-no-data | layer=config | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent
#
# GATE-SRC-NO-DATA: src/ 下禁止 data/ 子目录校验
#
# 真源（治本 2026-06-29）：directory_contract.yaml global_forbidden[].forbidden_prefix
#       消除原硬编码 FORBIDDEN_PREFIX = "src/data/"，前缀变更只需改契约一处
#
# 原理：data/ 是运行态数据（brain passport / audit_logs / telemetry / capability_cards 等）
#       唯一合法存放位置。src/ 下创建 data/ 子目录会导致双真源漂移。
# 历史教训：src/data/brain/passports/ 与 data/brain/passports/ 并存导致版本漂移
#           （2026-06-27 清理，commit 36871193）
#
# 模式：--ci 硬阻断（违规 exit 1 拒绝提交）/ --warn-only 只警告
# 触发：pre-commit（事件驱动，staged 文件检测，自动运行自动关闭）
# 消费者：.pre-commit-config.yaml gate-src-no-data
"""
import argparse
import subprocess
import sys
from pathlib import Path

__manifest__ = """
args: []
description: '# [A_full] module_id=CFG-check-src-no-data | layer=config | stability=stable
  | safety=L | ai_autonomy=human_gated'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


# ── 路径设置（一次性 bootstrap，随后用 _shared.constants.REPO_ROOT）──
# 约束：REPO_ROOT 真源唯一为 zephyr.shared.io.paths.REPO_ROOT
#       scripts/ 包外消费者仅允许一次性 bootstrap 算 sys.path（N 值固定且仅用一次）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import yaml as _yaml  # noqa: E402
from _shared.constants import REPO_ROOT  # noqa: E402

# ── 真源加载：从 directory_contract.yaml 动态加载 forbidden prefixes ──
_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "contracts" / "directory_contract.yaml"
)


def _load_forbidden_prefixes() -> tuple[str, ...]:
    """从 directory_contract.yaml global_forbidden 提取所有 forbidden_prefix 值。

    真源：directory_contract.yaml global_forbidden[].forbidden_prefix
    治本（2026-06-29）：消除硬编码 FORBIDDEN_PREFIX，前缀变更只需改契约一处。

    fail-closed 例外：契约文件不存在时返回空 tuple（不阻断）——避免 contract 缺失
    导致 pre-commit 全局失效；GitCommitGateway 内部有独立的等效校验作为第二道防线。
    """
    try:
        contract = _yaml.safe_load(_CONTRACT_PATH.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        return ()
    rules = contract.get("global_forbidden", []) or []
    return tuple(
        r.get("forbidden_prefix") for r in rules
        if isinstance(r, dict) and r.get("forbidden_prefix")
    )


FORBIDDEN_PREFIXES: tuple[str, ...] = _load_forbidden_prefixes()


def get_staged_files():
    """获取 staged 文件列表（相对路径，仅新增/修改/重命名）"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_src_no_data(files):
    """检测是否有 src/data/ 路径的 staged 文件（大小写不敏感）

    遍历 FORBIDDEN_PREFIXES（从 directory_contract.yaml 动态加载），
    任一前缀命中即违规。
    """
    violations = []
    for f in files:
        f_lower = f.lower()
        for prefix in FORBIDDEN_PREFIXES:
            if f_lower.startswith(prefix.lower()):
                violations.append(f)
                break
    return violations


def main():
    parser = argparse.ArgumentParser(
        description="GATE-SRC-NO-DATA: src/ 下禁止 data/ 子目录（数据真源唯一位置为 data/）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ci", action="store_true", help="硬阻断模式（违规 exit 1）")
    mode.add_argument("--warn-only", action="store_true", help="只警告不阻断")
    args = parser.parse_args()

    files = get_staged_files()
    if not files:
        return 0

    violations = check_src_no_data(files)
    if not violations:
        return 0

    msg = (
        f"[GATE-SRC-NO-DATA] 违规：src/ 下禁止 data/ 子目录（数据真源唯一位置为 data/）\n"
        f"  违规文件：{violations}\n"
        f"  真源：directory_contract.yaml global_forbidden[].forbidden_prefix\n"
        f"  原因：src/ 仅放代码，运行态数据必须放 data/ 下\n"
        f"  历史教训：src/data/brain/ 与 data/brain/ 并存导致版本漂移（2026-06-27 清理）"
    )
    print(msg, file=sys.stderr)

    if args.ci:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
