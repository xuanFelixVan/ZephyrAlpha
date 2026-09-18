---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——虹吸态识别（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：虹吸态识别（P21）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sector/sector_siphon.py`
- TDM 节点: TDM-E-L2-04-2
- 生产调用方: sector_divergence（P15 `_compute_siphon` 真实消费，grep 实证）
- 测试文件: tests/signal_ashare/sector/test_sector_siphon.py（合批 49 passed）

## 1 对象快照
MOD-SIG-026 supplement（143 行）：三信号（HHI 0.4/净流入集中度 0.35/净流出比例 0.25）滚动 z-score 加权，z>1.5σ 触发虹吸态。纯函数。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 三信号定义正确（HHI=头部 N 份额平方和；集中度=头部净流入/全市场|净流入|；流出比例=其余净流出家数占比）；权重和=1.0；**加权 z 和≠标准正态**：三 z 相关（HHI 高时集中度常同向高），加权和方差>1，阈值 1.5σ 实际触发率低于名义 93% 分位——语义为"裁量阈值"非统计分位（docstring ~93% 分位声明数学上不成立） | :23-24,42,129-135 | P3 | 独立正态 z 两两相关 0.5 时 Var(sum)=1+2×0.5×(0.4×0.35×2+...)>1 手算 |
| A 边界 | 空板块→is_siphon=False；total_turnover/total_abs=0→信号 0；历史<2/σ=0→z=0 降级不误报（契约齐）；NaN 历史：var→NaN→std==0.0 False→z=NaN→score NaN→`NaN>1.5` False（侥幸不触发）但 siphon_z=NaN 透传 P15 输出 | :70-82,114-117,135 | P3 | 造含 nan 的 history 看 siphon_score |
| A A股 | 虹吸态语义（头部吸金/其余缺血）配 2026 实证锚（国海固收 2026-07 电子+86% vs 商贸-29%）——本土语境完备 | :17-21 | 已查无 | — |
| B 上游 | 三 history 序列由调用方构造（P15 侧逐日重放）；历史窗不含当日（:98 契约）防自比——P15 :606-609 `if d >= current_date: continue` 落实；id() 同性判 top_n 成员（frozen dataclass 场景成立，调用方复用对象则误判——当前 P15 每日新建 Snapshot 成立） | :98,125-126 | P3 | 复用对象调 detect 观察 rest 集合 |
| C 下游 | 唯一消费方=P15；siphon_flag→siphon_chaos_flag→M2 降档评估注解（爆炸半径=降档评估输入维度） | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 与 P20 串联分工（绝对阈值 vs 相对 z）文档化；与 P15 _signals() 内联 HHI 计算重复实现（P15 :591 自算 top-N HHI vs 本件 :115——**同公式两处实现**，口径当前一致=漂移隐患 checklist #4） | :114-117 vs sector_divergence.py:588-597 | P3 | 对读两处 HHI 代码 |
| E 对抗 | 五问：①无吞异常（降级返回 0）②NaN 侥幸不触发（见 A）③无监控面 ④纯函数幂等 ⑤无时序面 | 全文件 | 已查无 | — |
| F 新鲜度 | 受阻/不适用：虹吸态为项目自定义复合 z 指标（2026 实证为内部数据锚），无外部对照对象 | — | — | — |

## 3 SOTA 对照
受阻/不适用（项目自定义指标）。

## 4 缺陷清单
1. P3 "~93% 分位"名义声明与相关 z 加权的实际分布不符（阈值语义应为裁量）。
2. P3 NaN 历史透传（z=NaN 侥幸不触发但 score 污染）。
3. P3 HHI 公式与 P15 双实现（漂移隐患）。

## 5 挂起疑问
- 阈值 1.5σ/权重 0.4/0.35/0.25 待实盘标定（需 ≥3 个月样本，:27-28 自声明）——标定欠账族。

## 6 完备性自评
六轴全查（全文件 143 行逐行）。无长尾。
