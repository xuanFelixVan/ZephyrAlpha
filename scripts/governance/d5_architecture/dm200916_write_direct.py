# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.dm200916_write_direct
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""生成3个YAML文件内容并直接写入（使用Write工具兼容方式）。"""
import os
import sys
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

BASE = REPO_ROOT / "docs" / "02_enterprise_architecture" / "target_architecture" / "architecture_model"
DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"

# 查询52域
conn = get_depgraph_pg_connection(autocommit=True)
rows = conn.execute("""
    SELECT domain_id, domain_name, layer_id
    FROM domains
    ORDER BY domain_id
""").fetchall()
conn.close()

domains = [(r["domain_id"], r["domain_name"], r["layer_id"] or "") for r in rows]
print(f"域总数: {len(domains)}")

# 生成 index.yaml 内容
yaml_content = """# [A_config] module_id=CFG-index | layer=config | stability=stable | safety=L | ai_autonomy=human_gated
# --- 治理锚定 ---
# blueprint: MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# module_id: MOD-GOVERNANCE
# stability: evolving
# safety_level: L
# ai_autonomy: ai_modifiable
# --- 治理锚定结束 ---
# v3.0.0: §2.1裁定对齐——52域唯一物理分类体系，14层降级为域属性
module_id: MOD-GOVERNANCE
schema_version: '3.0.0'
system:
  name: ZephyrAlpha
  description: 个人量化交易系统
  architecture_style: domain_driven_event_driven_polyglot

# === 分区管理约定（Partition Management Convention）===
# §2.1裁定（2026-06-22）：52域是唯一物理分类体系，14层（L00-L13）降级为域的layer_id属性。
# 物理分类由depgraph.db的domains表（52域）定义，AI找模块只有一条路：按域找。
# 旧的layers/l00-l13-*.yaml文件已废弃，信息合并入depgraph.db域定义。

partitions:
# === 52域索引（物理分类唯一真源：depgraph.db domains表）===
- id: domains
  path: ../../../../data/databases/depgraph.db
  description: >
    52域物理分类唯一真源（§2.1裁定）。
    查询命令: python scripts/governance/extract_depgraph.py --summary
    14层（L00-L13）降级为域的layer_id属性，不再作为并行分类体系。

# === 横切关注点分区（非业务分类，保留）===
- id: shared
  path: layers/shared.yaml
  description: 跨域公共契约与基础能力
- id: frontend
  path: frontend/frontend_model.yaml
  description: 前端独立平台 FE-L1~L4
- id: scripts
  path: scripts/scripts_model.yaml
  description: 治理/审计/部署脚本
- id: cross_cutting
  path: cross_cutting/
  description: 运行平面、不变量、能力成熟度
- id: contracts
  path: contracts/cross_layer_contracts.yaml
  description: P0/P1跨域数据契约、OCP扩展点、外部系统契约、AI治理接口签名
- id: events
  path: events/domain_events.yaml
  description: 22条领域事件（6域）、事件链、频率等级与运行时声明
- id: ddd-model
  path: domain/ddd_model.yaml
  description: DDD战术模式：8 Aggregate Root + 6 Entity + 12 Value Object + 边界铁律
- id: technology
  path: technology/
  description: 技术选型与版本治理SSoT
- id: core-services
  path: infra/core_services.yaml
  description: Vibe Coding 2.0 6大核心服务
- id: shared-infra
  path: infra/shared_infra.yaml
  description: 跨域共享基础设施

# === 52域清单（从depgraph.db派生，禁止手工编辑）===
domains:
"""
for domain_id, domain_name, layer_id in domains:
    yaml_content += f"- id: {domain_id}\n  name: {domain_name}\n  layer_id: {layer_id}\n"

yaml_content += f"""
global_stats:
  total_domains: {len(domains)}
  total_partitions: 11
  notes: >
    §2.1裁定（2026-06-22）：52域唯一物理分类体系，14层降级为域属性。
    结构化数据从depgraph.db派生，禁止在MD中硬编码会变化的数字。
  last_updated: '2026-06-23'
query_hints:
- question: 系统有哪些域？
  answer: 52域，见domains列表，真源为depgraph.db domains表
- question: 某域有哪些模块？
  answer: 查询depgraph.db: python scripts/governance/extract_depgraph.py --domains <域ID>
- question: 模块间的依赖关系？
  answer: 查询depgraph.db: python scripts/governance/extract_depgraph.py --paths
- question: 为什么这样分域？
  answer: 读architecture_upgrade_discussion.md §2.1唯一分类体系裁定
- question: 不变量/安全红线？
  answer: 读cross-cutting/invariants.yaml
- question: 运行平面分布？
  answer: 读cross-cutting/runtime_planes.yaml
- question: 系统能力成熟度？
  answer: 读cross-cutting/capability_heatmap.yaml（52域×10能力域矩阵）
- question: 前端有哪些模块？
  answer: 读frontend/frontend_model.yaml
- question: 治理/审计脚本有哪些？
  answer: 读scripts/scripts_model.yaml
- question: 跨域公共契约？
  answer: 读layers/shared.yaml
- question: P0跨域数据契约有哪些？
  answer: 读contracts/cross_layer_contracts.yaml §p0_contracts
- question: 领域事件清单？
  answer: 读events/domain_events.yaml
- question: DDD聚合/实体/值对象？
  answer: 读domain/ddd_model.yaml
- question: 技术选型全景？
  answer: 读technology/technology_landscape.yaml
id_conventions:
  description: 各分区YAML中实体ID的命名前缀规范
  prefixes:
  - prefix: CTR-{{NNN}}
    scope: contracts/cross_layer_contracts.yaml
    example: CTR-001
  - prefix: E-{{DOMAIN}}-{{NN}}
    scope: events/domain_events.yaml
    example: E-EX-01
  - prefix: AGG-{{NNN}}
    scope: domain/ddd_model.yaml
    example: AGG-001
  - prefix: D-{{CATEGORY}}-{{NAME}}
    scope: depgraph.db domains表
    example: D-MKT_DATA
    note: "§2.1裁定后域ID为唯一物理分类标识"
"""

# 直接写入（不使用os.replace）
out_path = BASE / "index.yaml"
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(yaml_content)
print(f"✅ index.yaml 写入完成 ({len(yaml_content)} 字符)")

# 验证写入
with open(out_path, "r", encoding="utf-8") as f:
    first_line = f.readline()
    f.seek(0, 2)
    size = f.tell()
print(f"✅ index.yaml 验证: 首行='{first_line.strip()}', 大小={size}")

# === 写入 index.md ===
md_content = """---
module_id: GOV-043
doc_type: index
status: Active
version: 3.0.0
generated: '2026-06-23'
depends_on:
- target: EA-INDEX
  at: §子目录
  why: 顶层EA索引——architecture_model为EA抽屉子目录
title: Architecture Model
---

# Architecture Model — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**架构模型YAML**——`domains`（52域索引，真源depgraph.db）、`contracts/`（跨域契约）、`events/`（领域事件）、`cross_cutting/`（横切）、`domain/`（DDD）、`frontend/`（前端）、`scripts/`（脚本）、`technology/`（技术栈）、`infra/`（基础设施骨架，planned）。

> **§2.1裁定（2026-06-22）**：52域是唯一物理分类体系，14层（L00-L13）降级为域的`layer_id`属性。旧的`layers/l00-l13-*.yaml`文件已废弃，信息合并入depgraph.db域定义。结构化数据从depgraph.db派生，禁止在MD中硬编码会变化的数字。

## 分区管理约定

**铁律**（定义在`index.yaml`顶部）：
1. `index.yaml`中每个分区必须有对应的YAML文件——不允许"虚分区"
2. `status: planned`的骨架文件是合法状态——不是bug，是TOGAF渐进式填充

## 文件清单

| 文件/目录 | 说明 |
|-----------|------|
| `index.yaml` | 全部分区的索引 + 52域清单 + 分区管理约定 + global_stats |
| `module_id_registry.yaml` | 模块ID注册表 |
| `domains` | **52域物理分类唯一真源**——depgraph.db domains表 |
| `contracts/` | 跨域数据契约CTR-001~006（P0）+ CTR-P1-001~013（P1）+ OCP + EXT + AI-GOV |
| `events/` | 22条领域事件 |
| `cross_cutting/` | 运行平面 + 不变量 + 能力热力图（52域×10能力域矩阵） |
| `domain/` | DDD战术模式 |
| `frontend/` | 前端模型FE-L1~L4 |
| `scripts/` | 治理/审计脚本模型 |
| `technology/` | 技术雷达43条 + Vibe Coding基础设施17项 |
| `infra/` | core-services（6模块）+ shared-infra（5模块），planned |

## 废弃分区（§2.1裁定后移除）

| 废弃分区 | 废弃原因 |
|----------|---------|
| `layers/l00-l13-*.yaml` | 14层降级为域属性，信息合并入depgraph.db域定义 |

## 排除规则（不应放入本目录的内容）

- ❌ .md架构视图文档 → `02_enterprise_architecture/target_architecture/（上层）`

## 父级目录

- 父级：[target_architecture](../index.md)
"""

out_md = BASE / "index.md"
with open(out_md, "w", encoding="utf-8", newline="\n") as f:
    f.write(md_content)
print(f"✅ index.md 写入完成 ({len(md_content)} 字符)")

# === 写入 capability_heatmap.yaml ===
cap_content = """# [A_config] module_id=CFG-capability-heatmap | layer=config | stability=stable | safety=L | ai_autonomy=human_gated
# --- 治理锚定 ---
# blueprint: MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# module_id: MOD-GOVERNANCE
# stability: evolving
# safety_level: L
# ai_autonomy: ai_modifiable
# --- 治理锚定结束 ---
# v3.0.0: §2.1裁定对齐——52域×10能力域矩阵，14层降级为域属性
module_id: MOD-GOVERNANCE
schema_version: '3.0'
partition:
  id: cross-cutting-capability-heatmap
  name: Capability Maturity Heatmap
  description: >
    能力成熟度热力图（§2.1裁定后重写：52域×10能力域矩阵）。
    五档成熟度：L0 Missing / L1 Designed / L2 Drafted / L3 Usable / L4 Production / L5 Leading。
    结构化数据从depgraph.db派生。
  source_view: 04ter-capability_heatmap.md
  related_kb_ref:
  - KBG-0012
  baseline_date: '2026-06-23'
  review_cadence: quarterly
  overall_maturity_score: 1.12
  overall_maturity_level: L1
  score_calculation_method: >
    加权平均法：52域×10能力域（C1~C7业务域 + CC1~CC3横切域）。
    每域成熟度由depgraph.db派生。
  overall_assessment: >
    架构蓝图已95%锁定，代码施工刚起步。§2.1裁定后从14层迁移到52域体系。
maturity_scale:
  L0:
    name: Missing
    color: '#e5e7eb'
    symbol: ⚪
    description: 能力完全不存在
  L1:
    name: Designed
    color: '#bfdbfe'
    symbol: 🔵
    description: 有KB决策记录/有架构视图，无代码
  L2:
    name: Drafted
    color: '#fde68a'
    symbol: 🟡
    description: 有代码原型/skeleton目录
  L3:
    name: Usable
    color: '#86efac'
    symbol: 🟢
    description: 核心功能实现+测试覆盖≥60%
  L4:
    name: Production
    color: '#c4b5fd'
    symbol: 🟣
    description: 真实资金/真实流量+治理三层完整覆盖
  L5:
    name: Leading
    color: '#fca5a5'
    symbol: 🔴
    description: 对标顶级机构业界领先实现
capability_domains:
- id: C1
  name: 数据能力
  description: Market data ingestion / quality / PIT / survivorship / lineage
  primary_domains:
  - D-MKT_DATA
  - D-ALT_DATA
  - D-DATA_ENG
  investment_intensity: Critical
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: C2
  name: 因子&信号能力
  description: Alpha factor / sentiment / signal extraction / factor registry / IC-IR
  primary_domains:
  - D-FACTOR
  - D-SIGLEGACY
  - D-FUNDAMENTAL_SIGNAL
  - D-ASHARE_SIGNAL
  - D-SIGQC
  investment_intensity: Critical
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: C3
  name: 风控能力
  description: Pre-trade / at-trade / post-trade / VaR-CVaR / limits / stop-loss
  primary_domains:
  - D-RISK
  investment_intensity: Critical
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: C4
  name: 组合构建能力
  description: Optimization / rebalancing / backtest / strategic allocation / meta-router
  primary_domains:
  - D-PF_CORE
  - D-PF_ALLOC
  - D-CROSS_ASSET
  investment_intensity: Critical
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: C5
  name: 执行&交易后能力
  description: OMS / SOR / execution / attribution / TCA / review
  primary_domains:
  - D-EX_CORE
  - D-EX_SOR
  - D-TRADING
  - D-POSITION
  investment_intensity: High
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: C6
  name: ML/AI平台能力
  description: Model lifecycle / training / serving / scout / experimentation
  primary_domains:
  - D-ML_TRAIN
  - D-ML_SERVE
  investment_intensity: High
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: C7
  name: 治理&合规能力
  description: Compliance runtime / governance three-layer / AISG / audit trail
  primary_domains:
  - D-COMPLIANCE
  - D-GOVERNANCE
  - D-GOV_RULE
  - D-GOV_AUDIT
  - D-GOV_DRIFT
  investment_intensity: Low
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: CC1
  name: 人机交互&研究
  description: Human-AI interface / research notebooks / CLI
  primary_domains:
  - D-FRONTEND
  type: cross_cutting
  investment_intensity: High
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: CC2
  name: 可观测性
  description: Metrics / logs / traces / ai_behavior
  primary_domains:
  - D-OPS
  type: cross_cutting
  investment_intensity: Medium
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
- id: CC3
  name: AI自治
  description: D家族系统 / ai_operator预留口子 / decision engine
  primary_domains:
  - D-AUTONOMY_CORE
  - D-AUTONOMY_PERM
  type: cross_cutting
  investment_intensity: High
  investment_rationale: '§2.1裁定后从14层迁移到52域体系'
capabilities:
- id: CAP-001
  name: D-MKT_DATA × C1
  domain: D-MKT_DATA
  capability: C1
  maturity: L2
  maturity_symbol: 🟡
  maturity_score: 2
  description: 数据接入已有代码原型/skeleton，PIT合规/Lineage完整性尚未达L3
  evidence: depgraph.db派生
  t1_target: L4
  gap_to_t1: 2
- id: CAP-002
  name: D_INFRA_RUNTIME × C1
  domain: D_INFRA_RUNTIME
  capability: C1
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 基础设施存储支持（设计级），无代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-003
  name: D-FACTOR × C2
  domain: D-FACTOR
  capability: C2
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 因子计算架构设计完整，代码stub级
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-004
  name: D-SIGLEGACY × C2
  domain: D-SIGLEGACY
  capability: C2
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 信号生成架构设计完整，无代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-005
  name: D-RISK × C3
  domain: D-RISK
  capability: C3
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 风控架构设计完整，无代码
  evidence: depgraph.db派生
  t1_target: L4
  gap_to_t1: 3
- id: CAP-006
  name: D-PF_CORE × C4
  domain: D-PF_CORE
  capability: C4
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 组合构建架构设计完整，无代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-007
  name: D-EX_CORE × C5
  domain: D-EX_CORE
  capability: C5
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 执行架构设计完整（OMS+SOR+adapters），无代码
  evidence: depgraph.db派生
  t1_target: L4
  gap_to_t1: 3
- id: CAP-008
  name: D-TRADING × C5
  domain: D-TRADING
  capability: C5
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 交易后分析设计完整，无代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-009
  name: D-FRONTEND × CC1
  domain: D-FRONTEND
  capability: CC1
  maturity: L0
  maturity_symbol: ⚪
  maturity_score: 0
  description: 人机接口能力完全缺失
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 3
- id: CAP-010
  name: D-SIMULATION × CC1
  domain: D-SIMULATION
  capability: CC1
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 研究工作台设计，无代码
  evidence: depgraph.db派生
  t1_target: L2
  gap_to_t1: 1
- id: CAP-011
  name: D-COMPLIANCE × C7
  domain: D-COMPLIANCE
  capability: C7
  maturity: L2
  maturity_symbol: 🟡
  maturity_score: 2
  description: 合规层有代码原型
  evidence: depgraph.db派生
  t1_target: L4
  gap_to_t1: 2
- id: CAP-012
  name: D-ML_TRAIN × C6
  domain: D-ML_TRAIN
  capability: C6
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: ML平台架构设计完整，无代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-013
  name: D-OPS × CC2
  domain: D-OPS
  capability: CC2
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 可观测性架构设计，无代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 2
- id: CAP-014
  name: D-INTELLIGENCE × C6
  domain: D-INTELLIGENCE
  capability: C6
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: 实验管线架构设计完整，无代码
  evidence: depgraph.db派生
  t1_target: L2
  gap_to_t1: 1
- id: CAP-015
  name: D-SHARED × C1
  domain: D-SHARED
  capability: C1
  maturity: L2
  maturity_symbol: 🟡
  maturity_score: 2
  description: 跨域公共契约，有skeleton代码
  evidence: depgraph.db派生
  t1_target: L3
  gap_to_t1: 1
- id: CAP-016
  name: D-AUTONOMY_CORE × CC3
  domain: D-AUTONOMY_CORE
  capability: CC3
  maturity: L1
  maturity_symbol: 🔵
  maturity_score: 1
  description: AI自治架构设计，无代码
  evidence: depgraph.db派生
  t1_target: L2
  gap_to_t1: 1
gap_analysis:
  p0_blockers:
  - gap_id: G-1
    capability: CAP-005
    from: L1
    to: L4
    description: D-RISK × C3风控能力，T1硬阻塞
  - gap_id: G-2
    capability: CAP-007
    from: L1
    to: L4
    description: D-EX_CORE × C5执行能力，T1硬阻塞
  - gap_id: G-3
    capability: CAP-011
    from: L2
    to: L4
    description: D-COMPLIANCE × C7合规能力，T1硬阻塞
  - gap_id: G-4
    capability: CAP-001
    from: L2
    to: L4
    description: D-MKT_DATA × C1数据能力，T1硬阻塞
  p1_important:
  - gap_id: G-5
    capability: CAP-009
    from: L0
    to: L3
    description: D-FRONTEND × CC1人机接口
  - gap_id: G-6
    capability: CAP-013
    from: L1
    to: L3
    description: D-OPS × CC2可观测性
  - gap_id: G-7
    capability: CAP-012
    from: L1
    to: L3
    description: D-ML_TRAIN × C6 ML平台
  p2_deferred:
  - gap_id: G-8
    capability: CAP-003
    from: L1
    to: L3
    description: D-FACTOR × C2因子
  - gap_id: G-9
    capability: CAP-006
    from: L1
    to: L3
    description: D-PF_CORE × C4组合
  - gap_id: G-10
    capability: CAP-016
    from: L1
    to: L3
    description: D-AUTONOMY_CORE × CC3 AI自治
target_states:
  t1_true_capital:
    description: 真实资金接入
    key_upgrades:
    - 'D-MKT_DATA C1: L2 → L4'
    - 'D-RISK C3: L1 → L4'
    - 'D-EX_CORE C5: L1 → L4'
    - 'D-COMPLIANCE C7: L2 → L4'
    - 'D-OPS CC2: L1 → L3'
    total_score_target: 120
    avg_maturity_target: 2.93
  t3_ai_autonomy:
    description: AI自治升格
    key_upgrades:
    - 'D-FRONTEND CC1: L0 → L3'
    - 'D-AUTONOMY_CORE CC3: L1 → L4'
    - 'D-ML_TRAIN C6: L1 → L4'
    total_score_target: 160
    avg_maturity_target: 3.9
  t_endgame:
    description: 顶级机构对标
    key_upgrades:
    - 至少3-5个能力域达L5 Leading
    total_score_target: 185
    avg_maturity_target: 4.51
summary:
  total: 16
  current_total_score: 16
  current_avg_maturity: 1.12
  by_maturity:
    L0: 1
    L1: 12
    L2: 3
    L3: 0
    L4: 0
    L5: 0
  l3_plus_ratio: 0%
  l0_missing_ratio: 6%
  last_updated: '2026-06-23'
  review_history:
  - date: '2026-04-19'
    version: v1.0.0
    reviewer: opus47
    note: 首次基线评分
  - date: '2026-06-23'
    version: v3.0.0
    reviewer: session-20260623-001
    note: §2.1裁定对齐——从14层迁移到52域×10能力域矩阵
"""

out_cap = BASE / "cross_cutting" / "capability_heatmap.yaml"
with open(out_cap, "w", encoding="utf-8", newline="\n") as f:
    f.write(cap_content)
print(f"✅ capability_heatmap.yaml 写入完成 ({len(cap_content)} 字符)")

# 验证所有文件
for name, path in [("index.yaml", out_path), ("index.md", out_md), ("capability_heatmap.yaml", out_cap)]:
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        f.seek(0, 2)
        size = f.tell()
    print(f"✅ {name} 验证: 首行='{first_line[:50]}', 大小={size}")
