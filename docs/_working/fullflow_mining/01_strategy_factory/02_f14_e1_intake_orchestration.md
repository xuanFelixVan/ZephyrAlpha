---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F14 E1 想法进货编排（六车道薄编排）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-154
map_node: FAC-E1
---

# F14 · E1 进货编排（factory_intake_pipeline）

## 一、环节定义与边界
一句话：薄编排层——车道并发进货→统一卸 data/strategy_intake/ 台账（带出生证）→E2 预审幂等自动接续→过审公式候选自动构造（construct）→赛马计分板（race），一条命令串起"进货→预审→排产"。
上游供料=七车道声明表 _LANE_SPECS（D/B/C/F/G/I+C2C3 注释在案）；下游消费=E2 预审（同文件函数级接续）、E3 构造（auto_construct→159 桥）、Owner 夜批汇总（JSON 报告）。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | _LANE_SPECS 七车道（factory_intake_pipeline.py:50-72）：D=three_high_candidates / B=lane_b_candidates / C=lane_c_candidates（09-18 WO-⑤-06 漂移修正）/ F=grid_latest_manifest（latest_grid_manifest() 动态解析最新 grid_*/manifest.csv，:75-79）/ G=lane_g_candidates / I=lane_chain_candidates（T8 09-18 增补） |
| 下游消费 | run_pipeline→hypothesis_precheck.run 幂等消费 **D/B/C/C2/G/I 六源**（:130-146，F 不在内——recipe 适配器待挂）；auto_construct→factor_strategy_template.generate_strategy_file（159 桥）+creation_token 批登记（:225-233）+constructed_manifest 追加；race→纯函数 race_scoreboard 按 birth_channel 聚合 |
| 自动化触发 | **人工/会话触发**（STARTUP=manual，"本命令被触发即一次进货事件"）——schtasks 实测零工厂计划任务；"夜批"无常驻无日历触发器；符合"禁定时器"但"事件触发"亦缺位 |
| 真源与注册表 | MOD-BT-154 在 path_ownership_map.yaml:15928；tests/backtest/test_factory_intake_pipeline.py 在册（commit 9305f1f3a7 称 12 绿）；设计出处=讨论稿 v4"自研薄调度层" |
| 门禁与质量尺 | 编排层不评分（运动员不兼任裁判，INVARIANTS :10-14）；重车道 E0 问闸预检 preflight_compute_gate（:82-96，当前批全轻车道→全放行）；车道模块缺位不阻断（BLE001 降级 :138,143）；台账不可达 fail-closed 不构造（_e2_passed_by_channel :266-268） |
| 当前运行状态 | **绿（编排本体）+黄（触发与覆盖）**。证据：E2 台账 14 批（09-14~09-19）证明 run 通路真实跑通；constructed_manifest 1 行（09-15）证明 construct 通路真实跑通；git 史 d1d719a7df/d75df06d4c 证明车道 I/G 接线班次真实发生 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 车道规格表 _LANE_SPECS | factory_intake_pipeline.py:50 | built（七车道；C3 未列） |
| F 车道 manifest 解析 latest_grid_manifest | 同上:75 | built（无批次诚实返回 None） |
| E0 问闸预检 preflight_compute_gate | 同上:82 | built（接线点声明） |
| 主编排 run_pipeline（E1D→可选 E1B→E2 六源幂等） | 同上:99-164 | built |
| E2→E3 排产流转 auto_construct（C/C2 公式轨） | 同上:171-245 | built（creation_token 登记在内） |
| 过审集查询 _e2_passed_by_channel（CH，fail-closed） | 同上:248-268 | built |
| 赛马计分板 race_scoreboard+cmd_race | 同上:271-322 | built（E2 层漏斗；E4 层待首批入考试） |
| F 车道 recipe→假说适配器 | — | **missing**（E2 消费循环无 F；代码注释 :60-62 自认跨线协作项） |
| 事件触发器（收盘后日历事件→run） | — | **missing**（三铁律之三的"事件"半边缺位） |

## 四、堵点与病灶
1. **事件触发半边缺位**：现象=全厂 09-19 后候选侧停滞；根因=进货事件=人工记得跑命令，无常驻无日历钩子；修法=最小触发器（trade_calendar 收盘事件或数据到达哨兵→subprocess factory_intake_pipeline run，事件源复用 M5 计划任务体系但语义是"日历到达事件"而非定时器——需总筹裁口径）；工作量≈1 天；跨 M5/SF 边界，**待裁**。
2. **F 车道适配器缺**：recipe 行无 hypothesis_zh 列，E2 六问预审框架不适用——需先裁"F 车道 recipe 是否绕过 E2 直考（MOD-BT-211 旁路既成事实）"；**待裁**（裁定后或删 _LANE_SPECS 的 F 行或补适配器）。
3. **--limit-precheck 默认 10+head 语义**：run 的 E2 消费每源限 10 且 load_candidates 取文件头——重叠批次行堆积时新货饥饿（详见 F21 册堵点③）；修法=幂等过滤后再 tail 或全量；0.5 天；本车道可修。
4. **C3 未挂编排**：MCTS 第三轨产出 csv 路径已定（lane_c3_candidates.csv）但 _LANE_SPECS 无 C3 行；挂名 1 行+消费源 1 行即通（前提=C3 真实出货一次）。

## 五、提速与合并机会
- run/race/construct 三子命令已合并进货-预审-构造-计分为单入口（符合"能合并的合并"）；剩余合并点=车道 G/I 的"干活在各自 CLI"模式已把编排瘦身（不再复制车道逻辑），无需再并。
- 夜批报告 JSON 已是单读汇总面；若事件触发器落地，报告可直接投 .runtime/sessions staging 供晨报。

## 六、自审闸三态
- **三态结论：partial**（编排本体+三子命令 built；F 适配器、C3 挂载、事件触发器缺）。
- **差什么才算 built**：①事件触发器落地（或 Owner 裁定"人工事件=合法事件语义"并在图9 标注）；②F 车道裁定后要么通适配器要么从 _LANE_SPECS 除名；③C3 行挂载或除名；④（建议非必须）limit 语义修正。

## 七、复核命令
```bash
python scripts/backtest/factory_intake_pipeline.py run --dry-run     # 全链只看不写
python scripts/backtest/factory_intake_pipeline.py race              # 各车道×E2 漏斗（需 CH）
sed -n '50,72p' scripts/backtest/factory_intake_pipeline.py          # 七车道声明表
python -m pytest tests/backtest/test_factory_intake_pipeline.py -q
```
