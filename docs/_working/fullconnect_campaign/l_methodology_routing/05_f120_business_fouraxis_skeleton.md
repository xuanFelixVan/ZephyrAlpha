---
ttl: task_bound
title: L12 案卷 F120 — 业务层四轴+底板骨架（design 态：工单消化对账与三选项待裁面）
session: zc-l12-20260927
---

# F120 业务层四轴+底板骨架（M 段横切，无 M0 旧号，骨架态=design/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | Owner 口述愿景锚（"day-to-day 全自动…唯一人工门=转正"）；三层定案（治理层=不犯错/业务层=赚钱/AI 层=进化，AI 层建胃业务层点菜）；总册 F120 行"工单队列 P0-P2 在案" |
| 下游消费 | F72-F75/F73（模拟盘四件/转正门/联赛/生命周期）；工单落点散布 M1-M8 各车道（F02 上架流水线=F1 车道挖项、F74 汇总器、F96 胃、F20 事件接线） |
| 自动化触发 | 骨架本体=文档件（design）；其 §11 nightly_sentiment 双真源已结案（计划任务 Disabled，08:20 schedule.yaml 槽在跑——本日 m5 01 册 :61 复核）；§3 WeeklyRest=ops_weekly_rest 计划任务（registry :1415） |
| 真源与注册表 | `docs/_working/automation/20260917_fullauto_skeleton_v1.md`（125 行 v1.1，completes_when="8+1 工段缺口全部立卡施工完毕且 Owner 驳回本骨架，或被 v2 替代"）+ `20260917_decision_skeleton_mining_report_v1.md`（41 行）+ `campaign/CAMPAIGN_LEDGER.md`（施工对账） |
| 门禁与质量尺 | 宪法 §9.3 事件触发禁 cron（骨架 §2 裁定 2 自引）；花钱纪律（唯一持续花钱点=④API 判净）；在飞避让清单（docs/03_modules、TDM、AGENTS.md、pf_core/backtest 禁写） |
| 当前运行状态 | **design（两方证据并存）**：工单主体已由 campaign 施工批消化（CAMPAIGN_LEDGER §1.5：L1/L3/L4/L5/L6 六件在 71257b59b2 一批落地，本日 git ls-files 复现）；但 risk_redline 零消费、体检/采集件零排班登记、三拍板项零裁定（本日复现）——completes_when 未达，骨架仍=在册 active design |

## 二、子模块三级枚举（四轴 → 底板 → 工单队列）

1. 四轴（§6 骨架封顶声明："不会再有第五条轴；再往下拆全是血肉"）：
   - ①决策权轴 L1-L5（"另一 AI"）②时间节拍轴 T1-T4（"另一 AI"）③产线工段轴 8+1（§1 全景表：①源发现②原料入库③自动上架④洗数据⑤因子合成⑥策略合成⑦两级回测⑧模拟盘→转正门＋⑨骨架体检）④生命周期轴（§6，Owner 2026-09-17 定）
2. 治理底板：§8 标准库（考纲表定义/阈值/版本/改因）+ §9 实盘红线体系（分级红线+黑天鹅缓冲仲裁+赚太多三查）；配套 §7 A/B 联赛+分仓、§10 算法升级三级、§11 排班四件套自身升级、§12 nightly_sentiment 双真源结案
3. 工单队列（§4）：P0×2（③数据源上架流水线/⑧转正建议书汇总器）｜P1×7（搜索设备 v0/⑥号车道/⑨骨架体检/A-B 联赛编排/§8 标准库/§9 红线执行器——表列 7 行）｜P2×2（④AI 判净站/WeeklyRest）｜已立 GPU-01~04；§5 Owner 拍板项六项（动骨架/转正实盘/关机窗/外呼边界/修标/退役在飞）

## 三、接线四态独立复核

| 件 | 四态判定 | 证据（本日复跑） |
|---|---|---|
| P0 ③上架流水线 | **已消化** | scripts/data/onboard_source.py 在库+blueprint 卡；CAMPAIGN_LEDGER :37 六件批注 |
| P0 ⑧转正汇总器 | **已消化（真缺口收窄）** | src/zephyr/strategy_pipeline/promotion_advisory.py（40ca90eb88）；台账自证"勿重建"，真缺口=组合门打分器+一页报告 |
| P1 搜索设备/⑥车道/⑨体检/§8 标准库 | **已消化** | intel_harvester.py、lane_g_stomach_intake.py、generate_skeleton_health.py、standards_lib.py（真身=config/standards.yaml，LEDGER :88）全在库 |
| P1 §9 红线执行器 | **码成闸空（半接线）** | src/zephyr/ex_sor/risk_redline.py 在库，但全仓消费方 grep 仅自身（本日复现）——与 M7"合规门全家族码成闸空"同款 |
| P2 WeeklyRest | **已消化（口径漂移）** | ops_weekly_rest 注册（LEDGER :37 Owner 批=9729a73390）；但休息窗时刻双值：骨架 §3=04:00 vs resource_profile_registry :25=05:00 |
| 体检/采集件排班 | **未入册** | resource_profile_registry grep skeleton_health/intel_harvester 零命中（本日复现）——四要素"自动触发"缺一 |
| 三拍板项裁定化 | **未闭环** | ruling_registry grep "骨锁肉动"=0 命中（本日；较 09-25 证据册记的 1 处时序提及更清零）——拍板项②（WeeklyRest）已事实批准但裁定登记面无痕 |
| 四轴↔总册映射 | **未登记** | 决策权/节拍/工段/生命周期四轴与 13 段 122 环节的对账表不存在（09-25 证据册 §三.4 判词维持） |

## 骨架勘误

1. 总册 F120 行"design（工单队列 P0-P2 在案）"的**"在案"半真**：工单实态是"队列已基本消化但未销账"——消化知识只存在于 CAMPAIGN_LEDGER，骨架册 §4 状态列零回写，总册与骨架册两本台账互不引用。骨架态=design 的准确读法="框架收编未决"，非"工单未施工"。
2. 三拍板项裁定痕迹较 09-25 证据册再降：ruling_registry "骨锁肉动"=0（证据册记 :5187 一处时序提及，现册无）——登记面变动，拍板项②"事实批准"目前仅 CAMPAIGN_LEDGER :37 与 registry notes 双手载，无裁定号。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | risk_redline 零消费（码成闸空） | 移交 M7 合规门接线工单同批（其 P0=合规门 12 件零注入同门位） | P1 |
| 2 | 骨架册 §4 工单状态列未销账+四轴映射未登记 | 待裁三选项 A 收编结案/B 升格框架真源/C 部分收编+残项清单（09-25 证据册 §四并排陈列，本卷不裁）→裁后一次性回写 | P1（裁前阻塞全流通 F120 翻态） |
| 3 | 休息窗 04:00 vs 05:00 双值 | 以 ops_weekly_rest 实际任务 action 为准统一后回改败方文档 | P2 |
| 4 | 体检/采集件零排班登记（四要素缺一） | 二选一：入 resource_profile_registry 排班，或明示"月度手工触发"豁免登记 | P2 |
| 5 | 三拍板项无裁定号 | 拍板项②按已事实批准补登记；①③随缺口 2 选项 C 一并裁定化 | P2 |

## 五、自审闸三态

**挖干（design 态裁前证据面）**：工单逐条落地物 git/盘面双复现 ✅ 零消费/零排班/零裁定三零点复现 ✅；**待裁**：骨架本体收编路径（选项 A/B/C 并排，Owner 裁）；risk_redline 接线门位（随 M7）。

## 六、复跑命令

```bash
git ls-files | grep -E "onboard_source|intel_harvester|generate_skeleton_health|standards_lib|risk_redline" | head -8  # 六件在库
grep -rln "risk_redline\|RiskRedline" src scripts --include="*.py" | grep -v "ex_sor/risk_redline"   # 应无输出=零消费
grep -n "skeleton_health\|intel_harvester" config/resource_profile_registry.yaml                      # 应无输出=零排班
grep -c "骨锁肉动" docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml             # =0
grep -n "04:00\|05:00" docs/_working/automation/20260917_fullauto_skeleton_v1.md | head -1           # §3=04:00
grep -n "weekly_rest 周日 05:00" config/resource_profile_registry.yaml                                # registry=05:00
sed -n '40,55p' docs/_working/automation/20260917_fullauto_skeleton_v1.md                            # §4 工单队列原表
```
