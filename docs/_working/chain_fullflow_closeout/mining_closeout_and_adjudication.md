---
ttl: task_bound
title: 全流通战役 09-26 挖矿收口与合并裁定（五路案卷索引）
owner: st-audit-fix-20260924
language: zh
status: active
---

# 挖矿收口页（只作索引与合并裁定，细节以各案卷为准）

- 作业性质：五路并行挖矿（M1-M5），全程只读；本域其余案卷 = D 队 `business_pipeline_skeleton.md` + 8 本 `lane_pipe_*.md`。
- 交卷实测（本文件写就时读数，`ls -l docs/_working/chain_fullflow_closeout/`）：
  M1 20,648B / M2 38,947B / M3 20,692B + 40,091B / M4 23,061B / M5 11,353B（M5 在卷增补中）。
  镜像与全部复现脚本：`.runtime/tmp/mine_dossiers_20260926/`（含 census 脚本与 raw json）。

## 一、分母读数（各案卷首节均带取数命令，勿引本页数当权威）

| 面 | 实测分母 | 出处案卷 |
|----|---------|---------|
| 死信 | 682 件/3 日窗，其中门禁+登记族 **484=71%**（战役此前 46% 口径**低估**） | `mine_door_registration_completion.md` |
| 快进/级联族 | **17/686≈2.5%**，其中合并语义可救仅 2 件≈0.3% | `mine_snapshot_selfconsistency_witness.md` |
| 业务链路 | N=62（通 30/半通 23/不通 9）→ 本轮拆到五段子环节；假绿灯全扫 270 任务命中 **5** | `mine_pipe_blockage_substages.md`／`mine_pipe_false_green_census.md` |
| 排队等待 | done 804：p50=263s／p90=1.2h／p99=9.1h／max=12.3h／>24h=0 | `mine_queue_liveness_and_trigger_mass.md` |
| 门耗时 | CREATE-GUARD 4488 次 × mean 23.4s = **累计 105,154s**（名册无 files_trigger 登记却每链全跑） | 同上 |
| 护栏接线 | 四态判定（真执法/装饰/半接线/判据失效）普查在卷 | `mine_guard_wiring_census.md` |

## 二、合并裁定（执行 AI 自裁，依据=挖矿 SOP §6 终局全貌量尺）

1. **方案封矿**：`非注册表文件通用逐文件三方合并`（战役 task #17）。
   依据从"死因占比 6%"改钉为 M2 的新分母 2.5%，且占比最高的 .json/.py/.md 是生成器产物或代码，
   **合并即错**——不是"来不及做"，是终局架构里没位置。落地侧的正确层位是"袋自洽见证 + 门侧登记补齐"。
2. **施工队列**（按"消灭人工参与 × 死因占比 × 现成通道存在"排序，逐条解锁条件在各自案卷 §自审闸）：
   - C1 封死信第一族＝**旁路**：`requeue` 通道与 `enqueue_item` 直调第 4 入口无入队预检（M1：部署后仍死 47 件、degraded_pass=0）。
   - C2 快照自洽见证层（H 队盘上有判别力：同尺在 dev 面 7 failed、带见证盘态 7 passed）
     **＋** 必须同批补 W17：CLI `enqueue --base-head` 分支不填 `base_blobs` ⇒ 按官方处方操作＝关掉新见证。
   - C3 CREATE-GUARD 触发面登记（名册补 `files_trigger`，或改 own-scope 差分）＝提交链最大单项耗时。
   - C4 假绿灯交叉尺：`task_runs` 回执与"目标表真行数/最新数据日"必须互证；`rows_written` 记回执；
     日期口径归一（`FetchPayload.start/end` 注记 date 而消费端拿 ISO 字符串直比＝str<date 共因，M3 H1）。
   - C5 装饰件接线（M5 在卷）＋ 入队预检"当场补齐/点名拒绝"（M1 施工 3 条）。
3. **挂起排期**（终局要、现在不急，解锁条件见案卷）：派生件让路重算、归属去文本化、
   生产侧新鲜性（M2 W9 证"装了就安全"是过度承诺）、G 队余面、M4 的 C1/C4/C6/C7/C9。
4. **待 Owner 门位（只登记，夜间不自决）**：
   hfq 表族补 `lineage_version`（DDL）；9 张空壳表建腿 vs 退役；recon/consensus/score 三处真源收敛；
   `commit_queue_interactive` 出厂 OFF 翻转窗口；预检设计原则改册的净零声明；热册合并语义变更；
   M4 另登 4 条。Ollama 重启提案 **封矿**（已有终局判断，不再重提）。

## 三、本窗已交付

- **GATE-21 自洽台改读提交绑定面**（检测器自己不再被主区脏盘装绿）：
  袋 `q-20260926-st-audit-fix-20260924-0040`（3 件：验证器 + `heal_derived_scalars` 共享真源 + 永久尺 8→17 例，
  变异自证摘掉半边即 3 例红）。落地判读只认 `git show dev:`。
- 五路案卷 + 复现脚本入册（本目录）。

## 四、⚠ 新登记缺陷（他班刚落地面，本包不代修）

`gate_auto_registrar` FAIL-CLOSED：`DOC-HEADER-SUITE` 与 `BLUEPRINT-FORMAT` 同 priority=77
⇒ `preflight gateway 初始化失败，入队预校验跳过`（02-26 02:4x 实测于 dev 面 `daf5e53176`，
本包入队时被拦下并原文留痕）。后果＝**一次撞号把门侧预检整体 disable**，带病袋直入队列、到落地侧才死。
归因＝批·T8 簇2 七台合一（`f3cac8b953`）新立聚合门未分配唯一 priority；在册先例＝后到者让位
（`RULING-COMMIT-VERIFIED 77->109`）。属主班自修为宜，本包只登记（宪法 §3.4 owner 责任制）。
