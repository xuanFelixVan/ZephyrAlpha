---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——大盘指数传感器（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：大盘指数传感器（P08）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/features/index_sensor.py`
- TDM 节点: TDM-E-L1-S1
- 生产调用方: **零真实调用方**（仅 regime/features/__init__.py:44 re-export；L1-AGG 消费者 daily_condition_sensor.py:5 仅引用节点标签未 import）——孤儿
- 测试文件: tests/regime/test_index_sensor.py（实跑通过）

## 1 对象快照
MOD-REGIME-016 全文件（135 行）：指数趋势规则打分（MA20/MA60 排列+破位+60 日高点距离）clamp 到 [-2,+2] 纯函数。排除项：index_regime_panel（HMM 七态，分工见 docstring :31-33）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | **输出域上界不可达（P1）**：正向项只有 MA20>MA60 一项 +1，负向最多 -4；可达域实为 [-2,+1]——docstring/INVARIANTS 宣称 "+2 强势" 永不出现；且稳定牛市实测=0（+1 多头排列 与 -1 高位减分常抵消）：五档语义表（+2 强势/+1 偏多/0 中性）与可实现分布系统性错位，L1-AGG 若按 [-2,+2] 全域标定阈值将系统性偏保守 | :23-29,108-123；实测稳牛序列（100+0.5i, i=0..60）score=0 | **P1** | `python -c "import sys; sys.path.insert(0,'src'); from zephyr.regime.features.index_sensor import compute_index_trend_score; print(compute_index_trend_score(tuple(100.0+0.5*i for i in range(61))).score)"` |
| A 深度 | 术语错误：破 MA60 注释称"破**年线**级减两档"——MA60 是季线，年线=MA250；口径文档失真 | :27 | P3 | 读 ：27 与任意行情软件均线命名 |
| A 边界 | 样本 <61 拒、NaN(c!=c)/非正价拒、high60>0 保证 dist 有限；clamp 保域——边界完备 | :69-76,100-101,123 | 已查无 | 传 60 根/含 NaN 各测 |
| B 上游 | closes 为裸 float 序列无日期，"序列升序时间"不变量只能靠调用方自律（in-band 不可校验）；上游倒序喂入=静默按反转历史打分 | :84-95 | P3 | 传倒序序列观察无报错 |
| C 下游 | **孤儿**：全仓 grep 仅 __init__ re-export；声称消费方 L1-AGG（TDM-E-L1 聚合）无代码承接——五档分现在无人消费，P1 的域错位尚未实际发作（接线前必修） | grep 实证 | **P2** | `grep -rn "compute_index_trend_score" --include="*.py" src/` |
| D 旁系 | 与 index_regime_panel（HMM 概率视角）分工文档化互不替代；同包 market_features/trend_features 亦算均线族特征——MA 计算多件并存（视角不同：特征 vs 打分），暂无双承载冲突但 MA 窗口口径无统一常量 | :31-34 | P3 | grep ma20/ma60 常量对比 |
| E 对抗 | 五问：①无吞异常（全 fail-closed）②无假阳性面（纯函数）③无监控面（孤儿本体）④纯函数幂等 ⑤无时序面（升序契约不可验，见 B） | 全文件 | 已查无 | — |
| F 新鲜度 | **已检索**：MA 交叉/趋势规则属经典趋势跟踪族——"Optimal trend-following with transaction costs"（International Review of Financial Analysis, ScienceDirect, 2023）为 MA 规则提供理论+实证支撑；共识=趋势市有效、震荡市 whipsaw。结论：**对等已有**（本件=MA 排列规则打分，属该族内常规实现；高位减分项为项目自定义裁量，无外部对照） | https://www.sciencedirect.com/science/article/pii/S1057521923004441 （IRFA, 2023） | — | — |

## 3 SOTA 对照
MA 趋势打分：对等已有（经典趋势跟踪族，ScienceDirect/IRFA 2023 为代表来源）；"-1 距 60 日高点<3%"高位惩罚项无直接文献对照（项目裁量），记差异。

## 4 缺陷清单
1. **P1 输出域错位（+2 不可达/稳牛=0）**：五档语义表与可实现分布不符——接线前必须修（补正向项如"收盘>MA20 且多头排列 +1"或改文档为 [-2,+1]）。爆炸半径=L1-AGG 温度计系统性偏保守。验证法：见轴 A 单行复现。
2. P2 孤儿（L1-S1 未接线，L1-AGG 无承接）。
3. P3 "年线级"术语错误。
4. P3 升序契约 in-band 不可校验。

## 5 挂起疑问
- "高位减分"使持续牛市长期读 0（实测）——若 Owner 意图是"高位不远攻"则 0 是预期值，但此时"+1 偏多"档在牛市也几乎不可达，五档表实际退化三档，需 Owner 裁定语义表去留。

## 6 完备性自评
六轴全查。长尾：与 market_features/trend_features 的 MA 口径逐值对拍未做（孤儿状态降义）。
