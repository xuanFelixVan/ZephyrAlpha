# [BLUEPRINT] MOD-GOV_CHECK_RULE_COVERAGE
# [MODULE]# [MODULE] scripts.governance.check_rule_coverage
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""governance/check_rule_coverage 脚本 — 规则文件漂移检测

读取 data/rule_optimization/key_facts.yaml，验证 .trae/rules/*.md 和 AGENTS.md
是否与项目实际状态对齐。模拟 AI 冷启动时必须看到的一致事实。

[BLUEPRINT] architecture_upgrade_discussion.md §23 | 规则文件对齐方案
[MODULE] N/A（脚本，非模块）
[INVARIANTS] key_facts.yaml 是 SSoT 基准；exit 0 = 全部通过；exit 1 = 有漂移
[MODIFY-GUARD] 事实变更时先改 key_facts.yaml → 再改规则文件 → 再跑本脚本
[CONSUMERS] AI session 冷启动；规则文件优化工作流
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] key_facts.yaml 缺失 → exit 2；文件读取异常 → exit 3
[TESTS] python scripts/governance/check_rule_coverage.py --warn-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

PROJECT_ROOT = REPO_ROOT
KEY_FACTS_PATH = PROJECT_ROOT / "data" / "rule_optimization" / "key_facts.yaml"


def load_key_facts() -> dict:
    """加载 key_facts.yaml。"""
    if not KEY_FACTS_PATH.exists():
        print(f"ERROR: key_facts.yaml 不存在: {KEY_FACTS_PATH}")
        sys.exit(EXIT_ERROR)
    with open(KEY_FACTS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_fact_appears(fact: str, file_rel: str) -> tuple[bool, str]:
    """检查 fact 字符串是否出现在指定文件中。"""
    file_path = PROJECT_ROOT / file_rel
    if not file_path.exists():
        return False, f"文件不存在: {file_rel}"
    content = file_path.read_text(encoding="utf-8")
    if fact in content:
        return True, f"OK: '{fact}' 出现在 {file_rel}"
    return False, f"FAIL: '{fact}' 未出现在 {file_rel}"


def check_pattern_absent(pattern: str, file_rel: str) -> tuple[bool, str]:
    """检查 pattern 字符串是否不出现在指定文件中。"""
    file_path = PROJECT_ROOT / file_rel
    if not file_path.exists():
        return True, f"SKIP: 文件不存在，跳过: {file_rel}"
    content = file_path.read_text(encoding="utf-8")
    if pattern in content:
        return False, f"FAIL: 禁止模式 '{pattern}' 仍出现在 {file_rel}"
    return True, f"OK: 禁止模式 '{pattern}' 已从 {file_rel} 移除"


def check_file_existence(path_rel: str, must_exist: bool) -> tuple[bool, str]:
    """检查文件/目录是否存在。"""
    path = PROJECT_ROOT / path_rel
    exists = path.exists()
    if must_exist:
        if exists:
            return True, f"OK: {path_rel} 存在"
        return False, f"FAIL: {path_rel} 应存在但不存在"
    if not exists:
        return True, f"OK: {path_rel} 已删除（符合预期）"
    return False, f"FAIL: {path_rel} 应已删除但仍存在"


def main() -> None:
    """入口——读取 key_facts.yaml，逐项检查，输出报告。"""
    parser = argparse.ArgumentParser(description="规则文件漂移检测")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不返回非零退出码")
    args = parser.parse_args()

    facts = load_key_facts()
    results: list[tuple[str, bool, str]] = []

    for category in ["numeric_facts", "path_facts", "command_facts", "rule_facts"]:
        for item in facts.get(category, []):
            fact_id = item.get("id", "?")
            fact = item.get("fact", "")
            for file_rel in item.get("must_appear_in", []):
                ok, msg = check_fact_appears(fact, file_rel)
                results.append((f"{category}/{fact_id}", ok, msg))
            for neg in item.get("must_not_appear_as", []):
                file_rel = neg.get("file", "")
                pattern = neg.get("pattern", "")
                ok, msg = check_pattern_absent(pattern, file_rel)
                results.append((f"{category}/{fact_id}/neg", ok, msg))

    for item in facts.get("file_existence_checks", []):
        fact_id = item.get("id", "?")
        path_rel = item.get("path", "")
        must_exist = item.get("must_exist", True)
        ok, msg = check_file_existence(path_rel, must_exist)
        results.append((f"file_existence/{fact_id}", ok, msg))

    print("=" * 70)
    print("规则文件漂移检测报告")
    print(f"基准: {KEY_FACTS_PATH.relative_to(PROJECT_ROOT)}")
    print("=" * 70)

    pass_count = 0
    fail_count = 0
    for check_id, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {check_id}: {msg}")
        if ok:
            pass_count += 1
        else:
            fail_count += 1

    print("=" * 70)
    print(f"总计: {pass_count} PASS / {fail_count} FAIL / {len(results)} 项")

    if fail_count == 0:
        print("结论: 全部通过——规则文件与项目实际状态对齐")
        sys.exit(EXIT_PASS)
    print("结论: 存在漂移——规则文件需要修复")
    if args.warn_only:
        print("（--warn-only 模式，不阻断）")
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
