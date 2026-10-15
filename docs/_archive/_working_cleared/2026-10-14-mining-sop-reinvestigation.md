---
ttl: permanent  # st-docconsol-20261014 改：原 working 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
archived_doc_type: mining_log
title: 挖矿 SOP 复调——09-18 架构尽调 T1~T11 完成状态（三源正查修正版）
created: 2026-10-14
sop_ref: docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md (v1.9.1)
prior_artifacts:
  - docs/_working/archive/2026-09/c_class_scattered/2026-09-18-institutional-architecture-review.md
  - docs/_working/archive/2026-09/c_class_scattered/2026-09-18-issue-inventory-full.md
  - docs/_working/archive/2026-09/2026-09-18-HANDOFF-PROMPT.md
---

# 挖矿 SOP 复调报告（第二轮）

> **为什么有这份文件**：10-14 首轮收口核验用"关键词 grep 单文件"下结论，被挖矿 SOP §7.5 判为不合规（负存在断言无三源正查）。本轮按 SOP 重做，**自查推翻了自己 3 条断言**。

## 0. 母节点与触发

- 母节点 = **09-18 架构尽调派生的 T1~T11 整改任务**（当前完成状态）
- 触发 = SOP §1「给既有方案做完整性验收」（Owner 问"挖干了吗/还有没有遗漏"）
- 正查工具 = `python -m zephyr.library.lookup state "<关键词>"`（三源：馆索引 / git log 90d / 工棚+挂账面）

## 1. 六向寻路结果

| 向 | 内部反查 | 判定 |
|---|---|---|
| ①上游 | 09-18 三份交付物（已归档、正文零改动）+ 09-26/09-30/10-02/10-03/10-14 会话日志 | signal：后续会话大量工作未被首轮核验计入 |
| ②下游 | 本次结论 → Owner 收口决策 / 新会话指令 | 已产出本件 |
| ③算法/机制 | `cpcv.py` / `purged_kfold.py` / `SQLiteIdempotencyStore` / `overfitting_guard.py` | **signal（重大）**：embargo 与幂等均有专门实现，首轮漏判 |
| ④后端 | src/scripts/tests 三重搜索 + 跨 worktree | signal：`miniqmt_broker.py:71-74` 幂等落库；`walk_forward.py:23` CPCV v2 仍"配置预留" |
| ⑤前端 | 只登记不施工 | 不适用 |
| ⑥数据字段 | `data/audit_trail/` 目录实扫 | **signal（重大）**：`events.jsonl` 124,974 行真实审计事件在跑，与 `gate_chain.jsonl` 是两条链 |

## 2. 挖矿日志表（SOP §7 强制）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 交付物存活性 | signal | 三份文件在 HEAD 树（archive/2026-09 + fullflow_campaign/recovered），逐字节比对**正文零改动**，仅 frontmatter 归档标记变更 |
| R2 | 订单幂等（T3） | **signal·翻案** | `miniqmt_broker.py:71-74` import `SQLiteIdempotencyStore`；`:96` `order_idempotency.db`；`:260` 注释「R-L3（尽调 C1）：内存映射降级为快路径缓存，权威去重状态落库」⇒ **首轮"未完成"判定错误** |
| R3 | embargo（T5） | **signal·翻案** | `backtest/core/cpcv.py`（257 行）purge+embargo 完备；`purged_kfold.py`（130 行）`embargo: int = 0`；但 `walk_forward.py:23`「CPCV v2 配置预留（P1-18）…配置项待实现时添加」⇒ 模块有、主链未接 |
| R4 | 固种（T5） | signal | `regime_validation/e2_stationary_bootstrap.py:75` `seed: int = 42`、`:170` `default_rng(cfg.seed)`；但 `walk_forward.py:281` 仍 `default_rng()` 无参 ⇒ 主链仍未固种 |
| R5 | 审计链（T7） | **signal·翻案** | `audit_chain_verifier.py` 有 append-only hash 链 + 跨进程文件锁 + 重启恢复（5.37.8）；`events.jsonl` 93MB/124,974 行/mtime 10-13 真实在跑；`gate_chain.jsonl` 167 行全 G0 属"门禁结果未入该链"的分工问题，非审计失效 |
| R6 | 因子三重门（T6） | noise（维持原判） | `factor_factory.py:218-220` 仍 `lambda c: True` 默认恒真，依赖调用方注入 |
| R7 | 复权链（T1） | signal（维持完成） | `data_handler.py:279-303` `compute_qfq_close` + `:396` registry 真源 + `:430` adj_factor 列（X-2 修复） |
| R8 | worktree（T8） | noise（维持） | 42 → 54，反向恶化 |
| R9 | 实盘（T9）/CH-Redis（T10） | noise（维持） | 无实盘业绩产物；Redis 与 CH 仍同机 172.24.30.100 |
| R10 | pre-trade（T11） | noise（维持） | `probe is None` 仍在；`risk_veto_engine.py` 无 industry/sector/concentration/turnover/blacklist/liquidity |

## 3. 三源正查证据表（SOP §7.5：每条断言挂指针）

| 断言 | 首轮判定 | 本轮修正 | 证据指针 |
|---|---|---|---|
| T1 复权链 | ✅ | ✅ 维持 | `src/zephyr/backtest/core/data_handler.py:279,396,430` |
| T2 ETF 时区 | ◐ | ◐ 维持 | `scripts/ch/repair_etf_minute_tz_split.py` dry_run 非默认 True；无验收报告 |
| **T3 订单幂等** | ❌ | **✅ 已完成** | `src/zephyr/ex_core/adapters/miniqmt_broker.py:71-74,96,260-265` |
| T4 CI | ◐ | ◐ 维持 | `.github/workflows/governance.yml:124-127` nightly 全量 + cov70；`:350` collect-only 残留、`:108/:274` continue-on-error |
| **T5 embargo** | ❌ | **◐ 部分** | 模块：`backtest/core/cpcv.py:110,171`；主链未接：`walk_forward.py:23` |
| **T5 固种** | ❌ | **◐ 部分** | 有：`regime_validation/e2_stationary_bootstrap.py:75,170`；主链无：`walk_forward.py:281` |
| T6 因子门禁 | ◐ | ◐ 维持 | `factor/factor_factory.py:218-220` |
| **T7 审计链** | ❌ | **◐ 部分** | 机制：`gov_enforcement/rule_enforcement/audit_chain_verifier.py:8,23,108`；真实事件：`data/audit_trail/events.jsonl` 124,974 行；G0 链：`gate_chain.jsonl` 167 行 |
| T8 worktree | ❌ | ❌ 维持 | `git worktree list` = 54（.aidrafts 23 + .worktrees 20） |
| T9 实盘 | ❌ | ❌ 维持 | 无净值/成交/持仓产物 |
| T10 CH/Redis | ❌ | ❌ 维持 | `infrastructure_registry.yaml` INFRA-DB-007 host=172.24.30.100 |
| T11 pre-trade | ❌ | ❌ 维持 | `ex_core/pre_execution_checker.py` probe is None；`risk/core/risk_veto_engine.py` 无集中度类关键词 |

## 4. 修正后总账

| 状态 | 数量 | 任务 |
|---|---|---|
| ✅ 完成 | 2 | T1、T3 |
| ◐ 部分 | 5 | T2、T4、T5、T6、T7 |
| ❌ 未完成 | 4 | T8、T9、T10、T11 |

**首轮错误率**：11 项中 3 项判定失真（27%），全部为"用单文件关键词 grep 下的负存在断言"。

## 5. 挖后自审闸（SOP §6）

北极星 = 终局全貌（Owner 只做账号注册/API 申请/充值/策略转正，其余全自动化）。

- **T3 → 施工态已完成**，不再立项。
- **T5（主链接 CPCV + 固种）→ 施工**：零件齐全（`cpcv.py` 257 行），只差 `walk_forward.py` 接线与 seed 入参。属终局必需要件（无 embargo/固种 ⇒ 回测结论不可复现 ⇒ 无法支撑自动转正）。
- **T7（真实门禁入 gate_chain）→ 施工**：机制完备，只差写入面接线。
- **T8（54 worktree）→ 施工**：纯卫生，终局无人值守下不应堆 40+ 副本。
- **T9/T10/T11 → 挂起排期**：依赖实盘启动与硬件扩容，属 Owner 门位（宪法 §5），解锁条件=资金授权/采购。
- **不封矿**任何一项——终局全貌中均有位置。

## 6. 失败模式记档（SOP §8）

| 复发模式 | 本案表现 |
|---|---|
| 负存在断言零证据 | 首轮 3 条断言未跑三源正查，仅单文件 grep 即下"未完成" |
| 关键词窄口径 | `uuid4` 存在 ≠ 幂等未做（真实实现在 `SQLiteIdempotencyStore`，与 uuid4 共存）；`embargo` 不在 walk_forward ≠ 项目无 embargo |
| 链路分工误读 | `gate_chain.jsonl` 全 G0 不等于审计失效——真实事件在 `events.jsonl` |

**长期纠正**：本项目任何"XX 未做/不存在"结论，MUST 先跑 `python -m zephyr.library.lookup state "<kw>"`，再按 `git grep` 全仓（含 worktree）复核，最后才下判。
