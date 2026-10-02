---
ttl: task_bound
session: st-construct-20261002
date: 2026-10-02
title: 留待 Owner 裁定项清单（深挖后终版）
completes_when: 全部条目获 Owner 表态后销册
---

# pending_owner.md — st-construct-20261002 深挖批终版

> 2026-10-02 深挖批（Owner 令"全部深挖，先深度调查再给我裁定结果"）执行后大改：原 11 项中 **6 项当场销册**（已修/已执行/撤回），**origin/master 已由 Owner 删除销册**。当前真正留 Owner 的只剩 2 项等待态 + 1 项可选。

## 一、深挖批处置实录（全部闭环）

| 项 | 深挖发现 | 处置 | 状态 |
|---|---|---|---|
| TradingWatchdog SID 断裂 | "SID 断裂"只挡 XML 补丁通道；直接注销不受限。创建者=create-if-absent+建后立即禁用（92 D3） | 旧任务注销→创建者重建：**Disabled 保位+动作已指新路径 installers/**（含 wscript 隐窗范式） | ✅ 当场治好，销册（未来"启用"仍留 Owner 窗，设计如此） |
| OneShot0915×2 拒访 | 拒访仅限 XML 补丁路径；直接注销畅通。两任务=09-15/16 一次性重跑实验，lastRun 09-16 result=0（已完成使命），与正式线重复，禁用 16 天 | 按 RULE-THREE 三步审判通过→**两只已删除** | ✅ 销册 |
| migration 13 假 pending | **翻案**：非假 pending=账实漂移。拆分事实上早已完成（gate_engine/、rule_engine/ 目录实测在），且 **Owner 2026-09-30 已批退役排班**（67be6338f4 retirement_schedule 块：A 组 12 条批 done、B 组 1 条 rule_watcher 双亡 superseded，执行窗"≥2026-10 维护窗"） | 执行已批排班：12 条→done、1 条→superseded（entries 37 不变，零增删；执行留痕入块）。本包此前"二选一"裁定作废 | ✅ 执行完毕，销册 |
| 估值 quar_20260920 | 旧口径真数据 8125 行（含 7 行已知非交易日脏行，重建时已先导出 F 盘留存）；重建 09-20 验收+09-30 survey 绿；零消费方；超隔离窗 13 天 | **已 DROP**（三步验证在案；CH 夜备保留窗内可寻回）；known_data_gaps 留痕 | ✅ 执行完毕 |
| 估值 v2_quar_20261002 | 0 行空壳 | 维持 10-09 到期 DROP（通道纪律），到期自动走 | ⏳ 等待态，无需 Owner 动作 |
| requeue 通道缺陷（原拟升 P1） | **撤回——误诊**。读源码实证：requeue 文件集=死信袋自身清单（非全脏面），快照语义 D7 明文；连环死真因=袋中两件前朝残改件缺 ALGO_FLOW 锚（已补），与通道无关 | 撤回 P1 升级；无缺陷 | ✅ 销册（误诊更正留痕） |
| GATE-SELFDOC 无实现 | 确认全仓无实现后**当场接线**：detect_git_dangerous.py 增 frontmatter+行级双形态豁免（≤10 行，超限照拦，门 id 精确匹配禁通配） | 四向测试全过（超限拦/错id不豁免/行级精准/正确豁免）；legacy_v1（9 违规行）实弹过门 | ✅ 债清，销册 |

## 二、当前真正留 Owner 的项（2 项等待态 + 1 项可选）

1. **TRD-A10 实盘腿**（终留）：解锁条件=模拟盘 60 交易日+Sharpe>1+Owner 签字。等待态，无需动作。
2. **估值 v2 隔离壳 10-09 DROP**：到期自动执行，无需动作（想留再说）。
3. （可选）**Full0916×2 两只实验任务**：禁用中、路径已修新、无任何故障——留或删随 Owner 便，本包不动（不在深挖令范围）。

## 三、终留不变

- origin/master：**Owner 已删除，销册** ✅
- metaq .rda：留盘结案（CR-7），无新证据
