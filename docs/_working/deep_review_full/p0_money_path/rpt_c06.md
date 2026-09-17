---
oid: C06
title: 危机闸（crisis_gate MOD-PA-CRISIS-GATE；classify:193/block:265；当前仅模拟盘消费）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3（注：本件为未跟踪在途新文件，工作区现状审）
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C06 crisis_gate（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/pf_alloc/crisis_gate.py:193`（classify_crisis_state）、`:265`（crisis_block_check）、resolve:230/log:318/alert:365/CrisisGate 门面:413。
- 基线声明：**本件为 git 未跟踪新文件（`?? src/zephyr/pf_alloc/crisis_gate.py`），属他会话在途施工（WO-2a）**；tests/pf_alloc/test_crisis_gate.py 已跟踪（基线 2fa92002c3 已含），当前 **8 failed / 15 passed**——8 个失败全部引用尚不存在的接线符号（如 `allocation_orchestrator.alert_crisis_level`），是在途接线的前瞻规格测试，非本件本体缺陷。
- 消费现状（工作区实测）：L3 已接线（scripts/backtest/sim_paper_ledger.py:97,175,189）；L1 零接线（pipeline_events.py 无 crisis 引用）；L2 零接线（allocation_orchestrator.py 不 import crisis_gate）。
- 排除项：regime 快照上游质量（HMM/教材）归决策链审查。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 判定逻辑：crisis=dominant==r10（硬）；warning=p_r10≥θ；crisis⊃warning（floor 随行）——实现与 workbook §2 口径一致；无快照 fail-closed 平坦→normal 不误触（验收③），p_r10 向量经 allocation_inputs isfinite 兜底（NaN→0.0），NaN 不误触 | crisis_gate.py:193-227；allocation_inputs.py:419 | 已查无 | 15 个通过测试+代码阅读 |
| A | θ 域校验 (0,1]、未知键硬错、解析失败硬错（配置在但读不懂不得静默）——配置纪律合格 | :130-161 | 已查无 | 同上 |
| B | 上游追源：复用 load_regime_input（PIT，禁未来函数，勿另写 SQL）——SSOT 正确；CH 不可读上抛（安全闸禁静默放行）契约明确 | :240-246 | 已查无 | 代码阅读 |
| C | **三级接线现状**：L1（pipeline_events.run_pf_alloc_daily 短路）**零接线**；L2（orchestrator 消费）**零接线**；L3（sim_paper_ledger entry 拦截）已接线。头注 :8-9 自认"接线归总统筹"——非静默，但**当前生产资金链（分配额度重算）在 crisis 日照常运行**，管线级额度冻结不生效 | grep pipeline_events/allocation_orchestrator 零 crisis import；sim_paper_ledger.py:95+ | **P1**（显式待办，非暗坑） | grep 两文件 crisis 命中数=0 |
| C | **warning 档 floor 承载断链+数学不可达双问题**：①floor_active（warning⊃crisis）无人消费；②L2 的 CRISIS_SHRINKAGE_FLOOR=0.05 触发条件=is_crisis（dominant==r10）且在当前参数域数学不可达（conf≥0.30×risk≥0.30→raw≥0.09>0.05，regime_meta_allocator.py:103-109 自认 #208-①）→**is_crisis 对 L2 shrinkage 是 no-op，危机缩额实际完全依赖快照 risk_signal 字段隐式承载**——block_check 的 reason 文案"warning→CRISIS_SHRINKAGE_FLOOR=0.05 激活"（:304）许诺了双重不存在的效果（L2 未接+floor 不可达） | crisis_gate.py:188-190,304；regime_meta_allocator.py:103-109,417-418 | **P1** | 数值推演：min raw=0.30×0.30=0.09>0.05；grep floor_active 消费方=0 |
| C | L3 接线口径核查：resolver 异常 fail-closed 拦 entry、旁路开关零调用、被拦日无 sim_trade_log 事件——语义与 workbook §2 一致 | sim_paper_ledger.py:71-97 | 已查无 | 阅读该段 |
| D | 兄弟/双承载对查（特殊问句）：危机口径双承载——regime_meta_allocator（is_crisis→floor 0.05，不可达）vs crisis_gate（dominant==r10 硬拦 + p_r10≥θ warning），两处触发条件不同源；且 allocation_inputs 另有第三处 is_crisis=dominant==CRISIS_STATE（:523）——三处"危机"判定并存，其中两处对资金面实际无效果 | regime_meta_allocator.py:417 vs crisis_gate.py:213 vs allocation_inputs.py:523 | P1（合并建议） | 三处常量/判定对读 |
| D | 纯函数无墙钟：同 (快照,θ)→同 CrisisState 成立；resolve_crisis_state(trade_date=None)→date.today() 墙钟默认（:239-243）——文档化先例（sim_paper_ledger 同款），与"禁按墙钟猜交易日"纪律存在张力（周末取旧快照 PIT 安全，但 lag 无上界告警） | :239-243 | P3 | 代码阅读 |
| E | 静默失败：log/alert swallow-all 但契约明示"留痕/告警失败不阻断安全主流程"+日志兜底——**拦截判定本身不吞**（resolve 上抛）——设计正确；风险点：表未建时 crisis_gate_log 长期静默 False=审计盲区无聚合告警 | :334-359,357-359 | P3 | 表不存在环境跑一轮看 warning 日志 |
| E | 重放幂等：crisis_block_check skip=True 不落 marker，解除后同日可重放——契约由调用方保证（当前 L1 无调用方，悬空承诺） | :252-258 | P2（随 L1 接线） | 接线 diff 评审点 |
| E | 时序：快照滞后 lag_days 无上限告警（如 lag>5 日仍按旧判定）——时序攻击面：快照断更则闸长期按旧态判定（checklist#6 数据源静默死亡味：本件靠"无快照→normal 不误触"方向正确，但**有旧快照无新快照**=无限期沿用） | :174-175（lag 留痕）+无上界检查 | P2 | 构造 10 日旧快照→仍按其判定无告警 |
| A.3 | 测试审查：15 过用例覆盖双档判定/配置纪律/留痕降级；8 失败=在途接线规格（引 orchestrator/regime_meta_allocator 未存在符号），归属施工中非缺陷；**缺**：快照滞后上界、NaN p_r10（上游兜底依赖）专项用例 | tests/pf_alloc/test_crisis_gate.py 失败清单 | P3 | pytest 重放 |
| F | （见 §3） | | | |

## 3 SOTA 对照

- 危机快速切断（L1 额度冻结）：对等已有方向——volatility switching 文献强调对 regime 切换反应迟滞导致持续超险，支持"dominant 翻转即冻结"的快闸设计。来源：[Man Group: Volatility is Back — Better to Target Returns or Target Risk?](https://www.man.com)（man.com 官网观点件）。
- 危机期 vol-target/风险平价负反馈（强平放大）：本闸"存量不强平、只拦新增"（:18-19）恰好规避 ECB/IMF 指出的 forced-selling 放大机制——设计取向有源印证。来源：[ECB FSR 2020: Volatility-targeting strategies and the market sell-off](https://www.ecb.europa.eu/press/financial-stability-publications/fsr/focus/2020/html/ecb.fsrbox202005_02~f6616db9be.en.html)。
- θ=0.5 起步待校准（O1）：立卡候选——建议接 D1 敏感性网格（regime_meta_allocator 已有同款机制）对 θ 做 ±20% 扰动稳健性验收。

## 4 缺陷清单（按严重级）

1. **[P1] 三级接线断两级（L1/L2 零接线）**。现状：仅 sim 账本级拦截生效；管线级额度冻结与裁决级缩额不生效。影响：crisis 日分配链照常产出钱包额度（仅 L3 拦 sim entry）。建议修法：按在途 8 个前瞻测试的规格落地（pipeline_events 接 crisis_block_check 短路；orchestrator 接 floor/告警）。验证法：落地后 8 红转绿+grep 命中。
2. **[P1] warning 档效果双不存在（floor 无人消费+floor 数学不可达）**。影响：p_r10=0.5-0.9 的恐慌预兆区间，资金面实际零响应，与"缩额+告警"的声明不符；文案承诺放大认知偏差。建议修法：把 floor 语义收敛到单一承载（建议 crisis_gate.floor_active 为真源，经 run_kwargs 显式传 allocator，或将 warning 并入 is_crisis 通道），并同步修 regime_meta_allocator 注释消除"激活"误导；θ 校准立卡。验证法：grep floor_active 消费方+raw 下界推演。
3. **[P2] 快照滞后无上界**：建议 lag_days>阈值（如 3）时升级 warning 级告警（数据源静默死亡早期信号，checklist#6 同型）。验证法：旧快照场景断言告警。
4. **[P2] L1"不落 marker 可重放"承诺悬空**：随接线落地必须同批验证（幂等契约在调用方）。
5. **[P3]** crisis_gate_log 长期 False 无聚合告警；date.today() 默认与交易日纪律的张力（建议强制显式传日）。

## 5 挂起疑问

1. 在途施工基线漂移声明：本件+8 前瞻测试落地将改 pipeline_events/allocation_orchestrator/regime_meta_allocator 三文件——本报告 L1/L2 类发现在其落地后需收口方重验（可能部分过期）。
2. "warning 照跑+floor 承担缩额"是 workbook §2 原意还是转述走样——建议 Owner 对照 wo2_blackswan_workbook §2 裁定单一真源承载点。
3. crisis 与 C04 MARKET_REGIME_CAPS[CRISIS]（仓位上限 5%）两套"危机"语义的互认关系未定义。

## 6 完备性自评

六轴全查。长尾：wo2_blackswan_workbook §1②/§2 原文未逐条对读（以代码内引用口径为准）；CH regime_snapshot_history 数据画像（断更史）未取；Alerter 冷却语义未深查。
