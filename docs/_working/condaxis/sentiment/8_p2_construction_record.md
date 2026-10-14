---
ttl: task_bound
title: 情绪线 P2 施工台账——daban 缺日回补留证＋快照器事件门挂接＋词表收编余量处置
created: '2026-10-13'
session: st-cdx-sent-20261013
status: construction_record
family_id: CONDAXIS-CAMPAIGN
completes_when: 随 CONDAXIS-CAMPAIGN P2 批归档
---

# 情绪线 P2 施工台账（Owner 2026-10-13 全授权令 · 会话 st-cdx-sent-20261013）

## §1 daban 缺日回补（数据面，证据全文见 [7_deep_history_assessment.md](7_deep_history_assessment.md) §1）

| 项 | 结果 |
|---|---|
| 真缺日 | **09-29/30 两日**（09-25=中秋休市非交易日，四源互证——挖矿册"三缺日"前提更正） |
| daban_board_event | FINAL 1,906→**2,044 行**、22→**24 交易日**；09-29=68 行（封住 56）、09-30=70 行（封住 56）；富化 138/138 全、封单代理 112/138；既有日行数零变动 |
| daban_engine_load | 同根因月末裂缝同批补齐：0→138 行（68+70）、22→24 交易日（tasks.yaml 在册 daban 相关任务同机制 additive 重放） |
| 回补通道 | InternalComputeProvider.fetch（table 路由）→ ch_writer.write_result（调度器写通道同款原语）；纯 additive INSERT 零删改；reaper keep 登记跑前加/跑毕除（零残留核实） |
| 根因 | `daban_board_event_derive`（weekend_calibration+incremental=false）调度窗=[月初,今日]（scheduler `_compute_start_date`）——月末跨界日落洞；治本选项呈 Owner（7_deep §1.4） |

## §2 快照器事件门挂接（码袋；挖矿 5_self §4"日批半=立即施工"落地）

- **新增**：`pipeline_events.py` 产出者 `maybe_snapshot_emotion_index`（+常量组 EMOTION_SNAPSHOT_*，83 行纯增量）——唤醒词=`emotion_index_close_final` SUCCESS（落表任务本体，非 daily_kline 词族：kline 完成点上快照会抢跑在落表前，5_self §3.2 禁抢跑；pre_open 刻意不入唤醒词防盘前抢记号）。骨架=maybe_refresh_regime_snapshot 同款（业务日级 marker 先落再动手+永不反噬+人工逃生口=快照器 CLI 直跑）。执行体=run_subprocess_hidden 子进程调快照器 CLI（--out-dir 钉绝对路径；300s 有界超时）。挂位=唤醒链最末（L9 段后新尾段，证据面不占分配/拍板时序）。
- **改动**：`emotion_index_snapshot.py` 头部 CONSUMERS/STARTUP 元数据同步（CLI 本体仍 manual，日批自动面=事件门子进程同码零分叉）。
- **测试**：tests/data/alt_data/test_emotion_index_snapshot.py 新增 5 件挂点测试（非唤醒词/pre_open 跳过、marker 幂等零子进程、成功路径 CLI 参数/绝对 out-dir/超时断言、记号先落+失败出声、resolve 失败不抛）——9/9 passed（含原 4 件）；monkeypatch 全隔离零生产 IO。冒烟：钩子同款子进程调用实测 rc=0（8,666 行全表快照落车道临时区，manifest 行可解析）。
- **回归**：pipeline_events 三测试袋 62 passed＋5 failed——5 失败经主区基线（无本班改动码）复现完全一致=车道环境预存（CH 冷却/data/runtime 缺席），非本班引入。
- **车道测试要点（留班）**：worktree 跑测试须 `ZEPHYR_ALPHA_ROOT=<worktree>`——usercustomize 启动即预导入主区 zephyr，包缓存劫持 sys.path.insert(0)。

## §3 词表收编余量处置表（2_L2_phase"余量清单"逐项）

| 项 | 处置 | 证据/落点 |
|---|---|---|
| E1 SentimentPhase 五段映射 | **已核在册，无需补** | 映射册 E1 行（FREEZING→capitulation 等）+registry 战役块 E1 行；主块 sent-cycle-5-A verbatim 不动（双块结构=P-1 既定披露） |
| E2 4+1 硬标签＋方向注记 | **已核在册，无需补** | 映射册 E2 行（最热≥80→RETREATING 陷阱注记）+registry E2/sent-phase-5-B |
| E3 EmotionPhase 4+1＋方向注记 | **已核在册，无需补** | 映射册 E3 行（最热→MANIA 对照面）+registry E3/youzi-5 |
| **A3 INTRADAY_TO_SIX registry 漂移（本班新发现）** | **机械纠偏已施**（safe_write_text CAS＋allow_mass_edit 审计留痕；registry v1.0.0→1.0.1） | official_ontology：①四类 target 类名对齐代码真源（MacroRegimeVocab 等带 Vocab 后缀，chief3 09-26 恢复后类名）；②approved_edges 旧值 DEFENSE→ACCUMULATION/ATTACK→IGNITION **与代码 INTRADAY_TO_SIX 不符**（现代码=DEFENSE→DISTRIBUTION/ATTACK→EXPANSION，有 git blob 溯源；旧值系 09-22/24 盘上蒸发版残影零溯源）——已对齐代码镜像；③新增 edge_mirror_note＋gap_disclosures VOCAB-GAP-6 全程披露；④执法门后缀匹配验证通过（四类 Vocab 类名 gate-match OK，收集 702 串） |
| A3 EUPHORIC→IGNITION proposed 校准 | **Owner 门，未动，登记待办** | 代码 :103 proposed 标注原样；registry proposed_edges/proposed_note 原样（仅补 02 统一件 §3 第二步挂起出处引用）——待 4 态收敛专项定论后呈批 |
| S5↔emotion_index 互映射 | **Owner 门，未动，登记待办** | 前置=Q10"温度计≠档位计"真裁定补登（#400 撞号，2_L2 §4 挂起面） |
| 主块 intraday-five 注记矛盾（"防御→DISTRIBUTION 均 proposed"） | **披露未改**（主块 verbatim 保护） | 与立法件 01（仅 euphoric→ignition 为 proposed）不符——VOCAB-GAP-6 披露，纠偏归该条作者（同 P-2 通道） |
| 段灰度输出（六段版 analyze_grayscale） | **待排期（非本班授权面）** | 2_L2 §3.3 建议①（025 旁挂六段版，BM-SEL-25 先例）——随 P2 后续批 |
| 映射册 A3 行号锚（:95-101→:98-104） | **无需改** | 映射册自序"行号漂移以符号名定位为准"；册已归档 |

## §4 遗留清单（交总包/后续班）

1. **daban 深史重放排期**（7_deep §4 分支 A 建议）：C1/C2 深史=仓内可推导（era 矩阵 §2），重放属重批须 Owner 排期窗（月块分片+夜间+reaper keep）。
2. **月末裂缝治本**（7_deep §1.4）：weekend_calibration 档窗口改"近 N 交易日回看"或纳入 catchup_guard overdue 面——调度器语义改动呈 Owner。
3. **诚实快照 manifest 扩列**（5_self §1 行 3：完整度/降级/分母剔除当日一行）：随 P2 判据冻结同批。
4. **周批/月批半**（5_self §4 挂起排期）：解锁条件=P2 判据冻结+Q13 权限表。
5. **A3 校准呈批材料**（4 态收敛专项状态核实+EUPHORIC 两案对照表）+ **S5 互映射**（Q10 前置）——Owner 门双待办。
6. **E5/E6/E7 事件件**（3_L3）与 TDM 挂接（6_tdm，Q14 挂位两案）——P1 呈批后执行。
