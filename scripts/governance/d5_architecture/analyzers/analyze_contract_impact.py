# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/analyzers/analyze_contract_impact.py | §
# [MODULE] scripts.governance.d5_architecture.analyzers.analyze_contract_impact
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.analyzers.__init__
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
"""analyze_contract_impact.py — 契约变更影响分析器



分析修改一个 CTR 字段后，哪些层/模块会受影响。
基于 cross_layer_contracts.yaml 的 target_layers 字段进行静态影响分析。

用法:
    python scripts/governance/d5_architecture/analyze_contract_impact.py CTR-001
    python scripts/governance/d5_architecture/analyze_contract_impact.py CTR-001 --field price
    python scripts/governance/d5_architecture/analyze_contract_impact.py --all  # 全局影响矩阵

输出: 受影响的目标层列表 + 建议的测试清单
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  契约变更影响分析器——当跨层契约 YAML 变更时，递归分析所有下游 depends_on 引用链，
  输出受影响模块清单 + 变更范围评估。对标 YAML canonical SSoT + §6.2 原子事务。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

import yaml

CONTRACTS_YAML = (
    REPO_ROOT
    / "architecture_model/contracts/cross_layer_contracts.yaml"
)


def load_contracts() -> dict:
    """加载合约定义"""
    if not CONTRACTS_YAML.exists():
        print(f"[Impact] 契约文件不存在: {CONTRACTS_YAML}")
        sys.exit(EXIT_ERROR)
    return yaml.safe_load(CONTRACTS_YAML.read_text(encoding="utf-8"))


def find_contract(data: dict, contract_id: str) -> dict | None:
    """查找合约"""
    for ctr in data.get("contracts", []):
        if ctr["id"] == contract_id:
            return ctr
    return None


def find_consumers_in_source(data: dict, contract_id: str) -> list[str]:
    """查找源码中的消费者"""
    target = find_contract(data, contract_id)
    if target is None:
        return []
    target_layers = target.get("target_layers", [])
    contract_name = target.get("name", "")
    contract_type_name = contract_name.split(" / ")[0].strip()
    consumers: list[str] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    for layer in target_layers:
        layer_dir = src_dir / layer
        if not layer_dir.exists():
            continue
        for py_file in layer_dir.rglob("*.py"):
            if not py_file.is_file():
                continue
            content = py_file.read_text(encoding="utf-8", errors="replace")
            if contract_type_name in content or contract_id in content:
                rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
                consumers.append(rel)
    return consumers


def find_field_consumers(data: dict, contract_id: str, field_name: str) -> list[str]:
    """查找字段消费者"""
    target = find_contract(data, contract_id)
    if target is None:
        return []
    target_layers = target.get("target_layers", [])
    consumers: list[str] = []
    src_dir = REPO_ROOT / "src" / "zephyr"
    for layer in target_layers:
        layer_dir = src_dir / layer
        if not layer_dir.exists():
            continue
        for py_file in layer_dir.rglob("*.py"):
            if not py_file.is_file():
                continue
            content = py_file.read_text(encoding="utf-8", errors="replace")
            if f".{field_name}" in content or f'"{field_name}"' in content or f"'{field_name}'" in content:
                rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
                consumers.append(rel)
    return consumers


def build_impact_matrix(data: dict) -> dict[str, dict]:
    """构建影响矩阵"""
    matrix: dict[str, dict] = {}
    for ctr in data.get("contracts", []):
        cid = ctr["id"]
        source = ctr.get("source_layer", "unknown")
        targets = ctr.get("target_layers", [])
        matrix[cid] = {
            "name": ctr.get("name", cid),
            "source": source,
            "targets": targets,
            "priority": ctr.get("priority", "?"),
            "field_count": len(ctr.get("fields", [])),
        }
    return matrix


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="契约变更影响分析器")
    parser.add_argument("contract_id", nargs="?", help="契约 ID（如 CTR-001）")
    parser.add_argument("--field", type=str, help="分析特定字段的影响范围")
    parser.add_argument("--all", action="store_true", help="输出全局影响矩阵")
    parser.add_argument("--markdown", action="store_true", help="Markdown 格式输出")
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    data = load_contracts()
    if args.all:
        matrix = build_impact_matrix(data)
        if args.markdown:
            print("| 契约 | 优先级 | 来源层 | 目标层 | 字段数 |")
            print("|------|--------|--------|--------|--------|")
            for cid, info in sorted(matrix.items()):
                targets_str = ", ".join(info["targets"][:3])
                if len(info["targets"]) > 3:
                    targets_str += "..."
                print(f"| {cid} | {info['priority']} | {info['source']} | {targets_str} | {info['field_count']} |")
        else:
            for cid, info in sorted(matrix.items()):
                print(f"\n{cid} [{info['priority']}] {info['name']}")
                print(f"  来源层: {info['source']}")
                print(f"  目标层: {info['targets']}")
                print(f"  字段数: {info['field_count']}")
        return
    if not args.contract_id:
        parser.print_help()
        sys.exit(EXIT_FINDINGS)
    contract = find_contract(data, args.contract_id)
    if contract is None:
        print(f"[Impact] 契约 {args.contract_id} 未找到")
        sys.exit(EXIT_FINDINGS)
    print(f"\n契约: {args.contract_id} — {contract.get('name', '')}")
    print(f"优先级: {contract.get('priority', '?')}")
    print(f"来源层: {contract.get('source_layer', '?')}")
    print(f"目标层: {contract.get('target_layers', [])}")
    if args.field:
        print(f"\n分析字段 '{args.field}' 的影响范围:")
        consumers = find_field_consumers(data, args.contract_id, args.field)
        if consumers:
            for c in consumers:
                print(f"  - {c}")
        else:
            print("  (未找到直接引用该字段的代码——可能尚未实现)")
    else:
        print(f"\n所有可能受影响的消费者 ({len(contract.get('target_layers', []))} 层):")
        for layer in contract.get("target_layers", []):
            print(f"  - {layer}")
        consumers = find_consumers_in_source(data, args.contract_id)
        if consumers:
            print(f"\n源代码中引用该契约类型的文件 ({len(consumers)} 个):")
            for c in consumers:
                print(f"  - {c}")
    print("\n建议操作:")
    print("  1. 更新 cross_layer_contracts.yaml 并 bump schema_version")
    print("  2. 运行 python scripts/context/generate_architecture_context.py 重新生成上下文包")
    print("  3. 运行 pytest tests/architecture/ 确认架构适应度函数仍然通过")
    print("  4. 运行 python -m pytest tests/test_enforcer.py 确认 enforcer 测试通过")


if __name__ == "__main__":
    main()
