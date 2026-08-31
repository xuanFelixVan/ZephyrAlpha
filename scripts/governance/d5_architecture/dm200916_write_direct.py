# [BLUEPRINT] MOD-GOV_DM200916_WRITE_DIRECT
# [MODULE] scripts.governance.d5_architecture.dm200916_write_direct
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
# [TTL] permanent
"""从 depgraph (PostgreSQL) + 物理蓝图文件 派生 architecture_model/index.yaml。

治本改造（2026-07-30，#ARCH-INDEX-005）：
- domains 段：从 depgraph (PostgreSQL) domains 表派生（保留）
- b_track 段：原为脚本内嵌 f-string 手工模板（已漂移：幻影 kb + 漏登
  execution_model/system_telemetry + 硬编码统计数字 + 62↔72 域过期）
  现改为从物理蓝图文件 layers/b_*.yaml 派生（glob + yaml.safe_load）：
  - 物理文件即真源：b_ 前缀 = b_track 成员资格（schema.yaml 约定 track 仅 b_track）
  - 自动消除幻影 kb（无文件）
  - 自动纳入 execution_model/system_telemetry（有文件且 track: b_track）
  - 统计数字动态计算，禁止硬编码
  - 兼容两种 partition 格式（partition 块 / 顶层字段）

历史：
- v3.0.2 融合版（2026-06-30）：双树合并，b_track 12 模块手工模板
- v3.0.3 治本版（2026-07-30）：b_track 从物理文件派生，消除手工模板第二真源

派生范围：
- domains 列表 + global_stats.total_domains（从 depgraph domains 表）
- b_track 模块列表 + global_stats.b_track_*（从 layers/b_*.yaml 物理文件）

不派生（手工维护，静态设计意图）：
- partitions / query_hints / id_conventions / governance

循环安全：本脚本不修改 depgraph，不修改 layers/b_*.yaml，可被 reconciler 自动触发。
"""

import sys
from datetime import date
from pathlib import Path

# noqa: m11-perm-manual-legitimate  M11豁免: 永久派生脚本，由 reconciler/GATE-ARCH-MODEL 按需触发生成 index.yaml，非 cron/daemon/常驻服务
__manifest__ = """
args: []
description: 从 depgraph (PostgreSQL) + 物理蓝图文件 派生 architecture_model/index.yaml。
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
import yaml  # noqa: E402
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

BASE = REPO_ROOT / "architecture_model"


def _derive_domains() -> list[tuple[str, str, str]]:
    """派生1: domains 列表（真源：depgraph (PostgreSQL) domains 表）。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    rows = conn.execute("""
        SELECT domain_id, domain_name, layer_id
        FROM domains
        ORDER BY domain_id
    """).fetchall()
    conn.close()
    return [(r["domain_id"], r["domain_name"], r["layer_id"] or "") for r in rows]


def _derive_b_track_modules() -> list[dict]:
    """派生2: b_track 模块列表（真源：layers/b_*.yaml 物理蓝图文件）。

    治本（2026-07-30，#ARCH-INDEX-005）：b_track 从物理文件派生，消除手工模板第二真源。
    b_ 前缀 = b_track 成员资格（schema.yaml 约定 track 仅 b_track）。
    兼容两种格式：partition 块格式（partition.id/name/track/status）与顶层字段格式
    （顶层 name/human_name/architecture_track/status，如 b_feedback_loop.yaml）。
    """
    b_track_files = sorted((BASE / "layers").glob("b_*.yaml"))
    b_track_modules = []
    for f in b_track_files:
        # 文件名去 b_ 前缀作为 id（物理真源，稳定，不受 partition.id 不一致影响）
        mod_id = f.stem[2:] if f.stem.startswith("b_") else f.stem
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            data = {}
        partition = data.get("partition", {}) if isinstance(data, dict) else {}
        name = partition.get("name") or data.get("human_name") or data.get("name") or mod_id
        status = partition.get("status") or data.get("status") or "unknown"
        description = partition.get("note") or data.get("description") or ""
        if isinstance(description, str):
            description = description.strip().split("\n")[0].strip()
        else:
            description = ""
        b_track_modules.append(
            {
                "id": mod_id,
                "name": name,
                "path": f"layers/{f.name}",
                "status": status,
                "description": description,
            }
        )
    return b_track_modules


def _derive_event_stats() -> tuple[int, int]:
    """派生3: 领域事件统计（真源：events/domain_events.yaml，禁止手写计数避免漂移）。"""
    events_path = BASE / "events" / "domain_events.yaml"
    try:
        events_data = yaml.safe_load(events_path.read_text(encoding="utf-8")) or {}
        events_list = events_data.get("events", []) or []
        event_count = len(events_list)
        event_domain_count = len(
            sorted(set(e.get("domain", "") for e in events_list if isinstance(e, dict) and e.get("domain")))
        )
    except (FileNotFoundError, yaml.YAMLError):
        event_count = 0
        event_domain_count = 0
    return event_count, event_domain_count


def _b_track_yaml_block(b_track_modules: list[dict]) -> str:
    """生成 b_track modules YAML 片段（动态派生，禁止手工编辑）。"""
    lines = []
    for m in b_track_modules:
        lines.append(f"  - id: {m['id']}")
        lines.append(f"    name: {m['name']}")
        lines.append(f"    path: {m['path']}")
        lines.append(f"    status: {m['status']}")
        if m["description"]:
            lines.append(f"    description: {m['description']}")
    return "\n".join(lines)


def main() -> int:
    """Entry point: generate index.yaml from depgraph + physical blueprint files."""
    domains = _derive_domains()
    domain_count = len(domains)
    print(f"域总数: {domain_count}")

    b_track_modules = _derive_b_track_modules()
    b_track_count = len(b_track_modules)
    b_track_implemented = sum(1 for m in b_track_modules if m["status"] == "implemented")
    b_track_under_construction = sum(1 for m in b_track_modules if m["status"] == "under_construction")
    b_track_phase_2_complete = sum(1 for m in b_track_modules if m["status"] == "phase_2_complete")
    b_track_skeleton = sum(1 for m in b_track_modules if m["status"] == "skeleton")
    print(
        f"b_track 模块数: {b_track_count} (implemented={b_track_implemented}, under_construction={b_track_under_construction}, phase_2_complete={b_track_phase_2_complete}, skeleton={b_track_skeleton})"
    )

    event_count, event_domain_count = _derive_event_stats()
    print(f"领域事件: {event_count} 条 / {event_domain_count} 域")

    today = date.today().isoformat()
    b_track_yaml_block = _b_track_yaml_block(b_track_modules)

    # 生成 index.yaml 内容（domains 从 depgraph 派生，b_track 从物理文件派生，其余手工模板）
    yaml_content = f"""# --- 治理锚定 ---
# blueprint: MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §architecture-index
# module_id: MOD-GOVERNANCE
# stability: evolving
# safety_level: L
# ai_autonomy: ai_modifiable
# ttl: permanent
# --- 治理锚定结束 ---
# v3.0.3: 治本版（b_track 从 layers/b_*.yaml 物理蓝图文件派生，消除手工模板第二真源）
# 双树合并为单树（2026-06-30 治本）：architecture_model/ 是唯一架构模型存储位置。
# c_track（14层 l00-l13）已废弃：§2.1 裁定 14 层降级为域属性，物理分类由 depgraph domains 表定义。
# 本文件由 dm200916_write_direct.py 派生，禁止手工编辑 domains 与 b_track 列表：
#   - domains 列表：depgraph (PostgreSQL) domains 表派生
#   - b_track 模块列表：layers/b_*.yaml 物理蓝图文件派生（b_ 前缀即成员资格）
module_id: MOD-GOVERNANCE
schema_version: '3.0.3'
doc_type: register
ttl: permanent
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
    b_track 模块列表从 layers/b_*.yaml 物理文件派生，禁止手编。
    改 depgraph 或 layers/b_*.yaml 后由 GATE-ARCH-MODEL reconciler 自动重生。

# === 分区管理约定（Partition Management Convention）===
# {domain_count}域是唯一物理分类体系（depgraph domains表），4值（L0_infrastructure/L1_foundation/L2_domain/L3_application）是域的layer_id属性枚举。
# AI找模块只有一条路：按域找。
# b_track 是横切基础设施模块的施工视图（物理蓝图文件对齐），独立于域分类。

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
  description: 治理/审计/部署脚本（待建 scripts_model.yaml）
  status: planned
- id: cross_cutting
  path: cross_cutting/
  description: 运行平面、不变量、能力成熟度
- id: contracts
  path: contracts/cross_layer_contracts.yaml
  description: P0/P1跨域数据契约、OCP扩展点、外部系统契约、AI治理接口签名
- id: events
  path: events/domain_events.yaml
  description: {event_count}条领域事件（{event_domain_count}域）、事件链、频率等级与运行时声明
- id: ddd-model
  path: domain/ddd_model.yaml
  description: DDD战术模式：8 Aggregate Root + 6 Entity + 12 Value Object + 边界铁律
- id: technology
  path: technology/
  description: 技术选型与版本治理SSoT
- id: core-services
  description: Vibe Coding 2.0 6大核心服务（待建 infra/core_services.yaml）
  status: planned
- id: shared-infra
  description: 跨域共享基础设施（待建 infra/shared_infra.yaml）
  status: planned

# === b_track 横切基础设施模块（从 layers/b_*.yaml 物理文件派生，禁止手工编辑）===
- id: b_track
  description: 横切基础设施模块施工视图（从 layers/b_*.yaml 物理文件派生，b_ 前缀即成员资格）
  modules:
{b_track_yaml_block}

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
  b_track_modules: {b_track_count}
  b_track_implemented: {b_track_implemented}
  b_track_under_construction: {b_track_under_construction}
  b_track_phase_2_complete: {b_track_phase_2_complete}
  b_track_skeleton: {b_track_skeleton}
  notes: >
    {domain_count}域唯一物理分类体系，4值（L0_infrastructure/L1_foundation/L2_domain/L3_application）是域的layer_id属性枚举。
    b_track {b_track_count}横切基础设施模块（从 layers/b_*.yaml 物理文件派生）。
    结构化数据从depgraph + 物理蓝图文件派生，禁止硬编码会变化的数字。
  last_updated: '{today}'

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
- question: 前端有哪些页面/功能点？
  answer: 读frontend/frontend_map.yaml（第六全景图）
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
    with open(out_path, encoding="utf-8") as f:
        first_line = f.readline()
        f.seek(0, 2)
        size = f.tell()
    print(f"✅ index.yaml 验证: 首行='{first_line.strip()}', 大小={size}")
    return 0


if __name__ == "__main__":
    # 治本（2026-08-18 AI-00 全量复审）：模块级 I/O 移入 main()，消除 import 副作用（S4-C 零副作用铁律）
    sys.exit(main())

# 治本说明：不生成 index.md 和 capability_heatmap.yaml
# - index.md：根树不允许 .md（directory_contract.yaml 强制），人读视图在 docs/ 树
# - cross_cutting/capability_heatmap.yaml：含 maturity_score 等手工评估数据，手工维护
