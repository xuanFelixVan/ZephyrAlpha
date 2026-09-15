---
ttl: task_bound
title: T1-α 节点挖矿：整装回测决策内核（decision kernel）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 节点挖矿：整装回测决策内核（父环节 S11_assembled_backtest）

> 挖矿依据：kimi_deep_mining_charter §3 T1-α——"全景图决策逻辑本身：sleeve 权重生成/
> regime 切换/调仓频率/风控叠加/再平衡/现金管理/滑点与冲击成本建模/整装回测 runner 算法
> （三桥已接，决策内核没人挖过）"。S11 环节 README（st-fullauto-20260915）挖的是**接线**
> （断桥①②③+三件施工），本节点挖**算法本体**——组合数学、成员权重生成、成本与执行约束、
> 现金语义。产出=数据，采纳裁定归主力会话施工班。

## 1 现状盘点（基于投喂材料，逐条带 file:line 锚点）

### 1.1 合成层（framework_composer.py，MOD-FWCOMP-001）

- 静态合成 `compose_weight_panels`（framework_composer.py:381-490）：`W(t,s)=Σα_i·w_i`，
  参与成员 α 合计<1 时显式等比再归一（rescale_factor=1/α_total，L443-454）；随后**行级
  Σw 归一至 1.0**（L466-474，偏差>1e-9 记 notes）；全零行保留=现金日。
- 动态合成 `_compose_weight_panels_dynamic`（L579-683）：逐日查 `regime_overrides` 取
  α_i(t)，未覆盖 regime/日期归 `__base__` 组回退基准权重；各组独立校验+再归一；
  `regime_day_counts`/`regime_rescale_factors` 全披露（L620-653）。
- 面板对账 `verify_weight_panel_identity`（L686-751）：独立复算（不调 compose，防同源
  盲区）逐位 1e-9 硬验收。数学审查结论：**正确**——复算口径与 compose 可观察输出对齐
  （组内 rescale 后行归一吞掉 rescale，L734-739 注释自证）；NAV 层执行残差明确排除在
  容差外（归因披露），边界清晰。
- per-regime 分段摘要 `per_regime_summary`（L754-810）：组首日以上一净值点为基的链式
  贡献语义——数学自洽，仅作分段归因不可加（docstring 自述）。
- NAV 对账 `reconcile_composed_nav`（L818-889）：manual=Σ(α_i/α_participants)·nav_i
  （L858-864，与合成侧 rescale 同口径）。**边界缺口**：合成侧是"rescale×逐日行归一"
  双层，manual 侧是常数归一——成员面板行和=1 时两者逐位一致；成员某日返回空权重
  （行和=0）时 composed 该行为现金日而 manual>0，产生对账假阳性（静态模式适用场景，
  低频触碰，登记不施工）。

### 1.2 成员面板生成层（strategy_runner.py）

- `build_weight_panel`（strategy_runner.py:381-405）：load_history→因子面板→截面合成
  synthesize→PIT shift(1)→调仓日调策略权→ffill。
- **全员同参**（FrameworkBacktestConfig，framework_composer.py:988-993 v1 简化自述）：
  factor_ids=("momentum_20d",) 一个因子喂所有 kebab 成员；rebalance_freq=W-FRI 全员
  统一；top_n=10/max_single=0.10 全员统一。
- 调仓日选取 `_select_rebalance_dates`（strategy_runner.py:480-494）：每 freq 周期最后
  交易日（节假日鲁棒）；"B"=每日。
- 信号传递 `_rebalance_one_day`（L462-478）：**扁平标量契约** `signals={sym: float(v)}`。

### 1.3 成员权重函数信号契约逐一核对（本挖矿核心实证）

| 成员 | 期望 signals 形态 | 锚点 | 收到扁平标量后 |
|------|------------------|------|---------------|
| default-equity | {sym: float}（且默认 EQUAL_WEIGHT 模式忽略信号） | default_equity_strategy.py:139-174 | **正常参与**（等权） |
| topn-momentum | {sym: float} | topn_momentum_strategy.py:115-142 | **正常参与** |
| multifactor-sleeve | {sym: {factor_id: value}} 嵌套 | multifactor_sleeve_strategy.py:126-173（L153-156 取 per_sym 为 dict 的 factor_ids；非 dict→空→return {}） | **恒返回 {}——死成员** |
| daban-sleeve | {sym: payload dict}（四引擎负载） | daban_sleeve_strategy.py:181-218（L211 `if not isinstance(payload, dict): continue`） | **恒返回 {}——死成员** |
| eventdriven-sleeve | {sym: dict} 嵌套 | event_driven_sleeve_strategy.py:147-156 | **恒返回 {}——死成员** |
| 做T 三件 | tick-only | framework_composer.py:1001-1013 | skipped+披露 |

**前科佐证**：event_sentiment_adapter.py 模块头注自证"BTRUN_report §3.1 实证标量信号下
返回空权重"，并为此建了情绪分适配层 `build_event_weight_panel`（MOD-L05-001，
event_sentiment_adapter.py:31-38）——**但该适配层只接在回测跑批脚本，未接进
framework_composer._build_member_panels（L1016-1069 只有 STR- 前缀/kebab 原路两路路由）**。

### 1.4 量化后果（fw-tdm-current 16 员口径，framework_plans.yaml:243-291）

死成员+tick-skipped 权重质量 = multifactor 0.126 + daban 0.0945 + eventdriven 0.063
+ 做T 三件 0.1575 = **0.441**；真实参与 = STR-* 八件 0.37 + default-equity 0.126 +
topn-momentum 0.063 = 0.559 → 合成后显式再归一 ×1.789。**有效组合=STR 66.2% +
default-equity 22.5% + topn-momentum 11.3%**——与方案表"16 员各就各位"的纸面意图严重
偏离。三套人工预设同病：fw-balanced 死质量 0.40（multifactor 0.25+daban 0.10+做T 0.05），
有效组合=2 员再归一。该偏离不在 skipped 名单（面板非空、只是行全零），仅在 notes 里以
"行级 Σw 偏差已归一"的数字形态留痕——**语义上没有披露"死成员捐权重"**。

### 1.5 执行与成本层（vectorized_engine.py + matching_logic.py）

- 前视防护：execution_lag_days=1（T 日执行 T-1 日信号）、成交价=次日开盘优先/收盘兜底
  （vectorized_engine.py:199-206/227-251）——A 股 T+1 适配正确。
- 流动性：max_participation_rate=10%+Almgren-Chriss 冲击成本（P0-2，L112-114/161-165，
  复用 execution_simulation 真源）；无 volume 列时旁路+warn 一次（L241-245）。
- PIT 标的池：未上市/退市/ST/次新<120 日剔除（P0-3，L115-118）；CH 不可达 fail-open。
- 成本费率：印花税万5 卖出单边+过户费万0.1 双向（matching_logic.py:67-77，2023-08 法定
  口径）；最低佣金门槛存在（matching_engine.py:611 max(gross*rate, min_comm)）。
- **佣金默认万 0.854**（vectorized_engine.py:104 `Decimal("0.0000854")`）——低于常见
  零佣档（万 1~万 2.5），且与同文件 docstring 示例"万三=0.0003"（L80）不一致。
  **已裁定（Owner 2026-09-15）**：万 0.854=券商合作价，费率正确；欠账仅剩 docstring
  示例与默认值不一致的文字修正（T1A-4 降级为文档项）。
- 滑点默认 1bp 固定（L105）——对日频低换手偏乐观但方向安全（冲击成本层另有覆盖）。
- 合理性护栏 sanity_guard（P0-4，L119-123/351-360）：极端收益/trades=0 fail-closed。

### 1.6 现金与风控叠加（组合层语义审查）

- 现金管理：**不存在**。合成侧行归一（L466-474）+引擎侧 Σ=1 满仓归一
  （vectorized_engine.py:180-185 头注自证"Σ<1 的强度面板会被放大为满仓"）双层夹击，
  成员现金意图（行和<1）在组合层必被吞掉；唯一现金表达=全员全零行（现金日）。
- 风控叠加：组合层无回撤控制、无波动率目标、无相关性约束——regime 查表是唯一
  组合级风控；成员级仅 top_n/max_single 数量约束。与 TDM PP-001 的风控节点
  （如有）无执行层联动。
- regime 切换：纯查表无迟滞（hysteresis）——状态翻转日 α 全组跳变，换手与成本随行；
  `__base__` 回退组的存在（L92-93）使 r1/r2/r11 三态实际跑基准权重（三套预设只覆盖
  r3/r12/r4/r10，framework_plans.yaml:70/134/197）。
- activation 态不生效：fw-tdm-current 的 activation 只落 role/x_tdm_provenance 记录
  （framework_plans.yaml:241-242/298-314 自述 static_mode=true，"动态化待其支持零权重
  成员"——composer 权重合法域 (0,1] 不收 0，_parse_plan_weights L241 硬校验）。
  例：STR-VREV-025 activation=capitulation，回测中却全段持 4.5% 在仓。

### 1.7 方案真源治理

- fw-tdm-current=生成器产物（generate_framework_plan_from_tdm.py，禁手工维护，运维
  红线 5 合规）；三套人工预设 regime_overrides 头注"AI 代拟，Owner 审核后生效"，
  review_status 注释称基准权重已批、覆盖表"本会话裁定留痕"——**覆盖表的 Owner 裁定
  是否落 ruling_registry 待核**（本挖矿未查到对应裁定条目，标待验证）。

## 2 六向挖矿日志表

| 向 | 内部发现 | 外部发现（URL+发布方+年份） | 判定 |
|----|---------|---------------------------|------|
| ①上游 | 成员信号源单一：全员共享 momentum_20d 因子面板（framework_composer.py:988）；daban/eventdriven 的正主信号（打板漏斗负载/情绪分）无路进入 composer 路由（1.3 节实证） | 多策略组合成员应各自带信号源再进组合层（Man Group 多策略构建，man.com，2026 前后沿用；S11 README R7 已引） | signal |
| ②下游 | 整装产物 bt-fw-*.json 只进 data/backtest_artifacts+fw-auto 证据包；无消费方回灌 TDM/组合层（无"整装结果→sleeve 权重再校准"闭环） | 组合回测结果应反馈 sleeve 权重校准（walk-forward 组合校准，QuantInsti WFO，blog.quantinsti.com，2023-2025；S11 README 已登记远期） | signal |
| ③机制 | 死成员/现金吞没/activation 不生效/regime 无迟滞四大发现（1.3/1.4/1.6） | regime 切换配置框架含状态持续期与切换成本约束（MDPI Mathematics 13(17):2837，mdpi.com，2025）；宏观 regime TAA 含换手惩罚（arXiv:2503.11499，2025）；再平衡频率×交易成本权衡、阈值带 vs 日历制（techwhims.com/tradesys/macro/rebalance-optimization/，2026） | signal |
| ④后端 | 成员适配缺 payload 路；event_sentiment_adapter 现成未接（1.3）；composer 权重域 (0,1] 不收 0 阻断零权重成员表达（_parse_plan_weights L241） | 引擎层"权重面板进引擎"模式与业界同构（MathWorks Financial Toolbox，mathworks.com，2025 文档；S11 README 已引）——架构选型不改，缺的是成员侧适配 | signal |
| ⑤前端 | fw-* 方案与整装回测仅 api_server 两端点+manifest 消费；per_regime 摘要已透出 done 响应（L1224-1228）——面板级/呈现无新矿 | —（前端只登记不施工） | 已查无 |
| ⑥数据字段 | 死成员修复需的字段：打板 payload（selector/youzi/quant/fusion 四引擎输入）与事件情绪分（news_sentiment_window 已回填 19,756 行，event_sentiment_adapter.py:33-34）——**数据都在库**，缺的只是接线；佣金费率实际值（Owner 口径） | — | signal |

**计数：signal 5 / noise 0 / 受阻 0 / 已查无 1（⑤前端）。**

## 3 业界与开源对照（逐条过四闸结论）

| 对照项 | 来源（URL+年份） | 四闸结论 |
|--------|-----------------|---------|
| regime 切换权重框架（状态持续期/切换成本约束） | MDPI Mathematics 13(17):2837，mdpi.com，2025；arXiv:2503.11499，2025 | **立卡候选**：查表+回退+全披露已达骨架；缺切换迟滞/最小持续期/换手惩罚。A 股适配：T+1 下日频切换成本更高，迟滞收益更大。可回测（regime_snapshot_history 现成）。**待验证**（单来源+摘要级，施工前补第二来源） |
| 再平衡：日历制 vs 阈值带 | techwhims.com/tradesys/macro/rebalance-optimization/，2026；CSDN 周期阈值算法实操（blog.csdn.net/weitingfu/article/details/164204323），2026 | **登记远期**：W-FRI 日历制对本组合（低频、成员权重本身稳定）不是当前主要矛盾；死成员修复后换手结构才真实 |
| 现金/满仓纪律 | Rob Carver 系统化交易博客（qoppac.blogspot.com，2023）；DolphinDB A 股中低频组合回测教程（docs.dolphindb.cn，2024） | **对等已有+口径待裁定**：Σ=1 归一+禁静默披露与业界同款；但"组合层是否允许现金权重"是 Owner 裁定点（本引擎明确满仓语义，头注留痕 2026-08-19 AI-NIGHT-001 对齐） |
| 冲击成本模型 | Almgren-Chriss 已接（execution_simulation 真源，vectorized_engine.py:161-165） | **对等已有**：参与率上限+冲击成本为业界标准做法，无需立卡 |
| 组合回测反馈校准 sleeve 权重 | QuantInsti WFO（blog.quantinsti.com，2023-2025）；S11 README R7 已引 | **挂起排期**：对应 S11 README 欠账 7（walk-forward/归因章），不与本节点重复立项 |

## 4 堵点与欠账清单（concrete：文件/函数/验收标准——施工班直接消费）

| # | 堵点 | 位置 | 验收标准 |
|---|------|------|---------|
| T1A-1 | **死成员三件适配**（本挖矿最高优先）：composer 成员路由增 payload 路——eventdriven 复用 `event_sentiment_adapter.build_event_weight_panel`；multifactor 把扁平信号包 `{sym: {factor_id: val}}`（注意 runner 只喂 momentum_20d 一个因子，包嵌套后 multifactor 也只吃一个因子，修复后其选股=单因子 Top20）；daban 的四引擎负载无日频批产源，短期建议从 fw-tdm-current/fw-balanced **移除或显式置 0（需 composer 支持 0 权重）+披露**，而非硬造负载 | framework_composer.py:1016-1069（路由）；event_sentiment_adapter.py（现成适配层）；_parse_plan_weights L241（0 权重域） | fw-tdm-current 重跑：参与成员全部真出权重或 skipped 带明确 reason；notes 无"行级 Σw 偏差已归一"大额条目；产物 metrics 增 dead_weight_disclosed 字段 |
| T1A-2 | **死成员静默披露缺口**：行全零成员（面板非空但恒空权重）应进 skipped 或独立 dead_members 披露，而非靠行归一 notes 数字暗示 | framework_composer.py:429-435（panel empty 判定只查 DataFrame.empty） | 单成员面板行和恒 0 → 落 skipped("all-zero weight rows")；测试覆盖 |
| T1A-3 | **activation 态生效**：composer 支持 0 权重成员（合法域含 0）后，fw-tdm-current 动态化——activation 非当日态的成员 α=0 | framework_plans.yaml:241-242 自述阻断；framework_composer.py:241 | 动态整装回测：STR-VREV-025 仅 capitulation 日在仓；regime_day_counts 含各 activation 组 |
| T1A-4 | **佣金费率口径统一**：费率本身已裁定正确（万 0.854=券商合作价，Owner 2026-09-15）；剩 docstring 示例（万 3）与默认值不一致的文字修正+费率常量单一真源（matching_logic 与 vectorized_engine 同源引用） | vectorized_engine.py:104 vs L80 | docstring 修正；费率常量同源引用 |
| T1A-5 | **regime 覆盖补全或显式裁定**：r1/r2/r11 回退基准是否合理（低波震荡期跑进攻权重值得怀疑）需 Owner 裁定；三套预设覆盖表 AI 代拟的 Owner 批准裁定落 ruling_registry | framework_plans.yaml:70-106/134-166/197-233 | ruling 条目存在；覆盖表状态与裁定一致 |
| T1A-6 | **regime 切换迟滞**（远期）：α 切换加最小持续期/死区，或按切换日成本预算闸 | framework_composer.py:579-683 | 回测对比：迟滞开/关的换手率与净收益差（施工前补 MDPI 2025 第二来源验证） |
| T1A-7 | NAV 对账假阳性边界：成员空权重日 manual/composed 分叉——披露或对齐口径 | framework_composer.py:858-864 | 登记（低频触碰，不阻施工） |
| T1A-8 | scaffold md 子命令 `--force-override` 未暴露（本次被 alias 误拦的通道缺失） | scripts/scaffold.py md argparse | 登记工具欠账 |

## 5 子节点清单（挖出的新矿脉）

| 节点 | 为什么值得挖 | 建议投喂材料 |
|------|-------------|-------------|
| regime_detector 七态判定内核 | "regime 错=权重错"生死线的判定本体：七态语义/HMM walk-forward 自动回放（framework_composer.py:62-63 自述"另批立项"）从未被挖过；r1/r2/r11 无覆盖表的根因也在这端 | src/zephyr/regime/core/regime_detector.py + shrinkage_provider.py + c1_backtest regime_snapshot_history 写读链 |
| TDM PP-001 sleeves 权重生成逻辑本体 | auto_mount sleeve_plan 新 sleeve 0.05 等权起步/老 sleeve 等比缩水（S11 README §1.3）——这套资金分配规则本身没有业界对照过，0.05 起步是否合理从未论证 | auto_mount.py sleeve_plan 段 + trading_decision_map.yaml portfolio_plan + auto-mount-report |
| 组合层风控叠加（与 S15 衰减监控衔接） | 组合层唯一风控=regime 查表；无回撤控制/波动目标/相关性约束；S15 判死回灌闭环是否该在组合层有执行位 | TDM 风控节点 + S15 README + pf_alloc/core 库边界 |
| 打板/事件负载的日频批产源（T1A-1 的数据侧） | daban 四引擎负载若要真进整装，需要日频负载生产件（现只服务单策略回测跑批）——是接线前必答的"数据从哪来" | daban_sleeve_strategy.py 四引擎 + event_sentiment_adapter + 漏斗①产出件 |

## 6 封矿判定

- **核心矿已挖透，本节点未枯竭但主体封批**：合成/对账数学四问结论=正确（面板对账
  独立复算、行归一与 rescale 口径对齐、per-regime 链式贡献自洽）；四大内核发现
  （死成员/现金吞没/activation 不生效/regime 无迟滞+覆盖 4/7 态）已 concrete 到
  file:line+验收标准（§4 T1A-1~6）；外部对照过四闸（§3）。
- **未枯竭部分已转子节点**（§5 四件）：regime_detector 内核、TDM sleeves 生成逻辑、
  组合层风控叠加、打板/事件负载批产源——属 T1-α 范围内的新矿脉，待下一轮投喂。
- 一句话结论：**整装回测的"三桥"接线是通的，但桥上跑的组合是假的——16 员方案里
  44.1% 权重质量由死成员与 tick 跳过员构成，经显式再归一 ×1.789 静默摊给了幸存成员；
  修复优先级 T1A-1（死成员适配/移除+披露）> T1A-2（静默披露）> T1A-3（activation）
  > T1A-4/5（口径与裁定）> T1A-6（迟滞，远期）。**
