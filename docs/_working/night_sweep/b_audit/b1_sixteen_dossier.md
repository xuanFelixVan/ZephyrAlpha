---
ttl: task_bound
title: "T1-B1 旧数据治理包 16 件档案卡（给 Owner 的大白话报告底稿）"
session: st-menu-t1b1-20260930
updated: 2026-09-30
---

# B1 旧数据治理包（src/zephyr/data_eng/）16 件逐件档案卡

> **Owner 问**："旧数据治理包 16 件是什么东西有什么用？"
> **Owner 本夜批复（原文留痕）**："你挖矿确定是没用的就可以删除，你可以先告诉我旧数据治理包 16 件是什么东西有什么用。"
> **授权语义**：挖矿确认无用即可删（git 历史即留档，可回滚），且须交付本报告。

## 一、这包东西是什么（大白话总述）

2026 年 6-8 月"数据工程域"蓝图波（AUD-DRAFT-001-DIGEST，CAND-DATENG-001~009）按图纸一次性造出的
16 个 Python 文件（9 个真实现 + 7 个空目录占位），定位是"数据工程的五层流水线"：湖分层、冷归档、
流处理、增量更新、清洗、告警、期望校验、SLA 预测、GPU 配额。设计上全部是"纯内存裁决核 + 回调注入"，
等一个"运行时装配批"把它们接进生产——**但装配从未发生**：生产代码零 import、零计划任务、零触发
（F127 案卷 AST 实测 + 本夜逐件复扫复核）。与此同时它该干的活，真身早已由别的现役件承载
（冷归档=scripts/ch/archiver.py F08 链；清洗=cleaning_rule_engine/cleaning_anomaly_hosting 接线中）。

## 二、16 件逐件档案（五行卡）

### 1. cold_data_archive_manager.py（338 行）
- **干什么**：管"老数据搬冷宫"的调度员——决定哪些 ClickHouse 老分区该归档、记账（SQLite 索引）、定期清理。
- **为什么当初建**：B13-04331 蓝图波 P2（2026-08-26），想给冷归档配一个带索引和保留期的编排层。
- **现在为什么没用**：这活早有人干且干得全得多——现役 `scripts/ch/archiver.py`（920 行，四命令，
  MD5+抽样行校验/manifest/dry_run/restore 全链，F:/zephyr_cold 实库 2211 文件/117.6G）。本件零消费
  （AST PROD=0，唯一消费者=自己的测试），且它自建第二套归档索引=违反真源唯一铁律（RULE-SSOT），
  与 2026-09-28 Owner 终裁定 INFRA-STORE-003"一盘一责"直接冲突。
- **处置**：**删**（先归档留证后 git rm）。

### 2. data_lake_manager.py（335 行）
- **干什么**：数据湖三层管家——热层（CH 近 30 天）/温层（本地 Parquet）/冷层（归档）之间搬数据、清过期、压压缩。
- **为什么当初建**：B5-07240 蓝图波 P2（2026-08-26），对标大厂数据湖分层治理。
- **现在为什么没用**：零消费（PROD=0）；"三层湖"的存储哲学与 Owner 已裁定的"一盘一责"存储地图
  （冷库 F/备份 G/软件 E 各司其职）冲突——本仓根本不搞三层湖；层间迁移的活由 F08 链+存储分层件承担。
- **处置**：**删**（先归档留证后 git rm）。

### 3. stream_processing_engine.py（352 行）
- **干什么**：单机版迷你 Flink——事件流进窗口聚合、水位线、迟到数据处理、背压信号。
- **为什么当初建**：B5-07234 蓝图波 P2（2026-08-26），想要一个不引重依赖的流处理引擎。
- **现在为什么没用**：零消费（PROD=0）；且"常驻流处理"与宪法 §9.3"事件触发、禁 cron/Timer/常驻流"
  运维铁律相抵——就算接了也是违宪件。行情聚合真身=现役 kline_resampler 等件。
- **处置**：**删**（先归档留证后 git rm）。

### 4. cleaning_anomaly_engine.py（404 行）
- **干什么**：行情数据体检医生——对 OHLCV 帧查五类病（价格跳变/复权断点/重复 bar/量能异常/缺失），
  能自动修小病、标记大病、留审计。
- **为什么当初建**：CAND-DATENG-001（2026-08-25），清洗规则库+自动修复闭环。
- **现在为什么没用——【改判：有用，不能删】**：本夜实挖发现**在途会话已把它接进生产**
  （staged 未落地的 `cleaning_anomaly_hosting.py` 头注自证"五类检出真身"，挂 L13
  data_supply_sentinel 排班腿托管第三段，R-M1-06 四引擎接线台账 wired 在册）——删除会炸掉
  他会话在途的生产接线。NB1-B1 卡"同域重复簇"判据被新消费面证据推翻。
- **处置**：**储备**（保留在树，注记接线在途；判据"零消费者实证"不过）。

### 5. data_anomaly_alerter.py（458 行）
- **干什么**：数据异常报警器——四路检测（跳变 z-score/缺失率/量价背离/跨源偏差）+ 告警分级路由。
- **为什么当初建**：B13-04267 蓝图波（2026-08-26），与清洗引擎分工"它修它报"。
- **现在为什么没用——【改判：接口位被预留，不能删】**：在途 `cleaning_anomaly_hosting.py`
  四引擎接线台账明文"接口位预留 data_anomaly_alerter（六检测器，宿主同款托管待批）"——
  它是活跃接线工程的下一站，不是弃子。本夜 HEAD 生产消费=0 属实，但"功能被替代实证"不过
  （接线台账证伪"被替代"）。
- **处置**：**储备**（保留在树，注记接口位预留待批）。

### 6. expectation_governance.py（295 行）
- **干什么**：数据质量期望管家——用 YAML 写"数据应该长什么样"（列齐/非空/值域/分布/时效），
  违反了就 block/degrade/warn 三档处置。
- **为什么当初建**：CAND-DATENG-002（2026-08-25），轻量自研替代 Great Expectations 重依赖。
- **现在为什么没用——【改判：接口位被预留，不能删】**：同上，四引擎接线台账明文"接口位预留
  expectation_governance（期望套件，判据册 suite YAML 零在盘待批）"。质量门真身现有
  quality_gate/cleaning_rule_engine，但期望套件语义是台账预留槽位。
- **处置**：**储备**（保留在树，注记接口位预留待批）。

### 7. gpu_resource_manager.py（288 行）
- **干什么**：GPU 显存分家管家——训练/推理各分多少显存、盘中推理优先盘后训练、OOM 时降级 CPU 并告警。
- **为什么当初建**：B5-07239 蓝图波 P2（2026-08-26），B5 R-100 GPU 预算需求。
- **现在为什么没用——【改判：GPU 队领地交叉未裁，不能删】**：零消费属实，但 NB1-B1 卡自己标注
  "GPU 队（st-gpu-conv2 L2 薄核）在产——若其验收需要配额尺，复活并落 GPU 队领地，本车道不代裁"。
  GPU 面是别队领地（总纲避让图），"功能被替代"无法在本车道实证 → 按纪律降级。
- **处置**：**储备**（保留在树，注记待 GPU 队裁定，复活走 git 历史）。

### 8. incremental_update_engine.py（302 行）
- **干什么**：数据增量更新协调员——水位线/updated_at/行数哈希三通道查"哪些数据变了"，
  抽样对账防增量漏修。
- **为什么当初建**：91 增量更新协调引擎蓝图（2026-08-26），给因子窗口态供登记与快照。
- **现在为什么没用**：零生产消费；其 SamplingReconciler 与现役事件触发 reconciler 链职责相邻——
  现在接入会形成**第二 reconciler 真源**（违反真源唯一）。
- **处置**：**储备**（NB1-B1 卡原判；思路记 reconciler 氏族备忘，接事件触发版时从 git 历史取材）。

### 9. quality_sla_breach_predictor.py（249 行）
- **干什么**：SLA 违约预言家——用历史达成率趋势外推（最小二乘）+ 错误预算消耗双线预测
  "什么时候会违约"，Google SRE 式 burn-rate 分级提前报警。
- **为什么当初建**：B14-04723 蓝图波 P2（2026-08-26），给数据质量 SLO 配预测尺。
- **为什么值得救**：全网无同类（SRE 标准闭式解单机化，249 行零依赖）；F127 案卷自己指出的缺口
  "无 gate 保证归档计划被执行"正缺这把尺——本夜把它接给 F08 冷归档链当违约预言家用。
- **处置**：**融合**（迁 src/zephyr/data/quality/，消费面=归档 manifest 新鲜度 SLA burn-rate）。

### 10-15. 六个空目录占位件（各 27 行，纯占位）
`api/__init__.py`、`core/__init__.py`、`models/__init__.py`、`services/__init__.py`、
`infrastructure/__init__.py`、`_extensions/__init__.py`
- **干什么**：什么也不干——2026-06-21 脚手架批（a5c1a81787）按"经典分层目录"预挖的空文件夹标记，
  里面只有 `__all__ = []`。
- **为什么当初建**：蓝图波摆架构姿势（api/core/models/services 五层企业范式）。
- **现在为什么没用**：2026-08-22 STR-01 架构审查即标 [DORMANT]"未启用占位模板，勿当实现引用"；
  全仓零引用（无任何 `zephyr.data_eng.api/core/...` import）；四个月零内容零变化。
- **处置**：**删**（先归档留证后 git rm——空占位无功能可替代之说，纯删除）。

### 16. `__init__.py`（93 行，包门面）
- **干什么**：包大门——把包内几个类转口 re-export，并载有 2026-09-29 全包 [DEPRECATED]+successor 退役注记。
- **现在为什么没用**：不删——包内还住着 5 个储备件+1 个融合后剩余件，大门必须留；但退役注记
  需按本夜分件处置结果刷新（净删面收窄为 3 实体+6 空占位）。
- **处置**：**保留+注记刷新**。

## 三、处置总账

| 处置 | 件数 | 清单 |
|---|---|---|
| **删** | 9（3 实体+6 空占位）+3 测试 | cold_data_archive_manager / data_lake_manager / stream_processing_engine + api/core/models/services/infrastructure/_extensions 六空占位 + tests/data_eng/ 对应三测试 |
| **融合** | 1 | quality_sla_breach_predictor → src/zephyr/data/quality/sla_breach_predictor.py（消费面=归档 SLA burn-rate） |
| **储备** | 5 | cleaning_anomaly_engine（在途接线 wired）/ data_anomaly_alerter（接口位预留）/ expectation_governance（接口位预留）/ gpu_resource_manager（GPU 队领地）/ incremental_update_engine（reconciler 氏族备忘） |
| **保留** | 1 | 包 __init__.py（门面+注记刷新） |

## 四、判据与证据方法（可复算）

- 逐件判据三把尺：①零消费者实证（HEAD 全仓 grep+AST 面，区分运行时 import/TYPE_CHECKING/注释）
  ②功能被替代实证 ③数据无独有内容。**任一不过→降级储备不删**（本夜 4 件因此从"删"降级）。
- 新证据（NB1-B1 卡快照后出现）：staged 在途件 `src/zephyr/data/cleaning_anomaly_hosting.py`
  （含 tests，git status=A）+ `supply_sentinel.py` 接线改动（M）——头注载四引擎接线台账，
  推翻 cleaning_anomaly_engine/alerter/expectation 三件"弃子"定性。
- 与 #44（F130 ml_serve）同范：净删面勘误（NB1 卡表列 7 删→实证 3 删+5 储备）、
  G 盘 sha256 归档留证后 git rm、dangling 登记面移交维护班。

## 五、附录：储备件清单（deprecated/reserve 注记在树，不改行为）

| 件 | 注记语义 | 复活路径 |
|---|---|---|
| cleaning_anomaly_engine.py | 四引擎接线 wired（在途托管第三段检出真身） | 无需复活——在途件落地即现役 |
| data_anomaly_alerter.py | 四引擎台账接口位预留（托管待批） | Owner 批托管后按 cleaning_anomaly_hosting 同款接 |
| expectation_governance.py | 四引擎台账接口位预留（判据册零在盘待批） | 批后先立 suite YAML 判据册再接 |
| gpu_resource_manager.py | GPU 队领地交叉未裁（NB1-B1 不代裁） | st-gpu-conv2 L2 验收若需配额尺，从 git 历史复活并落 GPU 队 |
| incremental_update_engine.py | SamplingReconciler 备忘；禁第二 reconciler 真源 | 接事件触发版对账时从 git 历史取材，并入现役 reconciler 链 |

dangling 登记面（移交维护班，同 #44 先例）：MOD-DATA_ENG_api/core/models/services/infrastructure/
_extensions 六 module_id 翻译/文档条目；quality_sla_breach_predictor 的 module index.md
（docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/index.md）。
