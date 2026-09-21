---
ttl: task_bound
title: 深度审查报告——风格Regime模型（D14）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：风格Regime模型（D14）

- 状态: **已审**
- 级别: P1｜类型: 算法（大小盘×价值成长风格态识别+防抖+参数映射）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/style_regime_model.py:64(StyleRegimeModel)`（295 行全文通读，confirm 防抖状态机逐分支推演）
- 生产调用方: **模型本体查无生产调用**——`strategy_matrix_3d.py:42,60,128` 仅复用 `SizeAxis` 枚举作三维矩阵风格轴（词表层消费）；`StyleRegimeModel.analyze/confirm/params_for` 零调用方；[CONSUMERS] "运行时装配批（风格参数档查找）"未接线（checklist#8 家族，枚举半消费态）；AI_AUTONOMY=human_gated（治理档位高）
- 测试文件: `tests/regime/test_style_regime_model.py`（25 测试）

## 1 对象快照

- 审查范围：风格序列构建/HMM 注入与规则降级双路/防抖确认状态机/参数映射全文件。排除项：hmm_runner 注入实现（契约外置，本仓未见实现体——挂疑问）；MOD-SIG-130 矩阵本体。
- 材料包缺项声明：风格收益序列的数据源管道（大小盘/价值成长代理指数）未审——本模块纯内存，上游注入面归数据域。
- 测试覆盖概况：25 测试较全（校验/防抖/映射）；confirm 状态机的"未决中断候选连击"语义（F-A2）未见显式用例。
- 变更热力：4 次。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **规则降级在单期收益差上分档，阈值量纲存疑**：`magnitude_threshold=0.005`（0.5%）作用于**单期**大小盘/价值成长收益差——日频风格日收益差的日常波动多在 ±0.5% 带内，规则路大量未决（None），短窗口可能"全期未决"Fail-Closed 抛错；且首个未决期后的**第一个未决期即立态**（confirm 前导回填逻辑），初态由单日噪声钉死（防抖只保护后续切换，不保护初态） | style_regime_model.py:132,173-179,239-241,253-257 | P2 | 合成日频风格差（σ≈0.8%）跑 analyze(60 期) 统计未决率与初态稳定性 |
| A | F-A2 防抖状态机语义推演（全分支）：同态重置候选/异态连击计数/未决中断候选但不破旧态/达 N 切换——逻辑正确无死角；**未决中断候选连击**是语义选择（规则路 None 频发时确认被反复打断→切换延迟放大），与"未决期不破旧态"声明一致但文档未披露"未决也打断候选"半边 | :219-257 | P3 | [A,B,None,B,B,B] n=3 推演（本审查已验：切换被延后 1 期） |
| A | F-A3 输入校验完备（等长/非空/有限/bool 排除/词表闭合/参数映射 4 态必填/StyleParams 域检查）——Fail-Closed 纪律全域一致，无静默默认值；零随机源确定性成立 | :97-103,135-147,154-169,196-198 | 已查无 | 逐校验分支读 |
| A | F-A4 HMM 注入路径契约严格：标签词表校验（词表外抛）、等长校验、used_hmm 留痕——注入式设计的消费面防御到位；但 hmm_runner 的**统计语义无契约**（输入是差值序列、输出须是态标签——平滑/防抖责任在 runner 侧还是 confirm 侧未定义，双防抖/零防抖都可能被接出） | :200-211 | P2 | 读 hmm_runner 契约注释（无——隐式契约未文档化） |
| B | F-B1 纯内存零 IO：风格序列构建=逐期差（lead−lag），代理指数选择/复权口径全在上游——本对象无上游校验义务但有无契约声明（INVARIANTS 有"等长非空有限"——已声明 ✓） | :8,154-169 | 已查无 | — |
| C | F-C1 消费方核实：模型本体（analyze→params_for）零调用方=参数档查找能力空转；SizeAxis 被 strategy_matrix_3d 复用（词表真源地位成立）；爆炸半径当前=0，接线日=风格→仓位参数（position_pct）直达仓位的激活日——**position_pct ∈[0,1] 直连仓位语义，接线时须过人门位**（AI_AUTONOMY=human_gated 已自带该治理属性 ✓） | strategy_matrix_3d.py:28,42; style_regime_model.py:89-103 | P2 | grep 复核 |
| D | F-D1 查重分工声明与事实相符：core/regime_detector=大盘体制概率（正交）、regime_cycle_analyzer=时间节律（正交）、本件=截面风格——三对象词表/输出互不重叠（grep 复核无交叉 import）；风格态词表（large_value 等 4 态）全仓唯一 | :26-29 | 已查无 | grep 四词表无第二副本 |
| E | F-E1 静默失败面：全路径 Fail-Closed 无降级默认值、无 except 吞噬、日志仅 debug/info——静默面干净（与 D01/D05/D12 的"降级哲学"不同路线：统计小模块 fail-closed 正解） | 全文 | 已查无 | — |
| E | F-E2 幂等：纯函数零状态零随机——同输入必同输出 INVARIANT 可机械保证 | :8 | 已查无 | 双跑对拍 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 大小盘/价值成长风格差作风格轴 | **对等已有**——SMB/HML 因子差是风格定义的学术正源（Fama-French 1993）；本项目"收益差+规则/HMM 分档+防抖"是该谱系的工程化实现；Ken French 数据库即同构差值序列的官方产出 | [Fama & French 1993, Common risk factors in the returns on stocks and bonds, JFE](https://www.bauer.uh.edu/rsusmel/phd/Fama-French_JFE93.pdf)（ScienceDirect JFE 33(1)，1993，引用 ~37700）；[Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html)（Dartmouth，官方因子数据） |
| 2 | 风格态切换防抖（连续 N 期确认） | **对等已有**——regime switching 的确认滞后期（confirmation lag）是体制切换模型标准权衡（减少 whipsaw vs 延迟）；confirm_periods=3 与常规工程取值一致；文献多在 HMM 平滑概率上做阈值，本项目规则路+防抖为合理降级 | 体制切换文献谱系（Hamilton 1989 regime switching 起源；[Hamilton 综述见投研常识引用面](https://www.nber.org/papers/w4694)（NBER WP 4694，1994如实记检索面）） |
| 3 | 立卡候选：HMM 风格体制的标准做法 | **立卡候选（接线前）**——hmm_runner 接线时应明确：输入用累计/平滑差值而非单期原始差值（降低未决率与初态噪声），并在 runner 契约里写明防抖责任归属（F-A4） | 同上 Hamilton 谱系 |

## 4 缺陷清单（按严重级）

- **F-A1（P2）单期差分档的未决率与初态噪声**：建议=①阈值按差值序列波动率自适应（如 0.5×std）或改用累计/平滑差；②初态增加确认期（前导回填改为"前 N 期多数态"）→ 验证法=合成数据统计未决率。
- **F-A4（P2）hmm_runner 隐式契约**：接线前在类型注释/docstring 写明输入平滑预期与防抖责任边界 → 验证法=契约文档评审。
- **F-C1（P2）本体孤儿+枚举半消费**：接线计划登记；position_pct 直连仓位的接线必须走 human_gated 门位（已在 AI_AUTONOMY 声明，收口时核对执行）→ 验证法=grep。
- **F-A2（P3）未决中断候选语义文档化**——常规队列。

## 5 挂起疑问

1. hmm_runner 的实现体在仓内查无——B10-01447 的 HMM 风格识别是否已有独立实现待接（若无，HMM 路实际不可用，当前唯一能力=规则降级路）。
2. 风格收益序列上游代理（大小盘用什么指数对、价值成长用什么口径）——蓝图 §0 未回读，量纲与 PIT 归接线批。

## 6 完备性自评

- 六轴全查：A（防抖状态机全分支推演+阈值量纲发现+校验完备性）、B（纯内存无上游）、C（消费方=枚举半消费核实）、D（三对象查重分工核实）、E（静默面干净/确定性）、F（3 条带来源）。
- 长尾清单：①hmm_runner 实现体缺失；②蓝图 §0 原文；③StyleParams 各态参数档的取值依据（接线时人门位审查材料）。
