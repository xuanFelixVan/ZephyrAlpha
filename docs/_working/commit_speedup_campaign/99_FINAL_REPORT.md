---
ttl: task_bound
---

# 99_FINAL_REPORT — 提交链治本战役终报（st-commitspeed-tbl-20260924）

> 状态：**定稿（2026-09-29 st-finaldel-m5 HEAD 复核回填，增量见 §七）**。红蓝治理组已收、鲁棒组已收、flag immutable_tree 已翻、rules_integrity_db 出库已批②。
> 真源链：本报告 ← CAMPAIGN_STATE_SNAPSHOT.md ← decisions_log.md（60+ 条裁定全录）。

## 一、目标与结果总览

Owner 原始目标：查清"提交一个文件为何等 10-20 分"并彻底治本；未来 20+ 并发车道零死亡零覆盖零堵塞；速度持续提升直至连续两轮无可优化。

**已交付的系统级变化**（全部 HEAD 实证）：

| 批 | 内容 | 实测效果 |
|---|---|---|
| 批一 815312f93d | D3 波尾死锁+D4 幽灵 pending+A1/A2/A3 装表+B4 FCFS | 三工熄火根治（四工满速实证）；倒挂率 56%→0；观测面从零到全 |
| 2f86346f2c | T6 钩链瘦身 | ref 移动 git 子进程 5→1（1.25s→0.5s/次） |
| 6e47377b8f | 簇1 共册缓存 | CREATE-GUARD **p50 4.1→0.7s**、mean 197→45s（91 链持续） |
| 0124 | S1 接线（flag OFF） | 代码链路全流通；翻转即生效（呈 Owner） |
| T7 | 缓存键隔离 | 键去全局态（87 命中/24h 的根因拔除；flag OFF） |
| T5/M2 | 衍生再生出窗 | 意图账+卡死检测+主区单点（4×97.3 CPU-s 爆发消除） |
| W4/D2 | 环境变量泄漏 | per-spawn 注入+无残留（marker 金丝雀收口） |
| P3 | 完整性 HEAD 派生 | 假 TAMPERED 源头消除+_GATES_DIR 17→136 复权 |
| T14 | 名册治理 | ms≥1 盲区拔除+own_scope 机生补 53+对账生成器 |
| B5 | attempts 退避 | 毒药队首止血 |

## 二、残留优化管线（深挖 R1 排序+现状）

1. ~~重试环 723min~~ → 簇1 已收（CREATE-GUARD 塌缩实证）；T10 廉价门前置待逐 hook 取证定责
2. ~~hook 成本与件数脱钩~~ → 冷启动税证伪（0.49s×69）；own-scope 取证批框架已留
3. precommit 1200s 超时×3 → 待 hook own-scope 改造
4. S1 生效：flag 已翻（2026-09-29）；余量=生效验收实测（C04：重放对照 selfcheck100 + 四工新链 total_ms 读数）
5. residual 未解释 123s/笔 → 锁等待插桩（R2 前置）

## 三、Owner 呈报清单（唯一待裁定集，全部不阻塞链路）

1. **[已落地 2026-09-29]** flag `immutable_tree` 翻转（flags.yaml@HEAD `immutable_tree: true`）；余量=S1 生效验收实测（C04）（勘误补注 2026-09-29：翻转=ed935c29afd，Owner 09-26 批——防重复走门位）
2. flag `regen_scope: main_only` / `gate_result_cache` 同批翻转（可选）（勘误补注 2026-09-29：gate_result_cache+T7 新键已 live=df8507ac9b+cb3c13b74f8——防重复走门位；regen_scope 仍呈 Owner）
3. **[已批②]** DB `rules_integrity_db.json` 出库 git（Owner 终局批②）；处方待执行：git rm --cached + .gitignore + 再注册通道拦截（可全量重算=--register/--fold 重建基线；工单 C148）。C148 处方已立（含再注册白名单前提），待 Owner 批后执行
4. 死信处置：draft 时 119+59 分诊口径已过期——2026-09-29 审计窗 dead 已涨至 1079 封，按内容驱动新规分批（≤10 封/批）处置（C02），废弃/归还确认仍呈 Owner
5. T14 own_scope 14 条终裁 + 15 门 P4 家族处置
6. 归属级 HMAC 载体（红蓝④发现，登记待办）

## 四、测试与对抗

- 提交链七套合并回归：181-207 passed 多轮
- S1 selfcheck：100 笔/1522 文件/byte_mismatch=0/worktree_reads=0
- 红蓝治理组：④⑤⑥ 三场景 23 测试+红证三查（100 passed）
- 红蓝鲁棒组：①②③（执行中，报告 70_redblue/redblue_robust.md）
- R2 复测判据：深挖脚本全集对照 R1，连续两轮无可回收 >5min/天 = 终止

## 五、清洁清单（T17）

- 临时脚本：.runtime/tmp/csx_*（保留 cs-tbl/ 取证）
- scratch worktrees：csx-s1/csx_t13_wt/csx_t14_wt/csx-p3b/csx-w4/csx-d4/csx-b5/csx-p13/csx-replay + .runtime/tmp/csx_t13_wt/csx_t14_wt（git worktree remove + prune）
- claim 释放：读 .ailocks/registry.json 判成（禁信 stdout）
- 死信处置：按分诊清单执行（呈 Owner 项获批后）

## 六、事故与学费（全部在册）

worktree 局部队列陷阱×3（enqueue 三件套配方）/token 与文件同批违例（token 先行配方）/S1 前置件落错分支（branch --contains 铁律）/stash 前置 pwd 断言/自举 drain PYTHONPATH 毒/PYTHONPATH=src 测自改码。

## 七、定稿补记（2026-09-29 st-finaldel-m5 HEAD 复核）

本报告按 2026-09-29 HEAD 复核定稿，上文陈旧处已就地标注；增量对账表：

| 项 | draft 时口径 | HEAD 复核终态（2026-09-29） | 证据 |
|---|---|---|---|
| flag immutable_tree | 呈 Owner 待翻 | **已翻**：flags.yaml@HEAD `immutable_tree: true` | git show HEAD:config/flags.yaml |
| 红蓝鲁棒组 | ①②③（执行中） | **已收**：报告+测试面在 HEAD；F1 真实生产竞态（低频高后果）→移交 Owner 修复单 | 70_redblue/redblue_robust.md@HEAD |
| rules_integrity_db 出库 | 呈 Owner（MQ-1） | **Owner 终局批②已获**，处方未执行（出库后 --register/--fold 仍可全量重算基线；须同步拦截 commit_derived_sync/post_commit_ritual 再注册通道防回灌） | 工单 C148 |
| 死信 | 119 废弃+59 归还 | 审计窗 dead=1079 封且持续增长；按内容驱动新规 ≤10 封/批分诊处置 | 2026-09-29 终审清单 C02 |
| S1 生效 | 待 Owner 翻 flag | flag 已翻；**唯一余量=C04 生效验收实测**（连续两轮达标=战役终止判据） | C04 |

仍呈 Owner 面（§三收敛后）：regen_scope/gate_result_cache 可选同批翻转、T14 own_scope 14 条终裁+15 门 P4 家族处置、归属级 HMAC 载体立项、死信废弃/归还确认、rules_integrity_db 出库处方执行。T13 双袋终态以 .runtime/commit_queue done|dead 实读为准，本报告不再追记在飞袋号。
