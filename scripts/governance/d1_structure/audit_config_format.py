# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/audit_config_format.py | §
# [MODULE] scripts.governance.d1_structure.audit_config_format
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
audit_config_format.py — config/ 目录格式/注释/边界快速扫描



对标：AGENTS.md §4（编码安全 — UTF-8 / 无BOM / 行尾一致性）
     AGENTS.md §6.2（原子事务模式 — 注释与实际内容一致性）
     ITIL SACM §4.5（Configuration Audit — 配置项格式合规性）

检测内容：
- F1 编码格式：BOM、行尾混合、尾部空白、Tab 字符
- F2 注释准确性：YAML 注释中声称的数量与实际内容是否一致
- F3 数值边界：min/max 合理性、safety level 合法值、重复转换
- F4 Git 追踪：config YAML 是否被 git 追踪

与 validate_config_integrity.py 的关系：
本脚本是 L1-L9 纵深审计的轻量版，仅扫描 config/ 目录，
不加载代码消费者、不检查 CBAC、不做 manifest 对账。
适合快速格式检查或 CI pre_commit hook。

exit codes: 0=pass, 1=findings
"""

from __future__ import annotations

__manifest__ = """
args: []
description: config/ 格式/注释/边界快速扫描（F1-F4轻量版，CI pre_commit适用）
dimensions:
- D1
- D4
priority: P2
timeout_seconds: 15
warn_only: true
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

import yaml
from _shared.constants import CONFIG_DIR, EXIT_PASS, REPO_ROOT


def report(issues, level, code, msg) -> None:
    """记录并打印一条格式化问题行。"""
    issues.append((level, code, msg))
    icon = {"BUG": "\U0001f534", "DEFECT": "\U0001f534", "ISSUE": "\U0001f7e1", "LOW": "\U0001f7e2"}[level]
    print(f"  {icon} {code}: {msg}", file=sys.stderr)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="config/ 目录格式/注释/边界快速扫描")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现违规不阻塞（exit 0）",
    )
    args = parser.parse_args()

    issues = []

    all_yamls = sorted(f for f in CONFIG_DIR.rglob("*.yaml") if f.is_file())

    print("=" * 70, file=sys.stderr)
    print("[CONFIG-FORMAT] config/ 格式/注释/边界快速扫描", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    # =====================================================================
    # F1: Encoding / format
    # =====================================================================
    print(file=sys.stderr)
    print("--- F1: Encoding and format ---", file=sys.stderr)

    for yf in all_yamls:
        rel = yf.relative_to(REPO_ROOT)
        raw = yf.read_bytes()

        if raw[:3] == b"\xef\xbb\xbf":
            report(issues, "ISSUE", "F1-BOM", f"{rel}: UTF-8 BOM detected")

        crlf_count = raw.count(b"\r\n")
        lf_only_count = raw.count(b"\n") - crlf_count
        if crlf_count > 0 and lf_only_count > 0:
            report(
                issues, "ISSUE", "F1-MIXED-EOL", f"{rel}: mixed line endings (CRLF={crlf_count}, LF={lf_only_count})"
            )

        text = raw.decode("utf-8", errors="replace")
        trailing_ws_lines = [(i + 1) for i, line in enumerate(text.split("\n")) if line.rstrip("\r\n") != line.rstrip()]
        if trailing_ws_lines:
            report(issues, "LOW", "F1-TRAILING-WS", f"{rel}: trailing whitespace on lines {trailing_ws_lines[:5]}")

        if "\t" in text:
            tab_lines = [(i + 1) for i, line in enumerate(text.split("\n")) if "\t" in line]
            report(issues, "LOW", "F1-TABS", f"{rel}: tab characters on lines {tab_lines[:5]}")

    print("  \u2705 BOM, EOL, whitespace scan complete", file=sys.stderr)

    # =====================================================================
    # F2: Comment accuracy
    # =====================================================================
    print(file=sys.stderr)
    print("--- F2: Comment accuracy ---", file=sys.stderr)

    cap_path = CONFIG_DIR / "capabilities.yaml"
    if cap_path.exists():
        cap_text = cap_path.read_text("utf-8")
        cap_data = yaml.safe_load(cap_text)
        rule_count = len(cap_data.get("rules", []))
        count_comments = re.findall(r"(\d+)\s*条规则", cap_text)
        if count_comments:
            claimed = int(count_comments[0])
            if claimed != rule_count:
                report(
                    issues,
                    "ISSUE",
                    "F2-RULE-COUNT",
                    f"capabilities.yaml: comment says {claimed} rules, actual={rule_count}",
                )
            else:
                print(f"  \u2705 Rule count comment accurate: {rule_count}", file=sys.stderr)
        else:
            print(f"  \u2139\ufe0f  No rule count comment found (actual={rule_count})", file=sys.stderr)

    router_path = CONFIG_DIR / "trigger_router.yaml"
    if router_path.exists():
        router_text = router_path.read_text(encoding="utf-8")
        router_data = yaml.safe_load(router_text)
        trigger_count = len(router_data.get("triggers", {}))
        trigger_comments = re.findall(r"(\d+)\s*种\s*trigger_type", router_text)
        if trigger_comments:
            claimed = int(trigger_comments[0])
            if claimed != trigger_count:
                report(
                    issues,
                    "ISSUE",
                    "F2-TRIGGER-COUNT",
                    f"trigger_router.yaml: comment says {claimed} triggers, actual={trigger_count}",
                )
            else:
                print(f"  \u2705 Trigger count comment accurate: {trigger_count}", file=sys.stderr)

    policy_path = CONFIG_DIR / "compression" / "policy.yaml"
    if policy_path.exists():
        policy_text = policy_path.read_text(encoding="utf-8")
        policy_data = yaml.safe_load(policy_text)
        min_chars = policy_data.get("policy", {}).get("min_chars", 0)
        max_chars = policy_data.get("policy", {}).get("max_chars", 0)
        print(f"  \u2705 policy.yaml min_chars={min_chars} max_chars={max_chars}", file=sys.stderr)

    emb_path = CONFIG_DIR / "embedding_model_registry.yaml"
    if emb_path.exists():
        emb_data = yaml.safe_load(emb_path.read_text(encoding="utf-8"))
        model_count = len(emb_data.get("models", []))
        model_count_comments = re.findall(r"(\d+)\s*个.*?模型", emb_path.read_text(encoding="utf-8"))
        if model_count_comments:
            claimed = int(model_count_comments[0])
            if claimed != model_count:
                report(
                    issues,
                    "ISSUE",
                    "F2-MODEL-COUNT",
                    f"embedding_model_registry.yaml: comment says {claimed} models, actual={model_count}",
                )
            else:
                print(f"  \u2705 Model count comment accurate: {model_count}", file=sys.stderr)

    # =====================================================================
    # F3: Numeric boundaries
    # =====================================================================
    print(file=sys.stderr)
    print("--- F3: Numeric boundary rationality ---", file=sys.stderr)

    if policy_path.exists():
        if min_chars >= max_chars:
            report(issues, "BUG", "F3-MIN-MAX", f"policy.yaml: min_chars({min_chars}) >= max_chars({max_chars})")
        else:
            print(f"  \u2705 min_chars({min_chars}) < max_chars({max_chars})", file=sys.stderr)
        if min_chars <= 0:
            report(issues, "BUG", "F3-MIN-ZERO", f"policy.yaml: min_chars={min_chars} (must be > 0)")

    if router_path.exists():
        for trigger_name, trigger_conf in router_data.get("triggers", {}).items():
            safety = trigger_conf.get("safety", "")
            if safety not in ("L", "M", "H"):
                report(
                    issues,
                    "ISSUE",
                    "F3-SAFETY",
                    f"trigger_router.yaml: {trigger_name} safety={safety!r} (expected L/M/H)",
                )

    ctx_path = CONFIG_DIR / "context-rules.yaml"
    if ctx_path.exists():
        ctx_data = yaml.safe_load(ctx_path.read_text(encoding="utf-8"))
        for rule in ctx_data.get("rules", []):
            threshold = rule.get("threshold", None)
            if threshold is not None:
                if not (0.0 <= threshold <= 1.0):
                    report(
                        issues,
                        "ISSUE",
                        "F3-THRESHOLD",
                        f"context-rules.yaml: rule '{rule.get('name', '?')}' threshold={threshold}",
                    )

    ssm_path = CONFIG_DIR / "session_state_machine.yaml"
    if ssm_path.exists():
        ssm_data = yaml.safe_load(ssm_path.read_text(encoding="utf-8"))
        transitions = ssm_data.get("transitions", [])
        seen_transitions = set()
        for t in transitions:
            if not isinstance(t, dict):
                continue
            key = (t.get("from", ""), t.get("to", ""))
            if key in seen_transitions:
                report(issues, "ISSUE", "F3-DUP-TRANSITION", f"session_state_machine.yaml: duplicate transition {key}")
            seen_transitions.add(key)

    print("  \u2705 Safety levels and thresholds checked", file=sys.stderr)

    # =====================================================================
    # F4: Git tracking
    # =====================================================================
    print(file=sys.stderr)
    print("--- F4: Git tracking ---", file=sys.stderr)

    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--"]
            + [str(f.relative_to(REPO_ROOT)).replace("\\", "/") for f in all_yamls],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            untracked = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
            if untracked:
                report(issues, "ISSUE", "F4-UNTRACKED", f"{len(untracked)} config YAML not tracked by git: {untracked}")
        print("  \u2705 Git tracking check complete", file=sys.stderr)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("  \u26a0\ufe0f  Cannot check git tracking status", file=sys.stderr)

    # =====================================================================
    # FINAL
    # =====================================================================
    print(file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    if issues:
        print(f"FOUND {len(issues)} ISSUE(S):", file=sys.stderr)
        for level, code, msg in issues:
            icon = {"BUG": "\U0001f534", "DEFECT": "\U0001f534", "ISSUE": "\U0001f7e1", "LOW": "\U0001f7e2"}[level]
            print(f"  {icon} [{level}] {code}: {msg}", file=sys.stderr)
    else:
        print("NO NEW ISSUES FOUND \u2014 config/ is clean", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    if args.warn_only:
        if issues:
            print(f"\n⚠️  --warn-only 模式: 发现 {len(issues)} 个问题，不阻断", file=sys.stderr)
        sys.exit(EXIT_PASS)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
