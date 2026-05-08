---
task_id: "TASK-INF-0107"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2.1 A-J 盲点审计（55+ 盲点）——A.分布式系统 B4-A01~A10"
title: "盲点关闭——A.分布式系统与多节点 B4-A01~A10：Leader Election / Cluster Membership / Split-Brain / Sharding / HLC / CRDT / Anti-Entropy / Multi-Raft / Partition Healing"
description: |
  关闭分布式系统盲点 B4-A01~A10。
  B4-A01 Leader Election→SqliteLeaderElection（§5.3 代码骨架）——SQLite租约轻量级主选举+
  B4-A02 Cluster Membership→Gossip协议设计——节点加入/离开/崩溃感知+
  B4-A03 Split-Brain Protection→Fencing机制——网络分区一致性保护+
  B4-A04 Consistent Hashing/Sharding→事件路由算法——扩容不重构+
  B4-A05 Quorum-Based Decision→R+W>N 共识策略+
  B4-A06 Hybrid Logical Clock→跨节点事件偏序/全序——对齐 CockroachDB HLC+
  B4-A07 CRDT→多节点并发写入自动合并+
  B4-A08 Anti-Entropy→Read Repair + Hinted Handoff+
  B4-A09 Multi-Raft→按模块域分建共识组+
  B4-A10 Graceful Partition Healing→分区恢复渐进重建。
  §5.3 已提供 SqliteLeaderElection 代码骨架（29骨架之一）。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\leader_election.py"
    description: "SqliteLeaderElection——§5.3 代码骨架实现：try_become_leader/is_leader/step_down"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cluster_membership.py"
    description: "ClusterMembership——Gossip协议+节点健康追踪"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\split_brain_guard.py"
    description: "SplitBrainProtection——Fencing token+Partition检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\sharding.py"
    description: "EventSharding——Consistent Hashing+事件路由"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\hlc.py"
    description: "HybridLogicalClock——跨节点事件偏序/全序"
  - path: "D:\\ZephyrAlpha\\tests\\shared\\test_leader_election.py"
    description: "Leader Election 单元测试——租约竞争+续约+过期"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\leader_election.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cluster_membership.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\split_brain_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\sharding.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\hlc.py"
  - "D:\\ZephyrAlpha\\tests\\shared\\test_leader_election.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 SqliteLeaderElection 代码骨架"
    reason: "INSERT OR REPLACE 原子操作竞争 Leader + TTL 30s + 续约 10s"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§2.1-A 10项分布式系统盲点 + §5.3 SqliteLeaderElection 代码骨架"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 22000
timeout_minutes: 60
acceptance_criteria:
  - "SqliteLeaderElection: try_become_leader() 原子竞争——多节点仅1个成功（B4-A01）"
  - "ClusterMembership: 节点崩溃后 30s 内感知（B4-A02）"
  - "SplitBrain: 网络分区→Fencing token 阻止双主写入（B4-A03）"
  - "EventSharding: 扩容不重构——Consistent Hashing（B4-A04）"
  - "HLC: 跨节点事件有正确偏序关系（B4-A06）"
  - "Partition Healing: 渐进重建不雪崩（B4-A10）"
  - "所有新增文件符合 directory-structure-standard.md"
rollback_instructions: |
  1. 删除新增 production 文件：leader_election.py / cluster_membership.py / split_brain_guard.py / hlc.py
  2. 删除新增 events/sharding.py
  3. 删除新增测试文件
  4. 如 shared/production/ 被意外创建→检查是否空→删除目录
depends_on: []
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-002"
  - "MOD-INF-016"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
