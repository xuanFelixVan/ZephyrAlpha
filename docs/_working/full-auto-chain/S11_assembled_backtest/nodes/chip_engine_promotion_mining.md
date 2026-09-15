---
ttl: task_bound
title: T1-α 节点挖矿：chip_distribution_engine 转正审计（feature_pipeline_mining §4 遗留小节点）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 挖矿节点 7：chip_distribution_engine 转正审计（MOD-REGIME-005，403 行）

> 挖矿日期：2026-09-15 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 挖矿依据：feature_pipeline_mining §4（FPB-3 的 #12 现成件"402 行从未接入"）+ overlay_dims_mining §5 转正子节点
> 证据等级：全源码逐行 + 11.5 年真实 000300（4057 日）+ 5 年真实 600519（1221 日）CH 只读实测 +
> 单测套件 20/20 复跑；"转正"裁定对象=从孤儿状态接入决策链并配得上 production 声明

## 0. 状态认定先行：不是"未转正"，是"虚标 production 的孤儿"

任务假设"该引擎可能处于非 production 状态"。实测结论相反：**声明面三处自称 production，
实际是零消费端孤儿件，且在真实数据上输出伪分布**。转正审计的第一产出是把声明面打回原形：

| 声明位置 | 声明 | 实际 |
|---------|------|------|
| 模块头 `[MATURITY] production`（chip_distribution_engine.py:7） | production | src 内除 `__init__.py` 再导出外**零 import**（grep 全 src 实证）；唯一声称消费者 MOD-REGIME-002 的源码里没有它的 import |
| 蓝图 frontmatter `design_maturity/build_status: production`（blueprint.md:7-8） | production | 同文件 L25"成熟度: design 🟡待施工"、L374 §12.1"**本模块尚无已实现代码**"——蓝图内部三处自相矛盾 |
| decision_algo_registry.yaml:161-167 `DAL-CHIP-DISTRIB status: production` | production，outputs=[获利盘占比, 单峰密集度] | 引擎**不产出获利盘占比、不产出单峰密集度**（compute_metrics 只有 4 个其他指标，chip_distribution_engine.py:239-244）；TDM-E-L3-12 的决策问题（trading_decision_map.yaml:1997-2000"获利盘>90%…低位单峰密集"）所需的两个输出均不存在 |

battle_map_domain_policy.yaml:370-374 也自证未挂载（"待 MOD-REGIME-001 promote 后统一挂载"）；
backtest_backlog.yaml:965-977（BT-P2-040）confidence: **untested**、plan: null。

## 1. 头号发现 CHIP-1（P0）：真实数据下算法全面退化——输出是伪分布，非筹码分布

**两个独立退化叠加，任一都足以让输出不可用**：

1. **VWAP 量纲错配，三角形分布 0 天处于设计形态**。
   `compute_vwap = amount/volume`（chip_distribution_engine.py:96-105）。CH 实测：
   - 000300（kline_index，4056 有效日）：VWAP 落在 [low,high] 内 **0/4056（0.00%）**；
     示例末日 vwap=2766 vs close=4450（0.62×）→ vwap<low 逐日成立，三角左半消失，
     当日增量恒为"峰钉死在区间最低"的递减斜坡（L141-144 分支）。
   - 600519（kline_daily，1221 日）：**0/1221 在界内**；vwap/close=99.58~101.49——
     **kline_daily.volume 实际是手，schema 注释"成交量(股)"失真**（DESCRIBE vs 2026-09-10
     全市场抽查 8 票 ratio≈100 实证）→ vwap=100×close > high 恒成立，当日增量恒为
     "峰钉死在区间最高"的右三角斜坡（L135-136 分支）。
   - 三角分布是本引擎的存在理由（blueprint.md §3.1"华泰2026前沿"），真实数据上**一天都没成立过**。
2. **84% 的历史日被静默替换为均匀注入**。网格只按末 250 日构建（L294-304
   `recent=df.iloc[-lookback:]`），递推却跑全史（L323 `for t in range(n)`）。
   000300 全史 grid=[4328,5064]，**3406/4057（84.0%）日**的当日高低区间完全在 grid 外
   → L146-150 fallback 当日增量=均匀分布，无任何日志/标记。

**伪信号定量（000300 全史引擎输出）**：bottom_accumulation=**0.9950**（99.5% 筹码恒在
底部 1/4——"底部堆积"每天成立，与牛熊无关）、LTBR=0.002、UTP=0.00000。
600519（2021-09~2026-09 真实下跌中继段）：BA=0.1531、UTP=0.0035——量纲斜坡叠加
250 日窗网格迁移，套牢峰信号被淹没。**若今天把引擎接进 #12，四档系数映射将输出恒
"健康/底部堆积"，是把系统性伪影当 regime 信号喂给 Shrinkage。**

**单测为何全绿**：tests/regime/test_chip_distribution_engine.py:66 fixture 自带
`amount = volume * close`（自洽单位）——恰好把生产数据唯一会犯的量纲错配排除在测试
宇宙之外；20/20 passed（2026-09-15 复跑）属"mock 层扎实、真实层盲区"。

## 2. CHIP-2（P0）：消费端断链三路全空——转正没有受体

- 声称消费端 1：`[CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder 消费 #12/#5/S2)`
  （chip_distribution_engine.py:5）。实测 regime_feature_builder.py **无任何 chip import**
  （grep import 段全列，L57-88）；#12 的实际生产点是 risk_signal_builder.py:40
  "#12 chip_structure=1.0（chip 引擎按日成本高，Phase 2c 接）"，`_ACTIVE_PARAMS`（L68）
  无 12——**stub 是写在消费端的常量，与引擎零耦合**。
- 声称消费端 2：S2 底部筹码 → overlay_signals_builder.py **零 chip 引用**（grep 实证）。
- 声称消费端 3：factor_registry.yaml:3555/3851 两条因子"对接 chip_distribution_engine 模块"
  —— aspiration 性引用，无代码路径；ALGO_FLOW 自标 F1-F4 四断点"factor_registry: 无
  FCT 条目"（algo_flow/chip_distribution_engine.yaml:26/34/42/50）。
- 结论：**引擎当前无任何生产受体**。"转正"命题本身不成立——先有接线需求，才谈转正。

## 3. CHIP-3（P1）：任意历史长度依赖——同一"今天"三个答案，且 tau 归一含帧内未来量

同末日 2026-09-15、同一引擎参数，仅换数据起点（CH 实测 000300）：

| 数据起点 | 行数 | bottom_accumulation | LTBR |
|---------|------|--------------------|------|
| 2015-01-01 | 2845 | 0.9295 | 0.005 |
| 2021-01-01 | 1383 | 0.6924 | 0.090 |
| 2024-01-01 | 656 | 0.4189 | 0.109 |

**2.2 倍漂移**，根因三连：均匀初始化未声明 warmup 语义（L312-320）；tau 的
`avg_vol` 取**整个传入 df** 的正量均值（L307-309）——同一天的 τ 依赖帧内未来成交量
（历史日 τ 含未来量 → 中间态不可 PIT 抽取）；grid 随尾窗漂移。引擎无 `as_of` 参数、
只输出末态——单次末态调用因果干净（**PIT 正面**：grid=尾 250 日、递推只向前、无
shift 需求），但代价是日频序列只能逐日截断重算 = O(n²)，且每次重算结果随起点漂移。
**无收敛/预热语义的递推件不具备进入 walk-forward 回测的资格。**

## 4. CHIP-4（P1）：τ=2% 假设的失真度无界，且真实换手率数据侧断供

- 实现口径：`tau = clip(0.02 × vol/avg_vol, 0, 1)`（L307-310）——即"相对量能×常数 2%"，
  与流通股本无关。经典 CYQ/华泰口径 τ=volume/流通股本（blueprint.md §3.2 自己也是
  这么写的，L136）。失真方向系统性：大蓝筹真实换手 ~0.1%/日（记忆半衰期应 ~2 年）
  被按 2%/日衰减（半衰期 35 日）→ 引擎眼里的"长期筹码"只有月级记忆；小妖票真实
  换手 10%+ 被低估 → 死筹码虚增。
- 数据侧：kline_daily 有 `turnover` 列但**2019 年起覆盖率仅 4.5~6.1%**（2018 年 86.1%，
  现役 provider 均不进料——CH by-year 实测）；`adj_factor` 对 600519 distinct=[1]
  （无复权信息）。**修复 τ 无现成数据源**，要么回填 turnover、要么引入流通股本表——
  这是转正前置的数据工程，不是引擎内一行修复。

## 5. CHIP-5（P1）：契约漂移三件套（本仓惯发模式再现）

1. **NaN 行为与错误契约不符**：蓝图 ZA-REGIME-0050"OHLCV 缺失/**NaN** → 返回均匀分布，
   标记 degraded"（blueprint.md §5/§8）。实测注入 1 行 NaN low/high：输出**无任何
   NaN、无 degraded 标记、BA 与 clean 完全相同（0.1905）**——NaN 日被 L146-150
   fallback 静默当均匀增量吃掉。另有变体：NaN volume 会使 tau=NaN 毒化全序列
   （np.clip 不拦 NaN，L310）。输出 schema 根本没有 degraded 字段。
2. **蓝图不变量 §4"筹码龄分层 4 层之和 = total_distribution"（blueprint.md:248）不成立**：
   实现逐层独立归一（L377-381），实测各层 Σ=1.0×4 vs total Σ=1.0。模块头 INVARIANTS
   （L8）写的是"各层 Σ=1.0"——同一事实，蓝图与代码头各说各话。
3. **TDM/registry 决策语义 vs 实现输出错位**：TDM-E-L3-12 与 DAL-CHIP-DISTRIB 的
   获利盘占比/单峰密集度（现价上下筹码占比——经典 CYQ 核心输出）**未实现**；
   compute_metrics 的 4 指标无一与现价比较。消费端真要接线，第一天就会发现
   "注册的算法不产注册的输出"。

## 6. CHIP-6（P2）：age_layers 逐层归一丢失层间占比信息

每层独立归一（L377-381）后，"长期筹码占总筹码多少"这一 CYQ 关键量**不可回答**
（四层 Σ 恒等，占比信息在归一一步被抹掉）；long_term_bottom_ratio 只能回答"长期层
内部"的分布。迁移率 0.5/0.125/0.02（L57）经归一放大后有效动力学偏离标称值
（如 short 层 (1-τ) 收缩后再归一放大）。分层机制作为"旧筹码形状追踪器"仍可用，
但蓝图 §3.3 的层间份额语义（"long 层筹码占比高=底部堆积"）在当前实现下无从谈起。

## 7. CHIP-7（P2）：复权无处理、无声明

引擎与蓝图全篇无复权字样；分红/送转日价格跳空会把同一批筹码在 grid 上撕裂成两截。
adj_factor 列存在但 distinct=[1]（600519 全史）——表内亦无可用复权信息。个股级
使用前必须解决（指数级无此问题）。

## 8. CHIP-8（P2）：性能与 API 形态——指数级可用，全市场日频不可行

- 实测 1221 行个股单次 104ms；000300 全史 4057 行 0.42s。**指数级（regime 域唯一
  实际场景）完全够用**；全市场快照批（5400 票×250 日窗）≈2 分钟/批可接受。
- 但日频序列 = O(n²) 重算（无增量 API：engine 无状态保存/续算接口，L323 每次全史
  重递推）→ 全市场逐票日频因子产线不可行（外推 ~7 分钟/票量级）。"按日成本高"
  （risk_signal_builder.py:40）的真实含义是 **API 形态缺增量模式**，不是单次速度。
- 若转正走指数级试点，性能不是阻断项；若宣称个股级 32 网格跨股比较（蓝图 §3.5），
  需先补增量 API 或降采样设计。

## 9. 正面清单

- **纯函数分解干净**：triangular_pdf/compute_vwap/turnover_recurse/build_grid_prices/
  compute_metrics 五件各自可测可替换（L65-244），CHIP-1/3 的修复不伤及递推骨架。
- **换手递推公式本体正确**：C_t=(1-τ)C_{t-1}+τD_t 与华泰/经典 CYQ 口径一致，τ clip
  [0,1] 防发散，total Σ=1 不变量在真实数据下仍守住（实测）。
- **降级不抛错的契约方向正确**：空数据/单价位/量额 0 三路兜底都有（L287-289/299-302/
  96-105），符合 regime 管道 fail-open 风格（尽管缺 degraded 标记，见 CHIP-5）。
- **32 相对网格"0=最低/31=最高"的跨股可比设计意图正确**（L186-191），问题在窗口
  与递推范围错配（CHIP-1.2），不在网格化本身。
- **单测 20 个覆盖结构/归一/降级/性能基线**，性能断言带六轮 sweep 实证注释
  （test L376-378），mock 层工程素质在线。
- **治理面诚实**：ALGO_FLOW 自标 VWAP/F1-F4 五断点；battle_map 自认未挂载；
  backtest_backlog 自认 untested——下游治理件没有跟着头文件一起说谎。

## 10. 转正裁定建议：**暂缓转正**（先打回 trial，再修三缺口，后试点接线）

**第一步（立即，纯声明修正）**：模块头 `[MATURITY]` production→trial、蓝图
frontmatter 与正文矛盾三处对齐、§12.1 按实补代码索引；DAL-CHIP-DISTRIB 的 outputs
改为实际 4 指标（或补获利盘实现），status 改 trial。虚标 production 在本仓等价于
审计盲区驾照（wyckoff WYF-2 同型）。

**第二步（转正前置缺口，按序）**：
1. CHIP-1：VWAP 量纲（volume 手→股 ×100，或直接用典型价/表内 vwap）+ 递推窗口与
   lookback 对齐（`for t in range(n-lookback, n)` 或全史重建网格）——修完在真实
   000300/600519 上复测 BA 不再恒 0.99、同末日跨起点漂移 <0.05。
2. CHIP-3：warmup 语义（声明前 N 日丢弃）+ tau 改滚动窗均值（消帧内未来量）。
3. CHIP-5：degraded 字段落 schema + NaN 显式处理 + 蓝图不变量二选一改齐。

**第三步（试点接线）**：RegimeFeatureBuilder Phase 2c 以**指数级（000300）**接入 #12
——数据（kline_index 在库 4057 日）、性能（0.42s/次）、PIT（末态调用干净）三关已过；
个股级与获利盘语义（CHIP-4/7/TDM 错位）留待 turnover/流通股本数据工程后再议。

一句话结论：**这是一个公式正确、数据全错、无人消费、却自称 production 的引擎——
"转正"的正确路径是先把它的声明打回 trial，把伪分布修成真分布，再让它以指数级
试点身份第一次真正接入决策链。**
