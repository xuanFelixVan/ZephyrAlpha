---
ttl: permanent
---

# trend_analyzer 回迁子裁定书（推翻 #18 F5，#62 §六 C 机制行落地，2026-08-21 专项批）

> 授权：残余四项专项批交接指令 任务1——"推翻 #18 F5 回迁 DB_PATH（governance.db）或维持独立库但书面消解口径矛盾，从第一性原理（SSoT/测试隔离/100% AI 开发可追溯）给分析过程+裁定书"。
> 前置裁定：#62（2026-08-21-drift-events-ssot-adjudication.md）——drift_events 唯一真源=governance.db（22 列 legacy schema，append-only，零 ALTER 零迁移，唯一写方=drift_engine）；§五.4③ 登记"trend_analyzer 回迁子裁定随统一批再议"=本裁定。

---

## 一、调研实证（2026-08-21，探针 .runtime/_b8_probe_gov_triggers.py）

### 1.1 trend_analyzer 实际表集与消费列

本模块只读写一张表 `drift_events`，两个入口：

| 入口 | 性质 | 消费列 | 生产 22 列 schema 适配 |
|---|---|---|---|
| `compute_metrics` | 只读 | module_id / created_at / state / updated_at / detector_id | **5/5 全部存在，零改动** |
| `archive_old_data` | 读+DELETE | 上述 + drift_dimension / baseline_version / resolved_by / auto_fixed / rollback_verified | **5 列缺失**：drift_dimension（#62 writer 口径=description 列承载）、auto_fixed（writer 口径=auto_fixable 列）、baseline_version / resolved_by / rollback_verified（SSoT 从不承载，writer 不写） |

### 1.2 生产物理现状（直查 sqlite_master/PRAGMA）

- `data/drift_audit/drift_audit.db`（#18 F5 指向）：**物理不存在**，无任何写方。
- 生产 `governance.db` drift_events：**无 append-only trigger**（实证：全库 trigger 仅 tasks 表 4 个；tamper_proof_audit.setup_append_only 是从未对生产执行的能力）。
- legacy 386 行 state 全部='DETECTED'；created_at ∈ [2026-05-07, 2026-05-26]。
- TrendAnalyzer 生产消费方：**零**（仅 _analysis.py / behavioral_auditor `__init__` 再导出；archive_old_data 全仓仅测试调用）——休眠能力。
- F5 结构后果：`get_db_connection(不存在路径)` 建新空库但无 CREATE TABLE，生产 `compute_metrics` 必抛 `OperationalError: no such table: drift_events`——**该能力自出生起在生产从未工作过**。

## 二、第一性原理分析

1. **读方必须随写方**。观测事件的查询契约由写入契约定义；#62 已裁定唯一写方=drift_engine→governance.db。trend_analyzer 指向一个永远无人写的库=结构性死亡能力，且制造"同一逻辑事件、两个查询契约"的第四物理位置，与 SSoT 裁定直接矛盾。
2. **测试隔离 ≠ 独立生产库**。测试隔离的正解是注入（db_path property setter / tmp 夹具），F5 把测试手段当成了生产架构——为测试契约给生产配一个空库，本末倒置。#62 §七.3 已立硬约束方向：测试夹具复刻生产 schema，而非生产迁就测试。
3. **一写方原则推论：读方不得 mutate SSoT**。archive_old_data 的 delete-after-export 在独立库时代无副作用（库是自己的）；回迁后成为 SSoT 表第二写者：①违反 #62 原则 2（一个事件一个写方）；②与 tamper_proof `drift_events_no_delete` trigger（RAISE FAIL）的设计终局直接冲突——今天 trigger 未装能跑，装上即炸，是定时炸弹；③模块自身 INVARIANTS="趋势数据不可篡改"；④legacy 386 行中约 3/4 created_at < 90 天 cutoff，首次 archive 运行即物理删除大部分遗产观测数据——观测数据销毁权不属于读方。
4. **容量保留是治理动作不是读方侧效应**。blueprint §17（L925）："漂移事件 DB > 2GB → VACUUM + 归档 + 冷热分层"——保留策略需 trigger-aware 专项设计，登记为残余候选。
5. **100% AI 开发可追溯**：SSoT 单点意味着 AI 查 drift 只去一个地方；多物理位置=多脑冲突温床（本项目已三起同族事故）。

## 三、裁定结果

1. **推翻 #18 F5**：`db_path` 生产默认=`str(DB_PATH)`（governance.db SSoT）；第四物理位置 `data/drift_audit/drift_audit.db` 从代码消除。测试隔离走既有 `db_path` property setter 显式注入。
2. `compute_metrics` **零改动**（§1.1 实证 5 列全适配）。
3. `archive_old_data` 改 **export-only**：列重映射 drift_dimension←description、auto_fixed←auto_fixable；baseline_version/resolved_by/rollback_verified 从归档记录移除（SSoT 从不承载）；**DELETE 移除**（一写方原则+append-only 终局）。重复导出需下游去重（休眠工具，jsonl 为派生物）。
4. 测试夹具改**复刻生产 22 列 schema**（与 drift_engine CREATE DDL 逐字一致），归档用例契约同步翻转（导出后 SSoT 行保留）。
5. **残余登记**：①drift_events 容量保留/冷热分层策略（blueprint >2GB 触发）→ 候选库登记随任务4批一并；②`data/drift_audit/` 目录本身由 gate_persistence/scan_mutex/git_bisector 等继续使用，不动。
6. F5 注释段（L86-90）替换为本裁定引用。

## 四、落地核验（机器可核，#62 §七.1 纪律）

| 项 | 证据 |
|---|---|
| 施工 commit | 本批 gateway commit 见 tracker |
| 回归 | tests/audit/test_trend_analyzer.py 全绿（基线 12 passed → 改后见 commit 实证行） |
| 关联域零新增红 | gov_drift 关联测试域复跑 |

---

**裁定人**：专项统筹（Owner 授权调研裁定）｜**探针**：.runtime/_b8_probe_gov_triggers.py
