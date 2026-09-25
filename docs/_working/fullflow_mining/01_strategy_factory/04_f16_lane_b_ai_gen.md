---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F16 车道B·AI 生成（NL→假说量产）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-150
map_node: FAC-E1B
---

# F16 · 车道B-AI生成

## 一、环节定义与边界
一句话：12 主题种子→本地 qwen3:8b（经 OllamaChat 内置 LSG 闸门）批量生成结构化策略假说→内容寻址去重→出生证机器写入→卸 lane_b_candidates.csv，交 E2 把关。
上游供料=SEED_THEMES 12 策略族（价格动量…风险规避切换）+LLM；下游消费=E2 预审（factory_intake_pipeline run 或 hypothesis_precheck --source）→E3 假说轨翻译（MOD-BT-190 只取 D/B 过审）。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | OllamaChat(model=qwen3:8b)（lane_b_idea_generator.py:133-135）；主题种子 :56-59；生成 prompt 确定性（同主题同 N 必同 prompt :66-75）；temperature=0.4 |
| 下游消费 | data/strategy_intake/lane_b_candidates.csv（实测 4 行）；E2 台账实证消费两批：E2-20260914-070511（4 条：3 reject/1 pass）+E2-20260916-021246（11 条：8 reject/3 pass）；MOD-BT-190 翻译种子 SQL `birth_channel IN ('D','B')` |
| 自动化触发 | 无常驻（manual；由编排 with-lane-b 可选旗或直接 CLI 触发）；零计划任务 |
| 真源与注册表 | MOD-BT-150 在 path_ownership_map.yaml:16012；tests/backtest/test_lane_b_idea_generator.py 在盘；图9 FAC-E1B build_status=partial；QuantCode-Bench 警示（单轮通过率 70-76%）写进 INVARIANTS |
| 门禁与质量尺 | 出生证三件套机器写入（:106-117，含 prompt_md5 指纹）；内容寻址 id=CAND-md5(E1B:假说全文) 跨批稳定去重（:100-103）；台账损坏按空集宁可重写不误删（:120-128）；LSG fail-closed；本车道不打分 |
| 当前运行状态 | **黄**。两班真实出货：E1B-20260914-053418（4 条，csv 在）+E1B-20260916-021130（11 条，**进货行已蒸发**，CH 判定在案）；最近真实出货=2026-09-16 02:11；09-16 后零新增 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 生成主流程 run_generation（主题×N→解析重试→去重→卸货） | scripts/backtest/lane_b_idea_generator.py:131-184 | built |
| JSON 强解析 parse_ideas（数组优先+逐对象兜底） | 同上:78-97 | built（被 G 车道委托复用，CLONE-GUARD 决议在案） |
| 台账 id 集 load_existing_ids | 同上:120-128 | built |
| **已蒸发行重建**（11 条 E1B-20260916-021130） | 数据源=c1_backtest.hypothesis_precheck（hypothesis_zh+birth 三件套齐全，id 可按 md5 算法重算复核） | **missing（待施工）** |
| 台账只增守护（append-only 校验器） | — | missing（见堵点①） |

## 四、堵点与病灶（含 P0 事故）
1. **【P0】进货台账 11 行蒸发**：现象=CH 实证 02:11 班 11 条候选卸货（birth_batch=E1B-20260916-021130）、02:12 全部过 E2（3 pass/8 reject），现存 csv 仅 09-14 批 4 行（mtime 09-16 02:33——蒸发发生在该次写点，疑似会话 stash/合并把旧态文件盖回）；根因=data/strategy_intake/ 台账为裸 csv 追加，无只增守护、无与 CH 的对账面；修法=①从 CH 重建 11 行（hypothesis_zh 原文在判定台账，candidate_id 按 md5 算法可重算校验）②加 intake 台账对账校验器（csv id 集 vs CH 已审 id 集差集即告警，可挂 E2 run 前置）③台账写入统一走 safe_write_text CAS；工作量：重建 0.5 天+校验器 1 天；本车道可修。
2. **产出停滞**：09-16 后无新班；根因=触发靠人工（同 F14 断点④）；修法=并入事件触发器。
3. **生成多样性天花板**：12 主题固定种子+同 prompt 重复班会大量撞内容寻址去重（skipped_dup 上升）——量产需主题轮换/外部语料注入；P2 设计项。
4. **与 E3 的脱节**：09-16 批 3 条 precheck_passed 无任何推进（翻译班 09-15 已跑完且 SQL 按 prechecked_at DESC LIMIT 取——晚于翻译班的过审件永久错过）；同 F22 册断点②。

## 五、提速与合并机会
- parse_ideas/load_existing_ids 已被 G 车道委托复用（防双真源，正确）；B/G 两车道生成框架同构度高，若后续加"主题轮换"应改一处共享（提防再开第二份种子表）。

## 六、自审闸三态
- **三态结论：partial**（生成器本体 built；台账完整性事故未处置+产出停滞）。
- **差什么才算 built**：①蒸发 11 行重建落盘+对账校验器绿；②（触发口径裁后）进入常态化进货节奏；图9 其余承诺（验收集重试环）属 E3 侧职责，不计本车道。

## 七、复核命令
```bash
python -c "import csv;rs=list(csv.DictReader(open('data/strategy_intake/lane_b_candidates.csv',encoding='utf-8-sig')));print(len(rs),[r['birth_batch'] for r in rs])"
# CH 侧蒸发实证（birth_batch=E1B-20260916-021130 共 11 行）：
python scripts/backtest/hypothesis_precheck.py status
python -m pytest tests/backtest/test_lane_b_idea_generator.py -q
```
