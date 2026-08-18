# [BLUEPRINT] MOD-GOV-041 | docs/03_modules/_domain_governance/gov_generators/blueprint.md | §rule-ai-perception-index
# [MODULE] zephyr.scripts.governance.generators.generate_rule_ai_perception_index
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.io.yaml_utils
# [CONSUMERS] scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py; scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 真源是 docs/01_policies_and_standards/rules/trae_*.yaml（64条规则）；本生成器只读不写真源；输出 rule_ai_perception_index.yaml 到 catalogs/；--check 模式对比生成版 vs 磁盘版不一致→exit 1（GATE-21 静态清单漂移）；operations/gate_ids 从 triggers list 提取；paired_gate_id 字段预留（Phase 3.5 填充）
# [MODIFY-GUARD] 输出文件路径；module_id PS-REG-020；perception 字段清单
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 1 on --check drift；exit 2 on source YAML parse error
# [TESTS] tests/test_generate_rule_ai_perception_index.py
# [A_module] module_id=MOD-GOV-041 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""generate_rule_ai_perception_index.py — 规则AI感知索引生成器（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）

病根2治本：规则可发现性。64条 trae 规则分散在各 YAML 文件中，AI 无法在施工前
快速查询"我即将做的操作命中哪些规则"。本生成器从所有 trae_*.yaml 提取感知元数据
（operations/gate_ids/scope/domain/tags/aliases），聚合为单一索引文件。

消费方：
- sync_yaml_to_depgraph.py：同步到 PostgreSQL depgraph DB（rule_ai_perception 表）
- discover_applicable_rules MCP 工具（Phase 3.2b）：按 operation/gate_id/scope 查询
- M17 指标：统计 operations 覆盖率（无 operations 的规则 = 不可被AI感知）

用法：
  python scripts/governance/generators/generate_rule_ai_perception_index.py          # 生成
  python scripts/governance/generators/generate_rule_ai_perception_index.py --check   # 漂移检测
"""
from __future__ import annotations

__manifest__ = """
args: []
description: generate_rule_ai_perception_index.py — 规则AI感知索引生成器（#ARCH-GOV-CONVERGENCE-META
  Phase 3.2a）
dimensions:
- D1
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

# _shared 位于父目录 scripts/governance/_shared/，直接运行脚本时 sys.path[0]=本目录
# （generators/），找不到父目录的 _shared，需先把父目录加入搜索路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS

REPO_ROOT = Path(__file__).resolve().parents[3]
RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"
OUTPUT_PATH = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "rule_ai_perception_index.yaml"
)

MODULE_ID = "PS-REG-020"
GENERATED_BY = "scripts/governance/generators/generate_rule_ai_perception_index.py"


def _extract_triggers(triggers: list) -> tuple[list[str], list[str]]:
    """从 triggers list 提取 operations 和 gate_ids。

    triggers 格式（trae_*.yaml）:
        - operation: file_write
        - operation: file_create
        - gate_id: G0
    """
    operations: list[str] = []
    gate_ids: list[str] = []
    if not isinstance(triggers, list):
        return operations, gate_ids
    for trig in triggers:
        if not isinstance(trig, dict):
            continue
        op = trig.get("operation")
        if isinstance(op, str) and op:
            operations.append(op)
        gid = trig.get("gate_id")
        if isinstance(gid, str) and gid:
            gate_ids.append(gid)
    return operations, gate_ids


def _extract_perception_entry(rule_data: dict, rule_file: Path) -> dict | None:
    """从单条 trae 规则 YAML 提取感知索引条目。"""
    rule_id = rule_data.get("rule_id")
    if not isinstance(rule_id, str) or not rule_id:
        return None
    operations, gate_ids = _extract_triggers(rule_data.get("triggers", []))
    return {
        "rule_id": rule_id,
        "title": rule_data.get("title", ""),
        "module_id": rule_data.get("module_id", ""),
        "scope": rule_data.get("scope", ""),
        "domain": rule_data.get("domain", ""),
        "severity": rule_data.get("severity", ""),
        "stability": rule_data.get("stability", ""),
        "ai_autonomy": rule_data.get("ai_autonomy", ""),
        "safety_level": rule_data.get("safety_level", ""),
        "operations": operations,
        "gate_ids": gate_ids,
        "tags": rule_data.get("tags", []) or [],
        "aliases": rule_data.get("aliases", []) or [],
        "paired_gate_id": rule_data.get("paired_gate_id"),  # Phase 3.5 填充
        "rule_file": str(rule_file.relative_to(REPO_ROOT)).replace("\\", "/"),
    }


def _load_all_rules() -> list[dict]:
    """加载所有 trae_*.yaml 规则文件，返回感知索引条目列表。"""
    entries: list[dict] = []
    rule_files = sorted(RULES_DIR.glob("trae_*.yaml"))
    for rf in rule_files:
        try:
            data = yaml.safe_load(rf.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            print(f"ERROR: parse {rf.name}: {e}", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        if not isinstance(data, dict):
            continue
        entry = _extract_perception_entry(data, rf)
        if entry is not None:
            entries.append(entry)
    return entries


def _build_index_yaml(entries: list[dict]) -> str:
    """构建索引 YAML 内容。"""
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = {
        "module_id": MODULE_ID,
        "doc_type": "register",
        "ttl": "permanent",
        "title": "规则AI感知索引（trae 规则→operations/gate_ids 映射）",
        "status": "active",
        "generated_at": now_iso,
        "generated_by": GENERATED_BY,
        "maintenance": "auto",
        "source": "docs/01_policies_and_standards/rules/trae_*.yaml",
        "total_rules": len(entries),
        "rules": entries,
    }
    return yaml.dump(doc, allow_unicode=True, default_flow_style=False, sort_keys=False)


def generate() -> str:
    """生成索引 YAML 并返回内容字符串。"""
    entries = _load_all_rules()
    return _build_index_yaml(entries)


def write() -> Path:
    """生成并写入索引文件，返回输出路径。"""
    content = generate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    return OUTPUT_PATH


def check() -> int:
    """漂移检测：对比生成版 vs 磁盘版。不一致返回 1。"""
    generated = generate()
    if not OUTPUT_PATH.is_file():
        print(f"DRIFT: {OUTPUT_PATH.name} 不存在（首次生成请先运行无 --check）")
        return EXIT_FINDINGS
    on_disk = OUTPUT_PATH.read_text(encoding="utf-8")
    # 忽略 generated_at 时间戳差异（只比较结构）
    gen_lines = [l for l in generated.splitlines() if not l.startswith("generated_at:")]
    disk_lines = [l for l in on_disk.splitlines() if not l.startswith("generated_at:")]
    if gen_lines == disk_lines:
        print(f"OK: {OUTPUT_PATH.name} 一致（{len(gen_lines)} 行）")
        return EXIT_PASS
    print(f"DRIFT: {OUTPUT_PATH.name} 不一致")
    # 显示前5个差异
    import difflib
    diff = list(difflib.unified_diff(disk_lines, gen_lines, lineterm="", n=1))
    for line in diff[:20]:
        print(f"  {line}")
    return EXIT_FINDINGS
def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="规则AI感知索引生成器")
    parser.add_argument("--check", action="store_true", help="漂移检测模式")
    args = parser.parse_args()
    if args.check:
        return check()
    out = write()
    entries = _load_all_rules()
    print(f"Generated: {out.relative_to(REPO_ROOT)}")
    print(f"  total_rules: {len(entries)}")
    no_ops = [e["rule_id"] for e in entries if not e["operations"]]
    no_gates = [e["rule_id"] for e in entries if not e["gate_ids"]]
    print(f"  rules without operations: {len(no_ops)}")
    if no_ops:
        print(f"    {', '.join(no_ops[:10])}{'...' if len(no_ops) > 10 else ''}")
    print(f"  rules without gate_ids: {len(no_gates)}")
    if no_gates:
        print(f"    {', '.join(no_gates[:10])}{'...' if len(no_gates) > 10 else ''}")
    return EXIT_PASS
if __name__ == "__main__":
    sys.exit(main())
