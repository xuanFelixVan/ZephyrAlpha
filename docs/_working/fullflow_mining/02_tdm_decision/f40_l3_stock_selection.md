---
ttl: task_bound
title: F40 L3 个股选择——环节册（TD-A 前半）
session: st-ailayer-fullflow-td-a
creation_token: f40-l3-stock-book-tda-20260925
date: 2026-09-25
status: mined
---

# F40 L3 个股选择——环节册

> **一句话**：从全市场 5000+ 压缩到 10-20 只精选（业界漏斗压缩率 3000→10 参照）——Universe 剔除→九阶段主链→双池评分→负面否决→顺位→环境开关→策略专属链→候选池→分层维护→可交易预检→日内双通道→四维验证。
> 节点组：TDM-E-L3 + 01~12 组，共 25 节点。总册三态标 built｜P1｜T4。红节点：L3/L3-03/L3-07/L3-11/L3-12（structural 容器）；**L3-05 顺位与 L3-07 策略链容器 module_ref=null（structural 正常）**。

## 一、环节定义与边界

- **供料方**：F39 板块调节分+龙头定位（只两字段）；DS-150 日线/DS-082 涨停池/DS-181 资金流。
- **消费方**：F41 L4（最终候选池 10-20 只带 sleeve 标签+顺位分）；L3-09 持久池喂次日；L3-11-2 观察池喂盘中。

## 二、判定输入 / 输出

| 子环节 | 判定输入 | 判定输出 |
|--------|---------|---------|
| 01 Universe | 停牌/ST/退市风险/上市<60 日/市值<30 亿/日成交<5000 万 | ~3000 只 Universe |
| 02 九阶段主链 | Universe | 动量→流动性→波动率带→趋势→相对强度→量价→形态→负面→精选，每阶段砍 50-70% |
| 03 双池评分 | 精选池 | 短线池 5 分制（涨停基因/题材纯正/龙头定位/情绪位置/分时强度，≥4 进精选）+波段池 5 分制（趋势/量能/相对强度/回踩 A-B 级/筹码低位，≥4）；合流三维共振（趋势/资金/形态，**≥2 维达标才保留**防单因子幻觉） |
| 04 负面否决 | 公告/财务 | 七条一票否决：业绩暴雷/立案调查/大股东减持/解禁>5% 流通盘/商誉减值/配股圈钱/**高应计（Sloan，fundamentals.accrual_negative_screen 产出，裁定#231 2026-09-14 增补）**——命中即出池，优先级高于一切加分 |
| 05 顺位 | 候选特征 | 六顺位 妖>龙>中军>核心>趋势>跟风=资金分配顺序——**码面无枚举，见堵点 1**（码面 selection_confidence 实际输出 event/daban/multifactor 三类置信分，RankIC≥0.05 满分） |
| 06 环境开关 | L1 六段+两市成交额 | 六段×四开关封闭查表（首板/短线/波段/收紧）；成交<8000 亿=首板停（实证：地量首板次日溢价为负）；冰点=短线链全停；euphoria=反向收紧；未知状态 fail-closed |
| 07 策略专属链 | 各 sleeve 自选链 | 打板 5 步漏斗（板块前 3→涨停股→剔烂板→封单/流通盘>2%→龙头定位；码面=四引擎组装 Top-N≤10，负载从 c1_market.daban_engine_load PIT 真读：max(trade_date)<T 最近事件日分区+逐行剔除 day>=as_of 双保险，回退必发恰好一条 WARNING，2026-09-16 E2 接线）；多因子 IC 加权（60 日衰减，前 20 只，单行业≤4）；eventdriven 提前 3 日/topn 20 日动量/default 宽基网格 |
| 08 候选池输出 | 双池合流+策略链候选 | 最终池 10-20 只（**否决只标记不剔除**、去重确定序、三来源注入零 IO，37 单测） |
| 09 分层维护 | 漏斗日产出 | Tier1 精选/Tier2 观察/Tier3 备选：连续 2 日达标升、5 日不达标降、10 日陈旧剔、连击清零防连跳、一次一事；**池成员持久化归治理状态表/新 DS——外审 M-41 欠账待登记** |
| 10 可交易预检 | 停牌/一字/权限/资金/笼子 | 五查独立标签 fail-closed（SUSPENDED/LIMIT_UP/PERMISSION/LOT_CASH/DATA_MISSING）+笼子夹边建议价（CLAMPED 语义=夹边建议非拒单，按 ex_core 实装口径修正节点散文"会被拒"）；账户上下文缺省时权限查降级 detail 不阻断（L4-12 会再查）；2026-09-16 MOD-SIG-151 落码 |
| 11 日内双通道 | 竞价快照/涨速榜 | 竞价（9:26-9:28：量比>5+涨幅 2-5%+匹配量大单主导）；涨速（3-7% 拉升+5 分钟>2%+量比>3+非跟风；黄金窗 9:30-10:30，午后拉尾谨慎） |
| 12 四维验证 | 资金/席位/筹码/形态 | ≥3 维正面才进最终池。资金：大单净额/成交额≥20%；筹码：**裁定#257④ 量纲修复后回 trial——引擎现输出 4 指标（long_term_bottom_ratio/upper_trap_peak/bottom_accumulation/distribution_migration），节点"获利盘占比/单峰密集"语义未实现挂起（需流通股本数据工程），trial 期本维度信号不进决策** |

## 三、判定用离散状态集合

| 状态集 | 离散值与阈值 | 真源 file:line |
|--------|-------------|---------------|
| 环境开关六段×四开关 | _SWITCH_TABLE 封闭查表（bool×4），地量/冰点/疯狂三硬规则叠加 | environment_switch.py:40,80-90 |
| 回踩 A/B/C（消费侧） | 波段池评分 1 分=回踩 A/B 级；L4-01 分批置信度调节因子 | sector_pullback.py（L2-07 供） |
| 负面否决七条 | 二值（命中/未命中），优先级压倒加分 | negative_veto.py（DEDUP/ALGO_FLOW 外迁注） |
| 双池 5 分制 | 0-5 整数分，≥4 精选线 | fine_scoring_engine.py / quant_short_term_strength_engine.py |
| 分层三 Tier | TIER1/2/3 升降剔封闭规则 | pool_tier_maintenance.py 节点注 |
| 可交易五查标签 | SUSPENDED/LIMIT_UP/PERMISSION/LOT_CASH/DATA_MISSING + CLAMPED 笼子 | tradability_preflight.py:55 BlockedReason，:120 起 |
| 四维验证 | 每维正面/负面二值，≥3/4 通过 | L3-12 容器判据；筹码维 trial 期退出决策 |
| 打板 Top-N | final_score 降序 ≤10 | daban_sleeve_strategy.py 节点注 |

## 四、子模块清单与实件校验

22 个 module_ref 全部在盘（零缺件）。注记：L3-05 selection_confidence 与 L3-07-2 multifactor_synthesis 均在盘但与节点散文判据存在语义差（见堵点）；L3-08 candidate_pool_aggregator=2026-09-11 晚批落码（C13 纯函数核范式，设计态待 MOD id 统筹登记——**depgraph 登记欠账**）；L3-12-3 chip_distribution_engine 裁定#257④ 修订注已回填（note_confirmed 2026-09-16）。

## 五、触发链与当日闭环证据

- **盘后链**：漏斗/双池/否决/候选池属盘后批（activation=postmarket），经 dloop_post 日循环与 sector_state 面板供数。
- **盘前链**：L3-06 环境开关（premarket）+L3-10 可交易预检（premarket）在开盘前收口。
- **盘中链**：L3-11-1 竞价 9:26-9:28、L3-11-2 涨速扫描 9:30-10:30、L3-07-1 打板链盘中（负载读 T-1 事件日分区）。
- **持久池**：L3-09 日更（池成员持久化欠新 DS 登记，M-41）。
- 消费对接：daily_gate_snapshot 的 L2 admission 三原料"判定归 G05 选股引擎"——G05 未激活（同 F39 堵点 3）。

## 六、验证欠账清单（命中 25 件，全 untested——整层零验证运行）

| object_id | 对象 | 状态 |
|-----------|------|------|
| BT-P2-030 / 034 / 037 | L3 / L3-11 / L3-12 容器 | untested，testable=False |
| BT-P1-014~026 | 九阶段主链/双池/否决/顺位/环境开关/三链/候选池 13 件 | untested，plan=None |
| BT-P2-031~033, 035~036, 038~041 | Universe/分层/预检/竞价/涨速/四维 11 件 | untested，plan=None |

strategy_mounts 佐证：L3 节点挂载 8 sleeve 引用中 6 个 confidence=proposed evidence=None（仅 L3-07-3 的 STR-TSMALL-001/STR-VAL-001 verified 有 run 号）——S2 场景"该策略回测就是节点判据的验证证据，回填 evidence"在本层大面积未做。

## 七、堵点与病灶

1. **L3-05 六顺位判据-码面差异**：节点散文"妖>龙>中军>核心>趋势>跟风"在 selection_confidence.py 无对应枚举/排序函数（码面=三类置信分计算）｜修法：a) 码面补顺位分级（类别映射+同分 tie-break，1 天）或 b) S4 场景改判据为"置信分降序+打板/事件/多因子类内顺位"（D 裁定）｜判断成本低的 a 优先。
2. **L3-12-3 筹码维 trial 挂起**：四维验证实际三维在决策——"获利盘/单峰密集"需流通股本数据工程｜修法：数据工程立卡（M1 交界）或 S4 改判据为四指标语义；trial 解除须重跑回测（裁定#257④ "回 trial"承诺）。
3. **L3-09 池成员持久化无 SSOT**：外审 M-41 欠账——分层状态机的"昨日 Tier"无落库真源，升降剔规则空转风险｜修法：登记新 DS+治理状态表（0.5 天）。
4. **L3-08 候选池聚合器 depgraph 待统筹登记**（节点注自认"设计态待 MOD id 统筹"）——按 RULE-DEPGRAPH 属登记欠账非施工欠账｜0.5 小时。
5. **整层 25 件零验证**：同 F39 病灶——阈值预注册为瓶颈工序，传感器/漏斗类可用 sensor_monotonicity+exit_counterfactual 批量冻结。

## 八、三态自审

**挖干可施工**（实件零缺；两处判据-码面差异（顺位/筹码语义）+两处登记欠账（M-41/MOD id）已列修法；验证欠账 25 件路径明确）。

## 九、复核命令

```bash
sed -n '40,90p' src/zephyr/signal_ashare/core/environment_switch.py   # 六段×四开关表
sed -n '55,130p' src/zephyr/signal_ashare/tradability_preflight.py   # 五查
grep -n "def compute_" src/zephyr/signal_fundamental/selection_confidence.py  # 验证堵点1（无顺位枚举）
grep -n "获利盘\|单峰" config/trading_decision_map.yaml | head -3     # L3-12-3 挂起注
grep -n "M-41\|池成员持久化" config/trading_decision_map.yaml
```
