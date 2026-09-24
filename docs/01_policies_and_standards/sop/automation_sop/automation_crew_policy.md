---
doc_type: policy
ttl: permanent
title: 自动化班底值守 SOP（双引擎两班制：治理班×业务班）
status: active
version: 1.0.0
date: '2026-09-24'
owner: ZephyrAlpha-Owner
---

# 自动化班底值守 SOP

> **一句话定位**：Qoder（千问白班）+ ZCode（GLM 夜班）+ Owner 插单席的全部自动化施工的操作唯一真源——编制、切碎机制、重复指令、铁律、协议。
> **净零声明**：本册收拢 `docs/_working/cmd_ledger/automation_plan_discussion.md` 讨论册的口头机制成文，替代散落各包 LEDGER 的操作口径；不新增 gate/规则/注册表；任务清单（附录A）随战役在桥册滚动，本册只载编制与机制骨架。
> **审计分工**（防双真源）：域审计方法论唯一真源=根 `audit_prompts_20_ai.md`（AI-00+22 域）；本册只定义"谁在什么时间用切碎方式跑它"。

## 1. 引擎与窗口

| 引擎 | 模型/定位 | 窗口 | 截止 |
|---|---|---|---|
| Qoder | 千问 3.8 Flash，弱→纯执行+挖矿苦力 | 24h | 2026-09-30（免费止） |
| ZCode | GLM-5.3 Flash，较强→审裁+落地+自己干活 | 每晚 23:00-09:00 | 2026-10-08（免费止） |
| GPU | Owner 自己单独对话负责（编制外） | 见 GPU 战役册 | — |
| Owner 席 | 手机插单 | 随时 | — |

铁则：所有自动化带**免费窗止日自删条款**（到期夜出收官总报+提醒 Owner 删自动化）。

## 2. 两班编制

- **治理班**：项目本体干净/对齐/新鲜——全景图、图书馆、目录文件、临时文件归档清理、深审（表头字段全套）、死信堵点、注册表健康、提交链、收尾清账。
- **业务班**：挖 alpha——283问消费、挖数据源、挖因子、挖策略、**全网战法收集**（外网挖到挖不干净为止）、数据回补、模拟盘跟投。

### 2.1 夜班 9 席（ZCode，一席一事，裁定+干活双职饱和制）

| 席 | 事 | 班 |
|---|---|---|
| ① 总指挥 | 分派/点名催饱和/增量死信仲裁/AI层广播（核验两条件后自放）/晨报 | 两班总调度 |
| ② 283问消费席 | 工单+insuff 裁定+fail 处置+复考排程 | 业务 |
| ③ 审计对齐席 | 假绿核销/dedupe/fail_open_register/audit_all 缺口 | 治理 |
| ④ 提交优化席 | 提速六台包/心跳线程化/README | 治理 |
| ⑤ 死信清账席 | 存量死信按死因分诊→修复→requeue | 治理 |
| ⑥ 挖矿审查席 | 审白天矿产：合格入册/返工单/销项 | 业务 |
| ⑦ AI层/模拟盘收尾席 | 245件(广播后)/模拟盘17/压测hold看护 | 治理(收尾) |
| ⑧ 数据作业席 | 缺日回补/gaps 销号/断供对账 | 业务 |
| ⑨ 注册表健康观测席 | 每日 reconcile 探针防蒸发/W-M1 双轨对账/Phase2 扳机 | 治理 |
| ⑩ Owner 席 | 桥册"Owner 插单"节写一行，当夜①席优先调度 | — |

sid 规范：`st-night-<MMDD>-<席号>`（ZCode）；`st-qoder-<岗>-<MMDD>-<NN>`（Qoder）。

### 2.2 白天岗位（Qoder，写席 ≤5 + 读席不限）

| 岗 | 事 | 写席 |
|---|---|---|
| A1-A8 深审岗 | 22 域分片深审（映射见 §4.2），每批 100-300 文件，游标续批 | 台账追加型 |
| M1 挖数据源 | SL-B 线 mining memo | 写 |
| M2 挖因子 | prereg 备料（**Owner 签字前不实跑**） | 写 |
| M3 挖策略 | 组合候选+历史复盘素材（重算力归 GPU/夜班） | 写 |
| E1 数据回补实跑 | 既定 runner 实跑，失败即停 | 写 |
| E2 机械修复执行 | 销返工单+"改数不改逻辑"项 | 写 |
| R 读席组 | 证据采集/GPU-viability 扫描/盘点（只读） | 读 |

**千问改数不改逻辑**：配置/数据/文档直接改；代码逻辑只出补丁单，夜班 GLM 落。

## 3. 铁律（违者夜班仲裁回滚）

1. 冷启动三步（PATH 修 Python312→lock_files cleanup→process_reaper --status）；reaper 不在=禁写只报。
2. 改前 claim、毕后 release；提交唯一正门 `scripts/git_commit.py --enqueue`；禁裸 git commit。
3. 新建文件必登记 creation_token（token 批先行或与内容同袋）；热文件必 safe_write_text。
4. 写域互斥按桥册分派表；跨域先登记改派；外来 staged 违规 warn 不代修。
5. 失败即停：提交失败写堵点册即停，勿硬啃重试。
6. 禁无事生非：任务必须在桥册/任务清单有登记；新活先入册再开工。
7. Owner-only 禁入：prereg 签字/凭据 R4/生产流转门/注册表净删/flag 出厂翻转/GPU 终裁。
8. 长批先登记 process_reaper_keep；.runtime 根禁直写；.ps1 纯 ASCII；测试禁写生产路径。

## 4. 切碎四件套与重复指令（核心机制）

### 4.1 每岗四件套（`docs/_working/automation_campaign/<岗>/`）

`scope.md` 板块清单（静态）｜`checkpoint.md` 游标（每批推进）｜`ledger.md` findings 台账（追加式）｜`instruction.md` **恒定重复指令**。

自动化只能发重复指令 → 指令恒定+游标自寻址续批；板块审完自标 DONE 停工。

### 4.2 深审岗与 22 域映射（域定义唯一真源=audit_prompts_20_ai.md 第2章）

| 白天岗 | 承接域 |
|---|---|
| A1 根目录岗 | AI-01（仓根工程入口） |
| A2 文档文字岗 | AI-17~AI-20（文档与目录域） |
| A3-A6 代码岗×4 | AI-03~AI-16 代码域按域表四等分（分派时由总指挥按第2章现场切） |
| A7 配置测试岗 | AI-02（配置+架构元）+tests 域 |
| A8 scripts/横切岗 | AI-21/AI-22（横切）+scripts |

深审产出=findings 台账+补丁单；**审计员不改代码逻辑**（铁律 8/千问改数不改逻辑）。

### 4.3 重复指令模板

```
【<岗>】（本指令恒定，每次原样重发）
1. 冷启动三步（铁律1）；reaper 不在=禁写只报
2. 读 docs/_working/automation_campaign/<岗>/checkpoint.md；已 DONE 则短报退出
3. 从 scope.md 取下一批 ≤100 文件（游标起）
4. 按本岗判据逐文件处理；产出追加 ledger.md（safe_write CAS+先 claim）；代码逻辑问题只记补丁单
5. 推进 checkpoint.md；清单见底标 DONE 并报总数
6. 提交走 scripts/git_commit.py --session <sid> --files <清单> --enqueue；失败写堵点册即停
铁律：只做本岗板块；热册被并发改写立即停手上报；禁跨板块；禁新建规则/gate/注册表
```

## 5. 协议

- **晨报**：08:45 前①席出（真哈希/队列终态/各席一句话/呈批项），Owner 手机看板。
- **插单**：Owner 在桥册"Owner 插单"节写一行→当夜①席优先排。
- **AI层广播权**：①席核验（队列清空+件数与原令核对）后自放。
- **昼夜闭环**：白天挖+采+跑+审 → 夜里审+裁+落地+自己修 → 白天按判词继续。①席逐席点名，闲席转溢出活（饱和制）。

## 附录A：两班任务清单（v1，随桥册滚动）

**治理班**：全景图对齐（GOMAP 孤儿）｜图书馆治理（library_sop 编目+词典残差）｜目录/临时文件清理归档｜深审 A1-A8（含 registry 表头字段）｜死信+堵点+队列卫生｜注册表健康观测｜提交链优化+README｜audit_all 缺口收口｜W-M1 双轨观测至 Phase2｜AI层/模拟盘收尾清账

**业务班**：283问消费（工单11张/insuff96/fail45/复考142）｜挖数据源（SL-B 10线）｜挖因子（prereg 管道，签字前备料）｜挖策略（组合候选）｜全网战法收集（backtest_system_sop/sop_c §9 渠道）｜数据回补（known_data_gaps）｜模拟盘跟投

## 附录B：业务全链挂点（挖→考→接→装→用→巡）

| 环 | 真源 |
|---|---|
| 挖 | 数据源=data_ops_sop/data_source_onboarding_sop｜因子=mining_sop/factor_mining（八段）｜指标=indicator_mining（TASC）｜战法=backtest_system_sop/sop_c（+§9 外网渠道） |
| 考 | 因子/策略 E4 正考=backtest exam_policy｜问题金字塔 283 问考试=PG meta_question（运营 SOP 候补：升 exam_policy） |
| 接 | 模块施工=construction_sop 15步｜挂载=TDM 消费 S1-S9｜生产流转=strategy_production_map+risk_tier 门位 |
| 装 | 整装回测=backtest sop_a 全图编排+sop_b 节点循环（成本焊考尺+HOLDOUT） |
| 用 | 模拟盘/实盘管线（ops_sop 应急；实盘四禁常效） |
| 巡 | 新鲜窗复考（②席排程）｜退役=review_sop/rule_disposition 六闸六归宿+源线谱 U6 |

粒度定案（Owner 2026-09-24）：不按环节新造 SOP——挖矿按对象分族已有；考试→整装回测本就同族（backtest_system_sop）；缺环仅"问题金字塔考试运营"候补升级 exam_policy，全链索引即本附录。
