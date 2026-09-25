---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: 策略工厂供给链前半概述（F13-F22）——SF-A 挖矿作业簿总览与断点清单
date: 2026-09-25
status: mined
---

# SF 前半概述：E0 算力闸 → E1 编排+六车道 → E2 预审 → E3 构造

> **一句话**：策略工厂前半（进货侧）**代码件全在盘、单车道全部真实出过货**，但"编排→预审→构造"三段接线是**人工事件驱动**（无常驻/无日历触发器），且 2026-09-19 后全厂进货停滞；另实证一起新进货台账行蒸发事故（B 渠道 11 条）。
> 本册=SF-A（F13-F22 前半十环节）组级结论；F23-F29 后半归 SF-B。真源=config/strategy_production_map.yaml v0.2 + scripts/backtest/ 工厂脚本族 + data/strategy_intake/ 台账实测 + c1_backtest.hypothesis_precheck CH 台账实测（58 行）。

## 一、册清单与三态一行

| 册 | 环节 | 三态结论（图9 build_status） | SF-A 复核口径 |
|----|------|------------------------------|---------------|
| 01_f13_e0_compute_gate.md | F13 E0 算力闸 | partial → **闸门本体 built，缺审计落盘** | 拉式闸门+13 处消费端接线实证 |
| 02_f14_e1_intake_orchestration.md | F14 E1 进货编排 | partial → **编排本体 built，F 车道适配器+事件触发缺** | 七车道声明/E2 五源消费实证 |
| 03_f15_lane_a_community.md | F15 车道A 社区 | built（人工版口径） | 597 条台账+粗筛判定实测 |
| 04_f16_lane_b_ai_gen.md | F16 车道B AI生成 | partial → **生成器 built，台账蒸发事故+产出停滞** | 最新出货 09-14/09-16（11 行蒸发） |
| 05_f17_lane_c_formula_mining.md | F17 车道C 公式挖掘 | partial（三轨两通一零出货） | gplearn 16 条/智能体 8 条/MCTS 0 条 |
| 06_f18_lane_d_three_high.md | F18 车道D 三高 | partial → **筛选器 built，LLM 增补管线缺** | 40 条 2 批，最新 09-14 |
| 07_f19_lane_e_model_baseline.md | F19 车道E 模型基线 | partial（基线件全 built，出货=考尺件不卸进货台账） | QR 09-13/Kronos 09-16 实测 |
| 08_f20_lane_g_stomach_intake.md | F20 车道G 胃进货 | partial（本体 built，事件接线未挂+唯一一班零假说） | seen 5 条/候选 0 条，09-17 |
| 09_f21_e2_hypothesis_precheck.md | F21 E2 预审 | partial → **预审门 built，deferred 滞留+19 条不可达未重审** | CH 58 行 14 批实测 |
| 10_f22_e3_construct_translate.md | F22 E3 构造 | partial（159 桥+190 翻译 MVP built，过审消费无幂等推进） | 过审 13 条仅 6 条入 E3 |

## 二、重点回答：每车道「最近一次真实出货」（运行证据=data/strategy_intake/ birth_batch + CH 台账）

| 车道 | 台账 | 行数(实测) | 最新批次 | 最近真实出货 |
|------|------|-----------|----------|--------------|
| A 社区 | raw_manifest.csv + screen_c2.csv | 597 / 597 | C2 粗筛 2026-09-12 夜班（52cb9e8ab6） | **2026-09-12**（此后零新增，爬虫未建） |
| B AI生成 | lane_b_candidates.csv | 4（蒸发前应为 15） | E1B-20260914-053418；次批 E1B-20260916-021130（11 行已蒸发，CH 有档） | **2026-09-16 02:11**（判定存 CH）／进货台账现存批次 09-14 |
| C 公式(gplearn) | lane_c_candidates.csv | 16 | E1C-20260922-A101/HF（共 6 条） | **2026-09-22** |
| C 智能体(C2) | lane_c2_candidates.csv | 8 | E1C2-20260915-023956 | 2026-09-15 |
| C MCTS(C3) | lane_c3_candidates.csv | **不存在** | — | **零出货**（脚本+测试在盘） |
| D 三高 | three_high_candidates.csv | 40（唯一 id 22） | E1D-20260914-055847 | **2026-09-14**（文件 mtime 09-24 受合并事件污染，以 birth_batch 为准） |
| E 基线 | 不卸进货台账（设计如此：factor_registry/E4 考尺路线） | — | MOD-BT-084 落地 1ce3e275=09-13；Kronos GPU 冒烟 calibrated=true=09-16 | **2026-09-16**（考尺件出货） |
| F06 网格 | grid_*/manifest.csv | 最新完整批 200(080309)+8(smoke 102243) | grid_20260924-102243 | **2026-09-24**（全厂最活跃；213246 空壳目录+GPU 阵列批=T1 在飞禁中动） |
| G 胃进货 | lane_g_candidates.csv / seen_urls | 0 / 5 | E1G-20260917-070016 | **2026-09-17 消化 5 篇产 0 假说**（唯一一班） |
| I 产业链(编排声明) | lane_chain_candidates.csv | 10 | E1I-20260918-T8 | 2026-09-18（挖矿班直产） |

**组级结论**：最近一次进货侧真实出货=**2026-09-24（F06 网格批）**；候选想法侧最近=**2026-09-22（C 车道）**；E2 预审最近=**2026-09-19**（车道 I 10 条全 defer_llm_unreachable）；**2026-09-19 后候选侧全链停滞**。

## 三、断点清单（按施工价值排序；P0 首挖）

1. **【P0·数据完整性】B 渠道进货台账 11 行蒸发**：CH 实证 E1B-20260916-021130 批 11 条候选 02:11 卸货、02:12 全部过 E2（3 pass/8 reject），现存 csv 仅 4 行（mtime 09-16 02:33）——「台账只增」被违反或 stash/合并回退事故。**修复路径已验证**：CH hypothesis_precheck 带原假说全文+birth 三件套，可全量重建。工单=重建 11 行+对账校验器（csv id 集 vs CH 已审 id 集差集告警）。
2. **【P0·接线】E2→E3 过审滞留**：E2 过审 13 条仅 6 条进入 E3（translated_manifest 5 + constructed_manifest 1，均为 09-15 单次人工班产出）；余 7 条（含 09-16 批 3 条 B pass）无幂等推进——auto_construct 只认 C/C2 公式轨，hypothesis_translator 靠人工 `--seeds N`（LIMIT 取最近，非幂等全量消费）。
3. **【P0·滞留】E2 deferred 19 条永久滞留**：`fetch_prechecked_ids` 用全表 DISTINCT candidate_id 幂等过滤，deferred 行也被跳过→车道 I 09-19 批 10 条 defer_llm_unreachable 后**永无自动重审**（与代码注释"deferred 可重跑语义"不符——仅 CH 不可达时才全量重审）。修法=幂等 SQL 排除 `verdict='precheck_deferred'`（1 行 SQL+测试）。
4. **【P1·触发缺位】全厂无事件触发器**：工厂三铁律之三"事件触发禁定时器"现状=**既无定时器也无事件**——进货/预审/构造全部靠人工或会话触发（schtasks 实测零工厂计划任务）；"夜批"是文档概念，无常驻、无 trade_calendar+数据到达触发器接线。事件触发器=最小施工件（收盘后日历事件→factory_intake_pipeline run）。
5. **【P1】F 车道 E2 消费适配器未挂**：_LANE_SPECS 已声明 F 车道，但 E2 消费循环只含 D/B/C/C2/G/I——recipe 行（recipe_id/values_json 非 hypothesis_zh）需专用适配器（代码注释自认跨线协作项）。f06_survivors 1 条幸存者已可走 MOD-BT-211 WFA 直考（旁路存在），主流水未通。
6. **【P1】C3 MCTS 零出货且未挂编排**：mcts_expression_search.py（MOD-BT-202）run_search 写 lane_c3_candidates.csv，但 csv 从未产生、_LANE_SPECS 无 C3 行；且实现为"简化 MCTS"（随机扩展，UCB 选择未接入主循环）——MVP 名实相符度低。
7. **【P2】车道 G 事件接线未挂+收件箱枯竭**：图9 自认"收件箱落新班自动触发未挂"；inbox 现存 1 份 intel-20260916.md 已消化（seen 5 条/产 0 假说）——胃侧供给断流则 G 永久空转。
8. **【P2】E0 闸门判决零落盘**：store_refs 声称"调度日志 .runtime/logs/ 90 天"，实测闸门代码无任何写盘——重任务问闸无审计痕迹（谁在何时被拒/放行不可回溯）。
9. **【P2】图9 口径漂移两处**：①FAC-E1E 说 Kronos"实测已跑"而 FAC-E3 尾注说"MOD-BT-195 登记跳过（网络不可达）"——实况=09-15/16 实测过、资产（.runtime/tmp/kronos_repo+weights）现已清理、复跑待网络（两注各半真，建议下版图合并口径）；②FAC-E0 名"心跳"实为拉式库函数（无常驻心跳——这是符合铁律的正确形态，名称误导）。
10. **【卫生】scripts/backtest/ 残留 5 个 .tmp.* 文件**（factory_grid_executor.py.tmp.21732.*×2、sim_daily_runner.py.tmp.*×3）——safe_write/会话中断残骸，禁本挖矿车道代清（主区只读），登记待施工批处理。

## 四、与后半（SF-B F23-F29）交接面

- F22→F23：translated/ 实测 85 个 c4_*.py（=79 件命名件【35 条人工标准答案验收集+C4 批量翻译批产出】+6 件 c4_fact_* 159 桥机生）待 E4 考试侧对账。
- F21 台账（c1_backtest.hypothesis_precheck 58 行）为 E4/E5 侧赛马计分板的输入（factory_intake_pipeline race 已按 birth_channel 聚合，E4 层赛马待首批候选入考试）。
- F29 台账出生证：本组发现的**台账蒸发事故+重复 id 堆积**（D 车道 40 行唯一 id 仅 22）是 F29 册的直接输入。

## 五、矿脉增补（分工册未列、本组发现）

- **车道 I（产业链候选，E1I）**：编排 _LANE_SPECS 第 7 车道（2026-09-18 T8 线alpha 增补），挖矿班直产 csv、编排幂等消费——图9 节点未挂（同车道 F 的跨线欠账），建议下版图补 FAC-E1I 节点。
- **f06_e4_wfa_exam.py（MOD-BT-211）**：F 车道幸存者旁路直考件已存在——F 车道不经过 E2 假说预审的"配方直考"通道是既成事实，图9 无此边。
- **E2 head(limit) 语义**：load_candidates 用 `df.head(limit)`——limit 截取的是文件头部而非"最新候选"；重叠批次行（同 id）堆积在头部会挤占 limit 名额（D 车道 40 行唯一 22 的根因之一）。
- **B 车道 09-16 批 pass 率陷阱**：3 条 precheck_passed 的 B 候选被 09-15 的翻译班永久错过（翻译只跑了 09-15 一班）——过审≠排产，中间无看板。

## 六、复核命令（10 分钟组级复核）

```bash
# 1 台账行数+批次（本册 §二 全部数字的来源）
python -c "import csv;[print(f, sum(1 for _ in csv.DictReader(open('data/strategy_intake/'+f,encoding='utf-8-sig')))) for f in ['raw_manifest.csv','lane_b_candidates.csv','lane_c_candidates.csv','lane_c2_candidates.csv','three_high_candidates.csv','lane_chain_candidates.csv','lane_g_candidates.csv','translated_manifest.csv','constructed_manifest.csv']]"
# 2 E2 台账实测
python scripts/backtest/hypothesis_precheck.py status
# 3 车道出货批次分布（birth_batch Counter）
# 4 赛马计分板（需 CH）
python scripts/backtest/factory_intake_pipeline.py race
# 5 E0 闸门现态
python scripts/backtest/compute_window_gate.py window
# 6 计划任务=零工厂接线实证
schtasks /query /fo csv | grep -iE "factory|lane|intake" ; echo "(空=无)"
```
