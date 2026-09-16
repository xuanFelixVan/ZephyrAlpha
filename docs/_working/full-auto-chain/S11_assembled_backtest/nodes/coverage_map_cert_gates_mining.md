---
ttl: task_bound
title: T1-α 覆盖地图 + 认证/衰减闸门批挖（S11 决策链上游）
session: st-qoder-t1a-20260915
date: 2026-09-16
parent: S11_assembled_backtest
---

# 挖矿节点 7：覆盖地图（首张）+ 认证/衰减闸门批挖

> 挖矿日期：2026-09-16 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 本节点做三件事：① 给 S11 挖矿 campaign 补上第一张**世界地图**（哪些模块从未被挖过，
> 数字可复算）；② 按"钱路/风险路优先"批挖 5 个未挖节点（衰减认证器 / DSR 三实现 /
> 晋升建议器 / 生命周期 FSM / C4 跑批）；③ 用核验清偿 wyckoff_vix_mining §4/§6 两个尾。
> 产出=数据。采纳与施工裁定归主力会话（宪法 §9.11）。

---

## 1 现状盘点

### 1.1 覆盖地图：区域定义与口径（可复算，脚本见 §1.5）

**区域** = `src/zephyr/{backtest,regime,strategy_pipeline}` 递归全部非 `__init__` 模块
（整装回测决策链本体；`signal_ashare`/`simulation` 不在 94 之内，但钱路延伸处按
"钱路优先"一并挖，见 §2）。

| 桶 | 判据 | 数量 |
|---|---|---|
| **已挖（MINED）** | 模块名以 `<stem>.py` 文件锚点出现在 15 份节点报告任一正文中，**或**其 stem 出现在报告标题行（`#`~`######`） | **26** |
| **未挖（UNMINED）** | 其余 | **68** |
| ├ 顺带提及 | 正文里出现过 stem（作为依赖/上游/对照），但从未作为**被挖节点** | 10 |
| └ 零提及 | 15 份报告中从未出现 | **58** |

**核心数字：区域 94 个模块，已挖 26（27.7%），未挖 68（72.3%）；其中硬零覆盖 58（61.7%）。**

> 诚实注记：本次压缩前口头报过 "69/25"。以 §1.5 脚本重算为 **68/26**——差 1 个模块
> （`cost_attribution`/`cpcv` 一系的锚点判定边界）。以本文件数字为准。
> 另：任务书给的 charter 路径 `docs/_working/full-auto-chain/kimi_deep_mining_charter.md`
> 与 `deep_review_policy.md` 路径均与实际不符（政策件真身在
> `docs/01_policies_and_standards/sop/review_sop/deep_review_policy.md`），已按"提示词里的
> 断言也要验"处理——这本身即本仓病灶的一次现场复现。

### 1.2 本批挖到的 5 个节点（均原在 68 未挖名册内）

| 节点 | 真身 | 是否在生产链上 |
|---|---|---|
| `strategy_decay_certifier.py`（signal_ashare，区域外钱路） | 衰减侧三态判定+退役/复活台账 | **是**（`internal_compute_provider.py:791`） |
| `deflated_sharpe_calculator.py`（simulation，区域外钱路） | DSR 唯一 SSOT 计算件 | **是**（C4 批测全委托它） |
| `overfitting_adjudicator.py`（backtest/core） | 第二套 DSR 实现，682 行 | **否——零消费者** |
| `promotion_advisory.py` + `lifecycle_fsm.py`（strategy_pipeline） | Owner 批准→FSM 流转 | **是**（晋升终态通道） |
| `c4_deflated_sharpe_runner.py`（backtest/regime_validation） | DSR 编排壳 | **是**（纯委托） |

### 1.3 衰减认证器：判定逻辑与真数据分布

`strategy_decay_certifier.py` 判定序（L105-132）：

```
prev = history.get(sid) or {"state":"certified","failed_streak":0}      # L105 首见即豁免
if ds is None:                state = "probation"                       # L119-120
elif float(ds) < 0:           state = "failed"                          # L121-122 ← 不可达
elif float(ds) < _CERTIFIED_DS(0.5): state = "probation"                # L123-124
else:                         state = "certified"                       # L125-126
if prev["failed_streak"] >= FAILED_WINDOWS(8) and state == "failed":
                              state = "retired"                         # L131-132 ← 死链
```

真源读数（只读 ClickHouse，`role="reader"`；`c1_backtest.strategy_screen`，MergeTree，
`ORDER BY (screen_batch, strategy_id)`，含 `num_trials` 列）：

- 全表 **1203 行**，`deflated_sharpe` 非空 **269 行**，**负值 0 行**，全表最大 **0.1448**。
- 每策略最新行口径（复刻 `load_latest_metrics`）：**574 个策略，其中 83 个有 DS**，
  负值 0，≥0.5 **0** 个，最大 0.122。
- 批次分布：`C2-intake-2026-09-12` 597 行 DS 全 NULL；`SIM-DEV-2026-08` 12 行全 NULL；
  有 DS 的批次最大 0.1448（`C4-OOS-2024-2026`）。
- 生产台账 `data/runtime/strategy_decay_ledger.json`（未入 git，mtime 2026-09-15 05:32:39）：
  565 策略，**probation 561 / certified 4 / failed 0 / retired 0 / resurrected 0**，
  `failed_streak` 全体为 0（565 个 0）。

结论：`failed` 分支在真实定义域内不可达（DSR 是 Φ(·) 的值，域 = [0,1]，负值不存在），
连带 `retired`（L131-132 要求 `state == "failed"`）与 8 周连计数全部死码。

### 1.4 DSR 三实现横向对照（T3 同族全查）

同一仓内三处计算 DSR：`deflated_sharpe_calculator.py`（活，SSOT）、
`overfitting_adjudicator.py`（死，682 行）、`c4_deflated_sharpe_runner.py`（壳，纯委托 L23/L121-127）。

V[SR] 峰度项口径**互不相同**：

- canonical L216：`(kurtosis - 1.0)/4.0`，而入参 `kappa = _kurtosis(returns)`
  在 L172 返回 `m4/(m2**2) - 3.0`（**超额**峰度，正态=0）。
- adjudicator L270-272：`kurt_pearson = float(kurtosis) + 3.0` 后同式（**Pearson** 峰度，正态=3）。

论文/Lo(2002) 口径要求 Pearson（iid 正态须回落到 `V=(1+SR²/2)/(T-1)`）。iid 边界实测：
SR=1、T=250、γ=0、κ_超额=0 → canonical `V=0.00301205`，理论 `0.00602410`，**比值恰 0.5000**
（系数取成 `−1/4` 而非 `+1/2`）。共享锚点复算（SR=0.1, T=101, N=1，即
`tests/backtest/test_overfitting_adjudicator.py:145-151` 手算钉死的 0.01005 / 0.84074）：
canonical 给 `V=0.00997500 / DSR=0.841648`，**恒偏高**。

随机电池量化（6 seed × 6 组 (T,μ,σ) × N∈{10,50,600,4497} = **1440 例**，进程内复算）：
`max|ΔDSR| = 0.0818`；跨过 0.95 放行线的**假显著翻转 3 例（0.2%）**。
真实 C4 数据 SR≈0.14 处 Δ 较小（V 相对差 1.5%），但方向**恒为反保守**。

### 1.5 覆盖地图复算脚本（唯源，改口径=改本段）

```python
# python - <<'EOF'  （只读，无副作用）
import pathlib, re
region=[f for p in ("backtest","regime","strategy_pipeline")
        for f in sorted(pathlib.Path("src/zephyr",p).rglob("*.py")) if f.name!="__init__.py"]
R=sorted(pathlib.Path("docs/_working/full-auto-chain/S11_assembled_backtest/nodes").glob("*.md"))
L=[(r.name,ln) for r in R for ln in r.read_text(encoding="utf-8",errors="replace").splitlines()]
BODY="\n".join(l for _,l in L).lower(); HEAD="\n".join(l.lower() for _,l in L if re.match(r"^#{1,6} ",l))
wb=lambda s,t: re.search(r"(?<![a-z0-9_])"+re.escape(s)+r"(?![a-z0-9_])",t) is not None
mined=[f for f in region if f.stem.lower()+".py" in BODY or wb(f.stem.lower(),HEAD)]
inc  =[f for f in region if f not in mined and wb(f.stem.lower(),BODY)]
zero =[f for f in region if f not in mined and f not in inc]
print(len(region),len(mined),len(inc),len(zero))   # 94 26 10 58
```

---

## 2 六向挖矿日志表

| 向 | 查了什么 | 结论 |
|---|---|---|
| 上游 | `strategy_screen.deflated_sharpe` 生产路径：`c4_batch_screen.py:135-155` → `_c4_engine.batch_deflated_sharpe:316-348` → `c4_deflated_sharpe_runner` → canonical；N 口径=累计账本+本批 | **已查无（并发现健康件，§7）**；另发现生产表被 `UPDATE deflated_sharpe=…` 变异回填（见 SDC-2） |
| 下游 | 台账消费方：`git grep -nF "strategy_decay_ledger"` → 仅模块自身 L53 定义+自读；`git grep -n "run_strategy_decay_certify"` → 仅 provider L781/L791 + 测试 | **有矿**：判定产物无外部消费者（SDC-1 第二半） |
| 算法 | DSR 定义域（Φ 值域 [0,1]）、V[SR] 峰度口径、E[max] 两种近似（Acklam vs Euler–Maclaurin）、退化方差分支 | **有矿**：SDC-1 / SDC-3 / SDC-4 |
| 后端 | 落库列名与语义（`num_trials` 注释自证 NULL=历史批）、表引擎非 Replacing（L69 注）、`system.mutations` 台账 | **有矿**：SDC-2 台账与真源分叉；latest 选取依赖未定义平序（SDC-5） |
| 前端 | `git grep -nF "strategy_decay"` 于 `src/zephyr/frontend`、`scripts`、`config` | **已查无**（无任何展示/接线；与 SDC-1 同根） |
| 数据字段 | `deflated_sharpe`/`is_sharpe`/`oos_years_decay`/`verdict`/`num_trials` 逐列读注释+计数 | **有矿**：`certified` 门槛 0.5 vs 全表最大 0.1448（口径悬空，见 SDC-6） |

搜索受阻登记（宪章：受阻≠查无）：轴 F 外部文献二次 `WebFetch` 均 `fetch failed`，
`arxiv` 原文未取回。**故本节点 DSR 结论一律建立在内部互斥（两实现口径不可能同时对）
+ iid 边界复算 + 1440 例内部电池之上，不引外部权威句。**

---

## 3 缺陷清单（按后果定级）

### SDC-1 ｜P0｜衰减侧退役闭环两端皆断（不可达分支 + 零消费者）

- **缺陷**：`src/zephyr/signal_ashare/strategy_signal/strategy_decay_certifier.py:121-122`
  以 `deflated_sharpe < 0` 作 `failed` 判据；DSR 为 Φ(·) 值，域 [0,1]，真源 1203 行负值 0。
  ⇒ `failed` 恒不成立 ⇒ L131-132 `retired` 恒不成立 ⇒ L106-118 复活闸永不触发。
  第二半：`_DEFAULT_LEDGER`（L53）产出的台账 JSON 全仓零读者
  （`git grep -nF "strategy_decay_ledger"` 只命中定义处），而头 L5 `[CONSUMERS]` 声称
  "策略域会话（退役建议台账消费方）"——**代码里不存在该消费方**。
- **如何证明**：只读 CH 查询（§1.3 三项计数）+ 生产台账状态计数（561/4/0/0/0，
  `failed_streak` 全 0）+ 两条 `git grep -F` 零命中图。判据分支不可达属静态可判定。
- **后果定级**：衰减闸门名义在跑、每周写台账、`[MATURITY] design` 自陈，但**结构上不可能
  产出任何退役信号**——静默错账+闸门失效，且失败模式不可见（counts 里没有 failed 键时
  无人报错）⇒ P0。
- **健康对照**：`ds is None → probation`（L119-120）方向正确（判不了即封顶，非放行）；
  台账写入走 `safe_write_text` CAS（L137）；`[INVARIANTS]` 显式声明"状态翻转归策略域
  管线"边界，不越权。
- **测试侧共谋**：`tests/signal_ashare/strategy_signal/test_strategy_decay_certifier.py:31`
  以 `("STR-C", -0.2, 0.8, 0.3)  # failed` 作夹具——用**定义域外输入**把死分支"跑绿"，
  故 3 个既有用例（实测通过）对真数据零鉴别力；L21-26 `_FakeClient` 自带 last-wins 去重，
  真实 `load_latest_metrics`（L67-81，其"表非 Replacing、去重在内存做"注记在 L70）从未被同一测试路径覆盖。

### SDC-2 ｜P1｜认证台账与真源已分叉，且无任何新鲜度校验

- **缺陷**：台账把 `CAND-5301c5d9d7c8 / 65ae80c577c9 / dc5b80aa3614 / e3da6fa71af1` 标为
  `certified`，`ds` 记 0.5705 / 0.6696 / 0.8879 / 0.5309；同一策略在真源表的现值为
  0.0037 / 0.0006 / 0.0506 / 0.0793（全部远低于 0.5 线）。`system.mutations` 显示
  2026-09-15 **05:46:42** 有一批 `UPDATE deflated_sharpe = …` 回填，而台账 mtime 为
  **05:32:39**（早 14 分钟）⇒ DSR 口径被就地改写后，判定产物未重算，且无任何机制发现此事。
- **如何证明**：只读 CH（按 strategy_id 拉 18 行 + 按批次聚合 max/非空数）+
  `system.mutations` 命令文本与时间戳 + `stat` 台账 mtime + 台账 JSON 解析计数。
- **后果**：唯一"通过认证"的 4 条记录全部失效但显示为 `certified`。当前因 SDC-1 的
  零消费者而无资金后果——**一旦接线消费（该补的债），这 4 条会直接成为放行依据**，
  属定时炸弹型静默错账 ⇒ P1（若台账被消费即升 P0）。
- **健康对照**：回填本身留了 `num_trials` 列与"NULL=2026-09-15 前历史批"的自证注释；
  2026-09-16 05:52 的 `DELETE` 变异说明旧批在被清理，非无人看管。

### SDC-3 ｜P1（口径不一致，触发即 P0）｜DSR V[SR] 峰度项口径错误：超额峰度进 Pearson 公式

- **缺陷**：`src/zephyr/simulation/deflated_sharpe_calculator.py:172` 产出**超额**峰度，
  L216 却用 `(κ-1)/4`（要求 **Pearson**）。⇒ iid 正态下 SR² 系数取 `−1/4` 而非 `+1/2`，
  方差被低估（实测比值恰 0.5），DSR 恒偏高；同文件 L207 docstring 还自陈"kurtosis: 超额峰度"，
  即错误在契约上被固化。同族 `overfitting_adjudicator.py:270-272` 用 `+3.0` 修正，**同仓两实现
  数学互斥，必有一错**；错的是在跑的那个。
- **如何证明**：进程内复算（§1.4）——边界法：iid 正态须回落到 Lo(2002) `V=(1+SR²/2)/(T−1)`，
  canonical 给一半；锚点法：`tests/backtest/test_overfitting_adjudicator.py:145-151` 手算钉的
  0.01005/0.84074，canonical 同输入给 0.00997500/0.841648；电池法：1440 例 `max|Δ|=0.0818`、
  3 例跨 0.95 假显著。
- **后果**：C4 唯一的"多重比较折减"闸门系统性偏弱（方向恒反保守），随 SR²/T 增长；
  现网 SR 低（≤0.1448）故尚未误放，**但闸门设计目的正是拦高 SR**——恰在最需要它时最弱 ⇒ P1，
  任一批次 DSR 逼近 0.95 即 P0。
- **测试侧**：canonical 唯一相关用例
  `tests/simulation/test_deflated_sharpe_calculator.py:244-249` 只钉 `SR=0` 一点
  （V=1/99），**SR² 项系数（病灶本身）永不被断言**；其余仅 `0.0 < dsr < 1.0` 区间型弱断言
  （L54/L76/L151/L171）。反观死件却有独立 NormalDist 预言机对拍（L154-170）⇒ 轴 A.3 复现。
- **健康对照**：`_expected_max_sharpe` 有已知值锚点（L116-124 用例）；N 越大 DSR 单调下降
  被显式测试（L100-107）。

### SDC-4 ｜P1｜退化方差 fail-open：DSR 直接饱和到"最显著"

- **缺陷**：`deflated_sharpe_calculator.py:305-307` `if var_sr <= 0: dsr = 1.0 if sr > 0 else 0.5`
  ——方差非正（估计失效/病态序列）时给**最大显著性**；`overfitting_adjudicator.py:275-277`
  同形（`1.0 if sr > 0.0 else 0.0`）。
- **如何证明**：进程内构造即得——锯齿交替序列（`base±amp`，超额峰度 = **−2.000**，理论下界）
  使 `var_sr = −7.98e−3 ~ −4.40e−2 < 0` ⇒ `dsr = 1.0000`、`is_significant = True`、
  N=4497（年化 SR 31.7/63.4/47.5）。序列形态（±等幅摆动、极低方差）在 A股 T+1 小持仓策略
  日频净值里是**可出现的病态产物**，非纯数学玩具。已由本节点新测试固化。
- **后果**：一旦有策略产出量化/锯齿型日收益，C4 直接判"以 4497 次试验的折减口径仍极显著"，
  且下游 `probation`/`certified` 全部按真 DSR 处理 ⇒ 假策略晋级的单点通道 ⇒ P1（资金路径，
  实际触发即 P0）。
- **健康对照**：`_c4_engine.py:336-346` 官方件抛 `C4DeflatedSharpeError` 时**不静默**——留
  warning 并把整批置 None（注释点名"2026-09-13 OOS 批全 None 教训"），置 None 后认证器走
  `probation` 封顶，方向正确。
- **测试侧**：`tests/backtest/test_overfitting_adjudicator.py:198-201`
  `assert verdict.dsr in (0.0, 1.0)` ——把两种**相反**的后果同时算"通过"，等于没判
  （test-as-co-conspirator 第二例）。

### PA-1 ｜P1｜晋升终态路径自签 SIM 预授权卡（三条件全 True 硬编码）

- **缺陷**：`src/zephyr/strategy_pipeline/promotion_advisory.py:423-427`
  `fsm = build_strategy_fsm(sid)` 后 `if fsm.current_state == "candidate":`
  即 `fsm.transition(SIM, {"sim_promotion": SimPromotionContext(
  dual_window_pass=True, bh_fdr_pass=True, no_pending_decay_alert=True)})`。
  而 `lifecycle_fsm.py:112`（`build_strategy_fsm`，`initial=CANDIDATE` 见 L132）每次新建、
  无持久态读取 ⇒ **该分支恒被走**，`SimPromotionGuard`（AND 三旗，L78-84）被一张
  自签全 True 卡通过。注释"三条件已在其入册时预授权（intake 先例）"仅半真：
  `intake.py:165-169` 确实用实测 `dual/fdr/no_decay` 构造上下文，但**没有任何代码校验
  本策略当初是否满足**；且字段名 `no_pending_decay_alert`（L72 注"decay_watch 无未决
  decaying 行"）在本路径上从不查 `decay_watch`（`git grep` 显示 decay_watch 只被
  `scripts/backtest/*` 消费，FSM 侧零接线）。
- **如何证明**：读码 + `git grep -n "SimPromotionContext\|no_pending_decay_alert"` 全命中图
  （仅 intake 计算真值、promotion_advisory 硬编码、fsm 消费）+ `build_strategy_fsm` 无
  持久态读取的静态结构。
- **后果**：预授权门在终态通道上退化为橡皮图章（纸面证据卡）。Owner 人类回路本身
  **未被绕过**（`sim→production` 仍需合法 `owner_token`，`OwnerTokenGuard` fail-closed），
  故不升 P0；但台账/审计里"三条件已过"为虚假记录 ⇒ P1。
- **健康对照**：L432 `fsm.transition` 非法转换/Owner 门拒绝原样上抛（不吞）；L411-414
  注册表 lifecycle 白名单 `_OBSERVING_LIFECYCLES=("sim","paper")`（L76）先行把关；
  `lifecycle_fsm.py:79-80` guard 缺 context 即 False、`OwnerTokenGuard.check`
  （L97-109）无 token/无 secret 即 False。

### OV-1 ｜P1｜682 行 `[MATURITY] production` 判定器零消费者（产而不消 + 契约三处互斥）

- **缺陷**：`src/zephyr/backtest/core/overfitting_adjudicator.py`（682 行，MOD-BT-001 系）
  `git grep -n "overfitting_adjudicator" -- src scripts` **除自身与自身测试外零命中**。
  三处自陈互斥：文件头 L7 `[MATURITY] production`、L5 `[CONSUMERS] 上线评审流程
  (挂钩点预留, 未接真门禁)`（自相矛盾：production 却"未接真门禁"）、
  `capability_canonical_file_registry.yaml:10736-10739` 与
  `architecture_issue_registry.yaml:19685` 记为 **testing**。
- **如何证明**：零命中调用图（`git grep -F`）+ 三处登记文本对照。
- **后果**：其一，真正的 DSR 正确实现（Pearson 口径 + 独立预言机测试）**没有被任何生产路径
  使用**，生产用的是 SDC-3 的错误口径——死件里睡着对的那份；其二，`production` 标签污染
  成熟度台账与死码审计（红蓝①同族）⇒ P1。
- **健康对照**：该件错误码 `ZA-BT-0036`、33 单测、入参校验（`test_invalid_inputs_raise`
  覆盖 NaN/N=0/T=1）完整度高于在跑的 canonical。

### HDR-1 / HDR-2 ｜P2｜契约头与真源漂移（两处，方向相反）

- `c4_deflated_sharpe_runner.py:7` `[MATURITY] design`、L8 `[INVARIANTS] …离线跑批,不触发真实回测`、
  L5 `[CONSUMERS] 人工审查`——**实际**在 `scripts/backtest/c4_batch_screen.py:145` 的批产路径上被
  调，且是全仓 DSR 的 SSOT 编排点。头把活件说成设计件。
- `c1_runner.py:5` `[CONSUMERS] … ; scripts/regime/run_c1.py`——`scripts/regime/` **目录不存在**
  （真身在 `scripts/tests/repro_c1.py` 等）。虚构消费者名册。
- 另 `strategy_decay_certifier.py:8` 声明只读
  `c1_backtest.backtest_strategy_screen`，代码 L52 `_DEFAULT_TABLE = "c1_backtest.strategy_screen"`，
  且 **CH 里不存在 `backtest_strategy_screen`**（表名册实测）→ 头错代码对。
- 后果：以头为真源做治理/审计的一切推论失真；排障误导 ⇒ P2。

### SDC-5 ｜P2｜"每策略最新行"选取依赖未定义平序

- `load_latest_metrics` L69-81：`ORDER BY screen_batch, strategy_id` + Python 无条件 last-wins。
  表 ORDER BY 键为 `(screen_batch, strategy_id)` 且**非 Replacing**（L69 注自证），
  同键多 `run_id` 行并存（实测 `CAND-5301c5d9d7c8` 在 `C4-translated-20260912` 有 NULL 与
  0.0037 两行），ClickHouse 对重复键返回序**不保证**⇒ 与头 L12 `[INVARIANTS] 同输入必同输出`
  相冲。现网实测良性：`ORDER BY …, run_id` 平序显式化后 574 策略中值变化数 **0**，
  非空计数仍 83（与"至少有一行非空 DS 的策略数"83 全等 ⇒ **无 NULL 遮蔽**，
  该假设已验并排除，不当矿报）。⇒ P2（可靠性/可重现性）。

### SDC-6 ｜P2｜`certified` 线 0.5 与本真源的标度悬空

- `_CERTIFIED_DS=0.5`（L51）配全表 max 0.1448 / 最新口径 max 0.122 ⇒ 对**当前策略群体**
  经验上不可达（数学上可达：台账留有历史 0.8879）。0.5 线在 DSR∈[0,1] 上是
  "置信度 50%"，与 `DSR_SIGNIFICANCE_THRESHOLD=0.95`（`deflated_sharpe_calculator.py:52`）
  所服务的放行口径**不同数**：两处阈值无任何文档说明为何衰减侧取 0.5、晋升侧取 0.95
  ⇒ 阈值来源未预注册 ⇒ P2（口径一致性；改动属裁定，本节点只登记）。

---

## 4 正面清单（查过且健康，写给后续矿工当前提）

1. **N 账本接线是全仓纪律标杆**：`scripts/backtest/c4_batch_screen.py:135-155` 注释直书
   "N 口径（2026-09-15 裁定）：折减分母=全局累计可审计试验数（真源=N 账本 MOD-BT-200）+ 本批
   变体数；账本缺失/读数失败 **fail-closed**（拒猜测）"，代码即 `TrialLedger().cumulative_trials()`
   + `n_used = n_cum + len(nets_main)`，无 `nets_main` 时 `n_used=None` 而不猜数。
2. **官方件委托链干净**：`_c4_engine.batch_deflated_sharpe`（L316-348）不自算 DSR，全委托
   `c4_deflated_sharpe_runner`，并显式喂**日频净值序列**（L306-312 扣佣金/印花税/滑点后
   的 `net`），入口过滤 `<3 点 / 非有限 / std=0`（L327-329）。
3. **FSM 侧 fail-closed 到位**：`SimPromotionGuard.check` 缺 context 即 False（L79-80）；
   `OwnerTokenGuard`（类 L87）为 hmac/sha256 比较（L107-109），非"非空即真"。
4. **认证器不越权**：判定只产建议台账，状态翻转显式交回策略域（L132 注 + L8 不变式）；
   写盘走 `safe_write_text` CAS。
5. **§9.6 卫生**：三个消费方测试（`test_strategy_decay_certifier.py:35`、
   `tests/factor/test_red_blue_lifecycle.py:90,102`）全部 `tmp_path` 注入 fake client；
   生产台账文件未被 git 跟踪。
6. **本节点 5 个只读复算脚本零写入**，ClickHouse 全程 `role="reader"`。

---

## 5 子节点清单（挖出的新矿脉，交主力会话排批）

1. **regime/validation 15 件批**（全在 58 硬零名册内：a3/a4/b2/b3/b4/d1/d3/e1 + phase2 六件 +
   `overfitting_guard` + `wyckoff_walkforward`）：概率校准/Brier-CRPS/转移覆盖这一整族验证件
   从未被挖，且与 SDC-3 的显著性口径同族——**建议下一节点，一次扫完。**
2. **backtest/services 9 件批**（`decay_monitor`/`layered_validation_pipeline`/
   `result_comparator`/`data_quality_checker`/`anomaly_diagnoser`/`param_analyzer`/
   `report_generator`/`cache_manager`/`scheduler`）：`decay_monitor` 与 SDC-1 疑似功能重叠
   （两处衰减判定，一人在跑一人零消费？）——**同族横向排查（deep_review_policy T3）优先。**
3. **DSR 三合一裁定件**：SDC-3/SDC-4/OV-1 应并成一个裁定（口径统一 + fail-closed +
   死件处置三问一次答）。
4. **`anchored_state_machine` / `regime_state_anchored` 表**：本次表名巧合后仍在硬零名册，
   非误挖；与 `overlay_signals_builder` 锚定语义待验。
5. **台账新鲜度不变式**：任何"上游被回填"的表（`system.mutations` 有 UPDATE 史）下游产物
   应带 `source_version`/`as_of` 校验——SDC-2 的通用解法，属架构级欠账。

---

## 6 §4/§6 两尾清偿（Task C，按核验不按假设）

### SVX-1（"IV 路径零测试 → `_interp_vix_for_date` 插值/降级测试"）→ **已被车道 I2/S 清偿**

- 真身：`tests/regime/test_synthetic_vix_iv_path.py`，**实测 48 通过**（分文件单跑），
  组合跑（含 `test_wyckoff_engine.py`）**61 通过**；任务书 "~40 个" 为保守低报。
- 关键鉴别：`_interp_vix_for_date`（`synthetic_vix.py:57-81`，唯一消费者 L156
  `groupby("trade_date").apply(...)`）在 tests 里**无同名直调**
  （`git grep -nF "_interp_vix_for_date" -- tests` 零命中），但覆盖是真的：
  `TestInterpolationTo30Days`（L78-135，经公开入口 `compute_synthetic_vix` 打插值）
  用**手算真值**断言——`_interp_expected`（L73-75）+
  `test_two_leg_interp_matches_hand_computation` 同时钉住期望值自身（26.285714285714285，
  rel=1e-12）与输出；`test_dte_bucket_split_at_30_is_inclusive_for_near` 钉 L64 的 `<=30`
  边界；`TestSingleUnderlyingDegradation`（L136）/`TestNoInterpolableExpiry`（L292）
  钉 L70-75 降级与 L78-79 同 DTE 分支。
- **判定：已闭环（车道 I2 建网 47 例 → 提交 `38f616bf43`，车道 S 治本 → `23450e6315`）。
  建议原条目改标 "closed-by-I2/S"。** 残余非缺陷项（登记不升级）：L78-79 `t2 == t1`
  分支的覆盖经"同到期日"数据形态间接达成，未见点名用例；因入口路径断言为手算真值，
  该支改动仍会被现有网捕获。

### WYF-2（"零测试 → 6 阶段触发场景测试补齐"）→ **已被车道 F/WYF-1 清偿**

- 真身：`tests/regime/test_wyckoff_engine.py`，**实测 13 通过**。
- 六阶段逐一对号：`test_full_absorption_chain_all_six_stages_fire`（L150，整链六阶段齐发）+
  `test_ps_fires_on_down_day_above_prior_low`（L161）+ `test_sc_fires_on_normal_crash_day_
  low_below_close`（L174）+ `test_ar_fires_on_rebound_after_sc`（L190）+
  `test_st_and_spring_fire_only_after_ar_baseline_exists`（L200，ST 与 Spring 双阶段）+
  `test_test_sos_fires_on_volume_breakout_after_spring`（L223）= **PS/SC/AR/ST/Spring/Test-SOS
  六阶段全覆盖**，另有 cummax 计分（L257）、零结构零事件（L271）、PIT 前缀一致性（L284）、
  阈值钉死裁定 #264（L305）、三处**精确等号不触发**边界（L344/369/386）。
- **判定：已闭环（WYF-1 提交 `55903e7d4e` 即注明"6 阶段测试补齐（WYF-2）"，WYF-3 两批
  `9b417a8ba1`/`bcf9e48b43` 续钉阈值与边界）。建议改标 "closed-by-WYF-1/F"。**

### 本节点实际补的缺口

两尾既已闭环，本节点把力气用在**自己挖出的**定义域病灶上：
新建 `tests/signal_ashare/strategy_signal/test_strategy_decay_certifier_boundary.py`，
**实测 20 通过**（连同既有 3 例与 `test_red_blue_lifecycle.py` 9 例，合跑 **32 通过**，
ruff line-length 120 清洁）。要点：合法 DSR 域
（`None/1e−12/0.05/0.1448/0.5−ε/0.5/0.95/1.0`）循环 `FAILED_WINDOWS+2` 轮，机器钉死
"永不产出 failed/retired"（把 SDC-1 变成会响的测试，而非注释）；`_NoopClient`
一旦被触真读即抛（保证不触库、全走 `tmp_path`）；生产侧列不可发负值的证据测试；
以及 SDC-4 的锯齿序列退化方差 → `dsr == 1.0` 取证。

---

## 7 优先级裁定建议表（采纳权在主力会话）

| # | 级别 | 一句话 | 归属文件 | 阻塞方 | 建议动作 |
|---|---|---|---|---|---|
| SDC-1 | P0 | `ds<0` 不可达 → 退役闭环两端皆断（含台账零读者） | `strategy_decay_certifier.py:121-132` + L53 | 需"新判据"裁定 | 见 §9 提案 A/B |
| SDC-3 | P1→P0 | V[SR] 峰度口径错（iid 边界差 2×，方向恒反保守） | `deflated_sharpe_calculator.py:216` | 该件**已被 `st-btfix-p17-20260916` 占用**（不得抢锁） | 口径统一裁定 + 同族全查 |
| SDC-4 | P1→P0 | 退化方差 fail-open 至"最显著"（锯齿序列实测 dsr=1.0） | `deflated_sharpe_calculator.py:305-307`；`overfitting_adjudicator.py:275-277` | 同上锁 | §9 提案 C（无需新阈值） |
| SDC-2 | P1 | 台账 4 条 certified 与真源分叉，无新鲜度校验 | 台账/上游 | — | §9 提案 D |
| PA-1 | P1 | 终态通道自签 `SimPromotionContext(True,True,True)` | `promotion_advisory.py:423-427` | — | §9 提案 E |
| OV-1 | P1 | 682 行 production 件零消费者，且持正确口径 | `overfitting_adjudicator.py` | 在禁改名单之外，但涉死码处置裁定 | 并入 SDC-3 三合一 |
| HDR-1/2 | P2 | 三处契约头漂移（design 说成活件/虚构消费者/错表名） | `c4_deflated_sharpe_runner.py:5-8`、`c1_runner.py:5`、`strategy_decay_certifier.py:8` | 无 | 头改真（无需裁定） |
| SDC-5 | P2 | latest 选取依赖未定义平序（现网良性） | `strategy_decay_certifier.py:69-81` | 与 SDC-1 同件 | SQL 加 `run_id, ingest_ts` 平序键 |
| SDC-6 | P2 | 0.5 与 0.95 两条 DSR 阈值未预注册同族关系 | `strategy_decay_certifier.py:51` | 需 RULE-RULING | 只登记，未动 |

---

## 8 封矿判定

- **本批节点主体封矿**：5 节点六向均有明确结论（4 向"已查无+实证"，2 向产矿）；
  三条判据分支的可达性用真数据分布 + 定义域静态判定双重钉死；DSR 三实现横向对照闭合
  （互斥性可判定，不需外部权威背书）。
- **未枯竭、外溢为 §5 新脉**：`regime/validation` 15 件、`backtest/services` 9 件、
  DSR 三合一裁定、台账新鲜度不变式。
- **世界地图未枯竭，反而是本次最大产出**：94 中 68 未挖（硬零 58）——campaign 至今
  的覆盖是 **27.7%**。按"完备优先"，下一批应按 §5 批次扫，而非继续挑单点。
- 一句话结论：**这条链上最危险的错误不是算错，而是"判据落在定义域之外"——一个用负数当
  死刑的退役闸、一个把方差爆炸当最高荣誉的显著性闸、一张自签三 True 的预授权卡，
  三者共同点是把闸门写在纸面上、把放行留在默认里；而唯一正确的数学，睡在一个零消费者的
  682 行死件里。**

---

## 9 for main session（提案：证据 + 最小补丁；本会话未改动任何被挖文件）

> 未落地原因逐条如实：SDC-1 判据更换=阈值/谓词裁定（模块头自陈"改动=裁定"）；
> SDC-3/4 所在文件被 `st-btfix-p17-20260916` 持锁（规则：持锁者非本会话即不得抢）；
> PA-1/OV-1 涉契约与死码处置裁定。以下补丁均为最小面，可直接套用。

### 提案 A（SDC-1，钱路首选；二选一，不并行）

A1 —— **换可达且同语义的判据**（推荐；不引入新魔法数）：
```python
# strategy_decay_certifier.py  L119-126
-        if ds is None:
-            state = "probation"  # 无 DS=判不了，Fail-Closed 封顶
-        elif float(ds) < 0:
-            state = "failed"
-        elif float(ds) < _CERTIFIED_DS:
-            state = "probation"
-        else:
-            state = "certified"
+        # failed 判据改挂同表已落库的衰减列（0~1，>=0.5 判存疑=列注释自陈），
+        # 不再挂 DSR 的域外负值（DSR 是 Φ 值，域 [0,1]，永不为负）
+        decay = m.get("oos_years_decay")
+        if ds is None and decay is None:
+            state = "probation"  # 无 DS=判不了，Fail-Closed 封顶
+        elif decay is not None and float(decay) >= _DECAY_SUSPECT:
+            state = "failed"
+        elif ds is None or float(ds) < _CERTIFIED_DS:
+            state = "probation"
+        else:
+            state = "certified"
```
配套：`load_latest_metrics` L71 SELECT 增列 `oos_years_decay`；L51 邻
`_DECAY_SUSPECT = 0.5`（与 `scripts/backtest/strategy_lifecycle_advisor.py:36`
`DECAY_SUSPECT_LINE = 0.5 # 蓝图批 4 存疑线（oos_years_decay）` 同数——**取既有预注册线，非新裁**）。
验收：§6 新边界测试的"合法域永不产出 failed"须**转为**"存在合法输入可产出
failed/retired"，二者不可同时绿（当前测试会主动报警，这是刻意的）。

A2 —— **若裁定维持 DS<0 为语义**：把该态判为数据事故而非策略判决：
```python
+        elif not (0.0 <= float(ds) <= 1.0):
+            raise ValueError(f"deflated_sharpe 越出 [0,1]：{sid}={ds}（上游口径事故）")
```

### 提案 B（SDC-1 第二半：消费端）
台账零读者属接线债，不在本节点面内。若 SDC-2 修好而无人读，等于仍然产而不消。
建议与 H5（"风险信号产而不消+决策门零接线"）合并排批。

### 提案 C（SDC-4，唯一无需新裁定的方向修正）
```python
# deflated_sharpe_calculator.py L305-307
-        if var_sr <= 0:
-            # 方差为零(极少情况), DSR 退化为 0.5 或 1.0
-            dsr = 1.0 if sr > 0 else 0.5
+        if var_sr <= 0:
+            # 非正方差=估计失效（病态/退化序列，超额峰度 -2 的锯齿净值可达）
+            # 判"显著"=拿自己的失败当最高荣誉；Fail-Closed 封顶为 0（并保留可观测性）
+            dsr = 0.0
```
`overfitting_adjudicator.py:275-277` 同步（现形 `1.0 if sr > 0.0 else 0.0`，同方向错）。
兼容面：`tests/simulation/test_deflated_sharpe_calculator.py` 无钉 `1.0` 的用例
（L54/L76 为区间断言，退化路径不被现有正常样例触达）；
`tests/backtest/test_overfitting_adjudicator.py:198-201` 的 `in (0.0, 1.0)` 仍绿。
**注意**：SHELVED 后须把 `var_sr <= 0` 显式上报（否则 0.0 与真低显著混同）——
建议同批改 `DSRResult` 加 `degenerate: bool`。

### 提案 D（SDC-2）
台账文档加 `source_fingerprint`（读回时比对 `SELECT max(ingest_ts), count() FROM strategy_screen`）：
不匹配 → 整份判 `stale`，`counts` 里显式带 `stale: N` 并拒绝沿用历史态。纯代码，无阈值。

### 提案 E（PA-1）
```python
# promotion_advisory.py L423-427
-        fsm = build_strategy_fsm(sid)
-        if fsm.current_state == "candidate":
-            # 观察态（sim/paper）对位 FSM sim：三条件已在其入册时预授权（intake 先例）
-            fsm.transition(SIM, {"sim_promotion": SimPromotionContext(
-                dual_window_pass=True, bh_fdr_pass=True, no_pending_decay_alert=True)})
+        fsm = build_strategy_fsm(sid)
+        if fsm.current_state == "candidate":
+            # 预授权不得自签：三条件须逐条回读真源，读不到即 fail-closed（原样上抛）
+            from zephyr.strategy_pipeline.intake import load_intake_card  # 真源凭卡
+            card = load_intake_card(sid)  # 缺卡/缺字段 -> raise，不补默认值
+            fsm.transition(SIM, {"sim_promotion": card.sim_promotion_context()})
```
（`load_intake_card` 现不存在——落地形态归主力会话；本提案只钉"不得硬编码 True"这条不变式，
最小替代 = 直接把 L426-427 三 True 删除并让 `SimPromotionGuard` 因缺 context 而 False。）

### 提案 F（HDR-1/2，无需裁定）
`c4_deflated_sharpe_runner.py:5-8`：`[CONSUMERS]` 改
`scripts/backtest/c4_batch_screen.py:145（经 scripts/backtest/translated/_c4_engine.py:333）`、
`[MATURITY]` 改 `production`；`c1_runner.py:5` 删 `scripts/regime/run_c1.py`，
改指 `scripts/tests/repro_c1.py`；`strategy_decay_certifier.py:8` 表名改
`c1_backtest.strategy_screen`。

### 提案 G（CREATE-GUARD 登记；本会话按禁改名单未动 catalogs）
两条 `--dry-run` 本会话已实跑，均返回"计划登记 1 条 / DRY-RUN：零写入"，
正式登记（写 `capability_canonical_file_registry.yaml`，属禁改名单）交主力会话执行：
```
python scripts/governance/d3_metadata/batch_creation_tokens.py \
  --prefix docs/_working/full-auto-chain/S11_assembled_backtest/nodes/coverage_map_cert_gates_mining.md \
  --created-by st-qoder-t1a-20260915 --capability s11_coverage_map_mining --dry-run

python scripts/governance/d3_metadata/batch_creation_tokens.py \
  --prefix tests/signal_ashare/strategy_signal/test_strategy_decay_certifier_boundary.py \
  --created-by st-qoder-t1a-20260915 --capability sdc_boundary_net --dry-run
```

---

## 10 本会话落盘面（自证，便于回滚）

- 新建：`docs/_working/full-auto-chain/S11_assembled_backtest/nodes/coverage_map_cert_gates_mining.md`（本文件）
- 新建：`tests/signal_ashare/strategy_signal/test_strategy_decay_certifier_boundary.py`（20 例，实测全绿）
- **未改动**：任何 `src/**`、`scripts/**`、`config/**`、catalogs；未 `git add`/`git commit`；
  ClickHouse 全程只读；临时件仅落 `.runtime/tmp/`。

---

## 11 施工回填 SDC-3/SDC-4（2026-09-17，施工会话 `st-qoder-t1a-20260915`）

§10 的"未改动 src/**"只对该挖矿会话成立；本批是其后续**施工**，改了 `src/**` 与测试，
仍**未** `git add`/`git commit`。全部数值为本批进程内实测，非引用他文。

### 11.1 裁定（第一性原理，非口味）

> 本批口径更正已登记为 **裁定#291**（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`，
> 与本批 `src/**`+测试同 commit 原子落地，RULE-RULING 铁律#6）。编号注：拟号期间 #290~#294 曾被并行
> "排班 v2"会话占用，随后他会话一次 autostash/merge 把双方未提交条目一并扫回 HEAD（本批 `src/**`
> 同遭扫回，已按 lane 转录逐 Edit 重放复原，见 §12.4），#290 由"qwen3-coder 移除"会话重新落地，
> 本条按登记时注册表最大值+1 取 #291。

真源公式取 Lo(2002) / Bailey & López de Prado(2014) / Harvey-Liu-Zhu(2021) 同源式：

```
V[SR] = (1 − γ₃·SR + (κ_p − 1)/4 · SR²) / (T − 1)      ← κ_p 为 Pearson 峰度（正态=3）
```

全仓入参统一为**超额**峰度（正态=0），故内部恒 `κ_p = κ_超额 + 3`，SR² 系数落为
`(κ_超额 + 2)/4`。机检锚点 = iid 正态边界：`κ_超额=0 ⇒ 系数=+1/2 ⇒ V=(1+SR²/2)/(T−1)`
（Lo 原文该边界即校验式）。凡使该边界回落到 `−1/2` 的实现即为口径错，无需争。

**顺带定理**（本批实测 E2 佐证）：Pearson 不等式 `κ_p ≥ γ₃²+1 ⇒ κ_超额 ≥ γ₃²−2`，代入得
`V 的分子 ≥ 1 − γ₃SR + γ₃²SR²/4 = (1 − γ₃SR/2)² ≥ 0`。⇒ **正确口径下一致矩输入几乎不可能
产出 V≤0**；旧口径把符号写成 `−3/4`，等于**凭空造出**一大片退化区（见 11.4 E2）。
这直接改变了 SDC-4 的病灶边界（11.5 更正本档原展品归因）。

### 11.2 三实现峰度口径前后对照

| 实现 | 角色 | 施工前 SR² 系数（κ=入参超额峰度） | 施工前 iid 正态边界（SR=1,T=252 真值 0.005976096） | 施工后 |
|---|---|---|---|---|
| `src/zephyr/simulation/deflated_sharpe_calculator.py` | **活件 SSOT**（metrics/C4/衰减认证皆经此） | `(κ−1)/4` ⇒ κ=0 时 **−1/4**（符号反） | 实测 **0.002988048 = 真值一半（−50.000%）** ❌ | `(κ+2)/4` ⇒ κ=0 时 **+1/2** ✅，`+3` 常量唯一真源 `KURTOSIS_PEARSON_NORMAL` |
| `src/zephyr/backtest/core/overfitting_adjudicator.py` | 死件（未接生产线，但公式此前**正确**） | `+3.0` 转 Pearson ⇒ κ=0 时 +1/2 ✅ | 0.005976096 ✅ | **自建公式整块删除**（含 Acklam 有理逼近 Φ⁻¹，+60/−135），`adjudicate_dsr` 改调 `deflated_sharpe_from_moments` |
| `src/zephyr/backtest/core/metrics.py::calculate_full_metrics` | 活件（晋级闸门实际读数点） | 无自有公式，委托上表第一件 ⇒ **继承 −1/4** | 同第一件 ❌ | 仍委托（本件不该有公式）；新增 `dsr_degenerate` 出参，退化态不再与"测得不显著"混同 |

同仓两实现数学互斥、错的是在跑的那个——本档 §SDC-3 的判断经施工复核**成立**，
且修复方向取"活件向死件对齐"（死件此前是对的）。

### 11.3 同族第二缺陷（本批新发现，本档原 SDC-3/SDC-4 未拆出）

活件 `E[max(Z_N)]` 用的是 Euler–Maclaurin **N→∞ 渐近式**，却被用在 N=2 这类小样本上。
以数值积分精确值 `∫x·N·φ(x)·Φ(x)^{N−1}dx` 为预言机（先用解析锚 `N=2→1/√π=0.5641896`、
`N=3→3/(2√π)=0.8462844` 自校，两锚均吻合到 1e−7，方用于对拍）：

| N | 精确值 | 施工前（渐近式） | 偏差 | 施工后（论文闭式） | 偏差 |
|---|---|---|---|---|---|
| 2 | 0.564190 | 0.846932 | **+0.2827** | 0.519755 | −0.0444 |
| 3 | 0.846284 | 1.064448 | +0.2182 | 0.852804 | +0.0065 |
| 10 | 1.538753 | 1.684924 | +0.1462 | 1.574598 | +0.0358 |
| 50 | 2.249074 | 2.348696 | +0.0996 | 2.276303 | +0.0272 |
| 1000 | 3.241436 | 3.302954 | +0.0615 | 3.255122 | +0.0137 |
| 4497（生产年化 N） | 3.650272 | 3.702346 | +0.0521 | 3.660603 | +0.0103 |

**为什么历史上数字"看着还行"**：SDC-3 让 V[SR] 偏小 → DSR **偏高**（欠折减），渐近式让
E[max] 偏大 → DSR **偏低**（超折减）；两者在生产的大 N 端部分对消。**只修其一必偏另一向**，
故本批同修，且三方一致性测试才敢用 `rel=1e−12` 恒等式而非区间容差（避免造新同谋测试）。
闭式本身仍是近似（≤0.045 个 z 单位），已在 docstring 显式披露，禁止把断言改回钉自身输出。

### 11.4 数值复验（前后差，方向可解释）

| 场景 | 施工前 DSR | 施工后 DSR | Δ | 解释 |
|---|---|---|---|---|
| iid 正态 SR_期=0.05 T=252 **N=1** | 0.785935 | 0.785719 | −0.0002 | 无多重修正 ⇒ 只剩 V[SR] 的 0.02% 差 |
| 同上 **N=2** | 0.478254 | 0.607150 | **+0.1289** | E[max] 超折减 +0.283 z 消失，主导差值 |
| 同上 N=10 / 50 / 100 | 0.186055 / 0.059818 / 0.035753 | 0.216830 / 0.068818 / 0.041022 | +0.0308 / +0.0090 / +0.0053 | 差值随 N 单调收敛，与 11.3 一致 |
| 300 点正态样本 SR_期=0.1323 **N=50** | 0.477574 | 0.500474 | +0.0229 | **跨过 `DSR_OVERFITTING_FLOOR=0.5` ⇒ `is_overfitting` 由 True 翻 False**（判定级差异，非小数位） |
| 一致矩网格 18300 例（κ_超额≥γ₃²−2）V≤0 计数 | **4285 例（23.4%）** | 50 例（0.27%，全在 γ₃SR=2 取等号边界） | −4235 | 旧口径凭空造出的退化区，正是旧 fail-open 的入口 |

阈值面：`DSR_SIGNIFICANCE_THRESHOLD=0.95`、`DSR_OVERFITTING_FLOOR=0.5`、佣金率
`Decimal("0.0000854")`、`MIN_COMMISSION=5`、回撤阶梯 5%/10%/15% **一律未动**（本批零阈值改动）。

### 11.5 SDC-4 前后 + 本档原展品的归因更正

| 输入 | 施工前 | 施工后 |
|---|---|---|
| 矩互斥 γ₃=2, κ_超额=2, SR=1, T=100, N=5（V=0 恰取等号） | `dsr=1.0`、`is_significant=True` | `dsr=0.0`+`degenerate=True`+WARNING，**永不判显著**（threshold 降到 1e−9 也救不回） |
| 矩互斥 γ₃=3, κ_超额=0, SR=1, T=100（V=−0.0152） | `dsr=1.0` | 同上（旧 V=−0.0227 亦负，此例两代同判） |
| 零方差常数序列 T=10, N=50 | sr 被"除 0 保护"成 0.0 → 得 `Φ(−E[max])≈0.02` 这种**看着像结论的数** | `dsr=0.0`+`degenerate=True`+WARNING |
| 矩不可估（T=3，偏度/峰度取占位 0.0） | 同上，占位值伪装"薄尾" | `degenerate=True`（`_MIN_OBS_FOR_MOMENTS=4`，是既有可估性下限的推论，非新阈值） |
| `OverfittingAdjudicator.adjudicate` 汇总语 | "DSR 低于显著性阈值"（把估计失败说成测得不显著） | **"DSR 不可判定(V[SR]=… 退化: 矩输入互斥/样本不足=估计失效) → Fail-Closed 不放行"**，仍阻断 |

**归因更正（本档 §SDC-4 须读此条）**：原文展品"锯齿序列 `base±amp`、κ_超额=−2.000、
`var_sr=−7.98e−3`、年化 SR 31.7、N=4497 ⇒ dsr=1.0000"本批逐字节复现成功
（交替 0.06/0.02、T=250 ⇒ SR_期=1.995996、γ₃=0、κ_超额=−2.000000、旧 V=**−0.007984** ✓）。
但按 11.1 定理，该负方差是 **SDC-3 的 −3/4 系数所造**，非退化序列本身：
正确口径下 `(κ_p−1)/4=(−2+3−1)/4=0 ⇒ V=(1−γ₃SR)/(T−1)=+0.004016`，**不退化**，
其 `dsr=1.0` 出自年化 SR 31.7 的合法 Φ 饱和（该 SR 在 A股不可实现，属入参事故而非闸门事故）。
⇒ SDC-4 的**真实残余病灶**改为三条：外部喂入的互斥矩（adjudicator 公共面收矩，可达）、
零方差/近零方差序列、样本低于可估下限。方向不变（旧行为一律给"最显著"），**结论强度降级为
"修 SDC-3 后残余面收窄，但仍必须 Fail-Closed"**；`_check_status`（不认识的条件绝不触发）与
`_resolve_n_trials`（不猜，可溯）两范式已据此落地。

### 11.6 落盘面与门禁（自证）

- `src/zephyr/simulation/deflated_sharpe_calculator.py` **+242/−52**（新公共面
  `variance_of_sharpe`/`expected_max_sharpe_z`/`sharpe_variance_is_degenerate`/
  `deflated_sharpe_from_moments`/`KURTOSIS_PEARSON_NORMAL`/`EULER_MASCHERONI`/
  `DSR_UNDECIDABLE`/`_inverse_normal_cdf`；`DSRResult.degenerate`；私有名
  `_variance_of_sharpe`/`_expected_max_sharpe` 保别名不炸既有导入方）
- `src/zephyr/backtest/core/overfitting_adjudicator.py` **+60/−135（净 −75 行）**（删自建 Φ⁻¹/闭式/V[SR]，改委托；
  `DSRVerdict.degenerate`）
- `src/zephyr/backtest/core/metrics.py` **+9/−3**（`dsr_degenerate` 出参 + `[INVARIANTS]` 同步）
- 两份 ALGO_FLOW 外部真源 YAML 同步（canonical **+31/−20**：F3 峰度 `+3` 转换、F4 论文闭式、
  新增 **F5 退化门**、A1/O1 不变量、`code:` 行号刷新；adjudicator **+6/−6**：A1/A2 改委托，
  A3/A4 行号刷新），均经 `parse_algo_flow` 实解析通过（12 节点/19 边、12 节点/10 边）
- 测试：`tests/simulation/test_deflated_sharpe_calculator.py` **+279/−6**、
  `tests/backtest/test_overfitting_adjudicator.py` **+46/−0**（该文件头 guard 所限，只增不改）。
  新增 5 个类共 24 例（`TestAgainstIndependentOracle` 全链独立预言机对拍
  `fmean/pstdev/fsum`+`NormalDist`，`rel=1e−12`；`TestDegenerateFailClosed` 7 例含 caplog；
  `TestCrossImplementationConvergence` 三实现恒等 + metrics 委托；
  `TestAdjudicateDsrFailClosedSdc4` 5 例；`variance_of_sharpe` 4 例含 iid 边界网格），
  重写 1 例同义反复断言（`test_expected_max_known_value` 原钉渐近式自身输出）
- 门禁：**127 通过 × 连跑两次全绿**；DSR 消费方回归 `test_dsr_recalc_backfill /
  test_c4_deflated_sharpe_runner / test_c4_batch_smoke / test_sharpe_calculator_fixer /
  test_overfitting_protection_gate / test_overfitting_guard /
  test_correlation_overfitting_audit` 合跑 **137 通过**（无连带破坏）；
  5 个改动件 NO-HIGH-COMPLEXITY 扫描**输出为空**（全文件最大 14 ≤ 15，为既有
  `perturbation_stability`，本批未新增分支）；ruff 净零新增（残留 4 条
  `test_overfitting_adjudicator.py:136 B905/RUF007`、`metrics.py:35 I001 / :258 BLE001`
  经 `git show HEAD:` 比对确证为**既有**）；全程未写 `data/`，测试走 `tmp_path`

### 11.7 残余（本批不裁，登记待决）

- **R-1**｜**已清偿（收口批 2026-09-17，随本批同 commit）**，且本档原归因**说轻了**：
  `scripts/backtest/dsr_recalc_backfill.py::approx_dsr_from_sharpe` 不止 docstring 过期——
  它**自带** `var_sr = (1.0 - sr*sr/4.0)/(window_days-1)` 字面式，即 SDC-3 同一处错口径的
  **第 4 个实现**（也正违反本件自己的 `[INVARIANTS]`"DSR 数学全委托官方件，禁重写"）。
  收口处置：删自写式，改 `variance_of_sharpe(sr, 0.0, 0.0, T)` 委托；退化判据同官方件写成
  `not (var_sr > 0.0)`（吃掉 NaN，旧 `<= 0.0` 对 NaN 恒 False）；`expected_max_z` 由导入
  私有别名 `_expected_max_sharpe` 改公开名 `expected_max_sharpe_z`。
  数值影响（该件 is-only 补齐路径，γ=κ=0，SR_期=1.15/√252=0.07244319）：T=970 ⇒
  旧 V=1.030638e−3、新 V=1.034700e−3（**+0.394%**）；DSR N=1 由 0.987982→0.987842
  （−0.000139）、N=4481 由 0.080287→0.079629（−0.000659）——量级小，但旧式给不出正确
  方向（该项符号本就反了），且口径分叉本身即病。`tests/backtest/test_dsr_recalc_backfill.py` 15 passed
  连跑两次全绿（该文件对 approx 只做区间/单调断言，无钉值同谋）。
- **R-2**｜近奇异正方差：`γ₃SR→2⁻` 且 κ_超额 取下界 `γ₃²−2` 时 `V→0⁺`（实测 2.5e−7…2.5e−15），
  `dsr` 合法饱和为 1.0 而 `degenerate=False`；恰取等号（V=0）则判退化 → 两侧不连续。
  加"V 下限"需新造阈值 ⇒ **属 RULE-RULING，本批禁改阈值故未动**。Owner 若裁定，
  建议以 `V ≥ c/(T−1)` 形式（c 由裁定给），而非按 dsr 数值封顶。
  该边界已作为"明示不处置项"写进 **裁定#291** summary 尾段（含本行数值与推荐形态），
  待 Owner 另批裁定，不随本批夹带。
- **R-3**｜`DSRResult.expected_max`（z 单位）与 `DSRVerdict.expected_max_sharpe`（√V·E[max]，
  SR 单位）**同名不同量纲**。本批按"只做口径统一+去错、不大改"边界未合并，已写进两处 docstring。
- **R-4**｜`tests/backtest/test_overfitting_adjudicator.py:198-201` 的同谋断言
  `assert verdict.dsr in (0.0, 1.0)` 字面仍在——该文件头 `[MODIFY-GUARD] only_add_tests`
  禁改既有用例，故本批只**新增**严格类把同输入钉成 `0.0/不可判定`（弱断言不再单独承重）。
  清理需解除 guard 或另批。
- **R-5**｜三实现**类合并**（canonical/adjudicator/metrics 收为一个 DSR 门面）= **另案**。
  本批止于"口径单一真源 + 委托 + 去错"，公共面签名全保持向后兼容。
- **R-6**｜历史台账数值须按新口径重算后才可比：旧 `certified/probation` 读数与新读数
  **不可混比**（11.3 的双向偏差意味着差值非单调）。本批未跑任何写库/回填脚本。

---

## 12 收口批实测核验（2026-09-17，主会话 st-qoder-t1a-20260915 独立复测）

§11 的施工方子代理在 150 轮上限处中断（自述"引入两处结构性错误待修"），故本档 §11 全部
**数值断言由收口方逐条独立复测**后才落盘——复测不过的一律改写，不复用其自述结论。

### 12.1 落盘面 numstat 逐条复核（`git diff --numstat` 实测）

| 件 | 本档 §11.6 自述 | 实测 | 判定 |
|---|---|---|---|
| `deflated_sharpe_calculator.py` | +242/−52 | +242/−52 | ✅ |
| `overfitting_adjudicator.py` | +60/−135 | +60/−135 | ✅ |
| `metrics.py` | +9/−3 | +9/−3 | ✅ |
| `test_deflated_sharpe_calculator.py` | +279/−6 | +279/−6 | ✅ |
| `test_overfitting_adjudicator.py` | +46/−0 | +46/−0 | ✅ |
| ALGO_FLOW 两份 YAML | +31/−20、+6/−6 | +31/−20、+6/−6 | ✅ |

结构错误复核：5 件 `python -m py_compile` 全通过，`ast.parse` 全通过 ⇒ 自述的"两处结构性
错误"在中断前已自行修完，收口方未发现残留。

### 12.2 口径边界锚与影响面（收口方进程内复算，非引用 §11）

- iid 正态边界锚（γ=0、κ_超额=0、SR=1、T=252）：旧 V=0.002988048、新 V=0.005976096
  ⇒ 比值恰 **2.0000**，与 §11.2 表所记"旧式把方差砍半"逐位吻合（该锚即 Lo(2002) 自检式）。
- `E[max(Z_N)]`（旧 Euler–Maclaurin 渐近式 vs 新论文闭式）：N=2 旧 0.8469→新 0.5198、
  N=10 旧 1.6849→新 1.5746、N=4497 旧 3.7023→新 3.6606 —— 与 §11.3 表同向同量级。
- **影响面网格**（γ=0、κ_超额∈{0,1,3}、(T,N)∈{252×4497, 2520×4497, 252×10}、SR_期 0.05…1.0）：
  新/旧 DSR 比落在 **0.967…1.165**。分带读法：生产日频带（SR_期 0.05–0.10、T=252、N=4497）
  新值**偏高 +4%…+16%**（E[max] 去掉超折减主导）；SR_期 0.20–0.30 带新值**偏低 −0.4%…−3.3%**
  （V[SR] 去掉欠折减主导）；SR_期≥0.5 两误差近乎完全对消（比值 1.000）。
  ⇒ 净效应**非单调、随 SR 换向**，这是 R-6"历史读数不可混比"的定量依据，
  也是"只修其一必偏另一向"（§11.3）的直接证据。
- R-1 清偿后的本件自校（年化 SR=1.15、T=970）：V 由 1.030638e−3→1.034700e−3（+0.394%），
  DSR N=1 由 0.987982→0.987842。

### 12.3 回归与门禁（收口方实跑）

- DSR 全消费面：`tests/simulation` + `tests/backtest` 合跑 **2120 passed**；
  `tests/regime` + `tests/factor` 合跑 **1831 passed**（覆盖 c4_deflated_sharpe_runner /
  overfitting_guard / correlation_overfitting_audit / sharpe_calculator_fixer 等消费方）；
  `tests/backtest/test_dsr_recalc_backfill.py` **15 passed 连跑两次**。
- 复杂度：`deflated_sharpe_calculator.py` 全文件最大 cc=9、`overfitting_adjudicator.py`=14
  （既有 `perturbation_stability`，本批未加分支）、`metrics.py`=11 ⇒ NO-HIGH-COMPLEXITY 空输出。
- ruff：三 src 件与收口新碰的 `dsr_recalc_backfill.py` 与 `git show HEAD:` 基线**逐条同数**
  （metrics I001+258、backfill B905 皆存量），零新增。
- 阈值面零改动复述：`DSR_SIGNIFICANCE_THRESHOLD=0.95`、`DSR_OVERFITTING_FLOOR=0.5`、
  佣金 `Decimal("0.0000854")`、`MIN_COMMISSION=5`、回撤阶梯 5%/10%/15% 全部未动。

### 12.4 工作区扫回事故与逐 Edit 重放复原（2026-09-17 03:3x，收口方）

本批 9 件改动在 02:59 前后被他会话 `session_worktree` 的 **autostash/merge** 扫回 HEAD
（`git status` 由 ` M` 变干净、`git fsck` 侧无任何含本批改动的 stash 存活），同窗被扫回的还有
本会话的两份未提交节点档与一并行会话的 5 条裁定（#290~#294）。复原路径与自证：

| 件 | 复原来源 | 复原后 `git diff --numstat` | 与 §11.6/§12.1 记录 |
|---|---|---|---|
| `deflated_sharpe_calculator.py` | lane 转录逐 Edit 重放 | +242/−52 | ✅ 逐字一致 |
| `overfitting_adjudicator.py` | 同上（16 op，其中 1 op 当时即失败、重试 op 已覆盖） | +60/−135 | ✅ |
| `metrics.py` | 同上 | +9/−3 | ✅ |
| `test_deflated_sharpe_calculator.py` | 同上 | +279/−6 | ✅ |
| `test_overfitting_adjudicator.py` | 同上 | +46/−0 | ✅ |
| 两份 ALGO_FLOW YAML | 同上 | +31/−20、+6/−6 | ✅ |
| `dsr_recalc_backfill.py` | 主会话转录 Edit 重放 | +12/−7 | ✅（R-1 清偿） |
| 本档 | lane+主会话 Edit 重放 + 转录内 heredoc 取回 §12 | +202/−0（§12.4 本小节自身再 +27，故落盘总 +229/−0） | ✅ |

功能侧二次证明（非仅行数）：`py_compile` 5 件全通过；焦点测试逐档 49 / 38 / 15 passed；
`tests/simulation`+`tests/backtest`+`tests/strategy_pipeline` 合跑 2244 passed。
行数与测试结果同时吻合 ⇒ 重放不是"重写一份近似件"。

**治本建议（登记，非本批施工）**：`session_worktree` 的 autostash 路径在 merge 前把**非本会话**
的未提交改动一并扫走，且 `stash_notice.json` 只记自会话那 1 个文件——对无辜会话零告警。
建议：扫回前按 claim 归属过滤，或对被扫回的他会话文件写告警清单（与 §10 降级直改计数同源）。
