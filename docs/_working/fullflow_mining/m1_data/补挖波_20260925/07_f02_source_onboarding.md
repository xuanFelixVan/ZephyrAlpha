---
ttl: task_bound
lane: M1 数据链（补挖波，接续 st-commitspeed-tbl-20260924）
segment: F02 数据源接入生命周期（总册 P0 断链点：上架流水线=工段③最大空地）
mined_at: 2026-09-25
session: st-ailayer-fullflow-d
---

# 07_f02_source_onboarding — 数据源上架流水线补挖册（F02/D2 深挖）

> **与既有册关系**：01_ingest.md 只登记了 D2 SOP 入口不重挖（"治理侧归 M3"）；本册补挖其声明的 P0 断链点——**流水线串接现状**：SOP 七段逐段对照机械件，给出断点清单与工段③编排器施工面。

## 一、环节定义与边界

一句话：源发现→报批→建表→接入→验收三查→路由→退役的七段生命周期（SOP §1-§13），当前=**文档真源完整+零散机械件在位+全链零编排**。
- **供料方**：骨架总图 ⬜ 中类（供给侧）/消费端缺口（需求侧）/胃 F96 情报（总册 DAG F31→F02）。
- **消费方**：F01 采集调度（tasks.yaml）→ F06（DDL）→ F11（dataset 挂接义务）。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入 | 需求两入口（SOP §1：骨架 ⬜ 中类/消费端缺口）；三教训催生（股东户数断供两月/macro_data 频率口径/⬜ 中类从未挖矿——SOP 头注 2026-09-17 定调原文） |
| 下游消费 | tasks.yaml（271 任务）+schedule.yaml 槽位+business_data_categories 品类+data_asset_registry datasets（F11 挂接义务衔接）；消费端路由表=SOP §9 七域默认消费端 |
| 自动化触发 | **无编排器**（automation 骨架 20260917_fullauto_skeleton_v1.md:18 工段③原文："接线→建表→字段→下载→排班……DDL 工具/调度器/排班生成器零散在位；**全链最大空地**：数据源上架流水线，串起零散件"）；各段零散件自动化见 §三 对照表 |
| 真源与注册表 | 流程编排真源=data_ops_sop/data_source_onboarding_sop.md（v1.1.0，2026-09-18）；候选册=docs/_working/altdata_line/10_data_source_candidates.yaml（yaml 解析 **32 条**：27 candidate/1 integrated/1 graduated/3 rejected）；源资产册=architecture_model/data/data_sources_registry.yaml（**v2.6.0**，DS-* 条目，"同步 DB data_source_assets 派生 asset_catalog"）；纪律真源=data_ops_policy.md（本册引用不重挖） |
| 门禁与质量尺 | **门禁面收缩中**：DATA-TASK-COMPLETENESS（fallback_sources 盯防）**已于 2026-09-23 退役**（gate_registry.yaml:2054-2056，st-gslim P3，退役理由=warn-only 零触发零消费，w5_1 条2 直接命中，redirect=registry_incident_20260922/gate_audit_report_v1.md §C1）；table_registry.validate_tasks_yaml 仅 WARN 单检查（table⊆registry，:181-195）；disabled_reason 硬拦=**src 全树零实件**（grep 零命中，SOP §7 声称"门禁硬拦"失真） |
| 当前运行状态 | **黄（有通量但人肉编排）**。毕业两单实活：DS-CAND-000 股东户数→DS-EASTMONEY_DATACENTER（v2.5.0，2026-09-18 夜班 st-datapack-20260918，miniQMT 清退后续采正门）；DS-CAND-011 Hyperliquid→DS-HYPERLIQUID+DS-IRM（v2.6.0，st-ff-newsrc-20260918，"有源无册"登记债清偿）。近期全链手工串接范例=st-emomine 批（2026-09-23，git a9818b2ef2）：一个会话手工串 **provider 分支→schema DDL→品类登记→admin 建表→tasks.yaml 双任务→槽位→首跑落库→哨兵腿** 八件——流水线能走通，但每环靠会话记忆串接 |

## 三、七段×机械件对照表（取证核心）

| SOP 段 | 机械件现状 | 证据锚点 | 判定 |
|---|---|---|---|
| §1 立项/查重 | 查重三查（tasks.yaml+system.tables+known_data_gaps）全手工 | SOP §1.3 | 手工 |
| §2 全网挖矿 | 三重扫描方法论=mining_sop；产出登记 candidates.yaml | SOP §2 | 手工（方法论在） |
| §3 报批/毕业 | candidates.yaml 字段模板+四格评分在用（32 条实流）；毕业=手编 DS 册条目 | DS-CAND-000/011 两单实流 | **半手工，通量真实** |
| §4/§5 字段/表设计 | **最强环**：DDL-as-Code（schemas/categories/*.py+scripts/ch/apply_*_ddl.py 25 件+verify() 防假成功）+RULE-SCHEMA-TZ gate | 03 册已挖；SOP §5.2 | 机械在岗 |
| §6 Provider 接入 | capability 三闸实件在位（src/zephyr/data/capability_validator.py + capability_semantic_gate.py + capability_symbol_gate.py，scheduler 路由消费）；**fallback_sources 必填的登记时强制=真空**（DATA-TASK-COMPLETENESS 09-23 退役后无替代；现仅运行时消费 scheduler.py:1647-1685） | gate_registry:2054 | **门禁缺口** |
| §7 任务登记 | tasks.yaml 手编；validate_tasks_yaml 仅 WARN（table⊆registry 单检查，Phase 4 升 block 未做）；**disabled_reason 硬拦=零实件** | table_registry.py:181-195；grep disabled_reason src 零命中 | **门禁缺口×2** |
| §8 验收三查 | 失败留痕 failures/{date}_{task_id}.json=**实件在岗**（alerter.py:140 写、alert_webhook_dispatch.py:17 消费 CRITICAL 探针）；探活=supply_sentinel 腿（手工登记）；三查判定本身手工 | src/zephyr/data/alerter.py | 半机械 |
| §9 消费端接线 | "≥1 实际消费者"铁律=零机械化（05 册 T2 同案：品类↔dataset↔data_refs 三层覆盖率无对账器） | 05 册 T2 | **门禁缺口×3** |
| §10 退役 | #ARCH-351 退役映射表缺位（裁定#376 已授权设计，open P1）；DS-IFIND 能力迁移范式=registry v2.3.0 注释留痕范本在档 | architecture_issue_registry.yaml:22342-22360 | 断点已知 |
| §12 存储分层 | 抽屉登记制运转中（drawers.jsonl）；**但 §12 盘符已过时**（写 G:\zephyr_cold，2026-09-21 已 G→F 整迁，见 09 册）+§12 末段路径文本损坏（`\r` 转义事故：`G:\zephyr_cold` 后接乱码字节 0xC2 0x81+"esearch_reports"，应为 `\research_reports`） | SOP :157-166 cat -A 实证 | **修册件** |

## 四、堵点与病灶（断点清单=工单序列草案）

| # | 断点 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| O1 | **工段③编排器缺位**：候选→毕业→DS 册→provider→DDL→品类→tasks.yaml→槽位→首跑→哨兵腿，十环全靠会话人肉串接（st-emomine 批为实证） | 自动化骨架工单队列 P0 未开工（F120 design） | 单入口向导脚本（onboard_wizard：逐段校验+生成骨架件+16 查 checklist 机检化），复用零散件不重写 | 3-5 天 | 可立项（报总筹排期） |
| O2 | fallback_sources 登记时强制真空 | DATA-TASK-COMPLETENESS 以"零触发零消费"退役（09-23），SOP §6.2 仍引用它 | 两选一：①并入 O1 向导做硬校验（登记时拦截，非 commit gate）②SOP §6.2 改注"运行时消费+上架向导校验" | 0.5 天 | 是 |
| O3 | disabled_reason 硬拦=零实件，SOP §7 声称失真 | 声称的门禁从未落地或已随退役门删除 | 并入 O1 向导校验+修 SOP 措辞 | 0.2 天 | 是 |
| O4 | 毕业回写滞后：DS-CAND-000 已在 DS 册 v2.5.0 毕业，candidates.yaml status 仍 integrated | 毕业动作跨两册手工，无联动 | O1 向导内做"毕业=一键两册联动" | 0.3 天（并入 O1） | 是 |
| O5 | SOP §12 盘符过时（G:）+§12 末段路径乱码（转义事故损坏 policy 文本） | 09-21 G→F 迁移后未回扫 SOP；`\r` 转义写入事故 | safe_write_text 修 §12 两处：盘符 F:+修复路径文本 | 0.2 天 | 是 |
| O6 | 验收三查无自动判定器（①max(date) 新鲜②心跳记录③消费者可查，全人工目检） | 三查分散在哨兵/调度器/消费端三处 | supply_sentinel 腿覆盖①②已有；③=T2 对账器同批 | 1 天（与 05 册 T2 合并立项） | 是 |

## 五、提速与合并机会

1. O1 向导不是新造轮子：十环零散件全部已存在（DDL apply_*+verify+validate_tasks_yaml+alerter+supply_sentinel），向导=纯编排壳——符合内收判据"同真源可派生→必并"。
2. candidates.yaml 32 条中 27 条 candidate 滞留：四格评分已有，可加"四格≥3 自动出推进建议单"挂晨报，消化积压。

## 六、自审闸三态

**挖干可施工**（七段×机械件对照双源实证；O2/O3/O5 修册与校验可直开；O1 向导可立项施工报总筹排期；O6 与 05 册 T2 合并）。F02 断链点定性：**非零件断链，是编排断链**——总册"partial（流水线串接=工段③最大空地）"判定确认并细化。

## 七、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
grep -c "cand_id:" docs/_working/altdata_line/10_data_source_candidates.yaml        # 32
grep "status:" docs/_working/altdata_line/10_data_source_candidates.yaml | sort | uniq -c
sed -n '2054,2056p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml  # 退役注记
grep -rn "disabled_reason" src/zephyr/ --include="*.py" | grep -v __pycache__       # 数据域零命中
sed -n '18,18p' docs/_working/automation/20260917_fullauto_skeleton_v1.md           # 工段③原文
grep -n "G:\\\\zephyr_cold" docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md  # §12 过时盘符
git log --since=2026-09-17 --oneline -- src/zephyr/data/config/tasks.yaml           # 上架通量
```
