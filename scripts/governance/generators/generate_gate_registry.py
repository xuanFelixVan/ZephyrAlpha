# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_gate_registry.py | §
# [MODULE] scripts.governance.generators.generate_gate_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/generators/test_generate_gate_registry.py
# [TTL] permanent
"""
generate_gate_registry.py — 门禁登记表自动生成器

从 .pre-commit-config.yaml 自动派生 gate_registry.yaml。
对标 §6.16 静态清单自动生成铁律——手工维护的 gate-registry 将被此脚本替代。

Usage:
    python scripts/governance/generators/generate_gate_registry.py
    python scripts/governance/generators/generate_gate_registry.py --check
    python scripts/governance/generators/generate_gate_registry.py --output path/to/output.yaml
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 10
args:
  - {flag: --check, type: bool, description: "仅检测漂移，不写文件"}
  - {flag: --output, type: str, description: "输出路径"}
warn_only: false
description: >
  从 .pre-commit-config.yaml 自动派生 gate_registry.yaml。
  对标 §6.16 静态清单自动生成铁律。
"""

PRE_COMMIT_PATH = REPO_ROOT / ".pre-commit-config.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "gate_registry.yaml"

CATEGORY_MAP = {
    "01": "architecture_reachability",
    "02": "contract_integrity",
    "03": "invariant_governance",
    "06": "adr_status",
    "07": "event_routing",
    "11": "naming_convention",
    "12": "blueprint_truth_source",
    "13": "blueprint_overlap",
    "14": "ai_autonomy",
    "15": "frontmatter_metadata",
    "16": "architecture_compliance",
    "17": "orphan_detection",
    "18": "test_collection",
    "19": "static_manifest_drift",
    "22": "load_path_integrity",
    "ZR": "zero_residue",
    "SSOT": "ssot_guard",
    "BP-PLACE": "blueprint_placement",
    "SQ": "script_quality",
    "ADM": "manifest_admission",
    "IDX": "index_sync",
    "DD07": "dedup_gate",
    "C1": "ssot_status",
    "C2": "contract_drift",
}


# CommitGate 治本（2026-07-17）：CommitGates 在 GitCommitGateway 的 CommitGateRegistry
# 运行时注册（GateSpec 闭包），原生成器只读 .pre-commit-config.yaml 漏掉全部 ~50 个
# CommitGates。本函数复用 commit_gates/*.py 中已声明的 GateSpec(gate_id=, priority=)
# + 模块 docstring 提取元数据，不引入新真源（向内收）。
COMMIT_GATES_DIR = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "commit_gates"

# GateSpec(gate_id="XXX", priority=NN) 声明提取
# 每个 gate 文件含 3 处 gate_id="..." 匹配（[MODIFY-GUARD] 头部 + docstring + GateSpec 构造器），
# .search() 取首个——已验证 [MODIFY-GUARD] gate_id 与 GateSpec gate_id 一致（抽样验证
# PURE-ASSERTION/PURE-SHIM/CREATE-GUARD 均一致）。
_RE_GATE_ID = re.compile(r'gate_id\s*=\s*"([^"]+)"')
_RE_PRIORITY = re.compile(r'priority\s*=\s*(\d+)')
# 模块 docstring 第一行格式："""xxx.py — 描述..."""
_RE_DOCSTRING_FIRST_LINE = re.compile(r'^"""[^\n]*?—\s*(.+?)$', re.MULTILINE)


def extract_commit_gates() -> list[dict]:
    """扫描 commit_gates/*.py，从 GateSpec 声明 + docstring 提取 CommitGate 元数据。

    复用已存在的 gate_id/priority 声明（[MODIFY-GUARD] 头部 + GateSpec 构造器），
    不引入新真源。无 GateSpec 的辅助模块（gate_repo.py 等）自动跳过。

    Returns:
        CommitGate 条目列表，每条含 gate_id/name/entry/description/files_trigger/
        always_run/category/status/source 字段。
    """
    gates: list[dict] = []
    if not COMMIT_GATES_DIR.is_dir():
        return gates
    for py in sorted(COMMIT_GATES_DIR.glob("*.py")):
        if py.name in ("__init__.py", "_diff_helpers.py"):
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        m_id = _RE_GATE_ID.search(text)
        if not m_id:
            continue  # 辅助模块（如 gate_repo.py）无 GateSpec，跳过
        gate_id = m_id.group(1)
        m_pri = _RE_PRIORITY.search(text)
        priority = int(m_pri.group(1)) if m_pri else 100
        m_doc = _RE_DOCSTRING_FIRST_LINE.search(text)
        desc = m_doc.group(1).strip() if m_doc else gate_id
        gates.append(
            {
                "gate_id": gate_id,
                "name": f"{gate_id}: {desc}（CommitGate, priority={priority}）",
                "entry": "in-process (GitCommitGateway)",
                "description": desc,
                # CommitGates 触发逻辑在闭包内（如 _get_staged_md_files 只检 .md），
                # 无法从文本可靠提取；description 列含文件类型描述信息供 AI 参考。
                "files_trigger": "",
                "always_run": False,
                "category": "commit_gate",
                "status": "active",
                "source": "commit-gate",
            }
        )
    return gates


# 已合并/退役门禁的手动覆盖条目（ARCH-018 治本，2026-07-04）
# 这些条目不再作为活跃 hook 存在于 .pre-commit-config.yaml，但需在 registry 中保留
# 供历史引用可追溯。生成器每次运行时将这些条目 merge 到自动生成的 gates 列表末尾。
# 新增已合并门禁时在此追加条目即可，无需改 generate() 逻辑。
MANUAL_GATES: list[dict] = [
    {
        "gate_id": "GATE-SCHEMA-HEALTH",
        "name": "GATE-SCHEMA-HEALTH: depgraph Schema 健康度门禁（已合并到 GATE-C2，ARCH-016/017/018）",
        "entry": "N/A (merged into GATE-C2, see redirect_to)",
        "description": "【已合并/重定向】原独立 gate-schema-health 已于 ARCH-017 治本时合并到 GATE-C2 "
        "run_gate_chain（与 check_contract_code_drift + check_contract_physical_path 顺序执行）。"
        "本条目为重定向锚点，保留 gate_id 供历史引用可追溯。实际执行入口见 GATE-C2。"
        "检测真源：scripts/governance/d11_compliance/verify_schema_health.py"
        "（4 校验：DDL 列一致性/只读触发器/Schema 版本/PG 运行时健康）。"
        "capability：schema_health_verification。"
        "注：status=deprecated 因 DB CHECK 约束仅允许 active/deprecated/disabled"
        "（depgraph_schema.py _DDL_GATES），语义对标'已合并退役'。",
        "files_trigger": "",
        "always_run": False,
        "category": "schema_health",
        "status": "deprecated",
        "redirect_to": "GATE-C2",
    },
]


def extract_gates(config: dict) -> list[dict]:
    """extract_gates implementation."""
    gates = []
    local_hooks = config.get("repos", [])
    for repo in local_hooks:
        if repo.get("repo") != "local":
            continue
        for hook in repo.get("hooks", []):
            hook_name = hook.get("name", "")

            gate_match = re.match(r"GATE-([A-Z0-9]+(?:-[A-Z0-9]+)*)(?::|$)", hook_name)
            if gate_match:
                gate_suffix = gate_match.group(1)
            else:
                hook_id = hook.get("id", "")
                id_match = re.match(r"gate-(\d+)", hook_id)
                if not id_match:
                    continue
                gate_suffix = id_match.group(1)

            gates.append(
                {
                    "gate_id": f"GATE-{gate_suffix}",
                    "name": hook_name,
                    "entry": hook.get("entry", ""),
                    "description": hook.get("description", ""),
                    "files_trigger": hook.get("files", ""),
                    "always_run": hook.get("always_run", False),
                    "category": CATEGORY_MAP.get(gate_suffix, "unknown"),
                    "status": "active",
                }
            )
    return gates


def generate(entry_count: int | None = None) -> dict:
    """generate implementation."""
    pcc = load_yaml(PRE_COMMIT_PATH)
    gates = extract_gates(pcc)
    for g in gates:
        g["source"] = "pre-commit"
    # CommitGate 治本（2026-07-17）：合并 CommitGates（~50 个 in-process gate）
    # 源=src/zephyr/gov_enforcement/commit_gates/*.py 的 GateSpec 声明
    gates.extend(extract_commit_gates())
    # ARCH-018 治本：merge 手动覆盖条目（已合并/退役门禁的重定向锚点）
    # 避免生成器覆盖手动添加的 GATE-SCHEMA-HEALTH 等重定向条目
    auto_ids = {g["gate_id"] for g in gates}
    for mg in MANUAL_GATES:
        if mg["gate_id"] not in auto_ids:
            mg["source"] = "manual"
            gates.append(mg)
    if entry_count is not None:
        for g in gates:
            g["entry_count"] = entry_count
    return {
        "module_id": "PS-REG-014",
        "doc_type": "register",
        "ttl": "permanent",
        "title": "GATE 门禁登记表",
        "status": "active",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/governance/generators/generate_gate_registry.py",
        # maintenance 字段治本（2026-06-29）：声明 auto 让 generate_registry_master_index.py
        # 正确标记本表为自动维护——原缺省填 manual 是标记滞后根因（catalogs/index.md L47 误标 manual）
        "maintenance": "auto",
        # CommitGate 治本（2026-07-17）：三源合并（pre-commit hooks + CommitGates + MANUAL_GATES）
        "source": ".pre-commit-config.yaml + commit_gates/*.py + MANUAL_GATES",
        "total_gates": len(gates),
        "gates": gates,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="自动生成 gate_registry.yaml")
    parser.add_argument("--check", action="store_true", help="仅检测漂移，不写文件")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="输出路径")
    args = parser.parse_args()

    output = generate()

    if args.check:
        existing = load_yaml(args.output)
        if existing.get("total_gates") != output["total_gates"]:
            print(f"DRIFT: 磁盘 {existing.get('total_gates', 0)} 门禁 ≠ 生成 {output['total_gates']} 门禁")
            sys.exit(EXIT_FINDINGS)
        print("OK: 门禁登记表与三源（.pre-commit-config.yaml + commit_gates/ + MANUAL_GATES）一致")
        return

    # .md 文件用 --- frontmatter 格式（GATE-15 要求 .md 必须有 frontmatter）
    # .yaml 文件用纯 YAML（yaml.load 直接加载）
    if args.output.endswith(".md"):
        content = "---\n" + yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False) + "---\n"
    else:
        content = yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False)
    atomic_write_safe(args.output, content)
    print(f"已生成 {output['total_gates']} 条门禁 → {args.output}")


if __name__ == "__main__":
    main()
