---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——多因子打分链
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：多因子打分链（P38）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/factor/analysis/multifactor_synthesis.py`
- TDM 节点: TDM-E-L3-07-2（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-L02-011/D-FACTOR-ANA-10
- 生产调用方: **有：`pf_core/strategies/multifactor_sleeve_strategy.py:50,150`（多因子 sleeve 真实调用 synthesize）+ `ex_core/signal_providers.py:39,162`（信号供给管线）——非孤儿（头注 [CONSUMERS] 为空=登记缺口非实际孤儿）**
- 测试文件: `tests/factor/test_multifactor_synthesis.py`（20 用例，本班次实跑 20/20 绿）

## 1 对象快照

158 行三方法合成器：等权（DataFrame mean，pandas skipna）、IC 加权（历史 IC 归一化，Σ|w| 归一保符号）、回归合成（OLS 无截距，系数作权重，样本不足/求解失败/缺参→等权兜底+warning）。统一入口 synthesize 按 method 分派，默认从 analysis/_config.yaml 读（default ic_weighted）。ERROR_CONTRACT 全兜底+留痕。测试覆盖：三方法+兜底分支。排除项：ic_ir_calc（IC 来源，头注互认未接线）、multifactor_sleeve（P39 邻件）深审不在本件。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：等权 mean 逐行跳 NaN（pandas 默认 skipna）；IC 加权 `norm=w/Σ\|w\|` 保符号（负 IC 因子反向贡献=方向正确用法 :86-91）；回归 `lstsq(X,y)` 秩亏最小范数解（:121）数值稳定 | multifactor_synthesis.py:61-62,86-91,121 | 通过 | 手算双因子归一 |
| A 深度 | 边界②：空输入→空 Series；权重全无效/Σ\|w\|<1e-10/数据不足 n≤k/矩阵奇异/缺 forward_returns→等权兜底+log.warning（:83,88,114-116,123-124,153-155）全留痕；NaN 因子值：等权逐行跳过、IC 加权 `Series×float` NaN 传播到行、回归 X fillna(0)（:117）——**三种方法对 NaN 语义不一致（跳过/传播/置零），跨方法同一数据不同结果** | :59-62,86-91,117 | P3 | 同带 NaN 面板跑三方法对拍 |
| A 深度 | 假设③：**回归法 X.fillna(0) 隐含"0=因子中性"假设（仅对 z-score 化因子成立，原始值因子语义错误）+OLS 无截距（docstring 未声明）+拟合与应用同面板（in-sample 权重，无 train/apply 切分）**——三重隐式假设未文档化（policy 轴 B.2 隐式契约=高危类） | :117-125 | P2(文档化必修) | 阅 :94-125 对照 docstring |
| B 上游 | checklist #6 断供：输入=因子面板+IC/前向收益注入；ic_weights 来自历史 IC（INV-004 PIT 铁律 :8 声明，本件机械不可验，责任在调用方 ic_ir_calc——该件头注自declared"暂无 import 消费方…接线待排期"=**IC 权重生产端未接线，IC 加权法实际无可用的生产权重源**） | :8；ic_ir_calc.py:5 | P2(链路缺口) | grep ic_ir_calc 生产调用方 |
| C 下游 | 消费方=multifactor_sleeve（:50,150 真实）+signal_providers（:39,162；但 start_paper_session.py:102 仅消费其 mock makers，正式 provider 类的实盘接线未证实）；错值传导=sleeve 打分面；回归法 in-sample 权重的过拟合直接进入 sleeve 评分 | multifactor_sleeve_strategy.py:150 | P2(同假设案) | 核 start_paper_session 全文 provider 装配 |
| D 旁系 | checklist #4 双承载：与 P35 compute_multifactor_confidence（IC 共识代理）同用 IC 均值但用途不同（置信度 vs 权重），无同式两算；与 ic_ir_evaluator（语义后继，ic_ir_calc.py:5 自declared）存在 IC 计算族双代际并存——IC 生产端统一裁定待做（非本件缺陷，登记链路） | ic_ir_calc.py:5 | 通过 | — |
| E 对抗 | 五问：①静默失败=兜底链全 warning 留痕（良好）；但等权兜底=静默降级为不同算法，下游无方法标记（synthesize 返回值不带 method 元数据）②假阳性=回归 in-sample 过拟合当真信号③断供=缺参兜底有痕④重触发幂等⑤时序=INV-004 声明级 PIT 防线（机械不设防） | :146-158 | P3 | — |
| F 新鲜度 | 等权/IC 加权/回归三法为因子合成标准三板斧（Grinold-Kahn 框架 IC×√breadth 谱系；MSCI/Alpha Architect 因子组合实践同构）；业界进阶=IR 加权（兼顾稳定性）与最优边界组合——**对等已有**；IR 加权为低成本增强候选 | https://alphaarchitect.com/combining-factors-in-multifactor-portfolios/ ；https://dev.to/linou518/quant-factor-research-in-practice-ic-ir-and-the-barra-multi-factor-model-1h8k | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：三法与业界标准因子组合方法一一对应（equal/IC-weighted/regression 均为教科书手法）。
- 立卡候选：IR 加权（IC均值/IC标准差）作为第四方法——实现成本低，业界实证优于纯 IC 均值加权（噪声惩罚）。
- 驳回：无。

## 4 缺陷清单

1. P2：回归法三重隐式假设未文档化（fillna(0)=中性、无截距、in-sample 拟合即应用）——下游 sleeve 直接消费即过拟合信号；建议=docstring 声明+应用面板与拟合面板分离（滚动回归）；验证法=阅 :117-125。
2. P2（链路缺口）：IC 加权法为默认方法（config default ic_weighted）但 IC 生产端 ic_ir_calc 生产零接线——**默认方法实际跑在"调用方每次手工传 ic_weights"假设上，缺传即静默等权兜底**（:149 kwargs.get("ic_weights",{}) 空 dict→无有效权重→等权+warning）；验证法=不传 ic_weights 观察 warning。
3. P3：三方法 NaN 语义不一致（跳过/传播/置零）；P3：头注 [CONSUMERS] 空 vs 实际两处消费（登记失实，方向=漏登非虚标）。

## 5 挂起疑问

- multifactor_sleeve 的 ic_weights 实际来源（真算 IC 还是常量）——建议随 P39/多因子 sleeve 收口一并核对。

## 6 完备性自评

六轴全查（F 带 URL）。长尾：①config analysis/_config.yaml 的 default_method 实际配置值未核（读 config 属运行时行为）②lstsq rcond=None 在 numpy 版本间语义漂移（运行环境锁定项，留环境审查）③回归法样本量下限 n=k+1 偏松（统计功效无检验）。

## 7 收口裁定（收口方填）
