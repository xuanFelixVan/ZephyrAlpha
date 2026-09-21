---
ttl: task_bound
title: 深度审查作业簿——明日情绪盘中滚动预测（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：明日情绪盘中滚动预测（P05）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/intraday_tomorrow_forecast.py`
- TDM 节点: TDM-E-L0-04
- 生产调用方: **零 import**（candidate_pool_aggregator/environment_switch 仅注释引用"范式对齐/待接线"，见 C-1）
- 测试文件: tests/plan_engine/test_intraday_tomorrow_forecast.py（44 tests 实跑通过）

## 1 对象快照
MOD-PLAN-025 全文件（325 行）：8 态先验+相似日三档倾斜+Brier 降权三源融合，纯函数零 IO。排除项：next_day_8state_forecast / similar_day_inference / brier_calibration 三上游真源（各自域审查）。测试覆盖充分（19+25 passed）。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 融合数学扎实：档位轴线性插值平移+两端截停+重归一；凸组合保归一非负；argmax 平票降序迭代取更悲观态（方向保守）实现正确 | :199-233,292-294 | 已查无 | 单点分布 tilt=1.5 手算对拍 shifted 质量 |
| A 深度 | **Brier 随机基线口径缺陷**：`BRIER_RANDOM_REF=0.5` 注释称"uniform 瞎猜期望 Brier=0.5"——多分类 8 态均匀基线实为 (K−1)/K=0.875（Wikipedia/Hoessly 2026）；即二值均匀概率输出也是 0.25 非 0.5（0.5 是"随机输出 0/1"口径）。`SourceCalibration.brier` 契约未声明二值/多分类：若接线 brier_score_multiclass（8 态随机=0.875），`1−brier/0.5` 会把优于随机的中等信息源（brier∈(0.5,0.875)）系统性压到 floor 0.1 | :60-63,169-175 | **P2** | `python -c "print(1-0.6/0.5)"`（负→floor）；对照 wikipedia Brier score 多类定义 |
| A 边界 | 输入校验完备：缺态/负值/NaN/不归一（容差 1e-3）全 fail-closed；倾斜后全零拒；brier 非有限/负拒 | :145-161,191-195,207-208,231-232 | 已查无 | 造缺态/NaN 分布逐项应抛 |
| B 上游 | 先验/三档契约严密；唯一软点=calibration 来源契约不存在（见轴 D 幽灵引用） | :77-84 | P3 | — |
| C 下游 | **孤儿（诚实型）**：全仓 grep 仅 candidate_pool_aggregator.py:10（"对齐 C13 范式"注释）与 environment_switch.py:5（"待接线"注释）提及，零 import；downgrade_warning 消费方 L0-02（P03 本身也是孤儿）未接线——预警链两端都悬空 | grep 实证 | **P2** | `grep -rln "intraday_tomorrow_forecast" --include="*.py" src/` 且查 import 行 |
| D 旁系 | **幽灵引用**：SourceCalibration docstring 称由 `brier_calibration.compute_calibration 产出后注入`——brier_calibration.py 无此函数（实际仅有 brier_score/brier_score_multiclass/calibration_bins/expected_calibration_error）；且全仓无人调用这些函数喂本件（checklist #9 变体） | :79 vs brier_calibration.py:192,208,242,300 | P3 | `grep -n "def compute_calibration" src/zephyr/plan_engine/brier_calibration.py`（无命中） |
| E 对抗 | 五问：①无吞异常（全 fail-closed）②fallback_used/enabled 双防线防先验双计（好）③无监控面（纯函数）④纯函数幂等 ⑤无时序面；`__main__` selfcheck 只 print 不验算=假自检 | :265-271,316-324 | P3 | 跑 `--selfcheck` 观察输出无断言 |
| F 新鲜度 | **已检索**：多分类 Brier 随机基线=(K−1)/K——Wikipedia "Brier score"（含原始多类定义 BS=(1/N)ΣΣ(f−o)²）；Hoessly, "On misconceptions about the Brier score", PMC12818272, 2026（balanced 多类随机猜 1/K 基线 (K−1)/K）。结论：本件 0.5 参考与 8 态基线不符 → **立卡候选**（接线前先定 SourceCalibration.brier 口径：二值 or 多分类，再定 REF） | https://en.wikipedia.org/wiki/Brier_score ；https://pmc.ncbi.nlm.nih.gov/articles/PMC12818272/ | — | — |

## 3 SOTA 对照
- 多分类 Brier 随机基线 (K−1)/K：对等已有（学界标准）vs 本件 0.5 —— 不符，立卡候选修 REF 或声明二值口径。URL+发布方+年份见轴 F。

## 4 缺陷清单
1. **P2 Brier 基线口径潜伏缺陷**（0.5 vs 0.875/0.25，接线即发作）。建议：SourceCalibration 加 calibration_kind 字段或常量改名 BRIER_RANDOM_REF_BINARY 并断言输入口径。验证法：见轴 A。
2. **P2 孤儿（预警链双端悬空）**：本件无生产 import，其消费方 P03 亦是孤儿——TDM-E-L0-04→L0-02 降档预警链整体未运转。验证法：grep。
3. P3 幽灵函数引用 compute_calibration。
4. P3 假自检入口（--selfcheck 无验证力）。

## 5 挂起疑问
- BASE_W_PRIOR=0.7/0.3、TILT_MAX_TIERS=2、RELIABILITY_FLOOR=0.1 均标 "proposed 待实盘标定"——标定计划与数据源未见登记，需 Owner 确认标定路线。

## 6 完备性自评
六轴全查。长尾：三上游（8 态先验/相似日/Brier 校准器）内部数学未审（各自对象域）；期望档差弃用判据的论证接受文档口径未独立复推。
