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
from _shared.file_utils import (
    atomic_write_if_changed,  # noqa: E402  AI-20 幂等化接线补漏 import（AI-00 总控 merge 复检修复，F821 UNDEFINED-NAME 门禁命中）
)

REPO_ROOT = Path(__file__).resolve().parents[3]
RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"
OUTPUT_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule_ai_perception_index.yaml"
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
    # P0②（AI-20 2026-09-05）：幂等写——内容未变跳写（时间戳行不参与比对），
    # 消除 generated_at 每波 reconciler churn（原 OUTPUT_PATH.write_text 无条件落盘）。
    atomic_write_if_changed(OUTPUT_PATH, content, volatile_line_pattern=r"^generated_at: .*$")
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


# ============================================================================
# 规则纵向地图（图17）派生视图 —— 内收扩展（2026-10-14 规则地图战役）
# 真源：rules/trae_*.yaml（规则本体）+ 环节裁定（战役文档 + ruling 登记）
# 产物：docs/library/rule_map.md（人读总图）+ catalogs/rule_stage_routing.yaml（机读路由，供钩子/检索）
# ============================================================================

RULE_MAP_PATH = REPO_ROOT / "docs" / "library" / "rule_map.md"
ROUTING_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule_stage_routing.yaml"

# 环节裁定表（主环节；一岗多流程另记 DUAL）
STAGE_RULES: dict[str, list[int]] = {
    "S0": [24, 25, 26, 27, 41, 42, 43, 44, 60, 81],
    "S1": [2, 3, 34, 35, 56, 65, 77, 87],
    "S2": [
        4,
        5,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        28,
        29,
        30,
        32,
        33,
        36,
        37,
        38,
        46,
        47,
        52,
        54,
        55,
        58,
        61,
        80,
        82,
        83,
        86,
    ],
    "S3": [64, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 84, 85],
    "S4": [45, 50, 59, 62, 63],
    "S5": [],
    "S6": [51],
    "S7": [48, 49, 53],
    "X": [1, 6, 7, 8, 9, 18, 19, 20, 21, 22, 23, 31, 39, 40, 57],
}
DUAL: dict[int, list[str]] = {
    50: ["S4", "S5"],
    51: ["S6", "S4"],
    1: ["X", "S2", "S3"],
    62: ["S4", "X"],
    65: ["S1", "X"],
    77: ["S1", "X"],
    87: ["S1", "S0"],
}
STAGE_META: dict[str, dict] = {
    "S0": dict(
        name="治理与裁定",
        desc="宪法/元规则/裁定/对齐/审计——管所有环节怎么判、怎么留痕",
        sop=["sop/governance_sop/", "sop/review_sop/"],
        pol=["workspace_governance_policy.md"],
        case=["ruling_registry.yaml（裁定册）", "casebook_registry.yaml（案例册）", "alignment_checklist.md"],
        inter="—",
        when="开裁定/审计战役前；口径争执时；判定某条规则该留该改该退役时",
    ),
    "S1": dict(
        name="开工前置",
        desc="动手之前：能力反查、任务卡、预注册、新建登记——把规则前置到开工前",
        sop=["sop/library_sop/"],
        pol=[],
        case=["creation_token 账本", "module_translation_registry.yaml"],
        inter="—",
        when="写第一行业务代码前；新建文件/模块前；领任务卡时",
    ),
    "S2": dict(
        name="施工建造",
        desc="写第一行业务代码到模块成型：架构/命名/测试/文档/模块登记/前端",
        sop=["sop/construction_sop/"],
        pol=["c3_translation_pipeline_ruling.md"],
        case=["defect_pattern_checklist.md（缺陷模式册）", "fms_deadref_baseline.yaml"],
        inter="图14 施工流（map_build/fig14_construction/）",
        when="新模块施工前；前端拆件前；文档定稿前",
    ),
    "S3": dict(
        name="提交落地",
        desc="拿锁→验货→暂存→commit→入队→真落盘→死信归因——最痛环节的规矩集中地",
        sop=["sop/ops_sop/", "sop/governance_sop/commit_navigation_playbook.md"],
        pol=["branch_strategy_policy.md", "parallel_session_coordination_policy.md"],
        case=["death_cases_registry.yaml（死信册）", "landing_journey_registry.yaml"],
        inter="图11 提交链（map_build/fig11_delivery/）",
        when="提交前；冲突/死信/接管时；清理 worktree 前",
    ),
    "S4": dict(
        name="数据供给",
        desc="数据回灌/修复/判重/口径/PIT/SSOT——业务与挖矿之上的数据地基",
        sop=["sop/data_ops_sop/", "sop/data_audit_sop/"],
        pol=["graph_quality_standard.md", "expectation_consumption_design_policy.md"],
        case=["回填台账（daily_valuation/stock_basic）"],
        inter="图12 数据链",
        when="数据回灌/坏数据修复/表结构变更/判重/缺口处置前",
    ),
    "S5": dict(
        name="挖矿研究",
        desc="找方案/建策略/因子指标挖掘/骨架构建——无专属规则，SOP 驱动环节",
        sop=["sop/mining_sop/"],
        pol=[],
        case=["experiment_registry.yaml"],
        inter="—",
        when="全网调研/找方案/建策略前；新域开工挖骨架前",
    ),
    "S6": dict(
        name="业务决策",
        desc="回测体系/策略入库/TDM 地图/考试政策——业务侧怎么验证和出手",
        sop=["sop/backtest_system_sop/", "sop/trading_decision_map_sop/"],
        pol=["strategy_intake_acceptance6_evidence.md"],
        case=["backtest_backlog.yaml（预注册 backlog）", "trial_ledger_registry.yaml（试次册）"],
        inter="TDM 地图（docs/02_enterprise_architecture/10_trading_map/）",
        when="回测施工/策略入库/E4 正考前；改判据/建蓝图锚前",
    ),
    "S7": dict(
        name="运维自动化",
        desc="应急/冲突/清理/班底值守/会话活性——系统活着时的日常运维规矩",
        sop=["sop/ops_sop/", "sop/automation_sop/"],
        pol=[],
        case=["takeover_ledger.jsonl（接管台账）", "process_reaper_keep.txt"],
        inter="图13 日周期（map_build/fig13_daycycle/）",
        when="系统应急时；排班/插单前；清理前",
    ),
    "X": dict(
        name="横切轴",
        desc="全域生效的规则（文件锁/反幻觉/行为禁令/密钥/AI 线）——钉在每一段上",
        sop=[],
        pol=[],
        case=["ruling_registry.yaml", "casebook_registry.yaml"],
        inter="—",
        when="任何环节都生效：写文件/调 LLM/碰密钥/输出结论时",
    ),
}
PURPOSE_TAGS = [
    ("T1", "新东西上户口", "新建的东西必须登记姓名籍贯，否则门禁见一次拦一次"),
    ("T2", "施工队还活着吗", "证明施工队没死，死了别让它继续代表你说话"),
    ("T3", "规则谁在执行", "每条规则都要说得清谁在替它出手，否则就是纸上法律"),
    ("T4", "坏了谁发现", "每个环节都挂着一本病历本，环节病了翻得到档案"),
    ("T5", "一个东西只有一个真源", "同一事实只许一个家，其他副本都是快照"),
    ("T6", "AI 不吹牛", "AI 说的每句话都要能回到真源，不能靠记忆拍脑袋"),
    ("T7", "钥匙不外泄", "密钥权限走专道，裸拿硬编码都是开门揖盗"),
    ("T8", "Owner 看得懂", "非开发的人一遍能读懂这资产干嘛的、何时用它"),
    ("T9", "改坏能回来", "任何动作都要留得下回头路，删之前先想好怎么活过来"),
    ("T10", "累犯必须机械化", "同一个错犯第三次，就该把它变成机器判据而不是又写一遍提示词"),
]


def _gate_ids_on_disk() -> set[str]:
    """读门禁总册的 gate_id 全集（用于悬空指针判定）。"""
    p = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "gate_registry.yaml"
    if not p.is_file():
        return set()
    return {
        ln.split(":", 1)[1].strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.startswith("- gate_id:")
    }


def _sop_files(dirs: list[str]) -> list[tuple[str, str]]:
    out = []
    base = REPO_ROOT / "docs" / "01_policies_and_standards"
    for d in dirs:
        p = base / d
        if p.is_dir():
            for f in sorted(p.rglob("*.md")):
                rel = f.relative_to(base).as_posix()
                title = ""
                for ln in f.read_text(encoding="utf-8", errors="ignore").splitlines()[:40]:
                    if ln.startswith("title:"):
                        title = ln.split(":", 1)[1].strip().strip('"').strip("'")
                        break
                out.append((rel, title or f.stem))
        elif p.is_file():
            out.append((d, p.stem))
    return out


def _build_rule_map(entries: list[dict]) -> tuple[str, str]:
    """生成规则地图页 + 机读路由 yaml，返回 (md, yaml)。"""
    by_id = {e["rule_id"]: e for e in entries}
    gates = _gate_ids_on_disk()
    order = ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "X"]

    def ids(st: str) -> list[str]:
        return [f"TRAE-{n:03d}" for n in STAGE_RULES[st]]

    def dual_in(st: str) -> list[str]:
        return sorted({f"TRAE-{k:03d}" for k, v in DUAL.items() if st in v} - set(ids(st)))

    md = [
        "---",
        "doc_type: index",
        "ttl: permanent",
        "generated_by: scripts/governance/generators/generate_rule_ai_perception_index.py",
        "title: 规则地图（图17·治理域纵向地图）",
        "---",
        "",
        "# 规则地图（图17 · 治理域纵向地图）",
        "",
        "> **派生视图（机生禁手改）**：真源=`docs/01_policies_and_standards/rules/trae_*.yaml`（规则本体）+ 环节裁定；",
        "> 重扫：`python scripts/governance/generators/generate_rule_ai_perception_index.py`（同时产出机读路由册 `catalogs/rule_stage_routing.yaml`）。",
        "> **用法**：先判「我现在在哪个环节」→ 进该环节读规则包+SOP 包 → 再动手。主题检索：`python -m zephyr.library.lookup <关键词>`。",
        "> **与流程地图的关系（指针互链，不合并）**：本图答「每个环节守什么规矩」；图11 提交链答「链哪里卡」、图14 施工流答「怎么建」、图12 数据链答「数据怎么供」、TDM 答「买什么」。",
        "",
        "## §0 环节速查（纵轴）",
        "",
        "| 环节 | 名称 | 归属规则 | 一岗多流程指针 | 何时必读 |",
        "|---|---|---|---|---|",
    ]
    for st in order:
        m = STAGE_META[st]
        md.append("| %s | %s | %d | %d | %s |" % (st, m["name"], len(ids(st)), len(dual_in(st)), m["when"]))
    md += [
        "",
        "## §1 横切目的标签（T1-T10，待 Owner 终审冻结）",
        "",
        "> 同标签多钉 = 重复簇显形位（内收对审入口）。",
        "",
        "| 标签 | 大白话 |",
        "|---|---|",
    ]
    md += ["| %s | %s |" % (t[0], t[2]) for t in PURPOSE_TAGS]

    for st in order:
        m = STAGE_META[st]
        md += [
            "",
            "---",
            "",
            "## %s · %s" % (st, m["name"]),
            "",
            "> %s" % m["desc"],
            "",
            "- **何时必读**：%s" % m["when"],
            "- **互链地图**：%s" % m["inter"],
            "",
        ]
        rows = [r for r in (by_id.get(i) for i in ids(st)) if r]
        if rows:
            md += [
                "### 规则包（%d 条）" % len(rows),
                "",
                "| rule_id | title | scope | stability | severity | 关联门禁 |",
                "|---|---|---|---|---|---|",
            ]
            for r in rows:
                gs = r.get("gate_ids") or []
                flag = "、".join(g + ("" if g in gates else "⚠️悬空") for g in gs) or "—"
                md.append(
                    "| %s | %s | %s | %s | %s | %s |"
                    % (
                        r["rule_id"],
                        r.get("title", ""),
                        r.get("scope", ""),
                        r.get("stability", ""),
                        r.get("severity", ""),
                        flag,
                    )
                )
        if dual_in(st):
            md += ["", "**一岗多流程指针**（他环节主挂，此处只存指针）：%s" % "、".join(dual_in(st))]
        sops = _sop_files(m["sop"])
        if sops:
            md += ["", "### SOP 包（%d 件）" % len(sops), ""]
            md += ["- `%s` — %s" % (a, b) for a, b in sops]
        if m["pol"]:
            md += ["", "### 政策", ""] + ["- `policies/%s`" % p for p in m["pol"]]
        if m["case"]:
            md += ["", "### 病历/台账挂载", ""] + ["- %s" % c for c in m["case"]]

    md += [
        "",
        "---",
        "",
        "## §9 覆盖账本（机生）",
        "",
        "- 规则总数 %d：归属 %d 条，未归属 %d 条"
        % (len(entries), sum(len(ids(s)) for s in order), len(entries) - sum(len(ids(s)) for s in order)),
        "- 门禁总册 %d 台" % len(gates),
        "- 重扫命令：`python scripts/governance/generators/generate_rule_ai_perception_index.py --check`",
        "",
    ]
    md_txt = "\n".join(md)

    # —— 机读路由册（供钩子/检索消费）——
    rt = {
        "schema_version": "1.0.0",
        "module_id": "PS-REG-RULEMAP",
        "ttl": "permanent",
        "doc_type": "register",
        "title": "规则环节路由表（规则地图图17 机读面）",
        "total_rules": len(entries),
        "stages": {},
    }
    for st in order:
        rt["stages"][st] = {
            "name": STAGE_META[st]["name"],
            "when_to_read": STAGE_META[st]["when"],
            "rules": ids(st),
            "dual_pointers": dual_in(st),
            "sop": [a for a, _ in _sop_files(STAGE_META[st]["sop"])],
            "policies": STAGE_META[st]["pol"],
            "casebooks": STAGE_META[st]["case"],
            "intermap": STAGE_META[st]["inter"],
        }
    rt["purpose_tags"] = [{"tag": t[0], "label": t[1], "plain_zh": t[2]} for t in PURPOSE_TAGS]
    return md_txt, rt


def write_rule_map() -> tuple[Path, Path]:
    """生成并写入规则地图页 + 机读路由册。"""
    entries = _load_all_rules()
    md_txt, rt = _build_rule_map(entries)
    for p in (RULE_MAP_PATH, ROUTING_PATH):
        p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_if_changed(RULE_MAP_PATH, md_txt)
    import yaml as _y

    ytxt = _y.safe_dump(rt, allow_unicode=True, sort_keys=False, default_flow_style=False)
    atomic_write_if_changed(ROUTING_PATH, ytxt)
    return RULE_MAP_PATH, ROUTING_PATH


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="规则AI感知索引生成器")
    parser.add_argument("--check", action="store_true", help="漂移检测模式")
    args = parser.parse_args()
    if args.check:
        return check()
    out = write()
    mp, rp = write_rule_map()
    print(f"Generated: {mp.relative_to(REPO_ROOT)}")
    print(f"Generated: {rp.relative_to(REPO_ROOT)}")
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
