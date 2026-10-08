---
ttl: task_bound
completes_when: 本季三红清单经 Owner 裁定处置完毕（并/退/留/修四分执行或明确挂账）后本报告归档
title: 03_quarterly_red_report_v1 覆盖账本三红首报（2026-10-08 季度窗）
owner: st-fig13-followup-20261006
---

# 03_quarterly_red_report_v1 —— 覆盖账本三红首报（2026-10-08 季度窗）

> 车道：st-fig13-followup-20261006 线C（C4）。判据真源=[`../fig13_followup/c2_quarterly_ledger_criteria.md`](../fig13_followup/c2_quarterly_ledger_criteria.md)（封矿簿）；unknown-83 逐行清洗=[`../fig13_followup/c2_unknown83_classification.csv`](../fig13_followup/c2_unknown83_classification.csv)。
> 输入（只读零改写）：01_module_home_census_v1.csv（1618 行）+ 02_quarterly_ledger_prep_v1.csv（四段备料）。
> 图13 侧证据：config/trading_day_cycle_map.yaml（52 节点，validator 0 错 0 警，2026-10-08 重生成）。

## 0. 恒等式（对平备料头部，引用不抄写）

```
1618 = ①TEST 401（出宇宙，裁定在案） + ②unknown 83（本报 §2 清洗收敛） + ③真无家 767 + ④有家 367（单家 310 + 复数家 57）
```

## 1. 红1 · 孤儿（在册模块该挂没挂）

**修剪后宇宙**（c2 簿 §1 判据机械执行）：
- ②unknown-83 清洗结果：**f 类 55（家系归并建议）/ b 类 17（蓝图文档件，出代码模块宇宙）/ t 类 6（测试件出宇宙）/ c 类 2（币圈冻结）/ k 类 3（unknown-keep 交 Owner）**。
- b/t/c 三类共 25 行修剪出孤儿宇宙（判据逐行在 csv）；f 类 55 行归家系后**按家系参加覆盖对账**（家系已挂图者成员不判孤儿）。
- ③真无家 767 = 孤儿候选主体，域分组面（备料 3a 段 292 行带旗标）按 autonomy/cross_layer 等域给处置建议（§5 四分清单）。
- 与任务包分歧消解：预期 unknown=74 vs 严格 83 的 +9 = AUTO 暂编号族 7 行（归 autonomy 家系）+ BT-CHTP/L02-FS/ML-DENSITY 等在册 token 可归行——全量落 csv，分歧归零。

**红1 计数（修剪后口径）**：孤儿候选=③真无家 767 − 域分组面误入修剪类的行；**结构性孤儿判红须逐域"本命图"定性，本首报列清单给建议，批量定性交 Owner（§6）**。

## 2. 红2 · 抄写（复制非引用，INV-1）

**机械扫描（2026-10-08 实跑，脚本=.runtime/tmp 车道件，口径可复跑）**：
- 图13 yaml 节点散文段 >200 字符指纹对碰：扫描 evidence 91 段 + exec_evidence 31 段，**同文碰撞=0 → 红2 PASS 零抄写**。
- 豁免登记（合法内联，非抄写）：casebooks 25 格=件2 采纳矩阵 Owner 终批内联（864bfb1b99）；consumers=机生投影只指针（count+代表≤4+source 指针），结构性免疫。
- 复跑命令：见 §7。

## 3. 红3 · 未挂病历（casebooks 完备性）

**机械核验（2026-10-08 实跑）**：
- 挂载格=**25 环节格**（血肉批基线 25 格保持）、册码槽 35、涉及册码 17、五族全覆盖（MEM-F13×28 / AP×2 / SV×2 / DCS×1 / RV2×2）。
- 反向完备：图面 casebooks 与生成器 CASEBOOKS_ADOPTED 矩阵逐格对碰 **diff=0**（生成器单真源，图面零漂移）。
- 孤儿挂点（指向不存在册）=0。**红3 = PASS 全挂零孤儿**。

## 4. trigger_facts 实数化（C3 交付面，账本旁证）

图13 生成器 trigger_facts 由 obs 文本投影升级为**生成期实数三通道**（A=task_runs 30 日窗 sqlite ro-uri；B=Get-ScheduledTaskInfo 96h 节拍窗；C=CH reader 产物表；D=日志 glob；各自独立降级 no_count_reason）：
- 分布：**count=38 / 显式降级 reason=10 / gap=None=4 / 违规=0**；production 15 台全合规（count 或非空 reason 二选一在场，validator 新硬判 CV-BLOOD 实数化腿背书）。
- D13-21 在产实证：judgment_intraday_market_state 最新上海日=4 行；D13-34（decision_daily 居 c1_backtest）=reader 授权面外，显式降级理由在图（授权缺口归 ops 车道，登记 §6）。

## 5. 内收四判据机械跑（w5_1）

| 判据 | 机械结果 | 处置 |
|------|----------|------|
| 同真源可派生→必并 | unknown-83 中 f 类 55=同名家系重复登记面（AUTO 暂编号族/DAT↔DATA 双前缀等） | 并：归并建议清单（§6-②，涉注册册批量写=Owner） |
| 零触发零消费→退役 | 图13 台账：空转槽 post_auction（1）/孤儿任务 4/宇宙外任务 10；census 无家脚本域（cleanup/oneoff 族）零消费面归 fac9 F3 先例口径 | 退：候选清单交 Owner（§6-③） |
| 同域重复簇→收敛唯一 | D-DATA-CONCEPT-SYS / MOD-D-CONCEPT-SYS / D-DATA-IO-ANCHOR 同簇（scripts/industry_graph 三件，k 类） | 收敛建议交 Owner（§6-①） |
| 跨域不同对象→不并 | b 类 17（蓝图面）与代码模块同名族=不同对象（蓝图≠代码） | 留：登记不并（c2 簿 §2） |

## 6. 待 Owner 裁定清单（唯一留 Owner 面；其余并/留/修已自裁执行并留痕）

| # | 事项 | 建议 | 证据 |
|---|------|------|------|
| ① | k 类 3 行归属（D-DATA-CONCEPT-SYS / D-DATA-IO-ANCHOR / MOD-D-CONCEPT-SYS，同簇 scripts/industry_graph） | 三件同簇一并定性：并入 industry_graph 家系或登记退役 | c2 csv k 类行 |
| ② | f 类 55 行家系归并建议批量准驳（涉 module_id_registry / module_translation_registry / path_ownership 批量写） | 按 csv 逐行"guess 家系"批量归并；10-08 夜注册册多车道在途，落地窗另批 | c2 csv f 类行 |
| ③ | 真无家 767 各域"整域退役/整域补挂"定性 + 空转槽 post_auction 收敛 | 域分组清单（备料 3a 段）逐域裁决；post_auction 槽=图13 台账在案 | 02 备料 3a 段 + 图13 dangling 台账 |
| ④ | 复数家 57 行本命家裁定 | 逐行 single-home 收敛（备料 3b 段） | 02 备料 3b 段 |
| ⑤ | D13-34 计数面授权缺口（zephyr_reader 无 c1_backtest grant） | 授权扩面或该节点计数归数据班代跑（决策表口径） | 图13 D13-34 no_count_reason |

## 7. 真源与复跑

- 判据簿：docs/_working/fig13_followup/c2_quarterly_ledger_criteria.md；清洗 csv：docs/_working/fig13_followup/c2_unknown83_classification.csv（83 行四列：module_id/path/class/disposition）。
- 红2 复跑：对 config/trading_day_cycle_map.yaml 节点 evidence/exec_evidence（+mech/q/obs/clk）>200 字符段做归一化指纹对碰（本报道具=车道 tmp 件，配方在本报 §2）。
- 红3 复跑：图面 casebooks vs 生成器 CASEBOOKS_ADOPTED 逐格对碰（应 diff=0）+ 挂载格计数（应=25）。
- 实数化复跑：`python scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py` → `python scripts/governance/d5_architecture/validators/validate_trading_day_cycle_map.py`（应 PASS 且 count+reason+gap=52）。
