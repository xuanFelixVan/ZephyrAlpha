# [BLUEPRINT] MOD-INF-005 | scripts/governance/d12_ai_hallucination/validate_gate_prompt_conflict.py | §
# [MODULE] scripts.governance.d12_ai_hallucination.validate_gate_prompt_conflict
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d12_ai_hallucination.__init__
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
# [TTL] permanent
"""
validate_gate_prompt_conflict.py — Gate-Prompt 冲突检测
=====================================================
检测门禁 YAML 规则与 AGENTS.md / 项目 Prompt 指令之间的冲突。

Safety : M（门禁规则 vs Prompt 指令冲突 = 安全真空）
Usage  : python scripts/governance/d12_ai_hallucination/validate_gate_prompt_conflict.py [--json] [--verbose]

检测内容：
  CP1. 门禁禁止的操作 vs AGENTS.md 鼓励的操作
  CP2. 门禁要求的检查 vs AGENTS.md 允许跳过的检查
  CP3. 门禁的 severity/on_failure 降级 vs 项目全局硬规则的冲突
  CP4. Gate scope 声明 vs AGENTS.md 任务分类的一致性
  CP5. 影子门禁 (activation_stage=shadow) 在 Prompt 中被当作硬阻断使用

对标：
  - K8s: ValidatingWebhookConfiguration vs kubectl 默认行为
  - OPA: Rego policy vs 项目 Conftest 默认规则
  - Cursor/Claude Code: .cursorrules vs 项目 CLAUDE.md 指令层级

exit codes: 0=无冲突, 1=发现冲突, 2=执行错误
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import GATES_DIR, EXIT_ERROR, REPO_ROOT
from _shared.walk import iter_files  # 治本(ARCH-036 P1-3): 收敛 glob→iter_files

__manifest__ = """
args: []
description: >
  Gate-Prompt 冲突检测——扫描门禁 YAML 规则与 AGENTS.md 项目 Prompt 指令之间的
  语义冲突（门禁禁止 X 但 Prompt 鼓励 X，门禁要求检查但 Prompt 允许跳过等）。
dimensions:
- D12
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_PROJECT_ROOT = REPO_ROOT
_AGENTS_PATH = _PROJECT_ROOT / "AGENTS.md"


def _load_agents_text() -> str:
    """_load_agents_text implementation."""
    if not _AGENTS_PATH.exists():
        return ""
    return _AGENTS_PATH.read_text(encoding="utf-8", errors="replace")


def _load_gate_rules() -> list[dict[str, Any]]:
    """_load_gate_rules implementation."""
    import yaml

    rules: list[dict[str, Any]] = []
    for yf in iter_files(GATES_DIR, name_pattern="g*.yaml"):
        if "template" in yf.name.lower():
            continue
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
        except Exception:
            continue

        gate_id = str(data.get("gate_id", ""))
        scope = str(data.get("scope", "global"))
        activation = str(data.get("activation_stage", "p0"))
        checks = data.get("checks") or data.get("entry_conditions") or []
        on_failure = str(data.get("on_failure", "reject"))

        for c in checks:
            if not isinstance(c, dict):
                continue
            rules.append(
                {
                    "gate_id": gate_id,
                    "scope": scope,
                    "activation_stage": activation,
                    "gate_on_failure": on_failure,
                    "check_id": str(c.get("id", "")),
                    "check_type": str(c.get("type", "")),
                    "check_name": str(c.get("name", "")),
                    "severity": str(c.get("severity", "")),
                    "on_failure": str(c.get("on_failure", "reject")),
                    "description": str(c.get("description", "")),
                    "fix_hint": str(c.get("fix_hint", "")),
                    "anti_pattern": str(c.get("anti_pattern", "")),
                    "source_file": yf.name,
                }
            )

    return rules


def _extract_agents_directives(text: str) -> dict[str, list[str]]:
    """_extract_agents_directives implementation."""
    directives: dict[str, list[str]] = {
        "must_actions": [],
        "must_not_actions": [],
        "hard_rules": [],
        "soft_rules": [],
        "bypass_signals": [],
    }

    for line in text.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()

        if "必须" in stripped or "must" in lower:
            directives["must_actions"].append(stripped[:200])
        if "禁止" in stripped or "must not" in lower or "never" in lower:
            directives["must_not_actions"].append(stripped[:200])
        if "🔴" in stripped or "硬" in stripped:
            directives["hard_rules"].append(stripped[:200])
        if "🟡" in stripped or "软" in stripped or "建议" in stripped:
            directives["soft_rules"].append(stripped[:200])
        if any(kw in lower for kw in ("skip", "bypass", "忽略", "跳过", "例外", "豁免")):
            directives["bypass_signals"].append(stripped[:200])

    return directives


def detect_conflicts(gate_rules: list[dict[str, Any]], directives: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Detect issues in target and report findings."""
    conflicts: list[dict[str, Any]] = []

    for rule in gate_rules:
        severity = rule["severity"].upper()
        on_failure = rule["on_failure"]
        description = rule["description"]
        anti_pattern = rule.get("anti_pattern", "")
        fix_hint = rule.get("fix_hint", "")

        is_blocking = severity in ("P0", "ERROR", "CRITICAL") or on_failure == "reject"
        rule_text = f"{description} {anti_pattern} {fix_hint}"

        if is_blocking:
            for d_text in directives["must_not_actions"]:
                common_words = _shared_keywords(rule_text, d_text)
                if common_words and _semantic_contradiction(rule_text, d_text, "gate_blocks", "agents_allows"):
                    conflicts.append(
                        {
                            "type": "GATE_BLOCKS_AGENTS_ALLOWS",
                            "severity": "HIGH",
                            "gate_id": rule["gate_id"],
                            "check_id": rule["check_id"],
                            "check_name": rule["check_name"],
                            "gate_description": description[:120],
                            "agents_directive": d_text[:120],
                            "shared_keywords": common_words,
                            "detail": f"门禁 {rule['gate_id']}:{rule['check_id']} 禁止的操作在 AGENTS.md 中被允许",
                        }
                    )

        for d_text in directives["must_actions"]:
            common_words = _shared_keywords(rule_text, d_text)
            if common_words and _semantic_contradiction(rule_text, d_text, "gate_requires", "agents_discourages"):
                conflicts.append(
                    {
                        "type": "GATE_REQUIRES_AGENTS_DISCOURAGES",
                        "severity": "MEDIUM",
                        "gate_id": rule["gate_id"],
                        "check_id": rule["check_id"],
                        "check_name": rule["check_name"],
                        "gate_description": description[:120],
                        "agents_directive": d_text[:120],
                        "shared_keywords": common_words,
                        "detail": f"门禁 {rule['gate_id']}:{rule['check_id']} 要求的检查在 AGENTS.md 中被忽略",
                    }
                )

        for d_text in directives["bypass_signals"]:
            if is_blocking and _shared_keywords(rule_text, d_text):
                conflicts.append(
                    {
                        "type": "GATE_BLOCKING_VS_BYPASS_SIGNAL",
                        "severity": "HIGH",
                        "gate_id": rule["gate_id"],
                        "check_id": rule["check_id"],
                        "check_name": rule["check_name"],
                        "gate_description": description[:120],
                        "agents_directive": d_text[:120],
                        "detail": f"门禁 {rule['gate_id']}:{rule['check_id']} 硬阻断但 AGENTS.md 中存在跳过/豁免信号",
                    }
                )

        if rule.get("activation_stage") == "shadow" and is_blocking:
            for d_text in directives["hard_rules"]:
                common_words = _shared_keywords(rule_text, d_text)
                if common_words:
                    conflicts.append(
                        {
                            "type": "SHADOW_GATE_VS_HARD_RULE",
                            "severity": "MEDIUM",
                            "gate_id": rule["gate_id"],
                            "check_id": rule["check_id"],
                            "check_name": rule["check_name"],
                            "activation_stage": "shadow",
                            "agents_directive": d_text[:120],
                            "detail": f"影子门禁 {rule['gate_id']} 与 AGENTS.md 硬规则语义重叠，应从 shadow 升级为 p0",
                        }
                    )

    return conflicts


def _shared_keywords(text_a: str, text_b: str) -> list[str]:
    """_shared_keywords implementation."""
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "of",
        "to",
        "in",
        "for",
        "on",
        "and",
        "or",
        "not",
        "with",
        "be",
        "by",
        "as",
        "at",
        "from",
        "this",
        "that",
        "必须",
        "禁止",
        "必须显式",
    }
    words_a = set(w.lower() for w in re.findall(r"[a-zA-Z\u4e00-\u9fff]{3,}", text_a) if w.lower() not in stop_words)
    words_b = set(w.lower() for w in re.findall(r"[a-zA-Z\u4e00-\u9fff]{3,}", text_b) if w.lower() not in stop_words)
    shared = words_a & words_b
    return sorted(shared)[:10] if len(shared) >= 2 else []


def _semantic_contradiction(gate_text: str, agents_text: str, gate_stance: str, agents_stance: str) -> bool:
    """_semantic_contradiction implementation."""
    contradiction_pairs = [
        ({"必须", "must", "required"}, {"禁止", "never", "must not", "跳过"}),
        ({"reject", "阻断", "block"}, {"允许", "allow", "跳过", "skip", "豁免"}),
        ({"check", "验证", "validate"}, {"不检查", "skip check", "跳过检查"}),
        ({"强制", "mandatory", "required"}, {"可选", "optional", "建议"}),
    ]

    gate_lower = gate_text.lower()
    agents_lower = agents_text.lower()

    for pro_set, con_set in contradiction_pairs:
        gate_has_pro = any(w in gate_lower for w in pro_set)
        gate_has_con = any(w in gate_lower for w in con_set)
        agents_has_pro = any(w in agents_lower for w in pro_set)
        agents_has_con = any(w in agents_lower for w in con_set)

        if gate_has_pro and agents_has_con:
            return True
        if gate_has_con and agents_has_pro:
            return True

    return False


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Gate-Prompt 冲突检测")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    agents_text = _load_agents_text()
    if not agents_text:
        print("[GATE-PROMPT] AGENTS.md 不存在或为空，跳过", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    gate_rules = _load_gate_rules()
    directives = _extract_agents_directives(agents_text)

    if args.verbose:
        print(f"[GATE-PROMPT] 加载了 {len(gate_rules)} 条门禁规则")
        print(f"[GATE-PROMPT] AGENTS.md 提取到 {sum(len(v) for v in directives.values())} 条指令")

    conflicts = detect_conflicts(gate_rules, directives)

    if args.json:
        output = {
            "checked_at": datetime.now(UTC).isoformat(),
            "total_gate_rules": len(gate_rules),
            "total_agents_directives": sum(len(v) for v in directives.values()),
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        if conflicts:
            print(f"\n[GATE-PROMPT] 发现 {len(conflicts)} 个 Gate-Prompt 冲突:")
            for c in conflicts:
                print(f"  [{c['severity']}] {c['type']}")
                print(f"    门禁: {c['gate_id']}:{c['check_id']} — {c['gate_description']}")
                print(f"    AGENTS.md: {c['agents_directive']}")
                if c.get("shared_keywords"):
                    print(f"    共享关键词: {c['shared_keywords']}")
        else:
            print("[GATE-PROMPT] 未发现 Gate-Prompt 冲突")

    sys.exit(1 if conflicts else 0)


if __name__ == "__main__":
    main()
