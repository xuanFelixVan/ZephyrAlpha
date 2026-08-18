# [BLUEPRINT] MOD-GOV_ALIGN_BATTLE_MAP | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §8.3
# [MODULE] scripts.governance.align_battle_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.battle_map_reader (BattleMapReader); zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.persistence.dataflowgraph_schema (get_dataflowgraph_pg_connection); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); scripts.governance._shared.module_translation_loader (all_battle_map_step_ids, preload_battle_map_steps, get_module_name_bilingual, preload); scripts.governance._shared.constants (EXIT_*)
# [CONSUMERS] CI自动触发;人工审查作战地图对齐报告
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读PG（零写入）;只读YAML/文件系统（零写入）;输出幂等(相同输入→相同输出);输出到03_governance_reports/battle_map_alignment_report.md
# [MODIFY-GUARD] 修改需通过 battle_map_positioning.md §8.3 任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] battle_map 表不存在→exit 2;findings→exit 1(EXIT_FINDINGS);无 findings→exit 0(EXIT_PASS)
# [TESTS] tests/test_align_battle_map.py (规划中)
# [A_module] module_id=MOD-GOV_ALIGN_BATTLE_MAP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  合法 manual 对齐检测器：CI/人工按需调用，只读检测不做自动修复
# [ARCH-REF] battle_map_positioning.md §七 §八
# 真源说明：本检测器从 battle_map_* 三表（PostgreSQL）读取环节/锚点/流转边，
# 从翻译真源 module_translation_registry.yaml §battle_map_steps 段读取环节叙事，
# 从 depgraph/dataflowgraph/decisiongraph/candidate/blueprint 读取锚点目标合法 id，
# 从 battle_map_domain_policy.yaml 读取 flow_stage → 允许 domain 规则（BM-INV-004），
# 生成作战地图对齐报告（孤儿环节/幽灵锚点/缺失叙事/悬空边/域漂移）。
# 详见 battle_map_positioning.md §8.3 + §7.4（BM-INV-001~004）。
"""G-battle-map-align: 作战地图对齐检测器（battle_map_positioning.md §8.3）

依据：battle_map_positioning.md V0.2.0 §八（与全景图对齐体系的关系）+ §七（双向查找机制）

功能：
  - 从 battle_map_steps / battle_map_anchors / battle_map_edges 读取作战地图三表（DB 真源）
  - 从翻译真源 module_translation_registry.yaml §battle_map_steps 段读取环节叙事
  - 从 depgraph/dataflowgraph/decisiongraph/candidate/blueprint 读取锚点目标合法 id
  - 检测七类问题：
      (1) 孤儿环节（BM-INV-001）：环节无任何锚点 = 悬空决策 = 幻觉风险
      (2) 幽灵锚点（BM-INV-002）：anchor.target_id 在 target_graph 对应图/仓库找不到
      (3) 缺失叙事（BM-INV-003）：DB 环节在翻译真源 battle_map_steps 段无对应叙事
      (4) 悬空边：edge.from_step_id / to_step_id 指向不存在的环节
      (5) 域漂移（BM-INV-004）：anchor.target 的 domain 不在 step.flow_stage 允许列表
      (6) 父子嵌套（BM-INV-006）：父不存在/跨阶段/成环/depth超限
      (7) 孤儿模块（BM-INV-007）：业务域 depgraph 模块无任何锚点指向 = 造出来没用上
  - 输出 MD 报告到 docs/02_enterprise_architecture/03_governance_reports/battle_map_alignment_report.md

定位：只读检测器（君子协定告警，不做自动修复，不硬阻断 commit），由人工或后续工具根据报告处理。
与 align_panoramas.py 正交：align_panoramas 管 module_id 轴（全景模块一致性），
本工具管 step_id 轴（作战环节落地性）。互不干扰。

用法
----
    python scripts/governance/align_battle_map.py
    python scripts/governance/align_battle_map.py --output custom/path.md
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G-battle-map-align: 作战地图对齐检测器（battle_map_positioning.md §8.3）'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 添加项目根到 sys.path
# 本文件在 scripts/governance/，repo root = 含 scripts/ 和 src/ 的目录（marker 法保健壮）
_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = next(p for p in _THIS_FILE.parents if (p / "scripts").is_dir() and (p / "src").is_dir())
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# _shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# _common 在 scripts/governance/d5_architecture/generators，须将其目录加入 sys.path
_GENERATORS_DIR = str(_REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators")
if _GENERATORS_DIR not in sys.path:
    sys.path.insert(0, _GENERATORS_DIR)

from _common import DB_DISPLAY_NAME  # noqa: E402  # noqa: import-integrity  sys.path 动态加载的本地模块
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.module_translation_loader import (  # noqa: E402
    all_battle_map_step_ids,
    derive_name_from_path,
    get_module_name_bilingual,
    preload,
    preload_battle_map_steps,
)  # noqa: E402

from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402

# 日志配置：INFO 级别输出，带时间戳，便于后续监控运行情况（CI/人工触发均可观测）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("align_battle_map")

# 候选池 YAML 真源（target_graph=candidate 的合法 id 来源）
_CANDIDATE_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "candidate_module_registry.yaml"
)

# blueprint 扫描根（target_graph=blueprint 的合法 id 来源）
_BP_SCAN_ROOT = _REPO_ROOT / "docs" / "03_modules"

# 默认报告输出路径（03_governance_reports/ = 自动生成审计报告约定区，同 capacity_report.md）
_DEFAULT_REPORT = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "battle_map_alignment_report.md"
)

# 域漂移检查规则真源（battle_map_positioning.md §8.3 第三项）
# TRAE-062 规则数据真源——YAML 文件，禁止 DB 反向写入
_DOMAIN_POLICY_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "battle_map_domain_policy.yaml"
)

# depgraph SQL 常量（NO-BARE-SQL 集中化，§5.160.2）
SQL_SELECT_DEPGRAPH_VALID_IDS = (
    "SELECT blueprint_id, path FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"
)
SQL_SELECT_DEPGRAPH_DOMAIN_MAP = (
    "SELECT blueprint_id, path, domain_id FROM nodes WHERE domain_id IS NOT NULL AND domain_id <> ''"
)
SQL_SELECT_BUSINESS_MODULES = """
SELECT blueprint_id, path, node_name, domain_id, build_status, node_type
FROM nodes
WHERE domain_id = ANY(%s)
  AND (blueprint_id IS NOT NULL AND blueprint_id <> ''
       OR path IS NOT NULL AND path <> '')
  -- 只扫可执行业务模块（node_type='module'），排除 test/script/config/blueprint 等非业务节点
  -- （2026-08-06 治本：原 SQL 未过滤 node_type，test/config 节点被误报为孤儿模块）
  AND node_type = 'module'
  -- 排除已弃用模块（build_status='deprecated'）——已退役模块不应期望有作战锚点
  -- （2026-08-06 治本：deprecated 模块无作战使命是设计内状态，非遗漏）
  AND build_status <> 'deprecated'
  -- 排除 docs/03_modules/ 下的 blueprint.md 设计文档节点（误报治本，2026-08-04）：
  -- 这些 .md 是模块的"设计蓝图文档"，非可执行业务模块；项目约定它们登记为
  -- node_type=module（与 30+ 其他 blueprint.md 一致），但实际代码模块是 src/ 下的
  -- 独立节点。若不排除，设计文档节点会因无作战锚点而误报为"孤儿模块"。
  -- 例：MOD-INF-011 vector_memory/blueprint.md（D_KNOWLEDGE）、
  --     MOD-INF-039 agent_orchestrator/blueprint.md（D_INFRA_RUNTIME）。
  AND NOT (path LIKE 'docs/03_modules/%%' AND path LIKE '%%.md')
"""


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


def _make_frontmatter(generated_at: str) -> str:
    """生成 YAML frontmatter（03_governance_reports/ 属 permanent zone，
    GATE-TTL-METADATA 要求 audit_report 带 ttl+doc_type，范本对齐 capacity_report.md）。

    :param generated_at: 生成时间字符串（与报告体 generated_at 一致）
    """
    date_str = generated_at.split(" ")[0] if generated_at else datetime.now().strftime("%Y-%m-%d")
    return (
        "---\n"
        "doc_type: audit_report\n"
        "title: 作战地图对齐报告\n"
        'version: "1.0"\n'
        "status: active\n"
        f"date: {date_str}\n"
        "owner: auto-generator\n"
        "ttl: permanent\n"
        "---\n\n"
    )


@dataclass
class BattleMapAlignmentReport:
    """作战地图对齐检测报告。"""

    generated_at: str = ""
    db_name: str = DB_DISPLAY_NAME
    # 三表统计
    step_count: int = 0
    anchor_count: int = 0
    edge_count: int = 0
    narrative_count: int = 0  # 翻译真源已登记环节叙事数
    # 四类问题
    orphan_steps: list[dict] = field(default_factory=list)  # BM-INV-001 孤儿环节
    ghost_anchors: list[dict] = field(default_factory=list)  # BM-INV-002 幽灵锚点
    missing_narratives: list[dict] = field(default_factory=list)  # BM-INV-003 缺失叙事
    dangling_edges: list[dict] = field(default_factory=list)  # 悬空边
    domain_drifts: list[dict] = field(default_factory=list)  # BM-INV-004 域漂移
    parent_child_issues: list[dict] = field(default_factory=list)  # BM-INV-006 父子嵌套
    orphan_modules: list[dict] = field(default_factory=list)  # BM-INV-007 孤儿模块（违规）
    business_module_count: int = 0  # 业务域 depgraph 模块总数（BM-INV-007 扫描范围）
    # V1.1.0 三档分类（治本：补齐二元不变量第三态，消除 100%AI 开发下的治理振荡）
    acknowledged_orphan_steps: list[dict] = field(default_factory=list)  # BM-INV-001 已确认合理孤儿环节
    acknowledged_orphan_modules: list[dict] = field(default_factory=list)  # BM-INV-007 已确认合理孤儿模块
    # 降级告警（目标图源不可用时记录，非对齐问题）
    source_unavailable: list[str] = field(default_factory=list)
    # 裁定原则核心文本（单向派生自 battle_map_domain_policy.yaml §adjudication_principles.core）
    adjudication_principle: str = ""
    # 汇总
    issues_total: int = 0

    def to_markdown(self) -> str:
        """渲染为 Markdown 报告。"""
        lines: list[str] = []
        lines.append("# 作战地图对齐报告 (Battle Map Alignment Report)")
        lines.append("")
        lines.append(f"- 生成时间: {self.generated_at}")
        lines.append(f"- 数据源: {self.db_name}")
        lines.append(
            f"- 三表统计: steps={self.step_count} / "
            f"anchors={self.anchor_count} / edges={self.edge_count} / "
            f"叙事真源={self.narrative_count}"
        )
        lines.append(
            f"- 业务域模块: {self.business_module_count}（BM-INV-007 扫描范围，domain_classification.business_domains 内 node_type=module 的 depgraph 节点）"
        )
        lines.append(f"- 违规总数（须修复）: {self.issues_total}")
        lines.append(f"  - 孤儿环节（BM-INV-001，无锚点=悬空决策）: {len(self.orphan_steps)} 违规")
        lines.append(f"  - 幽灵锚点（BM-INV-002，target_id 找不到）: {len(self.ghost_anchors)}")
        lines.append(f"  - 缺失叙事（BM-INV-003，翻译真源无环节）: {len(self.missing_narratives)}")
        lines.append(f"  - 悬空边（edge 指向不存在环节）: {len(self.dangling_edges)}")
        lines.append(f"  - 域漂移（BM-INV-004，target domain 不在 flow_stage 允许列表）: {len(self.domain_drifts)}")
        lines.append(f"  - 父子嵌套问题（BM-INV-006，父不存在/跨阶段/成环/depth超限）: {len(self.parent_child_issues)}")
        lines.append(f"  - 孤儿模块（BM-INV-007，业务域模块无作战锚点=造出来没用上）: {len(self.orphan_modules)} 违规")
        # V1.1.0 三档分类：已确认合理孤儿（acknowledged）单独统计，不计入违规总数
        if self.acknowledged_orphan_steps or self.acknowledged_orphan_modules:
            lines.append("- 已确认合理孤儿（acknowledged，定期复审，不计违规）:")
            lines.append(f"  - 孤儿环节（BM-INV-001 acknowledged）: {len(self.acknowledged_orphan_steps)}")
            lines.append(f"  - 孤儿模块（BM-INV-007 acknowledged）: {len(self.acknowledged_orphan_modules)}")
        if self.source_unavailable:
            lines.append("")
            lines.append("> ⚠ 目标图源不可用（已跳过该图 BM-INV-002 校验）: " + ", ".join(self.source_unavailable))
        lines.append("")

        # 1. 孤儿环节
        lines.append("## 1. 孤儿环节（BM-INV-001：环节无锚点 = 悬空决策）")
        lines.append("")
        lines.append(
            "> 君子协定：每个 battle_map_steps 必须至少有一个 battle_map_anchors。"
            "无锚点环节 = 没有模块承载 = AI 写决策时凭记忆推断 = 幻觉风险。"
        )
        lines.append("")
        lines.append(f"### 1a. 违规孤儿环节（须修复）: {len(self.orphan_steps)}")
        if not self.orphan_steps:
            lines.append("> ✅ 无违规孤儿环节。")
        else:
            lines.append("| step_id | 环节名 | 阶段 | 设计成熟度 |")
            lines.append("|---|---|---|---|")
            for s in self.orphan_steps:
                lines.append(
                    f"| {s['step_id']} | {s.get('step_name', '—')} | "
                    f"{s.get('flow_stage', '—')} | {s.get('design_maturity', '—')} |"
                )
        lines.append("")
        # V1.1.0 三档分类：已确认合理孤儿环节（acknowledged）单独列出，不计违规
        lines.append(f"### 1b. 已确认合理孤儿环节（acknowledged，定期复审）: {len(self.acknowledged_orphan_steps)}")
        if not self.acknowledged_orphan_steps:
            lines.append("> 无 acknowledged 孤儿环节。")
        else:
            lines.append(
                "> 以下环节经架构审查确认为「计划中未实现」或「父环节已覆盖」，"
                "从违规列表排除。真源：battle_map_domain_policy.yaml §acknowledged_orphans.steps。"
                "AI 不应对这些环节尝试「修复」（消除治理振荡）。"
            )
            lines.append("| step_id | 环节名 | 阶段 | 设计成熟度 |")
            lines.append("|---|---|---|---|")
            for s in self.acknowledged_orphan_steps:
                lines.append(
                    f"| {s['step_id']} | {s.get('step_name', '—')} | "
                    f"{s.get('flow_stage', '—')} | {s.get('design_maturity', '—')} |"
                )
        lines.append("")

        # 2. 幽灵锚点
        lines.append("## 2. 幽灵锚点（BM-INV-002：target_id 在目标图找不到）")
        lines.append("")
        lines.append(
            "> 君子协定：anchor.target_id 必须能在 target_graph 对应的图/仓库里找到。"
            "找不到 = 幽灵锚点 = 指向不存在的模块/候选/蓝图。"
        )
        lines.append("")
        if not self.ghost_anchors:
            lines.append("> ✅ 无幽灵锚点（或锚点表为空，无对象校验）。")
        else:
            lines.append("| anchor_id | step_id | target_graph | target_id | 角色 |")
            lines.append("|---|---|---|---|---|")
            for a in self.ghost_anchors:
                lines.append(
                    f"| {a.get('anchor_id', '—')} | {a.get('step_id', '—')} | "
                    f"{a.get('target_graph', '—')} | {a.get('target_id', '—')} | "
                    f"{a.get('target_role', '—')} |"
                )
        lines.append("")

        # 3. 缺失叙事
        lines.append("## 3. 缺失叙事（BM-INV-003：翻译真源无对应环节）")
        lines.append("")
        lines.append(
            "> 君子协定：DB 每个环节必须在翻译真源 `battle_map_steps` 段有叙事"
            "（name_zh/plain_zh/mechanism_zh/indicators_zh）。缺失 = 生成器降级到 DB step_name。"
        )
        lines.append("")
        if not self.missing_narratives:
            lines.append("> ✅ 无缺失叙事，所有环节在翻译真源均已登记。")
        else:
            lines.append("| step_id | 环节名 | 阶段 |")
            lines.append("|---|---|---|")
            for s in self.missing_narratives:
                lines.append(f"| {s['step_id']} | {s.get('step_name', '—')} | {s.get('flow_stage', '—')} |")
        lines.append("")

        # 4. 悬空边
        lines.append("## 4. 悬空边（edge 指向不存在的环节）")
        lines.append("")
        if not self.dangling_edges:
            lines.append("> ✅ 无悬空边，所有流转边两端均为合法环节。")
        else:
            lines.append("| edge_id | from_step_id | to_step_id | edge_type | 缺失端 |")
            lines.append("|---|---|---|---|---|")
            for e in self.dangling_edges:
                lines.append(
                    f"| {e.get('edge_id', '—')} | {e.get('from_step_id', '—')} | "
                    f"{e.get('to_step_id', '—')} | {e.get('edge_type', '—')} | "
                    f"{e.get('missing_end', '—')} |"
                )
        lines.append("")

        # 5. 域漂移
        lines.append("## 5. 域漂移（BM-INV-004：target domain 不在 flow_stage 允许列表）")
        lines.append("")
        lines.append(
            "> 君子协定：anchor 的 target module/candidate 的 domain 必须在 step.flow_stage "
            "对应的允许域列表里。不在 = 域漂移 = 语义错位（如把卖出决策挂在买入流程）。"
            "规则真源：`docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`。"
        )
        # 裁定原则核心文本单向派生自 YAML §adjudication_principles.core（消除硬编码多真源）
        if self.adjudication_principle:
            lines.append(
                f"> 裁定原则：{self.adjudication_principle}。supplement 角色（工具被用到，"
                "不承载业务决策）豁免域漂移检查；仅 primary（承载决策）严查域。故本表只列 primary 锚点的漂移。"
            )
        lines.append("")
        if not self.domain_drifts:
            lines.append("> ✅ 无域漂移，所有锚点 target domain 都在对应 flow_stage 允许列表里。")
        else:
            lines.append("| anchor_id | step_id | flow_stage | target_graph | target_id | target_domains | 角色 |")
            lines.append("|---|---|---|---|---|---|---|")
            for a in self.domain_drifts:
                domains = a.get("domains")
                domains_str = ", ".join(domains) if domains else "—"
                lines.append(
                    f"| {a.get('anchor_id', '—')} | {a.get('step_id', '—')} | "
                    f"{a.get('flow_stage', '—')} | {a.get('target_graph', '—')} | "
                    f"{a.get('target_id', '—')} | {domains_str} | "
                    f"{a.get('target_role', '—')} |"
                )
        lines.append("")

        # 6. 父子嵌套问题
        lines.append("## 6. 父子嵌套问题（BM-INV-006：父不存在/跨阶段/成环/depth超限）")
        lines.append("")
        lines.append(
            "> 君子协定：parent_step_id 必须指向同 flow_stage 的已存在环节，"
            "depth≤3，parent 链不能成环。规则真源：battle_map_positioning.md §8.4。"
        )
        lines.append("")
        if not self.parent_child_issues:
            lines.append("> ✅ 无父子嵌套问题。")
        else:
            lines.append("| step_id | 环节名 | 问题类型 | 详情 |")
            lines.append("|---|---|---|---|")
            for s in self.parent_child_issues:
                lines.append(
                    f"| {s.get('step_id', '—')} | {s.get('step_name', '—')} | "
                    f"{s.get('issue_type', '—')} | {s.get('detail', '—')} |"
                )
        lines.append("")

        # 7. 孤儿模块（BM-INV-007）
        lines.append("## 7. 孤儿模块（BM-INV-007：业务域模块无作战锚点 = 造出来没用上）")
        lines.append("")
        lines.append(
            "> 君子协定：业务域（battle_map_domain_policy.yaml §domain_classification.business_domains）"
            "内的 depgraph 模块（node_type=module），必须至少有一个 battle_map_anchors 指向它"
            "（target_graph=depgraph，target_id 命中其 blueprint_id 或 path）。"
            "无任何锚点指向 = 没有作战使命 = 造出来没用上 = 幻觉/浪费风险。"
            "工具域（D_INFRA_RUNTIME/D_INTEGRATION/D_SHARED/D_SECURITY 等基础设施/管道/支撑）"
            "铁律5不挂作战地图，天然排除。V1.1.0 治本：用 domain_classification 显式分类替代并集推断。"
        )
        lines.append("")
        lines.append(f"### 7a. 违规孤儿模块（须修复）: {len(self.orphan_modules)}")
        if not self.orphan_modules:
            lines.append("> ✅ 无违规孤儿模块，所有业务域模块均已挂载到作战环节。")
        else:
            lines.append("| blueprint_id | 名称 / Name | domain_id | build_status | path |")
            lines.append("|---|---|---|---|---|")
            for m in self.orphan_modules:
                # 双语名称优先（翻译真源），无翻译时回退到 DB node_name，都无则 —
                name_bi = m.get("name_bi") or ""
                node_name = str(m.get("node_name") or "").strip()
                display = name_bi or node_name or "—"
                lines.append(
                    f"| {m.get('blueprint_id', '—')} | {display} | "
                    f"{m.get('domain_id', '—')} | {m.get('build_status', '—')} | "
                    f"{m.get('path', '—')} |"
                )
        lines.append("")
        # V1.1.0 三档分类：已确认合理孤儿模块（acknowledged，planned 待实现）单独列出
        lines.append(
            f"### 7b. 已确认合理孤儿模块（acknowledged，planned 待实现）: {len(self.acknowledged_orphan_modules)}"
        )
        if not self.acknowledged_orphan_modules:
            lines.append("> 无 acknowledged 孤儿模块。")
        else:
            lines.append(
                "> 以下模块经架构审查确认为「planned 待实现」，从违规列表排除。"
                "真源：battle_map_domain_policy.yaml §acknowledged_orphans.modules。"
                "实现后（build_status planned→stable）补挂锚点并移出此清单。"
            )
            lines.append("| blueprint_id | 名称 / Name | domain_id | build_status | path |")
            lines.append("|---|---|---|---|---|")
            for m in self.acknowledged_orphan_modules:
                name_bi = m.get("name_bi") or ""
                node_name = str(m.get("node_name") or "").strip()
                display = name_bi or node_name or "—"
                lines.append(
                    f"| {m.get('blueprint_id', '—')} | {display} | "
                    f"{m.get('domain_id', '—')} | {m.get('build_status', '—')} | "
                    f"{m.get('path', '—')} |"
                )
        lines.append("")

        # 处置建议
        lines.append("## 8. 处置建议")
        lines.append("")
        lines.append(
            "- 孤儿环节：用 `apply_battle_map.py --add-anchor` 为环节挂载承载模块/候选/蓝图"
            "（草图 §12 迁移第二批「锚点」）"
        )
        lines.append("- 幽灵锚点：修正 target_id 指向真实存在的模块/候选，或删除该锚点")
        lines.append(
            "- 缺失叙事：在 `module_translation_registry.yaml` §battle_map_steps 段补齐环节叙事"
            "（name_zh/plain_zh/mechanism_zh/indicators_zh）"
        )
        lines.append("- 悬空边：修正 edge 的 from/to step_id，或删除孤立边")
        lines.append(
            "- 域漂移：① 确认锚点是否挂错环节（如 D_SELL_DECISION 不应在 buy_flow）；"
            "② 若挂错，迁移到正确环节或删除；③ 若认为该 domain 应被允许，"
            "修改 `battle_map_domain_policy.yaml` 的 `flow_stage_allowed_domains` 段"
            "（真源在 YAML，禁止改代码）；④ target_domains 含多个 domain 时，"
            "任一在允许列表即通过（跨域蓝图如 MOD-INF-002 含 80+ 子模块跨 8 domain）"
        )
        lines.append(
            "- 孤儿模块（违规）：① 确认该模块是否该挂到某作战环节——若是，用 "
            "`apply_battle_map.py --add-anchor --target-graph depgraph --target-id <blueprint_id>` "
            "挂到对应 step；② 若确无作战使命（造出来用不上），走弃用流程——"
            "`apply_depgraph.py` 软删除（build_status→deprecated）+ 在 "
            "`candidate_module_registry.yaml` 记 rejected 条目（含否决理由，防未来误重设）；"
            "③ 工具域模块（D_INFRA_RUNTIME/D_INTEGRATION/D_SHARED/D_SECURITY）不应挂作战地图"
            "（铁律5），由 domain_classification.tool_domains 自动排除，无需处理"
        )
        lines.append(
            "- acknowledged 孤儿（已确认合理，不计违规）：① 真源在 "
            "`battle_map_domain_policy.yaml` §acknowledged_orphans；② 这些是「计划中未实现」或"
            "「planned 待实现」的显式登记，AI 不应尝试「修复」（消除治理振荡）；③ 到 review_frequency "
            "到期时强制复审，对应模块 build_status planned→stable 后补挂锚点并移出此清单"
        )
        lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 锚点目标合法 id 采集（BM-INV-002）
# ---------------------------------------------------------------------------


def _valid_ids_depgraph() -> tuple[set[str], bool]:
    """采集 depgraph 合法 target_id（blueprint_id ∪ path，宽松匹配防误报）。

    Returns:
        (valid_ids, available) — available=False 表示源不可用（跳过校验）
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        valid: set[str] = set()
        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SQL_SELECT_DEPGRAPH_VALID_IDS)
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row, strict=False))
                    bp = r.get("blueprint_id")
                    path = r.get("path")
                    if bp:
                        valid.add(str(bp))
                    if path:
                        valid.add(str(path))
        finally:
            conn.close()
        return valid, True
    except Exception:  # noqa: BLE001
        return set(), False


def _valid_ids_dataflowgraph() -> tuple[set[str], bool]:
    """采集 dataflowgraph 合法 target_id（entity_name ∪ job_name ∪ module_id）。"""
    try:
        from zephyr.governance.persistence.dataflowgraph_schema import (
            get_dataflowgraph_pg_connection,
        )

        valid: set[str] = set()
        conn = get_dataflowgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT entity_name, module_id FROM dataflow_datasets")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row, strict=False))
                    for k in ("entity_name", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
                cur.execute("SELECT job_name, module_id FROM dataflow_jobs")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row, strict=False))
                    for k in ("job_name", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
        finally:
            conn.close()
        return valid, True
    except Exception:  # noqa: BLE001
        return set(), False


def _valid_ids_decisiongraph() -> tuple[set[str], bool]:
    """采集 decisiongraph 合法 target_id（path ∪ module_id ∪ layer_id）。"""
    try:
        from zephyr.governance.persistence.decisiongraph_schema import (
            get_decisiongraph_pg_connection,
        )

        valid: set[str] = set()
        conn = get_decisiongraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT path, module_id FROM decision_nodes")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row, strict=False))
                    for k in ("path", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
                cur.execute("SELECT layer_id, module_id FROM decision_layers")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row, strict=False))
                    for k in ("layer_id", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
        finally:
            conn.close()
        return valid, True
    except Exception:  # noqa: BLE001
        return set(), False


def _valid_ids_candidate() -> tuple[set[str], bool]:
    """采集候选池合法 target_id（candidate_module_registry.yaml 条目 id）。"""
    try:
        import yaml  # type: ignore[import-untyped]

        if not _CANDIDATE_YAML.exists():
            return set(), False
        data = yaml.safe_load(_CANDIDATE_YAML.read_text(encoding="utf-8")) or {}
        valid: set[str] = set()
        # 兼容多种 schema：顶层 list / entries / candidates / modules
        entries: list = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            for key in ("entries", "candidates", "modules", "items"):
                v = data.get(key)
                if isinstance(v, list):
                    entries = v
                    break
        for e in entries:
            if not isinstance(e, dict):
                continue
            for k in ("id", "candidate_id", "module_id"):
                v = e.get(k)
                if v:
                    valid.add(str(v))
        return valid, True
    except Exception:  # noqa: BLE001
        return set(), False


def _valid_ids_blueprint() -> tuple[set[str], bool]:
    """采集蓝图合法 target_id（docs/03_modules/ frontmatter module_id）。"""
    try:
        import re

        if not _BP_SCAN_ROOT.exists():
            return set(), False
        fm_re = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
        valid: set[str] = set()
        for fpath in _BP_SCAN_ROOT.rglob("*"):
            if not fpath.is_file() or fpath.name in {"index.md"}:
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            m = fm_re.match(content)
            if not m:
                continue
            for line in m.group(1).split("\n"):
                if ":" not in line:
                    continue
                key, _, val = line.partition(":")
                if key.strip() in ("module_id", "id"):
                    v = val.strip().strip('"').strip("'")
                    if v and not v.startswith("[") and not v.startswith("{"):
                        valid.add(v)
        return valid, True
    except Exception:  # noqa: BLE001
        return set(), False


# target_graph → 采集器
_GRAPH_COLLECTORS = {
    "depgraph": _valid_ids_depgraph,
    "dataflowgraph": _valid_ids_dataflowgraph,
    "decisiongraph": _valid_ids_decisiongraph,
    "candidate": _valid_ids_candidate,
    "blueprint": _valid_ids_blueprint,
}


# ---------------------------------------------------------------------------
# 域漂移检查（BM-INV-004）—— flow_stage → 允许 domain 规则 + anchor domain 采集
# ---------------------------------------------------------------------------


def _load_domain_policy() -> dict[str, set[str]] | None:
    """加载 battle_map_domain_policy.yaml，返回 {flow_stage: set(allowed_domain_ids)}。

    文件不存在或解析失败时返回 None（跳过域漂移检查，记录 source_unavailable）。
    真源：docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _DOMAIN_POLICY_YAML.exists():
            return None
        data = yaml.safe_load(_DOMAIN_POLICY_YAML.read_text(encoding="utf-8")) or {}
        result: dict[str, set[str]] = {}
        stages = data.get("flow_stage_allowed_domains") or {}
        for stage, cfg in stages.items():
            allowed = cfg.get("allowed") if isinstance(cfg, dict) else cfg
            if isinstance(allowed, list):
                result[stage] = {str(d) for d in allowed}
        return result if result else None
    except Exception:  # noqa: BLE001
        return None


def _load_adjudication_principle() -> str:
    """加载 battle_map_domain_policy.yaml §adjudication_principles.core（裁定原则核心文本）。

    单向派生真源：YAML（规则真源）→ 本函数 → Report.adjudication_principle → 报告文案。
    消除多真源：报告文案不再硬编码裁定原则，改 YAML 自动反映到报告。
    文件不存在/解析失败/无该字段时返回空串（报告降级为不输出裁定原则行）。
    真源：docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _DOMAIN_POLICY_YAML.exists():
            return ""
        data = yaml.safe_load(_DOMAIN_POLICY_YAML.read_text(encoding="utf-8")) or {}
        ap = data.get("adjudication_principles") or {}
        return str(ap.get("core") or "").strip()
    except Exception:  # noqa: BLE001
        return ""


def _load_domain_classification() -> tuple[set[str], set[str]]:
    """加载 battle_map_domain_policy.yaml §domain_classification（V1.1.0 新增，治本）。

    返回 (business_domains, tool_domains)。
    - business_domains：承载交易/研究/风控决策的域 → BM-INV-007 扫描对象（必须有作战锚点）
    - tool_domains：基础设施/管道/支撑 → 铁律5不挂作战地图，天然排除 BM-INV-007 扫描

    治本背景：原 _business_domain_whitelist() 取所有 flow_stage allowed 域的并集，
    但并集含工具域（D_INFRA_RUNTIME 等作 supplement 被用到），导致 106 个基础设施模块
    被误报孤儿。此函数用 YAML 显式分类替代并集推断。

    文件不存在/无此段时返回 (set(), set())，调用方回退到并集逻辑（向后兼容）。
    真源：docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _DOMAIN_POLICY_YAML.exists():
            return set(), set()
        data = yaml.safe_load(_DOMAIN_POLICY_YAML.read_text(encoding="utf-8")) or {}
        dc = data.get("domain_classification") or {}
        business = {str(d) for d in dc.get("business_domains") or []}
        tools = {str(d) for d in dc.get("tool_domains") or []}
        return business, tools
    except Exception:  # noqa: BLE001
        return set(), set()


def _load_acknowledged_orphans() -> tuple[set[str], set[str]]:
    """加载 battle_map_domain_policy.yaml §acknowledged_orphans（V1.1.0 新增，治本）。

    返回 (acknowledged_module_ids, acknowledged_step_ids)。
    - acknowledged_module_ids：已确认合理的孤儿模块 blueprint_id 集合
    - acknowledged_step_ids：已确认合理的孤儿环节 step_id 集合

    治本背景：原不变量体系是二元逻辑（挂了/没挂），但现实需要三元逻辑
    （violations / acknowledged / planned）。此函数补齐第三态——已确认合理孤儿
    从 BM-INV-001/007 违规列表排除，带 review_frequency 到期强制复审。
    100% AI 开发适配：AI 看到三档分类后不再对 acknowledged 项尝试"修复"（消除治理振荡）。

    文件不存在/无此段时返回 (set(), set())（无 acknowledged，全部算违规，向后兼容）。
    真源：docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _DOMAIN_POLICY_YAML.exists():
            return set(), set()
        data = yaml.safe_load(_DOMAIN_POLICY_YAML.read_text(encoding="utf-8")) or {}
        ao = data.get("acknowledged_orphans") or {}
        mod_ids = {str(m.get("blueprint_id")) for m in (ao.get("modules") or []) if m.get("blueprint_id")}
        step_ids: set[str] = set()
        for grp in ao.get("steps") or []:
            for sid in grp.get("step_ids") or []:
                step_ids.add(str(sid))
        return mod_ids, step_ids
    except Exception:  # noqa: BLE001
        return set(), set()


def _anchor_domain_map_depgraph() -> tuple[dict[str, set[str]], bool]:
    """采集 depgraph 节点的 domain_id（key=blueprint_id/path, value=set(domain_id)）。

    与 _valid_ids_depgraph 互补：后者只采集合法 id 集合（BM-INV-002），
    本方法同时采集 domain_id 集合（BM-INV-004 域漂移校验用）。

    返回 set 而非 str：跨域巨型蓝图（如 MOD-INF-002 含 80+ 子模块跨 8 domain）
    的 blueprint_id 对应多节点多 domain，用 set 采集全部，校验时任一 domain 在
    允许列表即通过（防误报——单一 domain_id 对跨域蓝图是非确定性采样）。
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        domain_map: dict[str, set[str]] = {}
        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SQL_SELECT_DEPGRAPH_DOMAIN_MAP)
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row, strict=False))
                    domain_id = r.get("domain_id")
                    if not domain_id:
                        continue
                    for k in ("blueprint_id", "path"):
                        v = r.get(k)
                        if v:
                            domain_map.setdefault(str(v), set()).add(str(domain_id))
        finally:
            conn.close()
        return domain_map, True
    except Exception:  # noqa: BLE001
        return {}, False


def _anchor_domain_map_candidate() -> tuple[dict[str, set[str]], bool]:
    """采集候选池模块的 domain（key=candidate_id, value=set(domain)）。

    与 _valid_ids_candidate 互补：后者只采集合法 id 集合，本方法采集 domain。
    返回 set 与 _anchor_domain_map_depgraph 对齐（候选通常单 domain，但保持类型一致）。
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _CANDIDATE_YAML.exists():
            return {}, False
        data = yaml.safe_load(_CANDIDATE_YAML.read_text(encoding="utf-8")) or {}
        entries: list = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            for key in ("entries", "candidates", "modules", "items"):
                v = data.get(key)
                if isinstance(v, list):
                    entries = v
                    break
        domain_map: dict[str, set[str]] = {}
        for e in entries:
            if not isinstance(e, dict):
                continue
            domain = e.get("domain")
            if not domain:
                continue
            for k in ("id", "candidate_id", "module_id"):
                v = e.get(k)
                if v:
                    domain_map.setdefault(str(v), set()).add(str(domain))
                    break
        return domain_map, True
    except Exception:  # noqa: BLE001
        return {}, False


# target_graph → domain 采集器（BM-INV-004）
_DOMAIN_COLLECTORS = {
    "depgraph": _anchor_domain_map_depgraph,
    "candidate": _anchor_domain_map_candidate,
}


# ---------------------------------------------------------------------------
# BM-INV-007 孤儿模块：业务域白名单 + 业务模块采集
# ---------------------------------------------------------------------------


def _business_domain_whitelist(policy: dict[str, set[str]] | None) -> set[str]:
    """业务域白名单 = 所有 flow_stage 的 allowed 域并集。

    用于 BM-INV-007 孤儿模块扫描范围。基础设施/治理/工具脚本域
    （D_GOVERNANCE/D_GOV_SCRIPTS/D_GOV_RULE/D_FRONTEND 等）不在任何 flow_stage 的
    allowed 列表里，天然排除，避免"治理脚本没挂作战地图"的假孤儿误报。

    :param policy: _load_domain_policy() 返回的 {flow_stage: set(allowed_domain_ids)}
    :return: 业务域 id 并集；policy 为 None 时返回空集（跳过孤儿模块扫描）
    """
    if not policy:
        return set()
    return set().union(*policy.values())


def _business_modules_depgraph(whitelist: set[str]) -> tuple[list[dict], bool]:
    """采集业务域 depgraph 节点（domain_id ∈ 白名单）—— BM-INV-007 扫描对象。

    与 _anchor_domain_map_depgraph 互补：后者采集 domain 映射（BM-INV-004 域漂移用），
    本方法采集完整节点信息（blueprint_id/path/node_name/domain_id/build_status）供孤儿判定。

    :return: (modules, available) — available=False 表示 depgraph 不可用（跳过孤儿扫描）
    """
    if not whitelist:
        return [], False
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        modules: list[dict] = []
        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    SQL_SELECT_BUSINESS_MODULES,
                    (list(whitelist),),
                )
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    modules.append(dict(zip(cols, row, strict=False)))
        finally:
            conn.close()
        return modules, True
    except Exception:  # noqa: BLE001
        return [], False


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run_alignment(
    output_path: Path | None = None,
    *,
    write_report: bool = True,
) -> BattleMapAlignmentReport:
    """运行作战地图对齐检测，生成报告。

    Args:
        output_path: 报告输出路径。None 时使用默认路径
            docs/02_enterprise_architecture/03_governance_reports/battle_map_alignment_report.md
        write_report: True 写入文件（默认）；False 仅返回 report 不写文件
    """
    if output_path is None:
        output_path = _DEFAULT_REPORT

    # 预加载翻译真源（环节叙事 + 模块级双语名称）
    preload_battle_map_steps()
    preload()  # 模块级翻译（BM-INV-007 孤儿模块表双语名称）
    logger.info("开始作战地图对齐检测...")

    reader = BattleMapReader()
    try:
        steps = reader.get_all_steps()
        anchors = reader.get_all_anchors()
        edges = reader.get_all_edges()
        orphan_steps_raw = reader.find_steps_without_anchors()
    finally:
        reader.close()
    logger.info("数据加载完成：环节=%d 锚点=%d 流转边=%d", len(steps), len(anchors), len(edges))

    # V1.1.0 三档分类（治本）：已确认合理孤儿环节从违规列表排除
    # acknowledged ≠ ignored：是"已知且合理"的显式登记，带 review_frequency 到期复审
    ack_module_ids, ack_step_ids = _load_acknowledged_orphans()
    acknowledged_orphan_steps = [s for s in orphan_steps_raw if s["step_id"] in ack_step_ids]
    orphan_steps = [s for s in orphan_steps_raw if s["step_id"] not in ack_step_ids]

    # BM-INV-002 幽灵锚点：按 target_graph 分组校验
    ghost_anchors: list[dict] = []
    source_unavailable: list[str] = []
    graphs_present = {a["target_graph"] for a in anchors if a.get("target_graph")}
    reader2 = BattleMapReader()
    try:
        for graph in sorted(graphs_present):
            collector = _GRAPH_COLLECTORS.get(graph)
            if collector is None:
                # 未知 target_graph：所有该图锚点都是幽灵（target_graph 本身非法）
                ghost_anchors.extend(
                    {**a, "reason": f"unknown_target_graph:{graph}"}
                    for a in reader2.get_all_anchors()
                    if a.get("target_graph") == graph
                )
                continue
            valid_ids, available = collector()
            if not available:
                source_unavailable.append(graph)
                continue
            orphans = reader2.find_orphan_anchors_by_graph(graph, valid_ids)
            ghost_anchors.extend({**a, "reason": "target_id_not_found"} for a in orphans)
    finally:
        reader2.close()

    # BM-INV-003 缺失叙事：DB step_id 不在翻译真源
    narrative_ids = set(all_battle_map_step_ids())
    missing_narratives = [s for s in steps if s["step_id"] not in narrative_ids]

    # 悬空边：from/to 指向不存在的环节
    step_ids = {s["step_id"] for s in steps}
    dangling_edges: list[dict] = []
    for e in edges:
        miss = []
        if e.get("from_step_id") not in step_ids:
            miss.append("from")
        if e.get("to_step_id") not in step_ids:
            miss.append("to")
        if miss:
            dangling_edges.append({**e, "missing_end": "/".join(miss)})

    # BM-INV-004 域漂移：anchor.target 的 domain 是否在 step.flow_stage 允许列表
    domain_drifts: list[dict] = []
    policy = _load_domain_policy()
    # 裁定原则核心文本（单向派生自 YAML §adjudication_principles.core，供报告渲染，消除硬编码多真源）
    adjudication_principle = _load_adjudication_principle()
    if policy is None:
        source_unavailable.append("domain_policy_yaml")
    else:
        # step_id → flow_stage 查找表
        step_to_stage = {s["step_id"]: s.get("flow_stage") for s in steps}
        # 按 target_graph 采集 domain map（只对 depgraph/candidate 校验）
        graphs_for_domain = {a.get("target_graph") for a in anchors}
        domain_maps: dict[str, dict[str, set[str]]] = {}
        for graph in graphs_for_domain:
            collector = _DOMAIN_COLLECTORS.get(graph)
            if collector is None:
                continue  # dataflowgraph/decisiongraph/blueprint 暂不校验 domain
            dmap, available = collector()
            if not available:
                source_unavailable.append(f"domain_map:{graph}")
                continue
            domain_maps[graph] = dmap
        # 逐锚点校验
        for a in anchors:
            stage = step_to_stage.get(a.get("step_id"))
            if not stage or stage not in policy:
                continue  # 未知 stage 或无规则，跳过
            # 核心原则（battle_map_domain_policy.yaml §裁定原则）：
            # 域归属看"承载什么决策"，不看"被谁调用"。管道/协议层模块（MCP 等）即使被
            # 业务环节调用，域属性不变。supplement 角色 = 工具被用到（不承载业务决策），
            # 豁免域漂移检查；仅 primary（承载决策）严查域，防语义错位（如卖出挂到买入）。
            if a.get("target_role") == "supplement":
                continue
            tg = a.get("target_graph")
            tid = a.get("target_id")
            dmap = domain_maps.get(tg)
            if not dmap:
                continue  # 该 target_graph 无 domain 采集器或不可用
            domains = dmap.get(str(tid))
            if not domains:
                continue  # 查不到 domain（可能 depgraph 该节点无 domain_id）
            # 跨域蓝图任一 domain 在允许列表即通过（防误报）
            if not (domains & policy[stage]):
                domain_drifts.append(
                    {
                        **a,
                        "flow_stage": stage,
                        "domains": sorted(domains),
                        "reason": "domain_not_in_allowed_list",
                    }
                )

    # BM-INV-006 父子嵌套一致性：父存在/同阶段/无环/depth≤2
    parent_child_issues = _check_parent_child_consistency(steps)

    # BM-INV-007 孤儿模块：业务域 depgraph 节点无任何锚点指向
    orphan_modules: list[dict] = []
    acknowledged_orphan_modules: list[dict] = []
    business_module_count = 0
    # V1.1.0 治本：优先用 domain_classification.business_domains（显式分类），
    # 替代 _business_domain_whitelist 并集逻辑（并集含工具域 D_INFRA_RUNTIME 等 →
    # 106 个基础设施模块被误报孤儿 → 100%AI 开发下引发治理振荡）
    business_domains, _tool_domains = _load_domain_classification()
    if business_domains:
        whitelist = business_domains
    elif policy:
        whitelist = _business_domain_whitelist(policy)  # 向后兼容：无 domain_classification 时回退并集
    else:
        whitelist = set()
    if not whitelist:
        # policy 不可用时 source_unavailable 已在域漂移块记录 domain_policy_yaml
        logger.warning("业务域白名单为空（policy 不可用），跳过 BM-INV-007 孤儿模块扫描")
    else:
        business_modules, bm_available = _business_modules_depgraph(whitelist)
        if not bm_available:
            source_unavailable.append("business_modules:depgraph")
        else:
            business_module_count = len(business_modules)
            # 已锚定集合 = target_graph=depgraph 的所有 target_id（blueprint_id ∪ path 宽松匹配）
            anchored_depgraph_ids = {
                str(a["target_id"]) for a in anchors if a.get("target_graph") == "depgraph" and a.get("target_id")
            }
            for m in business_modules:
                bp = str(m.get("blueprint_id")) if m.get("blueprint_id") else ""
                pth = str(m.get("path")) if m.get("path") else ""
                # blueprint_id 或 path 任一命中已锚定集合 → 已挂载，非孤儿
                if bp not in anchored_depgraph_ids and pth not in anchored_depgraph_ids:
                    # 双语名称（翻译真源 module_translation_registry.yaml，中文在前 / English）
                    # fallback：翻译真源无翻译时从路径派生英文名，避免显示 "—"
                    name_bi = get_module_name_bilingual(pth) if pth else ""
                    if not name_bi and pth:
                        name_bi = derive_name_from_path(pth)
                    m["name_bi"] = name_bi
                    # V1.1.0 三档分类：已确认合理孤儿模块从违规列表排除
                    if bp in ack_module_ids:
                        acknowledged_orphan_modules.append(m)
                    else:
                        orphan_modules.append(m)

    report = BattleMapAlignmentReport(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        step_count=len(steps),
        anchor_count=len(anchors),
        edge_count=len(edges),
        narrative_count=len(narrative_ids),
        orphan_steps=orphan_steps,
        ghost_anchors=ghost_anchors,
        missing_narratives=missing_narratives,
        dangling_edges=dangling_edges,
        domain_drifts=domain_drifts,
        parent_child_issues=parent_child_issues,
        orphan_modules=orphan_modules,
        business_module_count=business_module_count,
        acknowledged_orphan_steps=acknowledged_orphan_steps,
        acknowledged_orphan_modules=acknowledged_orphan_modules,
        source_unavailable=source_unavailable,
        adjudication_principle=adjudication_principle,
        issues_total=(
            len(orphan_steps)
            + len(ghost_anchors)
            + len(missing_narratives)
            + len(dangling_edges)
            + len(domain_drifts)
            + len(parent_child_issues)
            + len(orphan_modules)
        ),
    )

    if write_report:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            _make_frontmatter(report.generated_at) + report.to_markdown(),
            encoding="utf-8",
        )
        logger.info("作战地图对齐报告已写入 %s", output_path)
        logger.info(
            "违规总数: %d (孤儿环节=%d, 幽灵锚点=%d, 缺失叙事=%d, 悬空边=%d, 域漂移=%d, 父子嵌套=%d, 孤儿模块=%d)",
            report.issues_total,
            len(orphan_steps),
            len(ghost_anchors),
            len(missing_narratives),
            len(dangling_edges),
            len(domain_drifts),
            len(parent_child_issues),
            len(orphan_modules),
        )
        logger.info(
            "三档分类: 违规孤儿环节=%d + acknowledged=%d | 违规孤儿模块=%d + acknowledged=%d",
            len(orphan_steps),
            len(acknowledged_orphan_steps),
            len(orphan_modules),
            len(acknowledged_orphan_modules),
        )
        logger.info(
            "BM-INV-007 孤儿模块扫描: 业务域模块=%d, 已锚定=%d, 违规孤儿=%d, acknowledged=%d",
            business_module_count,
            business_module_count - len(orphan_modules) - len(acknowledged_orphan_modules),
            len(orphan_modules),
            len(acknowledged_orphan_modules),
        )
        if source_unavailable:
            logger.warning("目标图源不可用（跳过校验）: %s", ", ".join(source_unavailable))

    return report


def _check_parent_child_consistency(steps: list[dict]) -> list[dict]:
    """BM-INV-006: 父子嵌套一致性检查。

    检查项：
      1. 悬空父引用：parent_step_id 指向不存在的 step
      2. 跨阶段嵌套：子 flow_stage 与父不一致
      3. 成环：parent 链 A→B→A
      4. depth 超限：depth > 3
      5. depth 不符：depth 值与 parent 链长度不一致
    """
    issues: list[dict] = []
    step_map = {s["step_id"]: s for s in steps}

    for s in steps:
        sid = s["step_id"]
        pid = s.get("parent_step_id")
        if not pid:
            continue  # 根环节，跳过

        parent = step_map.get(pid)
        if parent is None:
            issues.append(
                {
                    "step_id": sid,
                    "step_name": s.get("step_name", "—"),
                    "issue_type": "悬空父引用",
                    "detail": f"parent_step_id='{pid}' 不存在",
                }
            )
            continue

        # 同阶段校验
        if s.get("flow_stage") != parent.get("flow_stage"):
            issues.append(
                {
                    "step_id": sid,
                    "step_name": s.get("step_name", "—"),
                    "issue_type": "跨阶段嵌套",
                    "detail": f"子 flow_stage='{s.get('flow_stage')}' 与父='{parent.get('flow_stage')}' 不一致",
                }
            )

        # depth 上限校验
        depth = s.get("depth", 0)
        if depth > 3:
            issues.append(
                {
                    "step_id": sid,
                    "step_name": s.get("step_name", "—"),
                    "issue_type": "depth超限",
                    "detail": f"depth={depth} > 3（上限根→子→孙→曾孙）",
                }
            )

        # depth 与 parent 链长度一致性
        chain_depth = 0
        cursor = s
        seen = {sid}
        while cursor.get("parent_step_id"):
            pid2 = cursor["parent_step_id"]
            if pid2 in seen:
                issues.append(
                    {
                        "step_id": sid,
                        "step_name": s.get("step_name", "—"),
                        "issue_type": "成环",
                        "detail": f"parent 链成环: {' → '.join(seen)} → {pid2}",
                    }
                )
                break
            seen.add(pid2)
            cursor = step_map.get(pid2)
            if cursor is None:
                break  # 悬空父引用已在上面报过
            chain_depth += 1
        else:
            if depth != chain_depth:
                issues.append(
                    {
                        "step_id": sid,
                        "step_name": s.get("step_name", "—"),
                        "issue_type": "depth不符",
                        "detail": f"depth={depth} 但 parent 链长度={chain_depth}",
                    }
                )

    return issues


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="作战地图对齐检测器（battle_map_positioning.md §8.3，君子协定）")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="报告输出路径（默认 docs/02_enterprise_architecture/03_governance_reports/battle_map_alignment_report.md）",
    )
    args = parser.parse_args()

    try:
        report = run_alignment(output_path=args.output)
    except Exception as e:
        logger.error("检测失败: %s", e, exc_info=True)
        return EXIT_ERROR
    # 君子协定：有 findings 返回 EXIT_FINDINGS（调用方决定是否阻断），无 findings 返回 EXIT_PASS
    return EXIT_FINDINGS if report.issues_total > 0 else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
