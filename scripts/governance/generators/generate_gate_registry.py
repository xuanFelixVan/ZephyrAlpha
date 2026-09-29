# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_gate_registry.py | §
# [MODULE] scripts.governance.generators.generate_gate_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/generators/test_generate_gate_registry.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
generate_gate_registry.py — 门禁登记表自动生成器

从 .pre-commit-config.yaml 自动派生 gate_registry.yaml。
对标 §6.3 静态清单自动生成铁律——手工维护的 gate-registry 将被此脚本替代。

治本（ARCH-GATE-REGISTRY-SYNC-001）：post-commit 由 make_gate_registry_sync_reconciler
（priority=830）自动触发重生成——commit commit_gates/*.py / .pre-commit-config.yaml /
本生成器自身后，reconciler 自动跑本脚本重生成 gate_registry.yaml + auto_commit。

Usage:
    python scripts/governance/generators/generate_gate_registry.py
    python scripts/governance/generators/generate_gate_registry.py --check
    python scripts/governance/generators/generate_gate_registry.py --output path/to/output.yaml
    python scripts/governance/generators/generate_gate_registry.py --diff
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import (
    atomic_write_if_changed,  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT；P0② 幂等写（AI-20 2026-09-05）
)
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 10
args:
  - {flag: --check, type: bool, description: "仅检测漂移，不写文件"}
  - {flag: --diff, type: bool, description: "三账对账（F98 G1），纯只读，差集即红"}
  - {flag: --output, type: str, description: "输出路径"}
warn_only: false
description: >
  从 .pre-commit-config.yaml 自动派生 gate_registry.yaml。
  对标 §6.3 静态清单自动生成铁律。
"""

PRE_COMMIT_PATH = REPO_ROOT / ".pre-commit-config.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "gate_registry.yaml"
# 三账对账第二账（F98 G1 / M3 03 G1 治本 2026-09-27）：in_process 册路径提为模块常量，
# 供 _roster_triggers 与 three_account_diff 共用（消除内联重复构造，行为不变）。
IN_PROCESS_REGISTRY_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "in_process_gate_registry.yaml"
)

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
_RE_PRIORITY = re.compile(r"priority\s*=\s*(\d+)")
# 模块 docstring 第一行格式："""xxx.py — 描述..."""
_RE_DOCSTRING_FIRST_LINE = re.compile(r'^"""[^\n]*?—\s*(.+?)$', re.MULTILINE)


def _roster_triggers() -> dict:
    """in_process 名册的 files_trigger 字段（P5 条件触发真源），供统一册贯通。"""
    roster_path = IN_PROCESS_REGISTRY_PATH
    try:
        import yaml as _yaml  # noqa: PLC0415

        data = _yaml.safe_load(roster_path.read_text(encoding="utf-8"))
        return {g.get("gate_id"): g.get("files_trigger") for g in data.get("gates", []) if g.get("files_trigger")}
    except Exception:  # noqa: BLE001 — 名册不可得时统一册退回空触发面
        return {}


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
    seen_gate_ids: set[str] = set()
    # 递归扫描（st-gslim-20260923 P1 事故级漂移修复）：library/ 子目录三台
    # （BLOOD-FLESH/TAG-VOCAB/STATE-VOCAB-REGISTRY）与 registry_family/ 迁移件
    # 曾因 glob 非递归整批漏登统一册（117 vs 114 漂移，gate_audit_report_v1 §A1）。
    # seen_gate_ids 防迁移过渡态双拷贝（旧路径未删+新路径已在）产生重复条目。
    for py in sorted(COMMIT_GATES_DIR.rglob("*.py")):
        if py.name in ("__init__.py", "_diff_helpers.py"):
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        m_id = _RE_GATE_ID.search(text)
        if not m_id:
            continue  # 辅助模块（如 gate_repo.py）无 GateSpec，跳过
        gate_id = m_id.group(1)
        if gate_id in seen_gate_ids:
            continue
        seen_gate_ids.add(gate_id)
        _trigger_map = globals().setdefault("_TRIGGER_MAP", None)
        if _trigger_map is None:
            globals()["_TRIGGER_MAP"] = _trigger_map = _roster_triggers()
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
                # own-scope 派生标记（#ARCH-310 R2 落地，2026-09-12）：gate 模块源码
                # import _build_own_scope 即为 own-diff 作用域（外来 staged 降级审计）；
                # 未标记者默认全暂存区扫描（全仓例外须按 R2 登记理由）。
                "own_scope": "_build_own_scope" in text,
            }
        )
        # P5 条件触发贯通（st-gslim-20260923）：统一册 files_trigger 拉通自 in_process 名册
        gates[-1]["files_trigger"] = globals().setdefault("_TRIGGER_MAP", {}).get(gate_id, "")
    return gates


# 已合并/退役门禁的手动覆盖条目（ARCH-018 治本，2026-07-04）
# 这些条目不再作为活跃 hook 存在于 .pre-commit-config.yaml，但需在 registry 中保留
# 供历史引用可追溯。生成器每次运行时将这些条目 merge 到自动生成的 gates 列表末尾。
# 新增已合并门禁时在此追加条目即可，无需改 generate() 逻辑。
MANUAL_GATES: list[dict] = [
    {
        "gate_id": "ARCH-REFERENCE",
        "name": "ARCH-REFERENCE: #ARCH-NNN 悬空引用检测（已合并至 REFERENCE-INTEGRITY，st-gslim-20260923 P4）",
        "entry": "N/A (merged into REFERENCE-INTEGRITY, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 REFERENCE-INTEGRITY。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "REFERENCE-INTEGRITY",
    },
    {
        "gate_id": "RULING-REFERENCE",
        "name": "RULING-REFERENCE: 裁定 #NNN 悬空引用检测（已合并至 REFERENCE-INTEGRITY，st-gslim-20260923 P4）",
        "entry": "N/A (merged into REFERENCE-INTEGRITY, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 REFERENCE-INTEGRITY。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "REFERENCE-INTEGRITY",
    },
    {
        "gate_id": "DANGLING-REFERENCE",
        "name": "DANGLING-REFERENCE: AGENTS §X.Y 悬空引用检测（已合并至 REFERENCE-INTEGRITY，st-gslim-20260923 P4）",
        "entry": "N/A (merged into REFERENCE-INTEGRITY, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 REFERENCE-INTEGRITY。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "REFERENCE-INTEGRITY",
    },
    {
        "gate_id": "MANUAL-ONLY-PERMANENT",
        "name": "MANUAL-ONLY-PERMANENT: 永久系统 manual 无订阅检测（已合并至 PERMANENT-SYSTEM-TRIGGER，st-gslim-20260923 P4）",
        "entry": "N/A (merged into PERMANENT-SYSTEM-TRIGGER, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 PERMANENT-SYSTEM-TRIGGER。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "PERMANENT-SYSTEM-TRIGGER",
    },
    {
        "gate_id": "PERM-TRIGGER",
        "name": "PERM-TRIGGER: 时间触发无订阅检测（已合并至 PERMANENT-SYSTEM-TRIGGER，st-gslim-20260923 P4）",
        "entry": "N/A (merged into PERMANENT-SYSTEM-TRIGGER, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 PERMANENT-SYSTEM-TRIGGER。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "PERMANENT-SYSTEM-TRIGGER",
    },
    {
        "gate_id": "VOCAB-HARDCODE",
        "name": "VOCAB-HARDCODE: 新 py 词表硬编码检测（已合并至 GATE-VOCAB，st-gslim-20260923 P4）",
        "entry": "N/A (merged into GATE-VOCAB, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 GATE-VOCAB。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "GATE-VOCAB",
    },
    {
        "gate_id": "VOCAB-CHAIN",
        "name": "VOCAB-CHAIN: SSoT 词表路径硬编码检测（已合并至 GATE-VOCAB，st-gslim-20260923 P4）",
        "entry": "N/A (merged into GATE-VOCAB, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 GATE-VOCAB。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "GATE-VOCAB",
    },
    {
        "gate_id": "DEPGRAPH-PRE-REGISTRATION",
        "name": "DEPGRAPH-PRE-REGISTRATION: depgraph planned→production（已合并至 DEPGRAPH-ENFORCEMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into DEPGRAPH-ENFORCEMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DEPGRAPH-ENFORCEMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DEPGRAPH-ENFORCEMENT",
    },
    {
        "gate_id": "NEW-FILE-DEPGRAPH-ENFORCEMENT",
        "name": "NEW-FILE-DEPGRAPH-ENFORCEMENT: 新 py 未登记 depgraph（已合并至 DEPGRAPH-ENFORCEMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into DEPGRAPH-ENFORCEMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DEPGRAPH-ENFORCEMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DEPGRAPH-ENFORCEMENT",
    },
    {
        "gate_id": "RENAME-DEPGRAPH-SYNC",
        "name": "RENAME-DEPGRAPH-SYNC: 重命名 depgraph 同步（已合并至 DEPGRAPH-ENFORCEMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into DEPGRAPH-ENFORCEMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DEPGRAPH-ENFORCEMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DEPGRAPH-ENFORCEMENT",
    },
    {
        "gate_id": "DEPGRAPH-WRITE-PATH",
        "name": "DEPGRAPH-WRITE-PATH: depgraph 写路径白名单（已合并至 DEPGRAPH-ENFORCEMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into DEPGRAPH-ENFORCEMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DEPGRAPH-ENFORCEMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DEPGRAPH-ENFORCEMENT",
    },
    {
        "gate_id": "GATE-PANORAMA-ALIGNMENT",
        "name": "GATE-PANORAMA-ALIGNMENT: 三图模块对齐（已合并至 MAP-ALIGNMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into MAP-ALIGNMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 MAP-ALIGNMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "MAP-ALIGNMENT",
    },
    {
        "gate_id": "GATE-BATTLE-MAP-ALIGNMENT",
        "name": "GATE-BATTLE-MAP-ALIGNMENT: 作战地图对齐（已合并至 MAP-ALIGNMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into MAP-ALIGNMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 MAP-ALIGNMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "MAP-ALIGNMENT",
    },
    {
        "gate_id": "DECISION-MAP",
        "name": "DECISION-MAP: 决策图对齐（已合并至 MAP-ALIGNMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into MAP-ALIGNMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 MAP-ALIGNMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "MAP-ALIGNMENT",
    },
    {
        "gate_id": "FRONTEND-MAP",
        "name": "FRONTEND-MAP: 前端全景图对齐（已合并至 MAP-ALIGNMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into MAP-ALIGNMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 MAP-ALIGNMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "MAP-ALIGNMENT",
    },
    {
        "gate_id": "INDUSTRY-CHAIN-MAP",
        "name": "INDUSTRY-CHAIN-MAP: 产业链图工件（已合并至 MAP-ALIGNMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into MAP-ALIGNMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 MAP-ALIGNMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "MAP-ALIGNMENT",
    },
    {
        "gate_id": "FACTORY-MAP",
        "name": "FACTORY-MAP: 策略生产图对齐（已合并至 MAP-ALIGNMENT，st-gslim-20260923 P4）",
        "entry": "N/A (merged into MAP-ALIGNMENT, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 MAP-ALIGNMENT。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "MAP-ALIGNMENT",
    },
    {
        "gate_id": "BLUEPRINT-AMODULE-CONSISTENCY",
        "name": "BLUEPRINT-AMODULE-CONSISTENCY: A_module 头格式一致（已合并至 BLUEPRINT-HEADER，st-gslim-20260923 P4）",
        "entry": "N/A (merged into BLUEPRINT-HEADER, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 BLUEPRINT-HEADER。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "BLUEPRINT-HEADER",
    },
    {
        "gate_id": "BLUEPRINT-AMODULE-CROSS-CHECK",
        "name": "BLUEPRINT-AMODULE-CROSS-CHECK: 蓝图↔A_module 交叉校验（已合并至 BLUEPRINT-HEADER，st-gslim-20260923 P4）",
        "entry": "N/A (merged into BLUEPRINT-HEADER, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 BLUEPRINT-HEADER。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "BLUEPRINT-HEADER",
    },
    {
        "gate_id": "NO-GOD-CLASS",
        "name": "NO-GOD-CLASS: God Class 检测（已合并至 COMPLEXITY-GUARD，st-gslim-20260923 P4）",
        "entry": "N/A (merged into COMPLEXITY-GUARD, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 COMPLEXITY-GUARD。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "COMPLEXITY-GUARD",
    },
    {
        "gate_id": "NO-HIGH-COMPLEXITY",
        "name": "NO-HIGH-COMPLEXITY: 高循环复杂度检测（已合并至 COMPLEXITY-GUARD，st-gslim-20260923 P4）",
        "entry": "N/A (merged into COMPLEXITY-GUARD, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 COMPLEXITY-GUARD。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "COMPLEXITY-GUARD",
    },
    {
        "gate_id": "NO-LONG-PARAM-LIST",
        "name": "NO-LONG-PARAM-LIST: 长参数列表检测（已合并至 COMPLEXITY-GUARD，st-gslim-20260923 P4）",
        "entry": "N/A (merged into COMPLEXITY-GUARD, see redirect_to)",
        "description": "【已合并/重定向】P4 七簇合并（gate_audit_report_v1 §C2，Owner 2026-09-23 全批 E）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 COMPLEXITY-GUARD。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "COMPLEXITY-GUARD",
    },
    {
        # 裁定#347/#372：临界区锁机制实名登记（in-process 机制非钩子，生成器三源合并会漏——
        # 不入此清单则全量重跑会删该条，P9c3 附带发现②治本 2026-09-20）
        "gate_id": "COMMIT-CRITICAL-SECTION-LOCK",
        "name": "COMMIT-CRITICAL-SECTION-LOCK: commit 临界区全局文件锁（裁定#347 实名登记）",
        "entry": "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py::_GlobalCommitLock（in-process 机制，非独立钩子）",
        "description": "裁定#347/#372：机制实存于 git_commit_gateway.py:2360-2366（_GlobalCommitLock 临界区+审计兜底）。"
        "fail-closed 语义见 trae_079（逃生仅 emergency_commit）。",
        "files_trigger": "",
        "always_run": False,
        "category": "serialization",
        "status": "active",
        "source": "commit-gateway",
        "enforcement_channel": "in-process",
    },
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
    # st-gslim-20260923 P3 退役墓碑（gate_audit_report_v1 §C1，Owner 2026-09-23 全批 E）：
    # 三台 warn-only 零触发零消费退役（w5_1 条2）。统一册条目无路径字段，REGISTRY-MASS-DELETION
    # W3 机械验证对"条目+路径双消失"之外的删除判 fail-closed——按 GATE-SCHEMA-HEALTH 先例留
    # deprecated 重定向锚点，gate_id 供历史引用可追溯，不再有执行体。
    {
        "gate_id": "DATA-TASK-COMPLETENESS",
        "name": "DATA-TASK-COMPLETENESS: 数据任务完整性门禁（已退役 2026-09-23，st-gslim P3）",
        "entry": "N/A (retired, see redirect_to)",
        "description": "【已退役】warn-only 零触发零消费（窗口期 0 拦截 0 运行触发，src/scripts 外零引用）——"
        "w5_1 条2 退役判据直接命中。门文件+测试+in_process 条目+token 同批删除；tasks.yaml 内三处历史"
        "warn 提示注释为历史事实留档。退役依据：docs/_working/registry_incident_20260922/gate_audit_report_v1.md §C1/§E。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "gate_audit_report_v1.md#C1",
    },
    {
        "gate_id": "ISSUE-RESOLVED-INTEGRITY",
        "name": "ISSUE-RESOLVED-INTEGRITY: issue 标记真实性门禁（已退役 2026-09-23，st-gslim P3）",
        "entry": "N/A (retired, see redirect_to)",
        "description": "【已退役】warn-only；计时数据中从未出现（连执行都没有）；零消费方（0 处引用）——"
        "w5_1 条2 退役判据直接命中。门文件+测试+in_process 条目+token+外锚同批删除。"
        "退役依据：docs/_working/registry_incident_20260922/gate_audit_report_v1.md §C1/§E。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "gate_audit_report_v1.md#C1",
    },
    {
        "gate_id": "LIBRARY-COVERAGE",
        "name": "LIBRARY-COVERAGE: 馆藏覆盖观察闸（已退役 2026-09-23，st-gslim P3）",
        "entry": "N/A (retired, see redirect_to)",
        "description": "【已退役】warn-only 自述观察闸；0 拦截 0 触发；零消费方（0 处引用）——w5_1 条2 退役"
        "判据直接命中。门文件+测试+in_process 条目+token+外锚+fail_open 行同批删除；_has_call_number 纯函数"
        "迁 zephyr.library.ledger_schema（测试改挂 7 passed）。"
        "退役依据：docs/_working/registry_incident_20260922/gate_audit_report_v1.md §C1/§E。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "gate_audit_report_v1.md#C1",
    },
    {
        "gate_id": "BLUEPRINT-FORMAT",
        "name": "BLUEPRINT-FORMAT: [BLUEPRINT] 头部 module_id 格式检测（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
    {
        "gate_id": "BLUEPRINT-HEADER",
        "name": "BLUEPRINT-HEADER: A_module 头声明一致性聚合（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
    {
        "gate_id": "MODULE-ID-CONSISTENCY",
        "name": "MODULE-ID-CONSISTENCY: module_id 三声明轨道一致性（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
    {
        "gate_id": "TTL-METADATA",
        "name": "TTL-METADATA: TTL 元数据硬阻断（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
    {
        "gate_id": "FILE-PLACEMENT-TTL",
        "name": "FILE-PLACEMENT-TTL: 文件放置 TTL 三重校验（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
    {
        "gate_id": "EXEMPT-ZONE-FM",
        "name": "EXEMPT-ZONE-FM: 豁免区 frontmatter doc_type（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
    {
        "gate_id": "DOC-REF-BROKEN",
        "name": "DOC-REF-BROKEN: 文档相对路径断裂引用（已合并至 DOC-HEADER-SUITE，st-commitspeed-pkg8-20260925 T8簇2）",
        "entry": "N/A (merged into DOC-HEADER-SUITE, see redirect_to)",
        "description": "【已合并/重定向】T8 簇2 文档头七台合一（Owner 令：只合并不删门，7 判据零退役）。"
        "本条目为重定向锚点保留 gate_id 供历史引用可追溯，实际执行入口见 DOC-HEADER-SUITE。",
        "files_trigger": "",
        "always_run": False,
        "category": "commit_gate",
        "status": "deprecated",
        "source": "manual",
        "enforcement_channel": "manual",
        "redirect_to": "DOC-HEADER-SUITE",
    },
]


def _locate_entry_script(entry: str) -> Path | None:
    """定位 entry 命令的脚本源文件（scripts/ 或 src/ 下任意 .py 路径 token）。

    T14 own_scope 补全（st-commitspeed-tbl-20260924）辅助：pre-commit hook 的
    entry 形如 ``python scripts/governance/d5_architecture/checkers/check_arch.py``
    或 ``python src/zephyr/.../x.py`` 或 ``python -m zephyr.foo``。内联 ``-c`` /
    pytest 形态返回 None（不可机械判定，留待 Owner）。
    """
    for tok in entry.split():
        if tok.endswith(".py"):
            cand = REPO_ROOT / tok
            return cand if cand.is_file() else None
    m = re.search(r"-m\s+([\w.]+)", entry)
    if m:
        mod = m.group(1).replace(".", "/")
        for cand in (REPO_ROOT / "src" / f"{mod}.py", REPO_ROOT / "src" / mod / "__main__.py"):
            if cand.is_file():
                return cand
    return None


def _derive_own_scope_for_entry(entry: str) -> bool | None:
    """pre-commit 条目 own_scope 机械派生（判据与 commit-gate 通道同源同则）。

    T14 补全（2026-09-24）：#ARCH-310 R2 own-diff 作用域标记完备性——原生成器仅对
    commit_gates/*.py 派生 own_scope，pre-commit(55)/manual(12) 通道整片缺失
    （own_scope=None 67 条）。本函数对 pre-commit 脚本型同则派生：
    可定位源码且含 ``_build_own_scope`` 标记 → True；可定位无标记 → False
    （未标记者默认全暂存区扫描，全仓例外须按 R2 登记理由）；无可定位源文件
    （内联 -c / pytest 形态）→ None（不可机械判定，对账工具 pending_owner 节跟踪，
    改册是 Owner 门位）。manual 源（墓碑/机制实名条目）不经本函数，保持待 Owner。
    """
    script = _locate_entry_script(entry)
    if script is None:
        return None
    try:
        text = script.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return "_build_own_scope" in text


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
                    # T14 own_scope 机械派生（st-commitspeed-tbl-20260924，SW8 代投移植）：
                    # pre-commit 通道原 own_scope 整片缺失（own_scope=None），同则派生。
                    "own_scope": _derive_own_scope_for_entry(hook.get("entry", "")),
                }
            )
    return gates


def _account_gate_id_sets(reg_gates: list[dict], ip_gates: list[dict], pcc: dict) -> tuple[set, set, set, set]:
    """抽取三账 gate_id 集合（拆分自 three_account_diff，控圈复杂度）。

    Returns:
        (reg_active, ip_enabled, ip_disabled, hooks) 四个集合。
    """
    reg_active = {g["gate_id"] for g in reg_gates if g.get("status") == "active" and g.get("gate_id")}
    ip_enabled = {g["gate_id"] for g in ip_gates if g.get("enabled") is True and g.get("gate_id")}
    ip_disabled = {g["gate_id"] for g in ip_gates if g.get("enabled") is not True and g.get("gate_id")}
    hooks = {g["gate_id"] for g in extract_gates(pcc)}
    return reg_active, ip_enabled, ip_disabled, hooks


def _pairwise_account_diffs(reg_set: set, ip_en_set: set, ip_disabled: set, hook_set: set) -> dict:
    """两账差集 + 分类镜头（虚报/悬空/三账交集），全部排序保确定性。"""
    ip_all = ip_en_set | ip_disabled
    return {
        "registry_active_minus_inprocess_enabled": sorted(reg_set - ip_en_set),
        "inprocess_enabled_minus_registry_active": sorted(ip_en_set - reg_set),
        "registry_active_minus_precommit_hooks": sorted(reg_set - hook_set),
        "precommit_hooks_minus_registry_active": sorted(hook_set - reg_set),
        "inprocess_enabled_minus_precommit_hooks": sorted(ip_en_set - hook_set),
        "precommit_hooks_minus_inprocess_enabled": sorted(hook_set - ip_en_set),
        # 分类镜头（对位 F98 缺口清单 G2/G3，供周审计替换动作直接取用）：
        "virtual_claim_active_but_disabled": sorted(reg_set & ip_disabled),
        "dangling_no_mount": sorted(g for g in reg_set if g not in ip_all and g not in hook_set),
        "triple_agreement": sorted(reg_set & ip_en_set & hook_set),
    }


def _total_gates_self_check(reg: dict, ip: dict, reg_gates: list, ip_gates: list) -> dict:
    """两册 total_gates 字段与条目实数自洽检查（F98 卷缺口 G5 对位）。"""
    return {
        "gate_registry": {
            "total_gates_field": reg.get("total_gates"),
            "actual": len(reg_gates),
            "ok": reg.get("total_gates") == len(reg_gates),
        },
        "in_process_registry": {
            "total_gates_field": ip.get("total_gates"),
            "actual": len(ip_gates),
            "ok": ip.get("total_gates") == len(ip_gates),
        },
    }


def three_account_diff(
    registry_path: Path | None = None,
    in_process_path: Path | None = None,
    precommit_path: Path | None = None,
) -> dict:
    """三账对账（F98 缺口 G1 / M3 03 §四 G1 治本，2026-09-27 并入本生成器）。

    三账口径（对位人工周审计动作，净零声明：不新增脚本、不新增门）：
      账1 = gate_registry.yaml 中 status=active 的 gate_id（统一册活跃面）
      账2 = in_process_gate_registry.yaml 中 enabled=true 的 gate_id（运行时注册面）
      账3 = .pre-commit-config.yaml 的 GATE-* hooks（pre-commit 拦截面）

    任一两账差集非空，或任一册 total_gates 字段与条目实数不自洽，即判红（red=True）。
    本函数纯只读；红只代表"存在待审计差异"，修册归名册 owner 域，本工具不代修。

    Args:
        registry_path: 统一册路径（默认仓库真源，测试可注入 tmp_path）。
        in_process_path: in_process 册路径（默认仓库真源）。
        precommit_path: pre-commit 配置路径（默认仓库真源）。

    Returns:
        含 counts/diffs/field_self_check/red 的对账 dict；所有 gate_id 列表排序保证确定性。
    """
    registry_path = registry_path or DEFAULT_OUTPUT
    in_process_path = in_process_path or IN_PROCESS_REGISTRY_PATH
    precommit_path = precommit_path or PRE_COMMIT_PATH

    reg = load_yaml(registry_path)
    ip = load_yaml(in_process_path)
    pcc = load_yaml(precommit_path)

    reg_gates = reg.get("gates", []) or []
    ip_gates = ip.get("gates", []) or []
    reg_set, ip_en_set, ip_disabled, hook_set = _account_gate_id_sets(reg_gates, ip_gates, pcc)

    diffs = _pairwise_account_diffs(reg_set, ip_en_set, ip_disabled, hook_set)
    field_self_check = _total_gates_self_check(reg, ip, reg_gates, ip_gates)
    red = any(v for k, v in diffs.items() if k != "triple_agreement") or not all(
        c["ok"] for c in field_self_check.values()
    )
    return {
        "counts": {
            "registry_active": len(reg_set),
            "in_process_enabled": len(ip_en_set),
            "precommit_hooks": len(hook_set),
        },
        "diffs": diffs,
        "field_self_check": field_self_check,
        "red": red,
    }


def format_three_account_report(diff: dict) -> str:
    """将 three_account_diff 结果渲染为人类可读对账报告（周审计替换动作的输出形态）。"""
    lines = [
        "=== 三账对账（F98 G1 / M3 03）：gate_registry.active ↔ in_process.enabled ↔ pre-commit hooks ===",
        f"账1 gate_registry.active      : {diff['counts']['registry_active']}",
        f"账2 in_process.enabled        : {diff['counts']['in_process_enabled']}",
        f"账3 pre-commit hooks          : {diff['counts']['precommit_hooks']}",
        f"三账交集（三账一致面）        : {len(diff['diffs']['triple_agreement'])}",
        "差集:",
    ]
    label_map = {
        "registry_active_minus_inprocess_enabled": "账1 − 账2",
        "inprocess_enabled_minus_registry_active": "账2 − 账1",
        "registry_active_minus_precommit_hooks": "账1 − 账3",
        "precommit_hooks_minus_registry_active": "账3 − 账1",
        "inprocess_enabled_minus_precommit_hooks": "账2 − 账3",
        "precommit_hooks_minus_inprocess_enabled": "账3 − 账2",
    }
    for key, label in label_map.items():
        items = diff["diffs"][key]
        lines.append(f"  {label}: {len(items)} 项" + (f"  [{', '.join(items)}]" if items else ""))
    lines.append("分类镜头:")
    vc = diff["diffs"]["virtual_claim_active_but_disabled"]
    lines.append(f"  虚报（账1 active 但账2 enabled=false）: {len(vc)} 项" + (f"  [{', '.join(vc)}]" if vc else ""))
    dn = diff["diffs"]["dangling_no_mount"]
    lines.append(f"  悬空（账1 有名但账2/账3 均无挂载）  : {len(dn)} 项" + (f"  [{', '.join(dn)}]" if dn else ""))
    lines.append("字段自洽:")
    for name, c in diff["field_self_check"].items():
        lines.append(
            f"  {name}: total_gates 字段={c['total_gates_field']} 条目实数={c['actual']} -> "
            + ("OK" if c["ok"] else "MISMATCH（红）")
        )
    lines.append(
        "判定: "
        + (
            "RED（差集非空或字段不自洽）——差集清单即审计待办；修册归名册 owner 域"
            if diff["red"]
            else "GREEN（三账一致且字段自洽）"
        )
    )
    return "\n".join(lines)


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
    # 跨源去重（st-gslim-20260923）：家文件 gate_id 与 pre-commit hook 同名时保先到源，
    # 防 GATE-VOCAB 类跨源同名重复条目（三源合并旧口径只查 MANUAL_GATES 撞名）。
    seen: set = set()
    deduped = []
    for g in gates:
        if g["gate_id"] in seen:
            continue
        seen.add(g["gate_id"])
        deduped.append(g)
    gates = deduped
    auto_ids = {g["gate_id"] for g in gates}
    # 墓碑覆盖（st-nightsweep-sw15-20260929，92 册 G-81 尺"声明在册、无人装载"治本）：
    # extract_commit_gates 每文件只取首个 gate_id——薄工厂文件首匹配=自身 id 时（独立薄
    # 工厂文件）旧逻辑跳过墓碑 → 统一册恒为假 active，post-commit 重生成自我复活
    # （实测 15 台悬空：RULING-REFERENCE 等）。改为墓碑优先覆盖扫描条目；唯 id 已回装
    # in_process 名册时让位装载事实（防误墓活门）。
    try:
        loaded_ids = {
            g.get("gate_id") for g in (load_yaml(IN_PROCESS_REGISTRY_PATH).get("gates") or [])
        }
    except Exception:  # noqa: BLE001 — 名册不可得时退回旧口径（只追加不覆盖）
        loaded_ids = set()
    for mg in MANUAL_GATES:
        mg["source"] = "manual"
        if mg["gate_id"] in auto_ids and mg["gate_id"] not in loaded_ids:
            gates = [mg if g["gate_id"] == mg["gate_id"] else g for g in gates]
        elif mg["gate_id"] not in auto_ids:
            gates.append(mg)
    # 裁定#341（2026-09-19 W1-D2）：enforcement_channel 执行通道字段——照 source 现值
    # 机械标注（pre-commit 55 台 / commit-gate 113 台 / manual 1 台），防"守规会话永久
    # 免检"类通道归属误判再生（#341 亲验：in_process 113 与 commit-gate 全等、与
    # pre-commit 交集 0）。
    for g in gates:
        g["enforcement_channel"] = g["source"]
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
    parser.add_argument(
        "--diff",
        action="store_true",
        help="三账对账（F98 G1）：gate_registry.active ↔ in_process.enabled ↔ pre-commit hooks；纯只读，差集即红",
    )
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="输出路径")
    args = parser.parse_args()

    if args.diff:
        # 三账对账段（F98 G1 治本 2026-09-27）：替代人工周审计动作；纯只读不写任何册。
        diff = three_account_diff()
        print(format_three_account_report(diff))
        sys.exit(EXIT_FINDINGS if diff["red"] else EXIT_PASS)

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
    written = atomic_write_if_changed(args.output, content, volatile_line_pattern=r"^generated_at: .*$")
    skip_note = "" if written else "（内容未变，跳写——P0② 幂等）"
    print(f"已生成 {output['total_gates']} 条门禁 → {args.output}{skip_note}")


if __name__ == "__main__":
    main()
