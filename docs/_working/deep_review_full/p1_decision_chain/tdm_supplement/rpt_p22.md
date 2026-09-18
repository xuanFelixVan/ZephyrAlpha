---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——水温档推导（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：水温档推导（P22）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/sentiment/sentiment_cycle.py`
- TDM 节点: TDM-E-L2-05-1
- 生产调用方: sentiment_engine / sentiment_cycle_evaluator / extreme_sentiment_reversal_detector / environment_switch / candidate_pool_aggregator / correlation_sentiment_stratifier + G07 验证脚本（grep 实证，高扇入活件）
- 测试文件: tests/signal_ashare/sentiment/test_sentiment_cycle.py（合批 68 passed）

## 1 对象快照
MOD-SIG-140 全文件（1334 行）：情绪周期五阶段标准函数集 8 件（温度计/定位器贝叶斯/转换检测/纪律表/regime 软影响/联合指令/部署矩阵/Hawkes 验证）。排除项：market_sentiment_analyzer（异枚举同名件，docstring :30-33 已警示）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 贝叶斯定位器（先验平滑 diag=0.6 邻接 (1-d)/2 归一）/高斯隶属度/七维温度计权重和=1.0 数学正确；**兜底后 confidence=1.0 伪造确定性（P2）**：置信度<0.6 才触发兜底，兜底却把 confidence 置 1.0+one-hot 分布——"证据不足"被改写成"完全确定"，任何下游按 confidence 加权/审计读数的消费方被误导（position_scale 收缩不能抵消语义失真） | :431-439；实测 fallback=True confidence=1.0 | **P2** | `python -c` 见验证法（造均衡证据输入触发兜底，读 out.confidence） |
| A 深度 | `_membership_in_range` 999 魔数（hi=999 表∞，center=lo/span=10 分支）与 PHASE_CHARACTERISTICS 区间值强耦合——区间表改动（如 (80,999) 改 (80,500)）静默改变隶属度几何 | :494-502,81-137 | P3 | 改 range 对比 score |
| A 深度 | Hawkes 分支比 η=α/β 定义正确（β≤0→inf）；block-bootstrap p 值=P(\|ρ_boot\|≥\|ρ_obs\|) 双侧合理；seed=42 固定可复现；corrcoef 常量序列有 std>0 守卫 | :1185-1282 | 已查无 | 常量序列输入应得 0.0 |
| A 边界 | 序列不足→transition none/空结果（契约）；空 ladder→0；total_attempt=0→rate 0；后验 max(1e-9) 防零除；regime_prob 空→"Unknown" | :294,205-213,424-426,915 | 已查无 | 造短序列/空 dict |
| A A股 | 冰点/反核/主升/疯狂/退潮五段+涨停/跌停/炸板/连板/核按钮全 A 股本土语义；炸板率>70% 强制禁交易（24号§3.10）；游资圈对照锚（55188/xueqiu/eastmoney）为中文来源（合规） | :52-64,553 | 已查无 | — |
| B 上游 | daban_next_day_premium/northbound 净流入等标量全注入无来源校验；**北向字段停发风险未声明**（2024-08 起北向实时额度披露调整，若上游断供恒 0 → 定位器静默少一维证据——checklist #6 变体，证据维度降级无留痕） | :375 | P3 | 断供场景北向=0 与真实 0 不可区分 |
| C 下游 | 高扇入（7+ 生产文件+3 G07 脚本）；dominant_phase 错判→PHASE_DISCIPLINE 全套（仓位/新开/节流）错档，爆炸半径=三 sleeve 纪律层（最大扇出对象之一） | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 三模块同名 SentimentPhase 枚举（本件/market_sentiment_analyzer/youzi_relay_emotion_engine）docstring 明示勿混用（:30-33）——自觉登记但仍构成混 import 隐患（无 assert 拦截）；SENTIMENT_REGIME_MAPPING/PHASE_DISCIPLINE/STRATEGY_DEPLOYMENT_MATRIX 三表内部数值互查：daban FERMENTING 纪律 position_scale=1.0 vs 部署矩阵 0.7——**同阶段同策略仓位两表不一致**（纪律表管 sleeve 缩放/部署矩阵管部署描述，语义有别但数值并存易误读） | :30-33,594-602 vs :975-983 | P3 | 对读两表 FERMENTING daban 行 |
| E 对抗 | 五问：①无吞异常 ②兜底只回收缩态（宁保守）设计好 ③fallback confidence=1.0=监控盲区（见 A）④wrapper 无递归（INVARIANT 实证）⑤转移平滑防阶段跳变（时序面有防） | :400,433-438 | P3 | — |
| F 新鲜度 | **部分受阻**：五段情绪周期=游资圈本土方法论（中文来源合规，本仓多锚）；Hawkes 金融应用为成熟方法（模块自引 Filimonov & Sornette 2012，本批未独立复核 URL——如实记受阻半态）；regime 软影响权重待 Phase 2 实盘调参（自声明） | — | — | — |

## 3 SOTA 对照
五段周期：对等已有（游资圈中文方法论，本仓多锚合规）；Hawkes：对等已有（模块锚 Filimonov-Sornette 2012，独立复核受阻记档）。

## 4 缺陷清单
1. **P2 兜底 confidence=1.0 语义伪造**：建议保留真实置信度另加 fallback 标记位（已有 fallback_triggered 字段，confidence 不该改写；或改 confidence=confidence_threshold 下界）。验证法：python 探针。
2. P3 北向断供无证据维降级留痕。
3. P3 999 魔数隶属度几何耦合。
4. P3 daban FERMENTING 两表仓位数值不一致（1.0 vs 0.7，语义有别需注释仲裁）。
5. P3 三同名枚举无防混机制。

## 5 挂起疑问
- SENTIMENT_TO_REGIME_MAP 权重"Phase 1 经验值待实盘调参"（28号 §6 待裁定-2）——标定欠账族最大单（12 态×5 阶段矩阵全人工初值）。

## 6 完备性自评
六轴全查（1334 行全读）。长尾：Hawkes 参数估计（无 MLE 拟合，仅 η 计算——§3.7.4 估计器缺位是否收缩登记未查 spec）；G07 验证脚本产物未核对。
