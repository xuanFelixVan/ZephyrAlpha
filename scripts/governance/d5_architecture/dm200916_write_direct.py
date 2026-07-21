# [BLUEPRINT] MOD-GOV-dm200916_write_direct
# [MODULE]# [MODULE] scripts.governance.d5_architecture.dm200916_write_direct
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""从 depgraph (PostgreSQL) 派生 architecture_model/index.yaml。

治本改造（2026-06-29）：
- 原脚本是一次性写入脚本，硬编码 52域 + §2.1 裁定语境，会覆盖手工修复
- 现改为真正的派生脚本：从 depgraph (PostgreSQL) 读取域列表，动态生成 index.yaml
- 不再生成 index.md 和 capability_heatmap.yaml（含手工内容，应手工维护）
- 域数用 f-string 动态生成（{len(domains)}域），消除硬编码数字漂移源

v3.0.2 融合版（2026-06-30 双树合并治本）：
- 模板从 v3.0.1（EA 树 11 partitions）升级为 v3.0.2（根树 12 partitions + b_track 12 模块 + governance）
- BASE 路径从 EA 树改为根树 architecture_model/
- domains path 从 ../../../../data/databases/depgraph.db（EA 树相对）改为 ../data/databases/depgraph.db（根树相对）
- shared path 从 layers/shared.yaml 改为 layers/b_shared.yaml
- query_hints 中 cross-cutting 规范化为 cross_cutting

派生范围：
- index.yaml 的 domains 列表 + global_stats.total_domains（从 depgraph (PostgreSQL) 派生）
- index.yaml 的其他部分（partitions, b_track, query_hints, id_conventions, governance）是手工模板（不变）

不派生的文件（手工维护）：
- index.md：含责任声明、物理分类说明等手工内容（注：根树不允许 .md，人读视图在 docs/ 树）
- cross_cutting/capability_heatmap.yaml：含 maturity_score 等手工评估数据

循环安全：本脚本不修改 depgraph (PostgreSQL)，可被 reconciler 自动触发。
"""
import sys
from pathlib import Path

__manifest__ = """
args: []
description: 从 depgraph (PostgreSQL) 派生 architecture_model/index.yaml。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

BASE = REPO_ROOT / "architecture_model"

# 查询域列表（真源：depgraph (PostgreSQL) domains 表）
conn = get_depgraph_pg_connection(autocommit=True)
rows = conn.execute("""
    SELECT domain_id, domain_name, layer_id
    FROM domains
    ORDER BY domain_id
""").fetchall()
conn.close()

domains = [(r["domain_id"], r["domain_name"], r["layer_id"] or "") for r in rows]
domain_count = len(domains)
print(f"域总数: {domain_count}")

# 生成 index.yaml 内容（domains 列表从 PG 派生，其他部分手工模板 v3.0.2 融合版）
yaml_content = f"""# v3.0.2: 融合版（EA v3.0.1 域视图 + 根树 v2.0.0 b_track 施工视图 + governance）
# 双树合并为单树（2026-06-30 治本）：architecture_model/ 是唯一架构模型存储位置。
# c_track（14层 l00-l13）已废弃：§2.1 裁定 14 层降级为域属性，物理分类由 depgraph domains 表定义。
# 本文件由 dm200916_write_direct.py 从 depgraph (PostgreSQL) 派生，禁止手工编辑 domains 列表
module_id: MOD-GOVERNANCE
schema_version: '3.0.2'
system:
  name: ZephyrAlpha
  description: 个人量化交易系统
  architecture_style: domain_driven_event_driven_polyglot

governance:
  canonical: true
  derives_from: "YAML canonical SSoT 铁律"
  conflict_rule: "YAML 为准，Markdown 视图同步更新"
  gate_alignment: "GATE-A 代码↔YAML 对齐"
  domains_source: >
    domains 列表由 dm200916_write_direct.py 从 depgraph domains 表派生，禁止手编。
    改 depgraph 后由 GATE-ARCH-MODEL reconciler 自动重生。

# === 分区管理约定（Partition Management Convention）===
# {domain_count}域是唯一物理分类体系（depgraph domains表），4值（L0_infrastructure/L1_foundation/L2_domain/L3_application）是域的layer_id属性枚举。
# AI找模块只有一条路：按域找。
# b_track 是横切基础设施模块的施工视图（代码目录对齐），独立于域分类。

partitions:
# === {domain_count}域索引（物理分类唯一真源：depgraph domains表）===
- id: domains
  path: depgraph (PostgreSQL)
  description: >
    {domain_count}域物理分类唯一真源。
    查询命令: python scripts/governance/extract_depgraph.py --summary
    4值（L0_infrastructure/L1_foundation/L2_domain/L3_application）是域的layer_id属性枚举。

# === 横切关注点分区（非业务分类）===
- id: shared
  path: layers/b_shared.yaml
  description: 跨域公共契约与基础能力
- id: frontend
  path: frontend/frontend_model.yaml
  description: 前端独立平台 FE-L1~L4
  status: planned
- id: scripts
  path: scripts/scripts_model.yaml
  description: 治理/审计/部署脚本
  status: planned
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
  status: planned
- id: shared-infra
  path: infra/shared_infra.yaml
  description: 跨域共享基础设施
  status: planned

# === b_track 横切基础设施模块（施工视图，代码目录对齐）===
- id: b_track
  description: 横切基础设施模块施工视图（context_engine/core/db 等代码模块对齐登记）
  modules:
  - id: context_engine
    name: Context Engine (CE)
    path: layers/b_context_engine.yaml
    status: implemented
    description: 上下文四阶段流水线：build→compress→validate→inject
  - id: core
    name: Core
    path: layers/b_core.yaml
    status: implemented
    description: 蓝图分解器 + TaskCard 核心模型
  - id: db
    name: Database
    path: layers/b_db.yaml
    status: implemented
    description: 元数据持久化层（SQLite + PostgreSQL）+ 原子事务管理器
  - id: feedback_loop
    name: Feedback Loop Engine (FLE)
    path: layers/b_feedback_loop.yaml
    status: implemented
    description: 系统自调节闭环：collect→detect→dispatch
  - id: gates
    name: Gates
    path: layers/b_gates.yaml
    status: implemented
    description: 门禁引擎、断路器、契约模板管理器
  - id: kb
    name: Knowledge Base
    path: layers/b_kb.yaml
    status: implemented
    description: 知识生命周期管理：摄取→分析→提取→验证→激活
  - id: llm_security
    name: LLM Security Gateway (LSG)
    path: layers/b_llm_security.yaml
    status: implemented
    description: LLM 四层安全防御：输入/System Prompt/输出/Pattern
  - id: mcp
    name: MCP Servers
    path: layers/b_mcp.yaml
    status: implemented
    description: MCP 协议服务端：task_manager/gate_engine/knowledge_base 等
  - id: orchestrator
    name: Agent Orchestrator (Orc)
    path: layers/b_orchestrator.yaml
    status: implemented
    description: 任务生命周期 + Agent 调度 + 沙箱执行 + 幻觉检测
  - id: pipeline
    name: Pipeline
    path: layers/b_pipeline.yaml
    status: implemented
    description: M1-M11 双管线：生产管线(M1-M5) + 审计管线(M6-M11)
  - id: shared
    name: Shared
    path: layers/b_shared.yaml
    status: implemented
    description: 跨层共享基础设施：契约、工具、不可变核心
  - id: vector_memory
    name: Vector Memory Service (VMS)
    path: layers/b_vector_memory.yaml
    status: skeleton
    description: 向量化存储与检索：ChromaDB + BGE-M3 ONNX（代码以骨架为主，部分能力由 kb/ 过渡承担）

# === {domain_count}域清单（从depgraph派生，禁止手工编辑）===
domains:
"""
for domain_id, domain_name, layer_id in domains:
    if layer_id:
        yaml_content += f"- id: {domain_id}\n  name: {domain_name}\n  layer_id: {layer_id}\n"
    else:
        yaml_content += f"- id: {domain_id}\n  name: {domain_name}\n  layer_id:\n"

yaml_content += f"""
global_stats:
  total_domains: {domain_count}
  total_partitions: 12
  b_track_modules: 12
  b_track_implemented: 11
  b_track_skeleton: 1
  notes: >
    {domain_count}域唯一物理分类体系，14层是域的layer_id属性枚举。
    b_track 12横切基础设施模块（context_engine/core/db等），implemented 11 + skeleton 1(vector_memory)。
    结构化数据从depgraph派生，禁止在MD中硬编码会变化的数字。
  last_updated: '2026-06-30'

query_hints:
- question: 系统有哪些域？
  answer: {domain_count}域，见domains列表，真源为depgraph domains表
- question: 某域有哪些模块？
  answer: "查询depgraph: python scripts/governance/extract_depgraph.py --domains <域ID>"
- question: 模块间的依赖关系？
  answer: "查询depgraph: python scripts/governance/extract_depgraph.py --paths"
- question: 为什么这样分域？
  answer: 读architecture_upgrade_discussion.md（域分类体系背景）
- question: 不变量/安全红线？
  answer: 读cross_cutting/invariants.yaml
- question: 运行平面分布？
  answer: 读cross_cutting/runtime_planes.yaml
- question: 系统能力成熟度？
  answer: 读cross_cutting/capability_heatmap.yaml（{domain_count}域×10能力域矩阵）
- question: 前端有哪些模块？
  answer: 读frontend/frontend_model.yaml
- question: 治理/审计脚本有哪些？
  answer: 读scripts/scripts_model.yaml
- question: 跨域公共契约？
  answer: 读layers/b_shared.yaml
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
  - prefix: D_{{NAME}}
    scope: depgraph domains表
    example: D_MKT_DATA
    note: "域ID是唯一物理分类标识（全大写+下划线）"
"""

# 直接写入 index.yaml
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

# 治本说明：不生成 index.md 和 capability_heatmap.yaml
# - index.md：根树不允许 .md（directory_contract.yaml 强制），人读视图在 docs/ 树
# - cross_cutting/capability_heatmap.yaml：含 maturity_score 等手工评估数据，手工维护
# 如需重生这两个文件，应手工编辑或新建专门的派生生成器（区分框架派生 vs 数据手工）
