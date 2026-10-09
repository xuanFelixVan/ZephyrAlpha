---
ttl: task_bound
completes_when: Owner 消费本报告 + 车道F-1b 与 A-12 接单 + F-1b 消费完由本专案做残余二次裁定
---
# 死信清偿专案 · 端到端交付报告（sid=st-deadcure-20261009 · 2026-10-09）

锚点 HEAD=`f07c41c1cffb`｜冻结存量 **1704 件**（dead/ 袋 1701 + 零字节空壳 1 + .bak-orig 1 + 当班新袋 1）
｜**账面覆盖 100%（未决 0）**，两轮 cycle_check 全 CLEAN，红蓝对抗通过（伪造袋能红）

## 一、四终态账面（生成器产出：tools/account.py + tools/cycle_check.py）

| 终态 | disposition | 件数 | 实物位置 |
|---|---|---:|---|
| ②归档留痕 | archived_superseded | 358 | mv 进 `dead_archive_20261009_deadcure/`（manifest 逐件，restore 一步回退） |
| ③判废留痕 | scrapped_recorded | 5 | 同上（含零字节空壳、重复备份件、本专案自伤重试袋） |
| ①复活已落地 | revive_landed | 1 | HEAD 验真 `e48349275d`（§卅一 DR 定性勘误，此前同签名死 40 次） |
| ①复活在途 | revive_requeue | 14 | ghost_session 类走机械重投；CREATE-GUARD/ALGO 类见 §四 |
| ①复活工单 | revive_with_ticket | 1185 | **留 dead/ 原位**（保一步 `requeue --from-bag` 通道；总统筹裁定第 3 条认可） |
| ①新增件工单 | revive_additive_new | 89 | 其中 **53 件非 tests 机械可落地子集本批随件落地**，其余（src/tests/生成物/csv）转工单 |
| ④属主退回 | returned_to_owner | 12 | 属主活会话（st-fullflow2/st-chiefc），不代处置 |
| 呈报 Owner | pending_owner | 40 | 见 `10_owner_menu_deadcure40.md`（归并 11 组，每组两选项） |

实物核对：dead 现存 1340｜本专案归档 364（manifest 同数）

## 二、本专案立的两条判据（建议升成仓规）

1. **盲重投=回退机器**：1397 袋（82%）属 regression_risk——HEAD 已含更新行且 91.5% 条目无 `base_blob`，
   整档重投即覆盖演进内容。实例：某袋 `macro_regime_sensor.py` 仍是"上溯 4 级找仓库根"旧写法，HEAD 已含 G-1 修复。
   **判据=投前测 `lines_only_in_head`，>0 禁重投**；只增行不毁行才允许机械复活。
2. **禁路径存在级判据**：官方 `dead-archive --days 0` dry-run 计划归档 305 袋中 **251 袋内容实测未落地**。
   本专案全部归档改用三方字节对拍（袋 blob × HEAD × dev 行血）+ 车道语义取代证据双判。

## 三、P0（查出而非造成）：tests 树被删未补

删除提交 `6324c9e0f6fd`（10-05）自述"内容真身=终装袋 0030-0044·内容零删失"，而那些袋全在 dead/。
实测 HEAD `tests/` 4089→2003 件，逐字节可对上者仅 407 件；**2325 条缺失路径可从死信 blob 零考古恢复**
（pure_move 313／edited_move 1843／novel 52；2325 条 `py_compile` ok=2324；60 件抽样 collect 289 items 0 error）。
按总统筹裁定交割车道 **F-1b**，交割包=`09_handoff_laneF1b.md`，清单=`05_tests_restore_manifest.yaml`。
本专案不投的理由：HEAD 自身在该目录已有 1 件 collection ERROR，"投下即绿"不成立（违开工总纪律 #6 先跑绿才投）。

## 四、13 袋重投处方执行结果与残余分类

- **机械类（ghost_session）已执行**：修因=换 chief 词缀活身份 + `mark_logical`（本专案自证：非 logical 身份两袋死于 ghost）。
- **CREATE-GUARD 类**：`scripts/backtest/grid_stats_engine.py`/`lead_lag_validator.py` 两枚袋的死因是"当时无 token"，
  而今日 HEAD 已有这两件且 14 字段齐——**死因陈旧**，重投前须按新判据 `lines_only_in_head` 复核（结果记 `lanes/chief_requeue2_log.jsonl`）。
- **ALGO-FLOW-LINK 类**：缺 3 处锚/卡片链接＝施工面，随 §三 交割单转车道 A/F，不在本专案扩面。

## 五、热册蒸发（P1 立项证据已交割 A-12）

本专案台账袋第一次落地即死于 `CREATE-GUARD 无 creation_tokens`——袋内自带 25 行册面，门禁落地读盘：
主区盘上 token 读数在 06:33-06:53 间三次归零（别道陈旧整档快照压制）。
**已验证正解=token 先行落地 + 内容随后**（token 批落 HEAD 后重投即通），全文见 `08_hot_registry_eviction_evidence.md`。

## 六、诚实申报（未达成与边界）

1. **dead/ 物理未归零**：1340 件仍在，其中 1185 件是**主动保留**的复活通道
   （总统筹裁定认可并设出口：F-1b 消费完后由本专案对残余做二次裁定，被超集取代即归档，索引已备 `07_residual_bags_index.yaml`）。
2. 账面 100% 覆盖 ≠ 内容全部落地；本报告不把"归档"写成"已落地"。
3. 未虚构任何 Owner 裁定：全文只引在册 #459/#480/#488/#489/#494/#495；40 件业务资产/受保护面一件未判废。
4. 车道并发教训已记：同 sid 并发袋会静默取代——本专案收尾时曾出现双驱动并发，已终止至单驱动后重跑。

## 七、复核命令

```bash
cd /d/ZephyrAlpha
ls .runtime/commit_queue/dead/q-*.json | wc -l
python .runtime/tmp/st-deadcure-20261009/tools/cycle_check.py
python .runtime/tmp/st-deadcure-20261009/tools/account.py
python .runtime/tmp/st-deadcure-20261009/tools/redblue.py
git show --stat e48349275d | head -5
git cat-file -p 6324c9e0f6fd^:tests 2>/dev/null | head -0; git ls-tree -r --name-only HEAD tests/ | wc -l
```

## §G 波收尾回执（生成件，勿手改）

- G5 袋 22 件／token 袋＋G6-G8 数据 4 件＋G7/G9/G10 文档 5 件／53 件复活甲乙两袋——逐件 `git show HEAD:<path>` 与车道 index 字节对拍，明细见 01_ledger §G 二节表。
- 授权链消费裁定#496（同一批文不重复登记）；G4 因 GATE-NAMING N-16 文件名唯一性受阻呈 Owner。
