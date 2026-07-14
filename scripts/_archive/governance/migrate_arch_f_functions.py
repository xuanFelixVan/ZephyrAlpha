# [BLUEPRINT] ARCH-FUNC-DEP-001 | docs/02_enterprise_architecture/core_function_dependency_design.md | §十一
# [MODULE] scripts.governance.migrate_arch_f_functions
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.apply_depgraph
# [CONSUMERS] 架构升级AI session
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 节点创建失败→exit 1; 边创建失败→exit 2; 域迁移失败→exit 3; 事件注册失败→exit 4
# [TESTS] python scripts/governance/migrate_arch_f_functions.py --dry-run
# [TTL] task_bound
"""
阶段1迁移脚本：创建37个F功能设计态节点 + 56条依赖边 + 5个域迁移 + 12个事件注册。

数据真源：docs/02_enterprise_architecture/core_function_dependency_design.md §4.1(边清单) §8.4(节点+域迁移) §7.1(事件)

用法:
  python scripts/governance/migrate_arch_f_functions.py --dry-run    # 预览
  python scripts/governance/migrate_arch_f_functions.py              # 执行
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 治本（2026-06-27）：删除 DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源，未使用）+
# 删除 import sqlite3（P2 迁移后无 sqlite 调用，残留 import）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()。

# 导入 apply_depgraph 的写入锁（含 git 备份门禁 + 物理备份 + 文件锁）
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import apply_depgraph as _ad  # noqa: E402, I001

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402


# ===== §8.4 + §11.5: 37个F功能设计态节点定义 =====
# (F_id, name, path, blueprint_id, domain_id, build_status, layer)
# domain_id: §8.4设计域(18个) 或 §11.5代码域(其余19个)
# build_status: runtime=stable, design=unbuilt, not_found=unbuilt, archived=deprecated

F_FUNCTIONS = [
    # L0 基础设施层（出度0）
    ("F22", "事件总线+共享核心", "F22-event-bus/", "", "D_SHARED", "stable", "L0"),
    ("F25", "数据库集成层", "F25-db-integration/", "", "D_INFRA_OPS", "stable", "L0"),
    ("F26", "运行时集成", "F26-runtime-integration/", "", "D_TRADING", "stable", "L0"),
    # L1 守护层
    ("F21", "IDE健康守护", "F21-ide-health/", "", "D_INFRA_OPS", "stable", "L1"),
    # L2 调度层
    ("F1", "自动驾驶/大脑", "F1-autopilot/", "", "D_TRADING", "stable", "L2"),
    ("F23", "Agent编排器", "F23-agent-orchestrator/", "", "D_AUTONOMY_CORE", "stable", "L2"),
    # L3 控制层
    ("F2", "门禁引擎", "F2-gate-engine/", "", "D_GOV_RULE", "stable", "L3"),
    ("F4", "预算执行器", "F4-budget-engine/", "", "D_OPS", "stable", "L3"),
    ("F7", "LLM安全网关", "F7-llm-gateway/", "", "D_SECURITY", "stable", "L3"),
    ("F8", "RBAC权限", "F8-rbac/", "", "D_SECURITY", "stable", "L3"),
    ("F27", "容量保障", "F27-capacity/", "", "D_INFRA_OPS", "stable", "L3"),
    ("F32", "状态机引擎", "F32-state-machine/", "", "D_AUTONOMY_CORE", "stable", "L3"),
    # L4 执行层
    ("F3", "任务系统", "F3-task-system/", "", "D_GOVERNANCE", "stable", "L4"),
    ("F11", "上下文引擎", "F11-context-engine/", "", "D_SHARED", "stable", "L4"),
    ("F12", "知识库", "F12-knowledge-base/", "", "D_INTEGRATION", "stable", "L4"),
    ("F13", "MCP集群", "F13-mcp-cluster/", "", "D_INTEGRATION", "stable", "L4"),
    ("F14", "管线编排", "F14-pipeline/", "", "D_INTEGRATION", "stable", "L4"),
    ("F24", "Agent Spec/Skill", "F24-agent-spec/", "", "D_AUTONOMY_CORE", "stable", "L4"),
    ("F33", "本地模型", "F33-local-model/", "", "D_INFRA_OPS", "stable", "L4"),
    # L5 治理层
    ("F6", "漂移检测", "F6-drift-detector/", "", "D_GOV_DRIFT", "stable", "L5"),
    ("F15", "自动修复", "F15-auto-fix/", "", "D_INFRA_OPS", "stable", "L5"),
    ("F16", "孤儿审判", "F16-orphan-judge/", "", "D_SECURITY", "stable", "L5"),
    ("F18", "治理脚本", "F18-governance-scripts/", "", "D_GOVERNANCE", "stable", "L5"),
    ("F19", "系统遥测", "F19-telemetry/", "", "D_INFRA_OPS", "stable", "L5"),
    ("F20", "监控统一", "F20-unified-monitor/", "", "D_OPS", "planned", "L5"),
    ("F28", "资产盘点", "F28-asset-inventory/", "", "D_GOVERNANCE", "stable", "L5"),
    ("F29", "语义审计", "F29-semantic-audit/", "", "D_GOVERNANCE", "stable", "L5"),
    ("F30", "红蓝对抗", "F30-red-blue/", "", "D_SECURITY", "stable", "L5"),
    ("F31", "注册表治理", "F31-registry-gov/", "", "D_GOVERNANCE", "stable", "L5"),
    ("F34", "代码去重", "F34-code-dedup/", "", "D_GOVERNANCE", "planned", "L5"),
    ("F35", "文件结构治理", "F35-file-structure/", "", "D_GOVERNANCE", "planned", "L5"),
    ("F36", "审计追踪链", "F36-audit-trail/", "", "D_GOV_AUDIT", "stable", "L5"),
    ("F37", "资源优化", "F37-resource-opt/", "", "D_INFRA_OPS", "stable", "L5"),
    # L6 应急层（入度0）
    ("F5", "升级/A2A", "F5-escalation/", "", "D_GOVERNANCE", "stable", "L6"),
    ("F9", "回滚系统", "F9-rollback/", "", "D_INFRA_OPS", "stable", "L6"),
    ("F10", "模型考试", "F10-model-exam/", "", "D_INTELLIGENCE", "stable", "L6"),
    # 已归档
    ("F17", "交易骨架清理(归档)", "F17-archived/", "", "D_TRADING", "deprecated", "ARCHIVED"),
]


# ===== §4.1: 完整依赖边清单（56条）=====
# (from_F, to_F, dep_type, description)
# dep_type: contract / event / runtime / data

F_EDGES = [
    # L1→L0
    ("F21", "F22", "runtime", "守护进程使用事件总线"),
    # L2→L0/L1
    ("F1", "F21", "runtime", "AutoPilot启动前确认守护进程"),
    ("F1", "F23", "runtime", "AutoPilot调度Agent编排器(同层协作)"),
    ("F1", "F3", "contract", "AutoPilot依赖TaskRepository Protocol(DIP)"),
    ("F1", "F14", "event", "AutoPilot发布pipeline_start事件F14订阅(事件解耦)"),
    ("F23", "F22", "runtime", "Agent编排器使用事件总线"),
    ("F23", "F32", "runtime", "Agent编排器使用状态机引擎"),
    # L3→L0
    ("F4", "F22", "runtime", "预算超限通过事件总线发布事件"),
    ("F8", "F22", "runtime", "RBAC使用共享核心的锁/幂等性"),
    ("F27", "F19", "data", "容量保障使用遥测数据计算SLO"),
    ("F27", "F22", "runtime", "Kill Switch熔断通过事件总线通知"),
    ("F32", "F22", "runtime", "状态机引擎使用共享核心"),
    # L3内部（单向）
    ("F2", "F4", "contract", "门禁校验预算是否超限"),
    ("F2", "F8", "contract", "门禁校验操作权限"),
    ("F7", "F4", "contract", "LLM调用前检查预算"),
    ("F7", "F8", "contract", "LLM调用前校验权限"),
    # L4→L0/L3
    ("F3", "F2", "runtime", "任务流转过门禁"),
    ("F3", "F25", "data", "任务卡持久化到数据库"),
    ("F3", "F12", "data", "任务卡元数据存入知识库"),
    ("F11", "F12", "data", "上下文存储到知识库"),
    ("F12", "F25", "data", "知识库持久化到数据库"),
    ("F13", "F8", "contract", "MCP调用前校验权限"),
    ("F14", "F2", "runtime", "管线阶段过门禁"),
    ("F14", "F22", "runtime", "管线使用事件总线编排"),
    ("F14", "F12", "data", "管线从知识库获取上下文"),
    ("F24", "F8", "contract", "Skill操作前校验权限"),
    ("F24", "F12", "data", "Skill认证数据存入知识库"),
    ("F33", "F7", "runtime", "本地模型经LLM安全网关"),
    # L5→L0/L4
    ("F6", "F12", "data", "漂移检测对比知识库基准"),
    ("F6", "F19", "data", "漂移检测使用遥测数据"),
    ("F6", "F36", "data", "漂移检测写入审计追踪链"),
    ("F15", "F11", "runtime", "修复时获取上下文"),
    ("F15", "F12", "data", "修复知识从知识库获取"),
    ("F16", "F12", "data", "孤儿审判对比知识库"),
    ("F16", "F28", "data", "孤儿审判使用资产盘点数据"),
    ("F18", "F6", "data", "治理脚本使用漂移数据"),
    ("F18", "F19", "data", "治理脚本使用遥测数据"),
    ("F19", "F22", "runtime", "遥测数据通过事件总线流转"),
    ("F20", "F19", "data", "监控统一从遥测获取数据"),
    ("F28", "F25", "data", "资产盘点数据存入数据库"),
    ("F28", "F31", "data", "资产盘点使用注册表治理数据"),
    ("F29", "F12", "data", "语义审计使用知识库"),
    ("F29", "F33", "runtime", "语义审计使用本地模型推理"),
    ("F30", "F22", "runtime", "红蓝验证通过事件总线订阅修复完成"),
    ("F31", "F25", "data", "注册表治理数据存入数据库"),
    ("F34", "F12", "data", "代码去重使用知识库基准"),
    ("F35", "F34", "runtime", "文件结构治理使用去重结果"),
    ("F36", "F25", "data", "审计追踪链持久化到数据库"),
    ("F36", "F22", "runtime", "审计链使用事件总线"),
    ("F37", "F19", "data", "资源优化使用遥测数据"),
    ("F37", "F22", "runtime", "资源优化使用共享核心"),
    # L6→L3（单向，入度0）
    ("F5", "F8", "contract", "委托前校验权限"),
    ("F5", "F9", "runtime", "委托失败触发回滚"),
    ("F9", "F8", "contract", "回滚前校验权限"),
    ("F10", "F7", "runtime", "模型考试经LLM网关"),
    ("F10", "F12", "data", "考试画像存储到知识库"),
]


# ===== §7.1: 12个事件注册 =====
# (event_name, publisher_F, subscriber_F_list, description)

F_EVENTS = [
    ("pipeline_start", "F1", ["F14"], "AutoPilot启动管线F14订阅执行"),
    ("budget_exceeded", "F4", ["F5"], "预算超限触发升级评估"),
    ("drift_detected", "F6", ["F5", "F15"], "漂移检测触发修复/升级"),
    ("pipeline_failed", "F14", ["F9"], "管线失败触发回滚"),
    ("mcp_call_failed", "F13", ["F9"], "MCP调用失败触发回滚"),
    ("fix_completed", "F15", ["F5", "F30"], "自动修复完成触发验证/升级"),
    ("fix_failed", "F15", ["F5"], "自动修复失败触发升级"),
    ("validation_result", "F30", ["F15"], "红蓝验证结果反馈"),
    ("gate_blocked", "F2", ["F6"], "门禁阻断触发漂移检测"),
    ("task_completed", "F3", ["F1", "F6"], "任务完成触发AutoPilot/漂移检测"),
    ("slo_violation", "F27", ["F4"], "SLO违规触发预算降级"),
    ("kill_switch_triggered", "F27", ["F9"], "Kill Switch触发触发回滚"),
]


def _get_f_node_id(conn, f_id: str) -> int | None:
    """查询F功能设计态节点的node_id（按path匹配）。"""
    path = next((f[2] for f in F_FUNCTIONS if f[0] == f_id), None)
    if not path:
        return None
    row = conn.execute("SELECT node_id FROM nodes WHERE path=%s AND design_maturity='design'", (path,)).fetchone()
    return row["node_id"] if row else None


def _domain_exists(conn, domain_id: str) -> bool:
    """检查domain_id在domains表中是否存在。"""
    row = conn.execute("SELECT 1 FROM domains WHERE domain_id=%s", (domain_id,)).fetchone()
    return row is not None


def _edge_exists(conn, from_id: int, to_id: int, dep_type: str) -> bool:
    """检查边是否已存在（幂等）。"""
    row = conn.execute(
        "SELECT 1 FROM edges WHERE from_node_id=%s AND to_node_id=%s AND dep_type=%s AND dep_maturity='design'",
        (from_id, to_id, dep_type),
    ).fetchone()
    return row is not None


def _event_exists(conn, event_name: str) -> bool:
    """检查事件是否已注册（幂等）。"""
    row = conn.execute("SELECT 1 FROM domain_events WHERE name=%s", (event_name,)).fetchone()
    return row is not None


def _detect_cycle_dfs(conn, start: int, target: int) -> bool:
    """DFS检测从start能否到达target（添加start->target会形成环）。"""
    if start == target:
        return True
    visited: set[int] = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        edges = conn.execute(
            "SELECT to_node_id FROM edges WHERE from_node_id=%s AND dep_maturity='design'", (node,)
        ).fetchall()
        for edge_row in edges:
            next_node = edge_row["to_node_id"]
            if next_node == target:
                return True
            if next_node not in visited:
                stack.append(next_node)
    return False


def run_migration(dry_run: bool = True) -> int:
    """执行迁移。返回 exit code（0=成功）。"""
    print(f"{'[DRY RUN] ' if dry_run else ''}阶段1迁移: F1-F37设计态节点+边+域迁移+事件")
    print(f"  节点: {len(F_FUNCTIONS)}  边: {len(F_EDGES)}  事件: {len(F_EVENTS)}")
    print()

    # P2迁移后：depgraph 已迁移到 PostgreSQL，不再检查 .db 文件是否存在
    # ===== DRY RUN: 只读，不获取锁 =====
    if dry_run:
        conn = get_depgraph_pg_connection(autocommit=True)
        _run_checks(conn, print_preview=True)
        conn.close()
        print("\n[DRY RUN] 无写入。执行请去掉 --dry-run。")
        return 0

    # ===== 实际写入: 使用 apply_depgraph 的写入锁 =====
    with _ad._db_write_lock(task="migrate_arch_f_functions"):
        # autocommit=False 以支持 commit/rollback 事务语义
        conn = get_depgraph_pg_connection(autocommit=False)
        try:
            errors = _run_checks(conn, print_preview=False)
            if errors:
                print(f"\n[ABORT] 前置检查发现 {len(errors)} 个错误，放弃写入", file=sys.stderr)
                for e in errors:
                    print(f"  - {e}", file=sys.stderr)
                conn.close()
                return 1

            # STEP 1: 创建/更新37个F功能设计态节点
            f_node_map: dict[str, int] = {}
            created_nodes = 0
            updated_nodes = 0
            for f_id, name, path, bp_id, domain_id, build_status, layer in F_FUNCTIONS:
                # 检查是否已存在
                existing = conn.execute(
                    "SELECT node_id FROM nodes WHERE path=%s AND design_maturity='design'", (path,)
                ).fetchone()
                blueprint_path = f"docs/03_modules/{bp_id}/" if bp_id else ""
                if existing:
                    # 更新
                    conn.execute(
                        """UPDATE nodes SET blueprint_id=%s, domain_id=%s, build_status=%s,
                        blueprint_path=%s
                        WHERE node_id=%s""",
                        (bp_id, domain_id, build_status, blueprint_path, existing["node_id"]),
                    )
                    f_node_map[f_id] = existing["node_id"]
                    updated_nodes += 1
                else:
                    # 新建（P2迁移：PG 要求 node_id 非空，用 DESIGN-{f_id} 生成唯一 PK；
                    # cur.lastrowid → INSERT ... RETURNING node_id）
                    cur = conn.execute(
                        """INSERT INTO nodes (node_id, node_type, path, granularity, domain_id, blueprint_id,
                        build_status, design_maturity, blueprint_path, can_build)
                        VALUES (%s, 'design_node', %s, 'directory', %s, %s, %s, 'design', %s, 1)
                        RETURNING node_id""",
                        (f"DESIGN-{f_id}", path, domain_id, bp_id, build_status, blueprint_path),
                    )
                    f_node_map[f_id] = cur.fetchone()["node_id"]
                    created_nodes += 1
            print(f"[STEP 1] 节点: 新建={created_nodes}  更新={updated_nodes}  总计={len(f_node_map)}")

            # STEP 2: 创建56条依赖边
            created_edges = 0
            skipped_edges = 0
            cycle_blocked = 0
            for from_f, to_f, dep_type, desc in F_EDGES:
                from_id = f_node_map.get(from_f)
                to_id = f_node_map.get(to_f)
                if from_id is None or to_id is None:
                    print(f"  WARN: 边 {from_f}->{to_f} 节点缺失，跳过", file=sys.stderr)
                    continue
                if _edge_exists(conn, from_id, to_id, dep_type):
                    skipped_edges += 1
                    continue
                # DFS循环检测（仅检测design边）
                if _detect_cycle_dfs(conn, to_id, from_id):
                    print(f"  WARN: 边 {from_f}->{to_f} 会形成循环，跳过", file=sys.stderr)
                    cycle_blocked += 1
                    continue
                conn.execute(
                    """INSERT INTO edges (from_node_id, to_node_id, dep_type, architecture_direction,
                    coupling_strength, invocation_method, failure_mode, fallback, activation_condition,
                    data_transfer_description, relationship_type, cross_domain, verified, dep_maturity)
                    VALUES (%s, %s, %s, 'downstream', 'medium', 'direct', 'runtime_error', 'no_fallback',
                    'always', %s, '', 0, 0, 'design')""",
                    (from_id, to_id, dep_type, desc),
                )
                created_edges += 1
            print(f"[STEP 2] 边: 新建={created_edges}  跳过(已存在)={skipped_edges}  循环阻断={cycle_blocked}")

            # STEP 3: 注册12个事件
            created_events = 0
            skipped_events = 0
            for event_name, publisher_f, subscriber_list, desc in F_EVENTS:
                if _event_exists(conn, event_name):
                    skipped_events += 1
                    continue
                pub_domain = next((f[4] for f in F_FUNCTIONS if f[0] == publisher_f), "")
                sub_domains = ", ".join(next((f[4] for f in F_FUNCTIONS if f[0] == s), "") for s in subscriber_list)
                event_id = f"E-ARCH-{event_name.upper()}"
                conn.execute(
                    """INSERT INTO domain_events
                    (event_id, name, source_domain, target_domains, payload_schema, priority, event_type)
                    VALUES (%s, %s, %s, %s, %s, 'P1', 'arch_event')
                    ON CONFLICT (event_id) DO NOTHING""",
                    (event_id, event_name, pub_domain, sub_domains, desc),
                )
                created_events += 1
            print(f"[STEP 3] 事件: 新建={created_events}  跳过(已存在)={skipped_events}")

            conn.commit()
            print(f"\n[OK] 迁移完成。节点={len(f_node_map)}  边={created_edges}  事件={created_events}")
            print(f"  node_id 映射: {f_node_map}")
            return 0
        except Exception as e:
            conn.rollback()
            print(f"\n[ERROR] 迁移失败，已回滚: {e}", file=sys.stderr)
            return 1
        finally:
            conn.close()


def _run_checks(conn, print_preview: bool) -> list[str]:
    """前置检查：验证所有domain_id存在、F功能无重复path。返回错误列表。"""
    errors: list[str] = []

    # 检查所有domain_id存在
    domains_checked: set[str] = set()
    for f_id, name, path, bp_id, domain_id, build_status, layer in F_FUNCTIONS:
        if domain_id not in domains_checked:
            domains_checked.add(domain_id)
            if not _domain_exists(conn, domain_id):
                errors.append(f"domain_id '{domain_id}' 不在domains表(F={f_id})")

    # 检查path无重复
    paths = [f[2] for f in F_FUNCTIONS]
    dup_paths = {p for p in paths if paths.count(p) > 1}
    if dup_paths:
        errors.append(f"path重复: {dup_paths}")

    # 检查边引用的F功能都存在
    f_ids = {f[0] for f in F_FUNCTIONS}
    for from_f, to_f, _, _ in F_EDGES:
        if from_f not in f_ids:
            errors.append(f"边引用不存在的F功能: {from_f}")
        if to_f not in f_ids:
            errors.append(f"边引用不存在的F功能: {to_f}")

    if print_preview:
        print("=== 前置检查 ===")
        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
        else:
            print("  所有检查通过")

        print("\n=== 节点预览 ===")
        for f_id, name, path, bp_id, domain_id, build_status, layer in F_FUNCTIONS:
            existing = conn.execute(
                "SELECT node_id FROM nodes WHERE path=%s AND design_maturity='design'", (path,)
            ).fetchone()
            status = f"已存在node_id={existing['node_id']}" if existing else "新建"
            print(
                f"  {f_id:4s} {name:20s}  domain={domain_id:20s}  build={build_status:10s}  layer={layer:8s}  {status}"
            )

        print(f"\n=== 边预览 ({len(F_EDGES)}条) ===")
        for from_f, to_f, dep_type, desc in F_EDGES:
            print(f"  {from_f:4s} -> {to_f:4s}  type={dep_type:10s}  {desc}")

        print(f"\n=== 事件预览 ({len(F_EVENTS)}个) ===")
        for event_name, pub, subs, desc in F_EVENTS:
            print(f"  {event_name:25s}  {pub:4s} -> {','.join(subs):15s}  {desc}")

        # 统计
        print("\n=== 统计 ===")
        print(f"  节点: {len(F_FUNCTIONS)} (含F17归档)")
        print(f"  边: {len(F_EDGES)}")
        print(f"  事件: {len(F_EVENTS)}")
        dep_type_counts: dict[str, int] = {}
        for _, _, dt, _ in F_EDGES:
            dep_type_counts[dt] = dep_type_counts.get(dt, 0) + 1
        print(f"  边类型分布: {dep_type_counts}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="阶段1迁移: 创建F1-F37设计态节点+依赖边+事件注册")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写入")
    args = parser.parse_args()
    sys.exit(run_migration(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
