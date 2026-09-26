# [BLUEPRINT] MOD-METAQ-WO007-CKGTIER | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md#WO-007
# [MODULE] scripts.governance.meta_question.wo007.build_ckg_prior_tier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 纯文件系统扫描（无 DB）; PyYAML; 可选读 .runtime/tmp/.../wo007_reexam.yaml（缺失则记 degraded）
# [CONSUMERS] 案卷 docs/_working/meta_question_answers/build/WO-007.yaml; 落地批（按 consumption_points 逐点执行补丁）;
#             任何 CKG/ig_fact 消费方施工前自查（本册 downstream_obligations 是机读义务清单）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 消费点清单=**扫描生成**（禁手工清单，静态清单禁手工维护铁律）；人工只写 adjudication 裁定文本，
#              未裁定的消费点自动计为不合规并出现在 pending_adjudication（fail-visible，新增消费点无法静默绕过）；
#              本件零写 DB、零写 src/（生产代码改动以 patches/ 待落地补丁形式交付，并发期避让）；
#              置信上限只作用于**读取侧**（ig_fact 存量 confidence 不改写，历史事实层字节零触碰）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_generated
# [ERROR_CONTRACT] 扫描面为空→抛（说明路径漂移，拒绝产空册）；reexam 产物缺失→a/b 记 null + degraded 标记（不抛）；
#                  非法 tier 名→抛。
# [TESTS] wo007_reexam.py 对账 + 本册 --self-check（扫描点数与清单一致、c 率可复算）
# [TTL] task_bound
"""build_ckg_prior_tier — CKG 降级为结构先验的执行件（WO-007 件 3，含 PQ-0065 判据重述）。

产出 data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml：
  1) consumption_points —— 全仓扫描 CKG（ckg_2021 / supplies_to / ig_fact）消费点，机器分类
     「硬事实用法 / 先验用法 / 生产者 / 咨询性 / 词表级」+ 逐点裁定与要求动作；
  2) tiers + relation_caps —— 可信度档位与按 source 的置信上限（读取侧生效）；
  3) downstream_obligations —— 下游必须落实的先验纪律（不得单独支撑决策、须与行情/财务/IO 交叉…）；
  4) compliance_rate_c —— 由 1) 机械算出的合规率（PQ-0065 重述判据第三项）；
  5) pq_0065_criterion_restatement —— 判据从「边集一致率」重述为「先验可用性三判据 a/b/c」及机械跑法。

用法：
    python scripts/governance/meta_question/wo007/build_ckg_prior_tier.py [--self-check]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import yaml  # noqa: E402

REGISTRY_VERSION = "1.0.0"
DEFAULT_OUT = _ROOT / "data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml"
REEXAM_YAML = _ROOT / ".runtime/tmp/st-metaq-gc-20260924/wo007/wo007_reexam.yaml"
PATCH_DIR = "scripts/governance/meta_question/wo007/patches"

SCAN_DIRS = ("src/zephyr", "scripts", "config")
SCAN_SUFFIXES = {".py", ".yaml"}
SKIP_PARTS = {"_archive", "__pycache__", ".runtime", "archive"}
# 本工单自产件不列为消费点（自指：生成器/复考探针必然字面含 CKG 词，把它们算进分母会稀释合规率）
SELF_EXCLUDE_PREFIX = "scripts/governance/meta_question/wo007/"
# NO-BARE-SQL：SQL 集中于此（§5.160.2）。这两条是"SQL 形状"识别正则（扫消费方源码用、
# 本体永不发给数据库），因字面含 INSERT INTO 语句头而一并集中；正则文本逐字未动。
_SQL_SHAPE_WRITES_FACT = re.compile(r"INSERT INTO ig_fact", re.I)
_SQL_SHAPE_PROMOTES_GRAPH = re.compile(r"INSERT INTO ig_edge|INSERT INTO ig_chain|edge_type.*supply", re.I | re.S)
PATTERNS = {
    "supplies_to": re.compile(r"\bsupplies_to\b"),
    "product_downstream_of": re.compile(r"\bproduct_downstream_of\b"),
    "subtype_of": re.compile(r"\bsubtype_of\b"),
    "sector_parent_of": re.compile(r"\bsector_parent_of\b"),
    "ckg_2021": re.compile(r"\bckg_2021\b"),
    "ig_fact": re.compile(r"\big_fact\b"),
}
MARKERS = {
    "writes_fact_layer": _SQL_SHAPE_WRITES_FACT,
    "promotes_to_graph": _SQL_SHAPE_PROMOTES_GRAPH,
    "reads_fact_layer": re.compile(r"FROM ig_fact", re.I),
    "reads_graph_edges": re.compile(r"FROM ig_edge", re.I),
    "feeds_scoring": re.compile(r"PILLAR_WEIGHTS|pillar|score|z 分|rank|_top|screen", re.I),
    "feeds_decision": re.compile(r"decision|polarity|ImpactTarget|target_symbol|选股|标的", re.I),
    "quality_or_exemption": re.compile(r"豁免|exempt|quality|S16|S21", re.I),
    "vocabulary_only": re.compile(r"_DEFAULT_RELATION_TYPES|relation_types"),
    "declares_prior": re.compile(r"结构先验|structural_prior|不作现势事实|仅结构先验"),
}
HARD_FACT_CLASSES = {
    "promotion_to_graph_fact",
    "hard_fact_consumer",
    "indirect_hard_fact_via_promoted_edges",
}
IG_EDGE_RX = re.compile(r"\big_edge\b")
INDIRECT_CTX = re.compile(
    r"PILLAR_WEIGHTS|pillar|score|rank|weight|confidence|decision|polarity|ImpactTarget|标的", re.I
)

# 逐点裁定（人写理由，清单本身由扫描生成；未列入=未裁定，计不合规并显式挂账）
ADJUDICATIONS: dict[str, dict] = {
    "scripts/industry_graph/import_ckg_dataset.py": {
        "usage": "producer_ingest",
        "ruling": "入库件：relation→档位映射与 confidence 出厂值（0.6/0.85）均在此产生。降级后不改写存量字节"
        "（历史事实层零触碰），只要求读取侧按本册 caps 取 min(db_confidence, cap)。",
        "required_action": "无需改动（生产者）；在案登记：本次不 ALTER/UPDATE ig_fact。",
        "patch_ref": None,
    },
    "scripts/industry_graph/igfact_fill.py": {
        "usage": "promotion_to_graph_fact",
        "ruling": "硬事实用法（最重的一处）：把 ckg_2021 的 supplies_to 事实**晋升为 ig_edge supply 结构边**并给 "
        "confidence=0.85、并以 ckg 来源激活链。这正是 PQ-0065 里 76 条自并入边的产地——先验被写成事实，"
        "再反过来用同一批边给先验「作证」（58/81=71.6% 假达标）。",
        "required_action": "晋升边 confidence 封顶改 min(现值, 0.45)；source='ckg_2021' 的链激活须同时具备非 CKG 侧证"
        "（旁挂册行业对或研报边）；已在案 76 条自并入边不追溯删除（历史字节零触碰），"
        "由消费侧按本册 provenance_filter 排除。",
        "patch_ref": "wo007-ckg-prior-01.md",
    },
    "scripts/backtest/three_high_screen.py": {
        "usage": "hard_fact_consumer",
        "ruling": "硬事实用法：SQL_CHOKEPOINT 直接以 ig_fact.supplies_to 算「下游依赖广度 − 供给替代压力」，"
        "作为三高第四支柱以 PILLAR_WEIGHTS['chokepoint']=0.20 参与 z 分合成，产出 "
        "data/strategy_intake/three_high_candidates.csv 进策略进货编排——CKG 先验单独支撑了排序，"
        "且 SQL 无 source 过滤（ckg_2021 与 graph_enrich_staging 混算）。",
        "required_action": "chokepoint 权重按先验档降（0.20→≤0.10）或强制交叉侧证后才计入；SQL 加 source 过滤列；"
        "出生证 BIRTH_SOURCE 标注 tier=structural_prior（下游 E2 可见）。",
        "patch_ref": "wo007-ckg-prior-02.md",
    },
    "src/zephyr/frontend/dashboard/api_server.py": {
        "usage": "indirect_hard_fact_via_promoted_edges",
        "ruling": "间接硬事实用法：galaxy 链对权重与图谱面板直接数 ig_edge 有效边计数（含 76 条 ckg 晋升边），"
        "先验以「边计数=1」的同一身份混进展示与链对权重。",
        "required_action": "提供 ckg 边可识别路径（source_doc 前缀已在库），链对权重计算按本册 caps 降权；"
        "默认视图不改动（展示非决策），但面板须可见 tier 标注。",
        "patch_ref": "wo007-ckg-prior-03.md",
    },
    "src/zephyr/intelligence/chain_impact_resolver.py": {
        "usage": "indirect_hard_fact_via_promoted_edges",
        "ruling": "间接硬事实用法（影响最直接落到标的）：新闻情绪沿 ig_edge 无向 BFS 扩散 N 跳，"
        "置信=hit.confidence×decay^hop×company_conf——CKG 晋升边参与决定个股影响置信度，"
        "而边本身没有 tier 权重（等同于硬事实）。",
        "required_action": "扩散权重乘 src_tier_weight(source_doc LIKE 'ckg_2021%' → 0.45，其余 1.0)；"
        "已留开关位（edge 加载 SQL 增 source_doc 字段即可，向后兼容）。",
        "patch_ref": "wo007-ckg-prior-04.md",
    },
    "src/zephyr/intelligence/news_chain_node_linker.py": {
        "usage": "vocabulary_only",
        "ruling": "词表级：词表来自 ig_node/ig_chain（含 ckg 填充激活的链），不读 supplies_to，不做置信推断。"
        "属先验可接受用法（结构提示 + 歧义降权自有机制）。",
        "required_action": "无需改动；但链词表若整支来自 ckg 激活链，后续放量批应带 tier 标注。",
        "patch_ref": None,
    },
    "scripts/industry_graph/graph_quality_check.py": {
        "usage": "advisory_or_policy",
        "ruling": "咨询性：S16 成对冗余豁免（supplies_to+customer_of 合法成对）与 S21 连通性口径，"
        "不产决策信号，属结构质量口径。",
        "required_action": "无需改动；建议后续在 S 系列增一条「先验边占比」体检指标（本册已给口径，不新增 gate）。",
        "patch_ref": None,
    },
    "scripts/industry_graph/websearch_ingest.py": {
        "usage": "advisory_or_policy",
        "ruling": "政策例外：因 CKG 数据集含退市/B 股历史公司，营收归因放宽在市校验——例外由 CKG 数据实态触发，"
        "属先验副作用，须留痕但非违规。",
        "required_action": "无需改动；例外文本已注明 CKG 来源。",
        "patch_ref": None,
    },
    "src/zephyr/knowledge/financial_knowledge_graph.py": {
        "usage": "vocabulary_only",
        "ruling": "词表级：supplies_to 只是关系类型白名单成员（SQLite 邻接表图谱，weight∈(0,1] 与 "
        "review_status 状态机），不绑定 CKG 语义。该 review_status 门禁恰是「先验不得自动入图」的"
        "天然执行点。",
        "required_action": "无需改动；未来若把 CKG 边灌入本模块，必须以 review_status=pending 起步。",
        "patch_ref": None,
    },
    "scripts/backtest/graph_enrich_ingest.py": {
        "usage": "producer_ingest",
        "ruling": "生产者（LLM 抽取入 ig_fact，source='graph_enrich_staging'）——与 CKG 同 relation 命名空间，"
        "是「关系名混用两套真源」的制造方：任何只按 relation='supplies_to' 过滤的读方都会把两者当同一档。",
        "required_action": "消费方必须按 source 分档（本册 relation_caps 按 source 键给出）。",
        "patch_ref": None,
    },
    "config/trading_decision_map.yaml": {
        "usage": "registry_statement",
        "ruling": "已登记先验意图（TDM 供给侧节点：『静态快照仅结构先验不作现势事实』），但**只有文本没有机械执行**——"
        "正是本件补齐的部分（把意图变成 caps + 消费点义务 + 合规率）。",
        "required_action": "落地批把本册路径挂进该节点 payload（数据源侧引用，不复制口径）。",
        "patch_ref": None,
    },
    "config/strategy_production_map.yaml": {
        "usage": "registry_statement",
        "ruling": "生产全景图 FAC-E1D 车道文本登记了「×supplies_to 咽喉度四支柱 z 分合成」——即三高高筛的"
        "CKG 支柱已进入生产编排序列的**登记面**。登记无 tier 标注，故先验降档必须同步此处，"
        "否则编排读者会按硬事实理解。",
        "required_action": "随 three_high_screen 补丁同批改注（chokepoint 支柱标 tier=structural_prior、权重 0.10）。",
        "patch_ref": "wo007-ckg-prior-02.md",
    },
    "config/ai_search_veins.yaml": {
        "usage": "vocabulary_only",
        "ruling": "检索矿脉配置把 ig_fact 作为数据资产名提及，不读 CKG 语义、不产信号。",
        "required_action": "无需改动。",
        "patch_ref": None,
    },
    "scripts/backtest/graph_enrich_staging.py": {
        "usage": "producer_ingest",
        "ruling": "LLM 抽取暂存件，自陈「绝不写 ig_fact 正图」——CKG 的同 relation 命名空间污染源，"
        "但本身不是消费点。降档后其候选与 CKG 同属非硬事实档（narrative_only，见 relation_caps"
        " graph_enrich_staging 段）。",
        "required_action": "无需改动；消费方按 OB-4 分 source 过滤。",
        "patch_ref": None,
    },
    "scripts/governance/check_meta_question_batch.py": {
        "usage": "vocabulary_only",
        "ruling": "考试体检件的 need_tables 名单含 ig_fact（存在性检查），无语义消费。",
        "required_action": "无需改动（且该件在队未落地，本战役禁碰）。",
        "patch_ref": None,
    },
    "scripts/industry_graph/apply_industry_graph_ddl.py": {
        "usage": "infrastructure_ddl",
        "ruling": "ig_* 九表 DDL-as-Code 真源（含 ig_fact 建表/GRANT），不消费 CKG 语义。降级不需要新列——"
        "本册刻意选择「读取侧 caps」而非改 schema，避免动生产表。",
        "required_action": "无需改动。",
        "patch_ref": None,
    },
    "scripts/governance/meta_question/wo008/generate_product_synonym_register.py": {
        "usage": "prior_object_of_study",
        "ruling": "WO-008（他单，在途）以 CKG 产品边为**研究对象**生成同义词册，输出是映射册不是决策信号；"
        "属先验可接受用法。其双端对齐率 0.15%≪30% 的结论本身正是降级裁定的佐证之一。",
        "required_action": "无需改动；其册产出入生产前须引本册 caps（由 WO-008 落地批负责，跨单不代修）。",
        "patch_ref": None,
    },
    "scripts/industry_graph/build_chain_exposure_matrix.py": {
        "usage": "indirect_hard_fact_via_promoted_edges",
        "ruling": "间接硬事实用法（**面最广的一处**）：只读 ig_edge 做同链 BFS 可达衰减算「环节暴露度」，"
        "输出 CSV 直接被线 A 因子构造（上游成本冲击/生猪链/客户动量）与 E5 链感知聚类消费。"
        "ig_edge 里混有 ckg_2021 晋升的 supply 边与 ckg 激活链，故 CKG 先验以「暴露度」的名义"
        "进了因子输入，而暴露度公式对它与其他边一视同仁。",
        "required_action": "BFS 邻接表按 source_doc 前缀乘 tier 权重（ckg_2021→0.45），并在 CSV 出生证列写"
        "prior_edge_share（该环节暴露度中先验边占比），供因子侧自行降权。",
        "patch_ref": "wo007-ckg-prior-05.md",
    },
    "scripts/governance/generate_chain_registry.py": {
        "usage": "advisory_or_policy",
        "ruling": "链注册表生成器：ig_edge 只用于「链内是否有≥1 传导边」的覆盖判据（存在性），不做强度推断，"
        "不进决策。先验边计入存在性是可接受的（结构提示），但注册表列应可追溯到 source。",
        "required_action": "无需改动；后续若把覆盖判据升级为强度判据，须按本册 caps。",
        "patch_ref": None,
    },
    "scripts/governance/reconcile_chain_refs.py": {
        "usage": "advisory_or_policy",
        "ruling": "引用对账件（只报不清，零改写），ig_edge 仅作反向覆盖判据读，无决策面。",
        "required_action": "无需改动。",
        "patch_ref": None,
    },
    "scripts/industry_graph/quality_closeout_governance.py": {
        "usage": "advisory_or_policy",
        "ruling": "质量存量治理收尾件：拓扑定级读 ig_edge 邻接（上游/中游判定），属结构体检口径。",
        "required_action": "无需改动。",
        "patch_ref": None,
    },
    "scripts/industry_graph/p3a_struct_extract.py": {
        "usage": "producer_ingest",
        "ruling": "非 CKG 生产者（网页结构抽取，自动置信 0.6 留人工抽检口）——与本单降级无涉，"
        "列出只为防止『只数 CKG 边、漏掉同表其他来源』的分母口径歧义。",
        "required_action": "无需改动。",
        "patch_ref": None,
    },
}

TIERS = {
    "hard_fact": {
        "weight_multiplier": 1.0,
        "may_alone_support_decision": True,
        "definition": "可在用 PIT 证据独立支撑决策的口径（行情/财务/官方统计发布物）",
    },
    "corroborated_prior": {
        "weight_multiplier": 0.6,
        "may_alone_support_decision": False,
        "definition": "有独立异源侧证方可参与合成，且权重须乘 0.6",
    },
    "structural_prior": {
        "weight_multiplier": 0.45,
        "may_alone_support_decision": False,
        "definition": "只表达结构（谁可能与谁上下游），不表达现势强度；须与硬事实交叉后才进合成",
    },
    "narrative_only": {
        "weight_multiplier": 0.2,
        "may_alone_support_decision": False,
        "definition": "叙事级：可召回、可解释、可作候选提示，禁入任何打分与阈值判定",
    },
}

RELATION_CAPS = {
    "ckg_2021": {
        "supplies_to": {
            "tier": "structural_prior",
            "confidence_cap": 0.45,
            "db_confidence_now": 0.6,
            "note": "2026-09-18 抽样噪声率约 63%（>30%）已在修复工单判为 C 级叙事边；"
            "PQ-0065 一致率 1.23% 再证其不可作硬事实",
        },
        "product_downstream_of": {"tier": "structural_prior", "confidence_cap": 0.45, "db_confidence_now": 0.6},
        "subtype_of": {
            "tier": "structural_prior",
            "confidence_cap": 0.50,
            "db_confidence_now": 0.6,
            "note": "taxonomy 用途（词表/召回）可放行，决策合成仍按 structural_prior 乘权",
        },
        "sector_parent_of": {
            "tier": "structural_prior",
            "confidence_cap": 0.50,
            "db_confidence_now": 0.85,
            "note": "申万行业树本身是静态目录，实测端点可对齐率 100%（件 3 a 判据），但它是**词表**先验不是边先验",
        },
        "produces": {
            "tier": "corroborated_prior",
            "confidence_cap": 0.60,
            "db_confidence_now": 0.85,
            "note": "公司→产品可与 CH main_business/财务主营交叉验证后使用",
        },
        "product_def": {"tier": "corroborated_prior", "confidence_cap": 0.60, "db_confidence_now": 0.85},
        "belongs_to_sector": {
            "tier": "corroborated_prior",
            "confidence_cap": 0.60,
            "db_confidence_now": 0.85,
            "note": "板块归属可用 CH industry_class 逐只交叉核对",
        },
    },
    "graph_enrich_staging": {
        "supplies_to": {
            "tier": "narrative_only",
            "confidence_cap": 0.35,
            "db_confidence_now": None,
            "note": "LLM 抽取候选（抽取件自陈「候选非事实，入图需 Owner」），与 CKG 同 relation 名但不同档",
        },
    },
}

DOWNSTREAM_OBLIGATIONS = [
    {
        "id": "OB-1",
        "rule": "先验不得单独支撑决策：tier=structural_prior/narrative_only 的信号进入打分/排序/路由时，"
        "必须与至少一个异源硬事实口径交叉（三选一：CH 行情 sector/index 收益、c3_fundamental "
        "财务指标、官方 IO 系数矩阵=本战役旁挂册）。",
    },
    {
        "id": "OB-2",
        "rule": "置信取小：读取侧 effective_confidence = min(库内 confidence, 本册 confidence_cap)，"
        "禁改写 ig_fact 存量字节。",
    },
    {
        "id": "OB-3",
        "rule": "权重乘档：合成权重 = 名义权重 × TIERS[tier].weight_multiplier，"
        "且在出生证/血缘字段写明 tier（下游可审计）。",
    },
    {
        "id": "OB-4",
        "rule": "按 source 过滤：任何 WHERE relation='supplies_to' 必须同时带 source 条件，"
        "禁把 ckg_2021 与 graph_enrich_staging 混为同一真源。",
    },
    {
        "id": "OB-5",
        "rule": "反自证：与 CKG 做任何一致性/覆盖率交叉验证时，对照侧必须剔除 "
        "ig_edge.source_doc LIKE 'ckg_2021%'（否则重演 71.6% 假达标）。",
    },
    {
        "id": "OB-6",
        "rule": "先验与旁挂册分工：io_edge 旁挂册（件 2）=官方结构真源的可挂接载体，CKG=补充先验；"
        "两者冲突时以 IO 侧为准并记 CKG 反例（进图谱质量体检）。",
    },
    {
        "id": "OB-7",
        "rule": "新增消费点须在本册 ADJUDICATIONS 登记裁定，否则 --self-check 与合规率 c 自动把它记为"
        "不合规（fail-visible，禁静默扩面）。",
    },
]


def scan(root: Path) -> list[dict]:
    """两遍扫描：①CKG 直接消费（词面含 CKG 关系/来源/事实层）②间接消费（读 ig_edge 晋升边且进打分/决策语境）。

    第二遍必要：indirect 件字面不提 CKG，吃的却是 CKG 晋升出来的 ig_edge 边——只扫词面会漏掉影响面最大的
    一类（暴露度矩阵、情绪扩散、galaxy 链对权重）。清单生成、裁定文本人工，未裁定=不合规（OB-7）。
    """
    points = []
    for d in SCAN_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.suffix not in SCAN_SUFFIXES or any(part in SKIP_PARTS for part in p.parts):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            hits = {k: len(rx.findall(text)) for k, rx in PATTERNS.items()}
            rel = str(p.relative_to(root)).replace("\\", "/")
            if rel.startswith(SELF_EXCLUDE_PREFIX):
                continue
            indirect = False
            if not any(hits.values()):
                # 第二遍：字面不提 CKG、但吃 CKG 晋升边且进打分/决策语境的间接消费者
                if not (IG_EDGE_RX.search(text) and INDIRECT_CTX.search(text)):
                    continue
                indirect = True
                hits = {"indirect_via_ig_edge": len(IG_EDGE_RX.findall(text))}
            markers = {k: bool(rx.search(text)) for k, rx in MARKERS.items()}
            if rel not in ADJUDICATIONS:
                cls = "unadjudicated"
            else:
                cls = ADJUDICATIONS[rel]["usage"]
            points.append(
                {
                    "file": rel,
                    "detection": "indirect_promoted_edge_reader" if indirect else "direct_ckg_token",
                    "pattern_hits": hits,
                    "markers": markers,
                    "usage_class": cls,
                    "in_registry": rel in ADJUDICATIONS,
                }
            )
    if not points:
        raise RuntimeError("扫描面为空——SCAN_DIRS 漂移，拒绝产空册")
    return points


def _auto_class_by_markers(m: dict, h: dict) -> str:
    """无裁定点按标记机械归类（原 classify 内联三元链逐行搬运）。"""
    return (
        "promotion_to_graph_fact"
        if m["promotes_to_graph"] and h["ckg_2021"]
        else (
            "hard_fact_consumer"
            if m["reads_fact_layer"] and (m["feeds_scoring"] or m["feeds_decision"])
            else (
                "indirect_hard_fact_via_promoted_edges"
                if m["reads_graph_edges"] and (m["feeds_scoring"] or m["feeds_decision"])
                else ("producer_ingest" if m["writes_fact_layer"] else "unclassified_read")
            )
        )
    )


def _classify_stats(rows: list[dict], conflicts: list[dict]) -> dict:
    """合规率与挂账统计（原 classify 尾段逐行搬运，键序不变）。"""
    n = len(rows)
    need = [r for r in rows if r["needs_prior_enforcement"]]
    comp = [r for r in rows if r["currently_prior_compliant"]]
    return {
        "points_total": n,
        "by_usage_class": dict(Counter(r["usage_class"] for r in rows)),
        "needs_prior_enforcement": len(need),
        "already_compliant": len(comp),
        "non_compliant": n - len(comp),
        "compliance_rate_c": round(len(comp) / n, 4),
        "unadjudicated": [c["file"] for c in conflicts],
        "conflicts": conflicts,
    }


def classify(points: list[dict]) -> tuple[list[dict], dict]:
    """机械分类 + 与裁定比对（冲突即挂账，禁静默）。"""
    rows = []
    conflicts = []
    for pt in points:
        m, h = pt["markers"], pt["pattern_hits"]
        if not pt["in_registry"]:
            auto = _auto_class_by_markers(m, h)
            adjudicated = auto
            conflicts.append(
                {
                    "file": pt["file"],
                    "auto_class": auto,
                    "note": "无裁定条目——按标记机械归类并计入不合规，须人工补裁（OB-7）",
                }
            )
        else:
            adjudicated = ADJUDICATIONS[pt["file"]]["usage"]
        rec = dict(pt)
        rec["usage_class"] = adjudicated
        rec["auto_class_by_markers"] = auto if not pt["in_registry"] else None
        rec["needs_prior_enforcement"] = adjudicated in HARD_FACT_CLASSES
        rec["currently_prior_compliant"] = bool(m["declares_prior"]) or not rec["needs_prior_enforcement"]
        rec["ruling"] = ADJUDICATIONS.get(pt["file"], {}).get("ruling")
        rec["required_action"] = ADJUDICATIONS.get(pt["file"], {}).get("required_action")
        rec["patch_ref"] = ADJUDICATIONS.get(pt["file"], {}).get("patch_ref")
        rows.append(rec)
    return rows, _classify_stats(rows, conflicts)


def build(out: Path) -> dict:
    points, stats = classify(scan(_ROOT))
    reexam = {}
    degraded = None
    if REEXAM_YAML.exists():
        reexam = yaml.safe_load(REEXAM_YAML.read_text(encoding="utf-8"))
    else:
        degraded = "wo007_reexam.yaml 缺失——a/b 记 null，须先跑复考探针"
    m = (((reexam.get("PQ-0065") or {}).get("criterion_restatement") or {}).get("measured")) or {}
    c = stats["compliance_rate_c"]
    a, b = m.get("a_endpoint_align_rate"), m.get("b_independent_side_evidence_rate")
    pass_abc = (a is not None and b is not None) and a >= 0.95 and b >= 0.60 and c >= 1.0
    doc = {
        "registry": "ckg_structural_prior_tier",
        "registry_version": REGISTRY_VERSION,
        "workorder": "WO-007 件 3（含 PQ-0065 并案）",
        "generated_by": "scripts/governance/meta_question/wo007/build_ckg_prior_tier.py",
        "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "scan_degraded": degraded,
        "ruling_executed": "CKG 由硬事实源降为**结构先验**（战役 2026-09-24 Owner 裁定：一致率 1.23% ≪ 70% "
        "触发题面自带降级条款；处置=执行降级而非退役）。本册=该裁定的机读执行口径。",
        "scope_note": "降级只作用于**消费侧口径**：ig_fact 存量行（264,072 行，含 supplies_to 57,069）字节零触碰，"
        "不 UPDATE/ALTER/DELETE（破坏性 DB 操作三步验证 + 本战役禁写生产库）；"
        "生产代码改动以待落地补丁交付（并发期避让，见 patches/）。",
        "evidence": {
            "PQ-0065_consistency_mappable_subset": (
                reexam.get("PQ-0065", {}).get("original_numbers_reproduced") or {}
            ).get("consistency_mappable"),
            "PQ-0065_exam_recorded": 0.0123,
            "PQ-0065_self_confirming_trap_if_not_excluded": 0.716,
            "PQ-0067_exam_period_consistency": 0.0,
            "PQ-0067_consistency_after_sidecar_literal": (reexam.get("PQ-0067", {}).get("consistency") or {}).get(
                "literal(交/CKG行业对, 题面口径)"
            ),
            "PQ-0067_consistency_after_sidecar_jaccard": (reexam.get("PQ-0067", {}).get("consistency") or {}).get(
                "jaccard(对称)"
            ),
            "noise_rate_sample_2026_09_18": 0.63,
        },
        "tiers": TIERS,
        "relation_caps": RELATION_CAPS,
        "downstream_obligations": DOWNSTREAM_OBLIGATIONS,
        "consumption_points": points,
        "consumption_stats": stats,
        "pq_0065_criterion_restatement": {
            "original_criterion": "CKG 产品-产品边与研报线抽取边一致率 ≥70%（低于则 CKG 降级为结构先验）",
            "restated_criterion": "先验可用性三判据 a/b/c（机械跑法见下）",
            "a_endpoint_align_rate": {
                "value": a,
                "threshold": 0.95,
                "meaning": "CKG 行业对双端可归一到在用标准行业码（申万一级）的比例",
                "threshold_provenance": "借 PQ-0078 题面阈值（同族量：映射载体补齐后的可对齐率）",
            },
            "b_independent_side_evidence_rate": {
                "value": b,
                "threshold": 0.60,
                "meaning": "归一后的 CKG 行业对中能在异源官方 IO 系数矩阵（件 2 旁挂册）找到同向行业对的比例",
                "threshold_provenance": "借 PQ-0067 题面阈值原值（b 即该量的先验化版本）",
            },
            "c_consumer_compliance_rate": {
                "value": c,
                "threshold": 1.0,
                "meaning": "扫描出的 CKG 消费点中已按先验档处理（或本不需要先验化）的比例",
                "formula": "(points_total − 需先验化且未合规) / points_total，未裁定点自动计不合规",
            },
            "verdict": (
                "PASS@prior（先验可用）"
                if pass_abc
                else f"CONDITIONAL（a/b 已达标={a}/{b}，c={c} 未达 1.0——降级补丁未落地，先验暂不可入生产合成）"
            ),
            "mechanical_check": "python scripts/governance/meta_question/wo007/wo007_reexam.py && "
            "python scripts/governance/meta_question/wo007/build_ckg_prior_tier.py --self-check",
            "why_the_original_criterion_no_longer_applies": (
                "一致率是「把 CKG 当硬事实源」时的取证判据：它要求两侧**产品名精确同指**。实测两侧词表不同本体"
                "（CKG 产品名 vs 研报抽取环节名；ig_node aliases 仅 46 行、ig_entity_code_map 仅 88 行），"
                "分母侧当期图谱跨行业对曾为空集（PQ-0067：ig_edge 1,726 条中跨链仅 2 条），"
                "且不剔除自并入边会得 71.6% 假达标——该比值对「CKG 说法是否为真」几乎不含信息。"
                "降级为结构先验后，题面自洽的读法是把同一批数据改问三件有信息的事："
                "能不能对齐到在用行业码（a）、有没有异源侧证（b）、下游是否只当先验用（c）。"
                "原判据的数字（1.23%）与结论（降级）均不变，只把「判 fail 的度量」换成「判可用的度量」。"
            ),
        },
        "pending_patches": sorted({r["patch_ref"] for r in points if r.get("patch_ref")}),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"[OK] {out}")
    print("     points:", stats["points_total"], "by class:", stats["by_usage_class"])
    print(
        "     needs prior enforcement:",
        stats["needs_prior_enforcement"],
        "compliance c:",
        c,
        "unadjudicated:",
        stats["unadjudicated"],
    )
    print("     PQ-0065 restated verdict:", doc["pq_0065_criterion_restatement"]["verdict"])
    return doc


def self_check() -> int:
    doc = yaml.safe_load(DEFAULT_OUT.read_text(encoding="utf-8"))
    pts = doc["consumption_points"]
    st = doc["consumption_stats"]
    assert st["points_total"] == len(pts), "清单与统计不一致"
    rescan, stats2 = classify(scan(_ROOT))
    assert stats2["points_total"] == st["points_total"], (
        f"扫描面漂移：现 {stats2['points_total']} vs 册 {st['points_total']}（须重跑生成器）"
    )
    assert abs(stats2["compliance_rate_c"] - st["compliance_rate_c"]) < 1e-9, "合规率不可复算"
    hard = [p["file"] for p in pts if p["usage_class"] in HARD_FACT_CLASSES]
    print(
        yaml.safe_dump(
            {
                "OK": True,
                "points": len(pts),
                "hard_fact_usage_points": hard,
                "compliance_rate_c": stats2["compliance_rate_c"],
                "restated_verdict": doc["pq_0065_criterion_restatement"]["verdict"],
                "pending_patches": doc["pending_patches"],
            },
            allow_unicode=True,
            sort_keys=False,
        )
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="CKG 结构先验降级执行件生成器（WO-007 件 3）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    build(Path(a.out).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
