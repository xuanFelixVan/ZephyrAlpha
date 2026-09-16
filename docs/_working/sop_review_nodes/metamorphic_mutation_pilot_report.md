---
ttl: task_bound
rule_form: data
verifiability: manual
title: GW5 分包五⑬施工收口——metamorphic 四条不变式落库 + mutation 窄试点
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-16
session: st-sopx-20260916
topic: deep_review
scope: global
depends_on:
  - subnode_mining_round1
---

# GW5 分包五⑬施工收口（2026-09-16 夜，metamorphic 四不变式 + mutation 窄试点）

> **定位**：[subnode_mining_round1.md](subnode_mining_round1.md) §47 子节点 3 立卡项的首批施工收口。四条不变式测试落库 `tests/metamorphic/`（纯 pytest 参数化，零新依赖）；mutation 窄试点按卡执行（mutmut 路径受阻后按预案切手写变异体），杀伤率 6/12 → 12/12（盲区整改后全杀）。
> **边界遵守**：生产源码（src/zephyr/**、scripts/backtest、注册表 catalogs 除 token 登记、docs/03_modules、api_server、tests/backtest 既有文件）零改动；mutation 全部作用于 `.runtime/tmp` 沙箱副本。

## 1 四条不变式：被测真源与测试落点

| # | 不变式 | 被测真源（file:line，2026-09-16 工作区） | 测试落点 |
|---|--------|------------------------------------------|----------|
| 1 | 价格缩放不变（价格×k 资金×k → NAV×k、收益率/夏普/回撤/胜率不变、P&L×k；同资金变体在整手误差界内不变） | `DefaultBacktestEngine.run` src/zephyr/backtest/implementations/vectorized_engine.py:170（S11 整装回测唯一执行引擎，framework_composer.py:1218 消费） | tests/metamorphic/test_s11_metamorphic_invariants.py `test_price_scaling_*` |
| 2 | 资产置换不变（行情行/信号列置换 → NAV 不变；成员面板列置换 → 合成面板逐格不变；一致重标端到端 NAV 逐日相等） | `compose_weight_panels` src/zephyr/pf_core/strategy_engine/framework_composer.py:381 + 同上引擎 | tests/metamorphic/test_s11_metamorphic_invariants.py `test_asset_permutation_*` + `test_portfolio_return_invariant_to_member_panel_permutation_endtoend` |
| 3 | 四闸样本置换不变（池化行/regime 切片置换 → p/q/shrunk/wilson/edge 与 state 判定不变） | `certify_family` / `within_regime_edge` src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py:182/:129 | tests/metamorphic/test_fourgate_metamorphic_invariants.py INV-3 组 |
| 4 | 效应量↑→p 值↓单调（含端到端 p/q/shrunk/wilson 链与镜像基线单调） | `binomial_ge_pvalue` 同文件:79（+ certify_family 端到端链） | tests/metamorphic/test_fourgate_metamorphic_invariants.py INV-4 组 |

附加不变式：信号强度×c → 引擎 Σ=1 归一化后逐位不变；`effective_n` 折扣单调。

**合计 63 条测试**（四闸文件 49 + S11 文件 14），合成数据（0.25 网格价/种子随机游走），不触库不触网。

## 2 pytest 统计（连跑两轮）

| 轮次 | 命令 | 结果 |
|------|------|------|
| 第 1 轮 | `pytest tests/metamorphic/ -q`（cache_dir 隔离到 .runtime/tmp 会话子目录） | **63 passed**，0 failed（4.10s） |
| 第 2 轮 | 同上 | **63 passed**，0 failed（3.96s） |

## 3 mutation 窄试点

**工具路径选择依据（两种路径登记）**：mutmut 3.8.0 `pip install` 成功，但运行时原生 Windows 硬拒绝（官方输出 "To run mutmut on Windows, please use the WSL"，issue #397）；本机 WSL 未安装（`wsl --status` 报未装子系统），安装 OS 级组件越出本车道权限 → 按任务预案切换**手写变异体**路径，对单文件副本手跑。

**试点对象**：pattern_evidence_certifier.py（MOD-SIG-148，四闸统计核——与 T2 被测面同域的 P0 纯逻辑文件）。**测试对象**：仅 tests/metamorphic/test_fourgate_metamorphic_invariants.py（本卡新增不变式测试的敏感度审计；既有教科书单测不混入）。**对照控制**：零变异副本经同一钩子跑测试必须全绿（钩子有效性自证，实测 exit=0）。

### 3.1 变异体清单与两轮结果

| ID | 类别 | 变异 | R1 | R2（整改后） |
|----|------|------|----|----|
| M01 | 比较符翻转 | 闸A `q>=q_thr`→`q>q_thr` | SURVIVED | killed |
| M02 | 比较符翻转 | 闸B `n_eff<min`→`<=min` | SURVIVED | killed |
| M03 | 比较符翻转 | 闸C `w_edge<=0`→`<0` | SURVIVED | killed |
| M04 | 比较符翻转 | 闸C `conc>max`→`>=max` | SURVIVED | killed |
| M05 | 常数漂移 | certify_family 先验 k 默认 PRIOR_K→×2 | SURVIVED | killed |
| M06 | 边界翻转 | 二项短路 `hits<=0`→`<0` | killed | killed |
| M07 | 删断言 | 删 `hits>n → return 0` | killed | killed |
| M08 | 返回值漂移 | `n==0 → 1.0` 改 `0.0` | killed | killed |
| M09 | 运算符翻转 | 收缩式 `+k·baseline`→`−` | killed | killed |
| M10 | 运算符翻转 | 加权 edge `/total_n`→`*` | killed | killed |
| M11 | 边界翻转 | n_eff 折扣 `max(1,w)`→`min(1,w)` | SURVIVED | killed |
| M12 | 删断言 | 删输出按 pattern_id 排序 | killed | killed |
| | | **杀伤率** | **6/12 = 50%** | **12/12 = 100%** |

### 3.2 第一轮盲区分析（6 存活 = 6 条测试盲区）

置换/单调类不变式的共性盲区：对**门位阈值恰等语义**与**常数漂移**天然钝感（置换不变只验证"同输入同输出"，变异在两次运行中同向生效即逃逸）。
- M01–M04（边界语义）：无"阈值恰等"构造 → 补四条门位边界钉扎（q==q_thr 判 failed、n_eff==min 放行、w_edge==0 判 probation、conc==cap 放行——锚点全取二进制精确构造，如 90/100==0.9）。
- M05（常数漂移）：无绝对值锚点 → 补 shrunk 手算式锚点 `(0.62·3000+100·0.5)/3100`。
- M11（折扣失效）：无 n_eff 绝对锚点 → 补 `effective_n(600,10)==60.0` 与 `n_eff==3000.0`。

整改断言并入正式测试文件（tests/metamorphic/test_fourgate_metamorphic_invariants.py "门位边界语义钉扎"节），非一次性补丁。**方法论结论**（印证挖矿报告"mutation score 测测试敏感度"）：metamorphic 套件的标准配置=置换/单调 MR + 边界语义钉扎 + 绝对值锚点，三者缺一即有系统性盲区。

## 4 红蓝对抗发现（诚实清单，生产代码零改动）

- **F-1（边界缺陷，建议裁定）**：`binomial_ge_pvalue` 的 `p0∈{0,1}` 且 `hits∈(0,n)` 时通过入参校验（`0<=p0<=1`）却在 `math.log(0)/log1p(0)` 抛 `ValueError: math domain error`——校验承诺与实现边界不一致。已以特征化测试钉扎现状（不修复，修复属裁定）。
- **F-2（有界输入假设）**：`hits=inf` 走 `hits>n` 短路返回 0.0（"不可能事件"）。有界输入假设下的特征化，无碍现网（统计表率值恒有界）。
- **F-3（缩放非逐位，试点正发现）**：价格×k+资金×k 的 NAV 在 Decimal 层非逐位 k 倍——28 位上下文除法舍入在整手地板/滑点链路累积，实测包络 NAV 相对偏差 ≤2.1e-7、P&L ≤1.1e-6（远小于一手粒度 ≥800 元，资金语义无影响）。容差=实测包络×5 并写明推导。理论上"比例制费用+同 lot"应逐位成立，实际被 Decimal 上下文舍入打破——**这正是文档不变式与工程实现的落差样本**。
- **F-4（fail-tolerant 特征化）**：NaN 收盘价不崩、成交继续、NAV 序列零 NaN 污染（钉扎防回归）；全零价/全零信号 → sanity_guard `ImplausibleBacktestError` fail-closed 拦截 ✓。
- **F-5（四闸 state 对效应量非单调=设计语义）**：闸C 集中度是正 edge 质量占比，单形态效应量↑可推高自身占比越 0.9 → certified→probation 属设计，非缺陷（测试注释已声明不 assert state 单调）。
- **环境观察（非本车道，不碰）**：①裸 python 下 zephyr 自举报 `ResourceScheduleAlerts` ImportError（他车道在途模块半成品，pytest 路径不受影响）；②capability registry 工作区含他车道 4 条在途 token（resource_sampler 等），本车道 token 已登记但 registry 整文件不入本批（多写手热文件，代提交违反 owner 责任制，落批归注册表收口方）。

## 5 工具副作用与清理

- mutmut 安装副作用：opentelemetry-sdk 被连带升级至 1.41.0，破坏 semgrep 的 `~=1.37.0` pin——**已回滚恢复**（pip install "opentelemetry-sdk~=1.37.0"，semgrep 依赖恢复一致）。mutmut 本体保留（卡面裁定的试点工具）。
- 沙箱（.runtime/tmp/mutation_pilot_st-sopx-20260916/：原始副本/变异副本/驱动脚本）用毕已删；pytest cache 隔离子目录已删；生产源文件 git diff 零触碰。

## 6 提交与归属

- 提交入口 scripts/git_commit.py（--session st-sopx-20260916），文件清单：tests/metamorphic/test_s11_metamorphic_invariants.py、tests/metamorphic/test_fourgate_metamorphic_invariants.py、docs/_working/metamorphic_mutation_pilot_report.md。
- creation_token 已登记进 capability_canonical_file_registry.yaml（capability=metamorphic_mutation_pilot_report，CAS 一次落盘）；registry 文件工作区同时含他车道 4 条在途 token，故 registry **不入本批**（多写手热文件代提交违反 owner 责任制），token 条目随注册表收口方落批。
- 提交后经 `git log -1 --name-only` 核实真实归属（结果见提交记录，无他会话文件被吸收）。
