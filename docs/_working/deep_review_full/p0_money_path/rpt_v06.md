---
oid: V06
对象: 过拟合裁决器（overfitting_adjudicator，三检验器+门禁挂钩点）
入口: src/zephyr/backtest/core/overfitting_adjudicator.py:514（OverfittingAdjudicator）
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 本对象零漂移）
材料包: 源码+测试全读；churn；消费方 grep（全仓）；运行时证据=logs 抽查
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V06 过拟合裁决器（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：expected_max_sharpe_z 委托封装（L95-112）、adjudicate_dsr（L147-223，数学全量委托 MOD-SIM-024）、summarize_walk_forward（L260-326）、perturbation_stability（L382-474）、OverfittingAdjudicator.adjudicate（L521-589）+ OverfitGateHook Protocol。
- 排除项：DSR 数学本体（V07 详审，本件只审委托与封装口径）。
- 测试：tests/backtest/test_overfitting_adjudicator.py 约 30 用例（含 SDC-4 严格化类与 NormalDist 独立预言机对拍），实测全绿。
- 变更热力：4 commits；最近 c88d5e33db（裁定#291 DSR 口径统一治本——峰度 Pearson 化+闭式+退化 fail-closed）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | DSR 数学零自写（委托 canonical，cross-implementation 收敛测试锁三处同源）；expected_max_sharpe_z 对 N<1 抛错（比官方件更严的输入契约，已文档化差异） | overfitting_adjudicator.py:95-112,189-197 + tests/simulation/test_deflated_sharpe_calculator.py:476-507 | 已查无 | 读委托链 + 收敛测试 |
| A | walk-forward 汇总：IS≤eps 折剔除（对齐 compare_in_out_sample 口径）、无有效折 fail-closed=False、is_stable=最差折≥0.70（最严语义）、std 用 ddof=1 | :289-326 | 已查无 | tests:53-113 手算锚 |
| A | 扰动检验：decay=(base−pert)/|base|、改善=负衰减计入稳健、min_robust_share 默认 1.0（全点须稳健，fail-closed）、零参/零基准绩效显式拒绝 | :407-452 | 已查无 | tests:275-349 |
| A | **debug 日志格式串非法（机验实证）**：`"pct=%.0%%"` 是非法 % 转换（%.0% 无此格式符）→ 格式化时抛 ValueError——logging 内部 handleError 吞掉并打 "--- Logging error ---" 到 stderr，不崩进程但每次 DEBUG 输出必报错 | overfitting_adjudicator.py:467 | **P3**（debug 级但确定性 bug） | `'pct=%.0%%' % (0.2,)` → ValueError（已机验）；修法=改为 `pct=%.0f%%%%` 或 f-string |
| A.3 | 测试强度高（手算+预言机双锚），旧 fail-open 断言 `dsr in (0.0,1.0)` 已被 SDC-4 类显式废除并留注释——测试自身演进可追溯 | tests:214-256 | 已查无 | 读测试注释 |
| B | 上游=注入 kwargs（folds/dsr 矩/扰动参数），校验在各自函数内（NaN/Inf/越界全抛）✓ | :176-184,277-287,407-427 | 已查无 | tests 各 raise 用例 |
| C | **生产调用方=0（grep 实证）**：文件头自认"上线评审流程(挂钩点预留, 未接真门禁)"，但 MATURITY 标 production——三检验器裁定件现无任何生产链路消费；"断路假象"风险=后人以为上线有 P-5 裁定把关 | overfitting_adjudicator.py:5 + grep（src/scripts 零外部调用） | **P2**（已登记型孤儿+成熟度标签失真） | `grep -rn "overfitting_adjudicator\|OverfittingAdjudicator\|adjudicate_dsr" src scripts` 除本文件外零命中 |
| C | 爆炸半径=现无（未接线）；接线后=全策略上线判定 | — | — | — |
| D | 阈值全复用 SSoT：0.70（overfitting_detector:62 实测）+0.30（:52）+0.95（MOD-SIM-024:70）——零自造 ✓；兄弟件 decision_gate（回测闸，已接线）与本件（裁定器，未接线）+protection_gate（四层闸，未接线）三件同域分层清晰但两件悬空 | :55-65 | 已查无（阈值）；合并建议见 V08 | grep 常量 |
| E | 五问：**假阳性过关面=adjudicate() 空参调用返回 is_overfitting=False（未检测=通过语义）**——"未提供检验器视为未检测"与 detect 口径一致且已文档化，但作为门禁输入即"什么都没跑=放行"；静默失败=logging bug（上）；断了没人知道=C 行孤儿态；重复触发=纯函数幂等 ✓；时序=无状态 ✓ | :540-589 | P3（接线前修） | `OverfittingAdjudicator().adjudicate().is_overfitting==False` 复现 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| DSR 三线裁决（0.95/0.5 阈值语义） | 对等已有（数学本体对照见 V07；本件阈值复用 SSOT） | Bailey & López de Prado (2014), SSRN 2460551：https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 |
| walk-forward 最差折 0.70 + OAT ±20% 扰动 | 对等已有（业界通行做法，保守取向） | 检索限流记"受阻"（通行性判断基于工具侧综述，无单条 URL 实证） |
| CSCV/PBO | 立卡候选：扰动 OAT 是较粗的稳健性探针，CSCV/PBO 提供组合级过拟合概率，可作检验器④补位 | Bailey, Borwein, López de Prado, Zhu (2015)：https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf |

## 4 缺陷清单（按严重级）

1. **P2｜生产零调用+production 标签失真（孤儿门禁）**：现状=三检验器无生产消费方；证据=文件头 L5 + grep 实证；影响=上线链是否存在 P-5 把关全凭口头记忆（checklist#8"空转多久没发现"之问现成）；建议=短期把 MATURITY 降 experimental/注明 reserved，长期按蓝图接线 gate_hook 或与 V08 四层闸合并接线；验证法=grep 一行。
2. **P3｜debug 日志格式串非法**：:467；验证法=§2 机验；建议=修格式串（低成本确定性修复）。
3. **P3｜空参 adjudicate=放行语义**：:540-589；建议=零检验器时 reasons 至少含"未执行任何检验器"显式标记，供门禁侧区分"全过"与"没跑"。

## 5 挂起疑问

- 上线流水线（门禁挂钩点真源）规划在哪批施工落地——V06/V08 两件悬空件是同一张施工票还是两张，需 Owner 拍板（合并建议见 V08 §4）。

## 6 完备性自评

六轴全查。长尾：①DSR 数学本体归 V07（已另审）；②扰动检验只覆盖 OAT 一维扰动（交互扰动未审——文献也少有，记局限非缺陷）。运行时证据：近 3 日 logs 无本对象 error（与"未接线"互证）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P3 %.0%% 格式串: 确认→治本(%.0f%%)。
- P2 孤儿门禁+production 标签失真: 挂起登记(与 V08 合并裁定)。
- 修复提交: 队列 q-20260918-st-deeprev-20260918-0007。
