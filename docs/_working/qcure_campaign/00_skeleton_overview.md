---
ttl: task_bound
title: QCure 战役环节总谱（骨架·封矿版 v1.0）
session: st-qcure-20260925
---

# QCure 战役环节总谱（骨架）

> 挖矿 SOP 合规本：母节点=提交队列全链路；六向寻路按 mining_sop_policy §2（每向=内部反查+全网参照）；
> 封矿判据=矿脉枯竭（六向全查无+无未挖长尾）；自审闸三态=施工/挂起排期/方案封矿。
> 逐环节详情见各子目录 workbook.md（10 本，五路挖矿代理产出）。

## 1. 环节清单（10 环节，矿脉枯竭封矿）

| # | 环节 | 作业簿 | 三态裁定 | 施工映射 |
|---|------|--------|---------|---------|
| 1 | producer_enqueue 生产线/入队 | producer_enqueue/workbook.md | 施工 | 线A: M1.1/M1.3/M2.2/M3.3 |
| 2 | bag_storage 袋与blob存储 | bag_storage/workbook.md | 施工(M3.1)/挂起(M5.4) | 线A: envelope继承；M5.4挂起 |
| 3 | queue_scheduler 队列与调度 | queue_scheduler/workbook.md | 挂起排期 | 让位预检；depends_on强前置二期 |
| 4 | landing_materialize 落地物化 | landing_materialize/workbook.md | 施工 | 线D: M5.1 自验前移 |
| 5 | gate_chain 门禁链 | gate_chain/workbook.md | 施工 | 线B: M2.1/M2.3；线D: M5.2 |
| 6 | cas_converge CAS推进与收敛 | cas_converge/workbook.md | 施工(前置排障) | P0已处置（见§3） |
| 7 | deadletter 死信与重投 | deadletter/workbook.md | 施工 | 线A: 处方/熔断；线E: 对消报表 |
| 8 | observability 观测与运维 | observability/workbook.md | 施工 | 线E: 对消报表（验收承重件） |
| 9 | approval_language 审批与授权语言 | approval_language/workbook.md | 施工 | 线C: M4 全套+#410修补 |
| 10 | fullflow 全流通验证面 | fullflow/workbook.md | 挂起排期（基线已交） | 线E: 红灯诊断修复 |

## 2. 挖矿战果量化

- 死信普查 395→397 笔全分类：Top3 = 热册三向合并 64（16.2%）/ 冲突标记残留 50（12.7%）/
  CREATE-GUARD 36（9.1%）；三分类表漏 98 笔（24.7% other）——本战役补齐标记表。
- enqueue 零预跑实证：三生产入口裸奔，唯一有预检的入口=git_commit.py --enqueue（18 道白名单）。
- pending 牺牲批预测：41% 再死率（18/44），处方化后应归零。
- 全流通基线：绿 8 / 黄 3 / 红 1（红=AI 层 NightlySentiment 09-16 起断）。

## 3. P0 拦路石处置记录（施工前置）

1. **陈旧基底覆写逆转**（2026-09-25 01:43）：主区 staged 的 commit_queue_landing.py +
   commit_belt_daemon.py 经 classify_workspace_wip.py 机械判为 stale_rollback（mtime<HEAD、
   无活跃会话认领、缺 09-24 CAS 治本标记 _heal_derived_totals 0/2）；尽核实查在飞袋
   （commitspeed-tbl-0030/wm1-wave0-0019）已含两文件内容（袋 blobs 固化，零工作丢失），
   执行 git restore 恢复 HEAD 干净版。
2. **daemon 设计换血**（01:45）：旧 PID 23356 内存版本不可判定（启动时盘上可能是陈旧版），
   击杀后 ZephyrAlpha_BeltDaemon 计划任务 PT1M 自启，新 PID 196 心跳 2 秒龄——全夜队列
   从此跑 HEAD 修复版落地代码。
3. 在飞陈旧袋不代修（属主责任制）：队列基底重验机制会正确拦截（cascade_stale 同款），
   本战役代码批排在其后落地。

## 4. 施工线编排（线内先挖后干、线间并行流水）

| 线 | 文件所有权（互斥） | 交付物 |
|----|------------------|--------|
| A | scripts/commit_queue.py + scripts/governance/enqueue_preflight.py(新) | M1.1 三入口之一挂线(skip={SESSION,CLAIM})、M1.3 requeue 补 base_blobs+envelope 继承+重投熔断(≥3 需 --force)、M2.2 冲突标记字节预扫、M3.3 死因处方字段、死因标记表补齐 |
| B | commit_preflight.py + create_guard.py + 翻译门适配 | M2.1 CREATE-GUARD 落地同源化(HEAD 册+袋内注册表覆盖)、M2.3 TRANSLATION 同源适配、token 处方串 |
| C | protected_paths_gate.py + approval_resolver.py(新) + ruling_registry.yaml | M4.1 共享裁定解析器、M4.2 gate/preflight 同源复用+marker 反查防伪、M4.3 #410 三失真修补 |
| D | commit_queue_landing.py | M1.2 reroute 拒绝不降级、M3.2 sid 断言、M5.1 快照写后读回自验(合并态基准)、M5.2 fresh-import 判别+活锁计数 |
| E | qcure_offset_report.py(新) + fullflow 红灯 | 对消报表生成器（验收承重）、NightlySentiment 红灯诊断修复 |

**落地顺序**：登记批（token 册+翻译册+depgraph 设计节点，单批先行）→ 战役文档批 →
A → B/C/E 并行 → D（等 A 的新模块入 HEAD）→ 红蓝对抗 → 对消报表验收。

## 5. 验收口径（战役级）

1. 395+ 笔历史死信回放预检：A/B/C 三因族拦截率 ≥95%；908+ 笔 done 回放误拦 ≈0。
2. 对消报表（线E 生成器）产出周窗死因族 × 预检拦截对照。
3. 红蓝对抗连续两轮零问题；全量相关测试两轮零失败。
4. 全流通面：红灯清零（NightlySentiment 修复或带处方挂起）、黄灯带矿脉登记。

## 6. 勘误（回放台实测对挖矿结论的修正，2026-09-25 03:3x）

1. **"冲突标记残留 50 笔（12.7%）"系误分类**：GATE-PRECOMMIT-RUN 死信文本里
   "检测未解决的合并冲突标记……"是 pre-commit 逐项打印的检查项**标题行**（绝大多数实际
   Passed），挖矿C按标题行归因出错。真实验（dead blob 全量字节扫 0 命中 + 死信全文验读）：
   该族真实死因主体是 **GATE-PROTECTED-PATHS Layer2（rules/ 受保护路径无批文）**与个别私钥/
   其他 hook 实败。治本归属不变——正是 M4 裁定适配器（#410 approved_paths）的靶子；
   M2.2 袋级冲突扫保留（防真实标记污染袋，回放证明对历史 50 笔非靶）。
2. 验收口径相应修正：不再以"冲突标记族拦截 95%"为靶，改为——
   ①CREATE-GUARD 无 token 族中"今日仍会死"的文件面拦截率 100%（实测 163/163）；
   ②done 袋回放误拦 0/74（untracked 抽样）；③对消报表（线E）持续观测。
3. #410 approved_paths 授权宽度提示：`docs/01_policies_and_standards/rules/` 全目录 +
   expires 2026-10-08，宽于 #410 字面三袋范围——有界豁免窗口内接受，到期自动收紧；
   续期须 Owner 重新裁定。

## 7. 长尾登记（本战役不施工，防遗失）

- depends_on 强制前置（排序锁）与 B5 退避——queue_scheduler 二期
- 热册三向合并 64 笔族治本（身份键规范/合并器歧义）——独立专包 M5.3
- pending 项 sidecar/DB 化（幽灵写手族根除）
- gate files_trigger YAML 注入校验
- blobs 退役通道（引用计数+宽限期+归档优于删除）
- 主区收敛 skipped_dirty 无人读的闭环（reconciler 事件触发补收敛）
- schtasks last-result 对账件；宪法"7 子命令"vs 实测 8 个的文档漂移
- gate 链 residual 段计时（landing_phase_stats 97.5% 残差）
