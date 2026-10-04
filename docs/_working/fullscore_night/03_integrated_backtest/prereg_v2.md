---
ttl: task_bound
campaign: fullscore_night/03_integrated_backtest
exam: IBT-v2 HOLDOUT 二次复考（此卷最后一考）
created: 2026-10-01
session: st-fullscore-20260930
schema_version: 1.0.0
status: LOCK-PENDING
---

# IBT-v2 HOLDOUT 二次复考预注册（先锁箱后开卷）

> 本卡=IBT-v2 唯一判据真源。**锁箱时序=池指纹入附录 A 之前，禁止任何窗口发车（含 W_IS）**。
> 池=考卷内容：fresh_pool_v2.yaml 于本夜前置检查中确认全机缺失（证据=BLOCKED_v2_pool_missing.md），
> 故本卡以 LOCK-PENDING 形态先行冻结"非池参数+合格线+签署"——池到位后**只准填写附录 A 指纹，
> 不得触碰 §1/§2/§3 任何已冻结条目**。缺失证据=blocked_v2_pool_missing.md（同目录）。

## §0 锁箱状态

- [x] 附录 A 池指纹（fresh_pool_v2.yaml sha256 + 员数核对=14）——已填=锁箱
- [x] 工具面指纹（runner/成本模块/引擎/标定表，见附录 A 已锁段）
- [x] regime 档判定依据（附录 C 独立复验，本夜完成）
- [x] 发车前 ART_ROOT 重定向披露（附录 B-3，一行 diff + A/B 零漂移实证 + v1 复现性披露）

## §1 冻结配置清单

| 项 | 冻结值 | 真源 |
|---|---|---|
| 池 | **LOCK-PENDING**：格式=ibt_runner `--pool-file` v1.1（`members: {sid: 翻译件文件名}` + `note`），员数=14（简报口径，入箱时核对） | 附录 A |
| 成本决定档 | CalibratedSlippage（`ZEPHYR_C4_COST_MODEL=calibrated`）：滑点腿=标定分层表 SLIPPAGE_TIER_BPS=(7.24,5.69,4.67,4.00,2.34)按 ADV 五分位，佣金 2.5bp 双边+印花 10bp 卖腿不动 | scripts/backtest/cost_model.py（daebf3bed4c0fdd6）+ cost_model_calibration.py（29e9f8e6e17e58c1） |
| 成本对照档 | LegacyFlat（`legacy`/缺席→引擎 verbatim 零漂移路径）；仅连续性披露，不进判据 | 同上 |
| 窗口 | W_IS=2019-04-01..2023-12-31；W_OOS=2024-01-01..2025-09-08；W_HOLDOUT=2025-09-09..2026-09-08；W_POSTD=2026-09-09..2026-09-18（FACT 族 IS 生效起点=2021-04-01） | ibt_runner WINDOWS 冻结常量（5dac62676982d8e3） |
| regime 档 | **关闭**（`--variants A`，禁 `--enable-regime-throttle`）；依据=裁定 R3（r4/r10/r1 方向语义退役，ruling_registry 2026-09-17 重校批）+附录 C 本夜独立 OOS 复验不过 | 附录 C |
| 组合 | 等权 α=1/N（N=池员数），compose_weight_panels，INITIAL_CAPITAL=1,000,000 | runner 冻结常量 |
| 引擎参数 | execution_lag_days=1，allow_same_bar_execution=False，enable_pit_universe_filter=True，exclude_st=True，min_listing_age_days=120，max_participation_rate=0.10，impact_cost_enabled=True，sanity_guard=True | runner run_engine 冻结面 |
| 随机性 | 无随机源（引擎全确定性；同输入逐位可复现），无种子需登记 | 引擎实现 |
| 敏感性 | 仅 W_IS/W_OOS：滑点五档 0/5/10/20/40bp + 零成本对照（runner 冻结格点，禁改） | runner run_sensitivity |
| 产物落点 | docs/_working/integrated_backtest/artifacts_v2/<WINDOW>/（v1 artifacts/ 目录=只读对照物，禁覆写） | 附录 B-3 |
| 发车序 | W_IS → W_OOS(+`--sensitivity`) → 三窗产物核对（完整性门预检）→ **W_HOLDOUT（`--holdout-guard` 单次）** → W_POSTD（披露窗可选） | 纪律流程 |

## §2 合格线（跑前锁定，禁跑中改动）

1. **HOLDOUT 主判**（对 IBT-A 净值曲线，成本=决定档 CalibratedSlippage）：
   - 净夏普 ≥ **0.5**
   - 年化换手 ≤ **10x**（换手定义=双边成交额合计 ÷2 ÷ 窗口平均净值，按窗长年化，244 交易日/年）
   - 最大回撤 ≤ **20%**
2. **IS/OOS 完整性门**：四窗产物齐（run_summary.yaml + nav_IBT-A.csv + trades_IBT-A.csv + composed_panel.pkl 各窗在盘）且无 lookahead 红旗（面板 ≤t 信息+T+1 执行引擎不变量 + ibt_redblue PIT 审计口径抽查 W_OOS）。
3. v1 对照（IBT-RUN-REPORT 四窗数字）仅作漂移披露，不进判据。
4. 判定顺序：完整性门先判（FAIL=考试无效，如实记档）；主判三条同时过=PASS，任一不过=FAIL。
5. **FAIL 就 FAIL，如实落 v2_verdict.md；禁止回头改参数重跑**（唯一例外=基础设施崩，可重跑一次并留痕 errata）。

## §3 签署

**此卷最后一考：跑完不改参数不复考。** 本卡冻结后禁改（改卡=作废重开，禁套旧成绩）；
W_HOLDOUT 仅有一次 `--holdout-guard` 单次烧毁机会，烧毁即落证书（v2_verdict.md §烧毁证书）。

- 签署人：st-fullscore-20260930 夜战代理（Owner 授权的纪律执行人）
- 签署时刻：2026-10-01（夜窗，pre-flight）
- 授权来源：Owner HOLDOUT 二次复考开工令（三纪律：先锁箱后开卷／合格线预注册／此卷最后一考）

## 附录 A 锁箱指纹

**池指纹（已填写=锁箱。池=被盗复原件，复原对账=同目录 fresh_pool_v2_notes.md）：**

```
fresh_pool_v2.yaml sha256: 38ee5ada3834e99279f76eb2ec2c455aa28af94ca611b0fb84668ccdbafd47cd
员数（应为 14）: 14（留任 8 + 新进 6；CH bothwin 台账 tested=85/passed=14 逐一相符，零出入）
FACT 族员数: 6（简报口径=6，相符——含 FACT-4db4c41e，其 #322 旧窗死刑 vs #326 全量重考的出处张力如实披露于 notes §4，不替判据做主）
锁箱时刻: 2026-10-01 10:2x（本行填写即锁箱；此前零窗口发车，W_HOLDOUT 零消耗）
```

**已锁工具面指纹（2026-10-01 实测 sha256[:16]）：**

```
scripts/backtest/ibt/ibt_runner.py                = 5dac62676982d8e3
scripts/backtest/cost_model.py                    = daebf3bed4c0fdd6
scripts/backtest/translated/_c4_engine.py         = 362137bdb178f798
src/zephyr/backtest/core/cost_model_calibration.py= 29e9f8e6e17e58c1
窗口边界真源=ibt_runner.WINDOWS 冻结常量（本卡 §1 逐字引用）
v1 对照物=docs/_working/integrated_backtest/artifacts/（四窗产物+IBT-RUN-LOGS.md，只读）
```

## 附录 B 待办接线（池到位后冻结，不改 §1/§2）

1. **成本档→组合引擎接线（已冻结=引擎原生逐笔标定面，B-1②达成态）**：
   实测组合引擎（DefaultBacktestEngine）`BacktestConfig.slippage_bps=None`（默认）即走
   `cost_model_calibration.resolve_slippage_bps` 逐笔 ADV 五分位标定（SLIPPAGE_TIERING_ENABLED=True
   默认开，分档表与 §1 决定档逐字一致；无流动性信息落 3.79bp 实证加权档）——
   **IBT-D01 口径统一已在引擎原生面达成，v2 组合曲线成本=决定档无需任何新接线**。
   池级代表滑点标量钉定（B-1①）**不采用**：钉平口径会把逐笔标定降级为一口价，属放松。
   对照档（LegacyFlat 1bp）仅连续性披露用，A/B 取证位点=`SLIPPAGE_TIERING_ENABLED`（调用期读），
   v2 判据跑批不启用。成员考尺面（`_c4_engine._net_line`+cost_model 三档）维持 §1 冻结口径不变。
2. **数据前置（已核，2026-10-01）**：disk D: 剩 31G（≥20G ✓）/CH 可达（strategy_screen+
   regime+kline_index 只读实测 ✓）/`data/runtime/process_reaper_keep.txt` 已含 `ibt_runner`（:120 ✓，
   reaper scanned=31 killed=0 存活 ✓）。
3. **ART_ROOT 重定向（一行 diff 已落）+ 回归对照（R-022，实测两条，如实披露）**：
   diff=`ibt_runner.py` ART_ROOT 值 `artifacts`→`artifacts_v2`（单行，产物落点改向，零计算面触碰）。
   - **重定向零漂移实证（A/B 同构双跑）**：同代码同数据同参数、仅产物目录不同的两次 v1 池
     W_OOS 重放 core+members 逐位相等（对照产物=artifacts_v2/_regression/ 下 ab_neutral_root vs
     artifacts_v2/W_OOS）→ 产物落点对数值无影响，实证成立。
   - **v1 复现性披露（不进判据）**：HEAD 代码+数据重放 v1 池 W_OOS **不能**逐位复现 v1 产物
     （legacy 1bp 口径重放亦 61 处数值漂移；标定档重放方向性一致）。根因=v1 跑后 9 天内
     成本标定落地（预注册决定档，方向性解释净值/回撤漂移）+数据面持续刷新（复权因子/行情）+
     引擎面演进。§2.3 已预注册"v1 对照仅漂移披露"——本发现即该披露的实证内容，v2=新考卷新跑，
     判据全部落在 v2 自身产物上。

## 附录 C regime 独立 OOS 复验（2026-10-01 本夜，只读 CH，只用已见段 ≤2025-09-08）

数据=VAL-P0-20260916-230726 dominant × 000300 fwd20（与裁定诊断同尺）；HOLDOUT 段（≥2025-09-09，
247 行）未读入任何统计。

| 态 | IS mean_fwd20 | OOS mean_fwd20 | 符号一致 | 备注 |
|---|---|---|---|---|
| r1 | -2.20% (n=319) | +3.69% (n=152) | ✗ | 反转（裁定 R3 已退役） |
| r2 | -0.74% (n=207) | +0.46% (n=69) | ✗ | 反转 |
| r3 | +1.33% (n=329) | **-0.79% (n=99)** | ✗ | **攻击槽独立复验不过**：pre924=-1.63%(n=39)/post924=-0.24%(n=60) 两段皆负 |
| r4 | +0.01% (n=207) | -1.64% (n=5) | ✗ | OOS 样本不足，节流语义无据 |
| r10 | +1.83% (n=93) | **+1.96% (n=60)** | ✓(同为正) | **节流=反弹卖压实证**（win=76.7%），0.2 节流系数方向性错误，退役语义证实 |

**结论：节流启用判据不过 → IBT-v2 跑 regime 关闭档（`--variants A`），预注册 §1 已冻结。**
与裁定"924 后 r3 OOS 优势含结构行情红利，上线前须独立 OOS 复验"的保留意见一致：复验不过，维持脱钩。
