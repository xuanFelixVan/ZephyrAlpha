---
oid: V08
对象: 过拟合保护闸（overfitting_protection_gate，四层防护统一门禁 MOD-SIM-028）
入口: src/zephyr/simulation/overfitting_protection_gate.py:138（OverfittingProtectionGate）
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 本对象零漂移）
材料包: 源码+测试全读；churn；消费方 grep（全仓 src+scripts）；运行时证据=logs 抽查
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V08 过拟合保护闸（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：ProtectionLayer/CheckStatus/GateDecision 词表（L66-87）、四层检查项注册表（register_check/checks_of L161-182）、统一裁决 evaluate（L186-247）、frozen 报告协议面。
- 定位：编排/注册/裁决协议件，检查器全注入（本件不重算 DSR/PBO 指标——查重分工在文件头声明）。
- 测试：tests/simulation/test_overfitting_protection_gate.py 19 用例（注册/裁决/缺层 fail-closed/检查器异常/语义检查器示例），实测全绿。
- 变更热力：4 commits（57d42b1b4f 出生→错误码转正→ALGO_FLOW 补登→出仓波次）——无语义返工，但也**长期零接线演进**（见 C 轴）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | 编排逻辑正确：层词表闭合枚举、check_id 层内唯一、按 check_id 确定性排序、任一失败→BLOCKED、blocked_by 全局排序、报告 frozen、同输入同输出（测试钉） | overfitting_protection_gate.py:130-247 + tests:99-200 | 已查无 | 读码+tests |
| A | fail-closed 三防线：缺层拒绝裁决（L195-197）、检查器异常按失败不旁路（L210-212，_log.exception 出声）、空 subject 拒绝——编排层面无 fail-open 洞 | :192-212 | 已查无 | tests:139-172 |
| A | 检查器返回非 CheckOutcome（如裸 bool）→ `.passed` 属性访问抛 AttributeError→被 except 捕获判失败——fail-closed，但错误信息是"检查器异常: AttributeError"（可诊断性略差） | :205-212 | P3 | 注册 lambda ctx: True 复现 |
| B | 上游=payload Mapping（无 schema 约定）：缺键时检查器内 KeyError→判失败（fail-closed ✓），但**payload 契约完全隐式**（各检查器自定义键名，四层无统一 payload schema 文档）——接错键名=静默判失败而非报错 | :186-194 | P3 | 传 {} → 全 BLOCKED 而非配置错误提示 |
| C | **生产调用方=0（grep 实证）**：src/scripts 除本文件外零引用 `OverfittingProtectionGate`；文件头 CONSUMERS 写"运行时装配批"——该装配批不存在。四层防护统一门禁从未在生产运行过；若有人以为"上线前有四层闸"即属"断了没人知道"（checklist#8 孤儿死码命中） | 文件头 L5 + grep 全仓零命中 | **P2** | `grep -rn "OverfittingProtectionGate" src scripts` 除本文件零命中 |
| C | 爆炸半径=现无（未接线）；接线后=全 subject（因子/策略/信号/ML）上线拦截面 | — | — | — |
| D | 语义检查器只存在于测试（tests:208-292 是示例 lambda，非生产件）；同域三件分层：decision_gate（回测三段闸，已接线）/overfitting_adjudicator（P-5 裁定器，未接线）/本件（四层统一闸，未接线）——**后两件悬空且功能交叠（strategy 层=DSR+PBO 与裁定器 DSR 完全同源），合并建议：接线时以本件为编排壳、adjudicator 作为 strategy 层检查器实现，勿造第四处编排** | tests:208-292 + V06 §2 C 行 | P3（合并建议，转挖矿） | grep 三件调用方对照 |
| E | 五问：静默失败=无（异常出声+判失败）；假阳性过关=**未接线本身**（C 行，该拦的全没拦）；断了没人知道=C 行；重复触发=evaluate 纯函数幂等 ✓；时序=payload 快照+注入时钟 ✓ | 全文件 | 见 C 行 | — |
| E | 默认时钟 `datetime.datetime.now`（朴素本地时间，无时区）——generated_at 若落库与全仓显式 UTC 口径（RULE-SCHEMA-TZ）不一 | :146 | P3 | 读构造函数；修法=datetime.now(timezone.utc) |
| E | 测试套件 importorskip 包裹（tests:20-23）：模块 import 失败时 19 用例**静默跳过=全绿**——模块损坏时测试线不报警（checklist#3 邻类：绿≠对） | tests/simulation/test_overfitting_protection_gate.py:20-23 | P3 | 临时注入 import 错误看套件 SKIP 即绿 |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| 四层过拟合防护分层（因子 IC 衰减+多检校正 / 策略 DSR+PBO / 信号 WF 一致性 / ML OOS 退化+对抗） | 对等已有（分层防御思想与文献一致：多重视角组合判定过拟合） | Bailey, Borwein, López de Prado, Zhu (2015), "The Probability of Backtest Overfitting"（PBO/CSCV）：https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf ；López de Prado, Advances in Financial Machine Learning (2018) CPCV（通行引文，URL 未实证记部分受阻） |
| PBO 判定阈值 | 立卡候选：测试示例用 pbo<0.5（掷硬币线）；文献实践更严（PBO 越低越好，常用 <0.2 为佳）——接线时阈值应预注册并对照文献 | 同上 2015 论文（PBO 定义与估计） |
| 统一裁决编排（任一失败即拦截+缺层拒绝） | 对等已有（fail-closed 门禁编排通行做法） | 无单条 URL（编排模式非算法），记"受阻" |

## 4 缺陷清单（按严重级）

1. **P2｜四层防护闸生产零接线（孤儿门禁）**：现状=src/scripts 零调用方；证据=文件头 L5 CONSUMERS 指向不存在的"装配批" + grep 实证；影响=该拦的（因子 IC 衰减/策略 DSR/PBO/ML OOS 退化统一拦截）全没拦，且 production+human_gated 标签制造"已有闸"错觉；爆炸半径=上线链整体；建议=①短期标注 reserved/experimental+在上线 checklist 显式注明"该闸未启用"；②中期施工接线（与 V06 合并：本件做壳、adjudicator 做 strategy 层检查器）；验证法=grep 一行复现零调用。
2. **P3｜测试 importorskip 静默绿**：tests:20-23；建议=改 fail-on-import-error（importorskip 仅限可选依赖件，本件是仓内核心件不适用）；验证法=同 §2 E 行。
3. **P3｜默认时钟朴素本地时间**：:146；建议=timezone.utc；验证法=读一行。
4. **P3｜payload 契约隐式/非 CheckOutcome 返回诊断性差**：:186-212；建议=接线时随施工补 payload schema 注释+isinstance 预检给明确报错。
5. **合并建议（D 轴转挖矿）**：V06 裁定器与 V08 四层闸两悬空件合并接线，避免第四处过拟合编排。

## 5 挂起疑问

- "运行时装配批"消费方从未落地——是待施工还是已废弃路线？需 Owner 裁定（决定本件是接线还是退役，规范预算净零原则适用）。
- 四层 payload 的指标真源（各层检查器应消费 decay_monitor/bhy_fdr/DSR/WF 产物）接线图不存在——接线施工前需先出装配设计。

## 6 完备性自评

六轴全查。长尾：①因零接线，各层检查器语义实现（IC 衰减算法/PBO 数值）无生产码可审——只能审测试示例 lambda，属结构性材料缺失；②运行时证据：近 3 日 logs 无本对象任何痕迹（与零接线互证）。
