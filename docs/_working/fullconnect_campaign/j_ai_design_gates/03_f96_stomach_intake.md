---
ttl: task_bound
title: F96 胃·全网搜索消化设备——挖干案卷
session: zc-l10-20260927
---

# F96 · 胃·全网搜索消化设备（搜索→清洗→情报 inbox→供 F20 点菜）

> 总册行（00_全环节总册.md:166）：partial（业务线代建 v0，升级归 AI 层）｜上游 F31｜下游 F20/F02｜P1
> 第一证据源：docs/_working/automation/inbox/＋20260917_fullauto_skeleton_v1.md §四＋fullflow_mining/m4_ai_layer/

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | F31 L9 源线（missing，登记态）；现行实际进料=scripts/automation/intel_harvester.py 产出收件箱条目 |
| 下游消费 | F20 车道G：scripts/backtest/lane_g_stomach_intake.py（MOD-AUTO-E1G-001）消化 inbox→data/strategy_intake/lane_g_candidates.csv 台账；E1 编排 factory_intake_pipeline.py |
| 自动化触发 | intel_harvester=计划任务驱动（register_model_intel_scan_task.ps1 在册）；lane_g_stomach=STARTUP manual（"手动 CLI 进货件非常驻服务…接线前人工/会话触发"，头部 noqa 实证）；**事件接线未挂**（总册 F20 行同判） |
| 真源与注册表 | 收件箱=docs/_working/automation/inbox/（实测 index.md+intel-20260916.md 共 2 文件=仅 1 期真产物）；骨架定调=20260917_fullauto_skeleton_v1.md:9"AI 层建胃，业务层点菜"＋:46 P1"搜索设备 v0（胃地基）本线代建" |
| 门禁与质量尺 | lane_g 头部 INVARIANTS：出生证机器写入/AI 禁手填、运动员不兼任裁判（判定权 E2/E4）、CAND-md5 内容寻址去重、LLM 必经 OllamaChat（内置 LSG fail-closed）、LLM 失败不入 seen；TESTS=tests/backtest/test_lane_g_stomach_intake.py |
| 当前运行状态 | **partial（黄）**：v0 链路件全在且 inbox 有 1 期产物，但①收件箱 09-16 后无新产物②点菜侧事件接线未挂③升级归 AI 层未启动 |

## 二、子模块三级枚举（胃三段+点菜）

1. **抓取/搜索段**：scripts/automation/intel_harvester.py（真源 L3 职责——lane_g 头部"本件不联网不抓取，抓取是真源 L3 的职责"）；配套 validate_intel_registry.py+register_model_intel_scan_task.ps1。
2. **收件箱段**：docs/_working/automation/inbox/（intel-*.md 制式）；容量实证=1 期（20260916），供给断流嫌疑。
3. **消化段**：scripts/backtest/lane_g_stomach_intake.py——收件箱→本地 LLM 抽 0-2 条可检验假说/篇→lane_g_candidates.csv 台账（只追加）；按 url 记账 seen log 防重消化。
4. **点菜段**（下游 F20）：E1 编排消费 lane_g_candidates.csv；总册 F20 行"事件接线未挂；车道 F=F06 网格仅代码车道，图节点补挂=跨线欠账"。

## 三、接线四态独立复核

- 总册判 **partial**：独立复核成立——件全在（harvester+inbox+stomach+tests 全实存）但零事件触发链（stomach STARTUP manual+lane_g noqa 自认"接线前人工/会话触发"）且 inbox 断流（最新 20260916，今日 09-27，11 天无新条目）。
- **骨架勘误**：总册 F96 行真源锚"automation 骨架 §4"——docs/_working/automation/ 下无 00_skeleton/ 目录，骨架真名=**20260917_fullauto_skeleton_v1.md**（本日 find 实证）；引用时按此名。

### partial→built 施工最小集建议
1. **inbox 断流排查**：intel_harvester 计划任务状态核验（schtasks 查询+最近 run log）；修复或改事件触发。
2. **点菜事件接线**：E1 编排挂 lane_g_candidates.csv 新增事件（对齐 F20 行修法"图节点补挂"）；stomach 从 manual 转事件调用后保留 manual 兼容。
3. **升级移交 AI 层**：按骨架 :9 分工——搜索设备 v0 后迭代归 AI 层 L1 外扫（与 F94 施工项 7 外扫节拍宿主合并立项，一 host 两消费）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | inbox 11 天断流（供给 starving 下游） | 先查 harvester 任务存活（复跑命令§六） | P1 |
| G2 | 车道G 事件接线未挂 | 与 F20 跨线欠账并单施工 | P1 |
| G3 | 胃升级 AI 层无立项载体 | 与 F94 L1 外扫宿主合并（同件两消费） | P2 |
| G4 | 收件箱条目无 schema 校验 gate | intel-*.md 制式机检（轻量 gate 立案走 OBJ_R） | P2 |

## 五、自审闸三态

**代码/链路面=挖干可施工**（三段件+invariants+tests 全实证）；**任务存活与断流根因=待裁**（计划任务运行态本车道只读，不代修）；升级 AI 层=挂起（等 F94 施工批）。

## 六、复跑命令

```bash
ls docs/_working/automation/inbox/                                   # 收件箱容量（今日=2 文件/1 期）
head -30 scripts/backtest/lane_g_stomach_intake.py                   # MOD-AUTO-E1G-001 锚定头
schtasks /query /tn "*model_intel*" 2>/dev/null || echo "任务名需按 register_model_intel_scan_task.ps1 核对"
grep -n "搜索设备\|胃" docs/_working/automation/20260917_fullauto_skeleton_v1.md | head -4
python -m pytest tests/backtest/test_lane_g_stomach_intake.py -q    # 点菜件测试网
```
