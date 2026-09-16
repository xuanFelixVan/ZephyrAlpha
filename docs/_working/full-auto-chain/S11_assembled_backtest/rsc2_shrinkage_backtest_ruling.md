---
ttl: task_bound
completes_when: RSC-2 Shrinkage 口径落地并在库（实现 067a8bdb8d + 登记 bcf9e48b43 + 本文档）；终态翻转（B 候选）另立新件
title: RSC-2「Shrinkage 进整装回测」目标口径裁定（裁定#270）
session: st-rsc2-20260916
date: 2026-09-16
parent: S11_assembled_backtest
---

# RSC-2「Shrinkage 进整装回测」目标口径裁定（裁定#270）

> Owner 令（2026-09-16 欠账清偿战）：解除 GW4 量化班（裁定#257 执行者）终报留档的
> "RSC-2 目标口径待裁"，由 GW-H 车道按客观专业架构师标准裁定并落地。
> 本文档=裁定真源；登记真源=ruling_registry.yaml 裁定#270（同 commit 原子）。

## 1 出处考证（RSC-2 是什么）

| 证据 | 位置 | 内容 |
|------|------|------|
| 编号出处（唯一定义） | `docs/_working/full-auto-chain/S11_assembled_backtest/nodes/regime_supply_chain_mining.md:128`（§4 表 RSC-2 行） | **Shrinkage 进整装回测**（F2 治本）：composer 增 shrinkage_by_date 可选参数，合成面板行乘当日 Shrinkage（≤1 只减不增），剩余质量落现金——与 decision_kernel T1A-5 现金语义裁定合并裁定；验收=动态整装回测双跑（开/关）两条净值曲线+差值章进证据包 |
| 裁定前提修正（裁定输入） | `nodes/pf_alloc_consumer_mining.md:76`（§3 PFA-3）与 :151（§9 表） | F2 原表述"实盘会被 Shrinkage 压缩"经 PFA-1 实证修正：实盘分配链（MOD-PA-007）**从未装配**（零生产调用方）——回测加 Shrinkage 是向**纸面（设计）口径**对齐；目标口径=满仓 vs Shrinkage 节流待裁（Owner 决策位→本次授权下裁） |
| 留档出处 | `docs/_working/greatwall_integration/2026-09-16-eight-greatwall-e2e-integration.md:66` | "RSC-2 口径——均按裁定登记，非欠账"（GW4 班留档项即本件） |
| 上游发现 | `nodes/regime_supply_chain_mining.md:59-70`（F2） | 整装回测链消费 regime=硬标签查表（fw_backtest.load_regime_series→composer 逐日查 regime_overrides），**不含 Shrinkage 节流（回测永远满仓）**；设计口径 Shrinkage 危机时最低 0.147（regime_detector.py）——回测证据外推系统性偏乐观 |

**语义考证结论（诚实条款）**：RSC-2 的 Shrinkage **不是** deflated_sharpe_calculator 的
DSR 统计收缩、**不是** Ledoit-Wolf 协方差收缩、**不是** pattern_evidence_certifier 的
shrunk_rate 贝叶斯收缩（三者均为同名不同域，任务书已预警勿混淆）。它=MOD-REGIME-001
RegimeDetector 五子模块之⑤的**风险节流标量**（Shrinkage=Confidence×Risk，危机时最低
0.147，regime_detector.py L805-829/L741），语义=当日组合资金部署比例（1.0=满部署）。
"进回测"=把该逐日节流因子接入整装回测（framework_composer 链），消除 F2 双轨分叉。

## 2 问题定义（第一性原理）

回测的唯一产出是**证据**；证据的价值取决于它与被模拟对象（设计口径的实盘）的行为一致性。

- 设计口径（纸面链）：MOD-PA-007 声明 `global_shrinkage` 总暴露缩放；regime 检测器输出
  Shrinkage 且危机强收缩——即**设计意图含风险节流，节流的剩余=现金**。
- 回测现状：整装回测永远满仓（F2 实证），且引擎数学上**强制满仓**——
  `vectorized_engine.py:187-189`（AI-NIGHT-001 审查对齐口径）明文：Σ<1 的强度面板会被
  `_normalize_day_signals` 放大为 Σ=1 满仓；"半仓/现金仓位意图请经 shrinkage 层表达"。
- 后果：危机/熊市段越长，整装回测证据越乐观（F2），且该偏差无人可见（无对照）。

## 3 口径候选与裁定分析

| 候选 | 内容 | 否/取理由 |
|------|------|----------|
| A 满仓（现状） | 回测永远满仓，Shrinkage 只留实盘 | 证据系统性偏乐观（F2 病灶不治）；且实盘链未装配（PFA-1），"实盘满仓"并非设计口径而是装配缺口——把缺口当口径=锚定错误 |
| B 默认节流 | 翻转默认，所有整装回测默认乘 Shrinkage | ①生产语义变更（历史 bt-fw-* 产物口径断裂，可比性损毁）；②Shrinkage 日序生产链未投产（RSC-3 供给件未挂，日序无自动真源）——默认依赖一条没有日更供给的表=回测结果受数据新鲜度摆布；③默认翻转属 §5 生产流转门位，越权 |
| **C 双轨披露制（裁定）** | 默认满仓（零漂移）；`shrinkage_by_date` 显式注入=节流口径；验收语义=**双跑对照**（开/关两净值+差值章披露） | 见下 |

**裁定：候选 C 双轨披露制。** 理由：

1. **证据论**：节流口径与满仓口径都不是"唯一真相"——真相是**两者的差值**（节流保护了
   多少下行、付出了多少上行）。C1 一票否决验证语义（验收原文）本身就是开/关对照而非
   单边宣称；整装回测同构。差值章进证据包=把 F2 的隐性偏差变成显性数字。
2. **可比性**：默认满仓保证既有调用方（api_server POST framework-backtest-run、
   fw_backtest_due）与历史 bt-fw-* 产物逐位零漂移（二期/三期消费方契约不破）。
3. **供给现实**：RSC-3 日序供给件未投产，自动默认节流的数据地基不存在；opt-in 口径
   允许验证与将来投产解耦。
4. **业界对齐**：regime 概率驱动动态配置的标准形态即"概率/风险信号→仓位节流→余量
   现金"（arXiv:2406.09578，2024）；回测/实盘分配语义同一性是 paper→live 过渡铁律
   （Concretum 生产十课，pf_alloc_consumer_mining ②下游引用）——双轨披露是走向
   同一性的第一步而非终态，终态（默认节流）待 RSC-3 投产+Owner 门位批准。
5. **实现真源约束**（关键考证发现）：验收原文"合成面板行乘当日 Shrinkage"若按字面在
   compose 层实现**是无效的**——引擎 `_normalize_day_signals` 会把 Σ<1 行放大回满仓
   （vectorized_engine.py:187-189），收缩被静默吞掉。正确接入位=引擎边界：
   `ShrinkageBacktestEngine._get_day_signals` 在**归一化后**乘当日 Shrinkage，权重和=当日
   Shrinkage≤1，差额经 MatchingEngine `target_value=NAV×weight` 天然留现金
   （shrinkage_engine.py:24-28 设计文档明示）。该件与 `ScheduleShrinkageProvider`
   （PIT as-of join，不查未来）均为现成真源（C1 已用），**复用勿重造**。故规格落点为
   "compose 面板保持 Σ=1 纪律不变；节流在引擎边界生效"——与验收原文语义一致
   （合成面板**被消费时**乘当日 Shrinkage），与字面落点（compose 算子内乘）不同，
   按实际定义裁。

## 4 裁定口径（规范陈述）

1. **默认口径=满仓**：`shrinkage_by_date=None`（或空表）时行为与既有语义逐位一致
   （向后兼容锚，二期/三期产物零漂移）。
2. **节流口径=引擎边界乘法**：`shrinkage_by_date` 注入 {date: factor} 时，
   run_framework_backtest 改用 ShrinkageBacktestEngine+ScheduleShrinkageProvider；
   当日 Shrinkage 经钳制 [0,1]（只减不增）乘于归一化后权重，**剩余质量一律落现金，
   禁任何形式的再归一化回填**（=与 T1A-5 现金语义裁定的合并部分；现金日=全零行
   既有语义不冲突）。
3. **PIT 铁律**：schedule 查表=as-of join（≤查询日最近一条，早于首条=1.0 未启动），
   真源 ScheduleShrinkageProvider，不查未来。
4. **双跑验收语义**：`run_framework_backtest_shrinkage_dual` 编排关/开两跑（同面板同
   参数，唯 shrinkage 不同），产出两条净值曲线+差值章（shrinkage_diff_stamp：终值差/
   总收益差/最大回撤差/逐日差/节流日数），供证据包组装方消费。
5. **披露纪律（禁静默）**：节流启用时 artifact metrics 落 `shrinkage_disclosure`
   （applied/供给语义/schedule 统计/逐日生效 log/节流日数），result 顶层 `shrinkage`
   键同源；不启用不加键（零漂移）。
6. **边界（本裁定不做）**：①fw_backtest_due 链自动双跑/默认节流——待 RSC-3 日序供给
   投产后按 §5 门位另行裁定编排；②C1 一票否决判定——属 C1ShrinkageComparator 域，
   本件只出披露章不出否决；③T1A-5 的 regime_overrides 覆盖表 r1/r2/r11 回退基准
   合理性——另行裁定，本件合并的仅现金语义；④B 候选（默认翻转）保留为终态选项，
   触发条件=RSC-3+RSC-4 落地+Owner 批准。

## 5 实现规格（最小正确件）

| 件 | 位置 | 内容 |
|----|------|------|
| 参数 | `FrameworkBacktestConfig.shrinkage_by_date`（framework_composer.py） | dict{date-like: float}，None/空=关；值钳 [0,1]；非法日期/值 fail-closed（FrameworkValidationError） |
| 接入 | `run_framework_backtest` 引擎选择处 | 启用时 ShrinkageBacktestEngine(config, shrinkage_provider=ScheduleShrinkageProvider(归一化 schedule))；否则 DefaultBacktestEngine（原路） |
| 引擎参数透传 | `ShrinkageBacktestEngine.__init__`（shrinkage_engine.py） | 补 enable_stk_limit_provider/universe_provider 透传（既有缺陷：构造丢父类引擎参数，composer 注入 enable_stk_limit_provider=False 的测试/离线路径会静默失效——与本裁定同 commit 修复，向后兼容） |
| 差值章 | `shrinkage_diff_stamp`（framework_composer.py，纯函数） | (curve_off, curve_on, shrinkage_log) → 披露 dict（schema=1，逐日两净值+差值+汇总统计；方向语义=on-off，无裁定判定） |
| 双跑编排 | `run_framework_backtest_shrinkage_dual` | 关/开各跑一次（共享 compose 面板语义，面板构建×2 如实披露），返回 {"off","on","equity_curves","diff"} |
| 主体提取 | `run_framework_backtest` 本体 → `_run_framework_backtest_core` 薄提取 | 返回 (result, ts)；run_framework_backtest 签名/返回不变；dual 复用其净净值曲线（防双跑函数克隆 60 行编排——CLONEGUARD） |

## 6 验收与验证

- 单测（tests/pf_core/test_framework_composer_shrinkage.py，tmp_path 隔离）：
  默认关逐位一致/开启 NAV 差值方向/钳制与退化（s=0 全现金日、s=1 等价、NaN→1.0
  满部署保守退化）/fail-closed/PIT as-of/披露键齐/引擎参数透传。
- 真数据回归：既有 test_framework_composer + test_shrinkage_engine +
  test_shrinkage_provider + DSR/decision_gate 套件两轮零失败。
- 双跑差值章实测：真实 bt-fw 产物窗口的合成收缩 schedule 对比（报告注明合成部分）。

## 7 红队自检（裁定脆弱点如实列出）

- "默认满仓"是否掩盖问题？——否：差值章使偏差可量化；且 due 链终态挂接已登记为
  RSC-3 后门位事项（非静默搁置）。
- 引擎边界乘法 vs compose 乘法的偏差？——compose 乘法会被引擎吞掉（无效）或需改引擎
  归一化契约（大改）；引擎边界乘法是 shrinkage_engine.py 设计文档（§接入点设计）声明
  的唯一正解，C1 先例同源。
- 双跑面板构建×2 的成本？——验证/证据场景非高频路径，如实披露；共享面板的重构
  （compose 一次双引擎）留待 due 链编排时一并做。

## 8 续做补记（GW-H2 接力，sess=st-rsc22-20260916，2026-09-16）

> GW-H 配额阵亡，GW-H2 接力清偿。本文档原为前任 staged 未提交件，本节=接力验证与
> 落库留痕；§1-§7 口径经复核**零修正采纳**（考证出处逐条重验：RSC-2 定义
> regime_supply_chain_mining.md §4、PFA-1/PFA-3 修正、GW4 留档、vectorized_engine
> 归一化强制满仓、shrinkage_engine §接入点设计——均与本文一致）。

**交接现场盘点**（本文档 staged 之外，前任工作已被并行车道 adopt 同批落库）：

| 件 | 状态 | 载体 |
|----|------|------|
| 实现三件（composer/shrinkage_engine/测试 457 行 20 例） | 已在库 | 067a8bdb8d（车道A st-qoder-t1a，18:43，与 T1A-1/2/3 同文件同批） |
| 裁定#270 登记 | 已在库 | bcf9e48b43（车道F，17:43，adopt 同批；affected_files 已列本文档） |
| 本文档 | staged 未提交 | 本 commit 补齐（登记↔文档原子对的最后半件） |
| 裁定编号 | #270 无撞号 | 接力时总包口径"max=269"；登记先于 #271/#272/#273 落库，本文档与登记同源同号 |

**验证结果**（GW-H2 复跑，非转抄）：

1. 套件两轮零失败：RSC-2 目标套件（test_framework_composer_shrinkage 20 +
   test_framework_composer 34 + test_shrinkage_engine + test_shrinkage_provider）与
   DSR/decision_gate 既有套件（test_deflated_sharpe_calculator + test_decision_gate +
   test_decision_gate_regime + test_n_trial_ledger）合计 **228 passed × 2 轮**。
2. 红蓝覆盖核验（既有测试实证，未新增）：s=0 全现金日（test_zero_shrinkage_full_cash）、
   s=1 满部署等价（test_none_provider_defaults_to_full_deploy）、provider NaN→1.0 保守
   退化（test_clamps_nan_to_full_deploy）、入参 NaN/非映射/坏日期 fail-closed
   （test_fail_closed 参数化 5 态）、钳制只减不增（test_clamp_only_reduce：1.4→1.0、
   −0.2→0.0）；极端 n_eff 属 DSR 域，由 n_trial_ledger/deflated_sharpe 套件守域（本件
   不越域，语义考证 §1 已切割）。
3. 双跑差值章实测（真窗口=bt-fw-823d7fd7 同窗 fw-tdm-current 2025-09-16→2026-09-15、
   242 净值点；**收缩 schedule=合成**，非 detector 生产输出，注明）：

| 情景（合成） | off 总收益/回撤 | on 总收益/回撤 | 差（on−off） |
|--------------|----------------|----------------|--------------|
| A 均匀 0.6×241 信号日 | −37.5129% / 38.1924% | −23.4026% / 23.7688% | 收益 +14.11pp、回撤 −14.42pp |
| B 危机谷 10 日 0.4 | −37.5129% / 38.1924% | −35.1913% / 35.8961% | 收益 +2.3216pp、回撤 −2.2964pp |

   方向正确性：亏损年内节流减损（A）、危机段节流护下行（B），与"Shrinkage=资金部署
   比例、剩余落现金"语义一致；run_id 实证 A=bt-fw-da26f575(off)/bt-fw-3c60a416(on)、
   B=bt-fw-d006b324(off)/bt-fw-df763adf(on)。
4. 零漂移实证：两情景 off 腿净值曲线**逐位一致**（242/242 点相等），且 off 腿产物无
   shrinkage_disclosure 键、on 腿键齐（schema=1 十二键）——§4.1 默认满仓逐位零漂移与
   §4.5 禁静默披露在真实产物上双确认。

**边界重申**：本接力未改任何实现代码（实现已达标在库）；本 commit 唯一载荷=本文档
（续做补记并入）。fw_backtest_due 自动双跑、C1 否决判定、B 候选终态翻转仍按 §4.6
边界外事项待 RSC-3/Owner 门位。
