---
ttl: task_bound
---

# 台风×BDI 事件因子：挖矿方案（2026-09-14）

> 母节点：**台风事件 × 航运运价（BDI）事件驱动因子**。
> 方法：挖矿 SOP v1.0.0（六向寻路/双噪音终止/防噪音四闸），本批 R1-R6 六向全扫，两轮 web 双 signal，时间盒封批。
> 数据底座（已全部在库）：`alt_typhoon_track` 127,930 行（2017+，含强度/风圈）、`alt_typhoon_landfall_history` 845 场（1949+）、`alt_shipping_index` BDI 9,537 交易日（1988+）、`alt_sz_port_monthly` TEU 月度 273 行、`alt_sz_marine_forecast` 147,716 行、`alt_sz_weather_warning` 9,349 行（源止 2020-09-23）。

---

## 0. 一页结论

1. **主卡立卡**：`EVT-TYPHOON-BDI-001`——强台风登陆（华东/华南主航线）后 BDI 5/10 日事件窗因子。先导 11 场实测后 10 日均值 **+8.86%（9/11 上涨）**，但 2025 年两场反例（蝴蝶 -24.6%/桦加沙 -12.4%）证明**方向受全球供需格局调制，不是无条件利多**——因子必须带强度+区域条件，并按事件研究纪律全样本验证。
2. **学术空白 = 双刃剑**：全网未检索到"台风×BDI 事件研究"直接文献（Zhang et al. 2026 只做网络层面威胁分析）——无现成结论可抄，但也意味着无拥挤交易。
3. **官方传导链背书**：交通运输部沿海散货运价月报明确记载"台风→港口封航→有效运力收缩→运价短暂走高→消退回落"（2026-09 报告实例）——机制真实，无需自证。
4. **关键反例必须入卡**：Arkansas 大学飓风×美国卡车运价研究未发现显著脉冲——"灾害→运价"并非普适规律，A股适配与窗口选择是本因子的核心工程量。
5. **施工路径**：全样本事件研究（C4 快筛）→ IC 网关（AltDataSignalExtractor 休眠件唤醒）→ 双窗口+衰减纪律（SOP-C §8）→ 策略库 sim 登记 → TDM 事件传导轴挂轴。工时 ~1 天。

## 1. 挖矿日志（六向寻路）

| 轮 | 矿脉 | 动作 | 判定 | 关键产出 |
|----|------|------|------|---------|
| R1 | ①上游（内部） | 表消费反查：alt_shipping_index/alt_typhoon_track 全仓 grep | signal | 零消费方（绿地确认）；bootstrap 治理接线已就位 |
| R2 | ②下游+④后端（内部） | 信号提取器/TDM/C4 快筛/策略库枚举 | signal | `AltDataSignalExtractor` 休眠件=现成 IC 网关（threshold 0.03 + half_life + 正交化 + CTR-002 出口）；C4 快筛引擎可复用；strategy_registry 156 条 STR 库为登记目的地；TDM 已有天气分方法论先例（滚动分位→加权合成，trading_decision_map.yaml L356） |
| R3 | ⑥数据字段（内部） | PIT/对齐精度核对 | signal | 事件日三口径（登陆日=landfall_history / 进关键区日=track 经纬度框 / 预警发布日=warning 表 2020 止）；BDI 为日度发布无前视；**增量锚 startDate=入库日期与登陆日不同轴**——回补用 crt_date，研究用登陆日 |
| R4 | ③算法/机制（全网） | SSRN/MDPI/PMC 事件研究检索 | signal | Zhang et al. 2026《Typhoon Threats to the Global Shipping Network》(MDPI Sustainability 18(7):3418)；COVID 冲击×BDI 事件研究范式（Chang 2023, MDPI 15(14):11367）；Kim 2025 BDI 金融数据预测（PMC12279113）；**反例**：U. Arkansas Walton College 飓风×卡车运价不显著；行业实证：台风 Bavi 上海港船舶活动 -50%（AXS Marine 2020）、台风 Dolphin BDI +3.3%（Bloomberg 转述） |
| R5 | A股适配（全网） | 券商事件驱动研报 + 官方运价月报 | signal | 交通运输部《中国沿海散货运输市场分析报告》2026-09 期：台风封航→运力收缩→运价短暂走高（官方传导链实证）；方法论模板：国盛"量价淘金"（四）事件→因子（2023-12）、（十三）事件簇规模化；东方证券事件驱动策略库（2024-12）；中金 A 股事件驱动十问十答；**确认空白**：无台风触发 A 股量化研报 |
| R6 | 失败模式（内部推演） | 混杂/样本量/多重检验推演 | signal（风险登记） | BDI 全球供需主导、台风是局部扰动——先导 11 场正效应存在幸存者疑虑；强登陆华东/华南年 3-6 场→全样本 n≈150-200（1988+），分强度后 n≈40-60，双窗口检验勉强够用；SOP-C §8 双窗口纪律强制 |

R1-R6 全 signal、零 noise、零受阻。**时间盒封批**（非挖干）：长尾矿脉见 §5。

## 2. 防噪音四闸过闸记录

| 闸 | 结果 |
|----|------|
| 来源可溯 | 全部外部发现带 URL+发布方+年份（§1 R4/R5 引文清单）；Bloomberg 转述的 Dolphin +3.3% 仅自媒体转载——降级为"行业轶事证据"不入卡 |
| 交叉验证 | 传导链"封航→运价走高"双源：交通运输部官方月报 + AXS Marine 港口活动数据 ✅；"灾害必然推高运价"**未通过**交叉验证（Arkansas 反例 + 2025 两场 A 股窗口反例）→ 因子定义为**条件因子** |
| A 股适配 | T+1：信号日收盘确认、T+1 执行；运价数据日度发布无前视；标的映射=航运港口板块（中远海能/招商轮船/宁波海运等敏感度分层）；台风对 A 股大盘无稳定方向，**只做板块/运价轮动不做择时** |
| 可回测+数据可得 | 全样本 1988-2025 可回测（landfall 845 场 × BDI 9,537 日 ✅ 在库）；强度/区域细化依赖 track 表 2017+（8 年）——分层回测样本量 GAP 已登记（§5 长尾） |

## 3. 因子卡（正式立卡）

### EVT-TYPHOON-BDI-001「强台风登陆×BDI 事件窗」

- **假说**：强台风（TY 及以上）登陆华东/华南主航线沿岸时，港口封航致有效运力短期收缩，BDI 在事件后 5-10 个交易日出现可测正脉冲；弱台风/远离主航线事件无效应。
- **证据**：先导 11 场（2026-09-12 实测）后 10 日 +8.86%（9/11 上涨），山竹/苏拉/海葵 2023 双台风 +32.9%/+43.6%；反例：蝴蝶/桦加沙 2025 -24.6%/-12.4%；官方机制背书 + 学术空白（§1）。
- **公式（草案，施工期定稿）**：
  - 事件集 E = {landfall_history 中 LANDLEV∈{TY,STY,SuperTY} ∧ LANDPROV∈{浙江,福建,广东,海南,上海,江苏}}（1988-2025，预计 n≈150-200；强子集 n≈40-60）
  - 信号 s(t) = 1 若 t ∈ [D0, D0+2]（D0=登陆日，track 表 2017+ 可用风圈/气压细化强度权重）
  - 因子值 f(t) = BDI(t)/BDI(D0-1) - 1 在窗口 N∈{5,10} 的累计收益；T+1 执行映射
- **消费方式**：① AltDataSignalExtractor 注册（feature_id=`evt_typhoon_bdi_10d`，half_life 待估）走 IC 网关；② TDM 事件传导轴挂轴（事件→运价→航运板块链）；③ 策略库 sim 登记（STR- 新条目，双窗口+DSR 纪律）
- **启动条件**：全部数据已在库 ✅；无外部依赖
- **工时**：全样本事件研究脚本+C4 快筛 0.5 天；IC 网关注册+双窗口验证 0.5 天；因子卡登记+TDM 挂轴 0.5 天
- **风险**：样本量（分强度后 n≈40-60，检验功效边缘）；混杂（BDI 全球供需主导——用"事件窗收益 - 同月历史基线"超额口径缓解）；幸存者偏差（先导 11 场是知名度高的大台风）

### 衍生候选（登记不施工，防候选堆积）

| 候选 | 一句话 | 启动条件 |
|------|--------|---------|
| EVT-TYPHOON-EQUITY-002 | 台风事件×A股航运板块个股（事件簇方法论，国盛 2023 模板） | 主卡全样本验证显著后 |
| EVT-WEATHER-HOG-003 | 台风×生猪区域价差（调运中断传导） | 主卡方法论复用；warning 表停更改用 track 表做事件源 |

### 不做（留痕防重复挖）

- 台风名字典/历史登陆档案：**字典类，不做因子**（仅作对齐辅助）
- 海洋预报：不做独立因子（作港口作业窗口辅助变量）
- 台风×A 股大盘择时：无稳定机制，不做

## 4. 施工图（批准后执行）

1. **P0 全样本事件研究**（0.5 天）：landfall 845 场 × BDI 对齐脚本 → 分强度/区域/年代窗口矩阵 → 出"是否显著"的初判（含 Arkansas 反例对照口径）
2. **P1 IC 网关+双窗口**（0.5 天）：AltDataSignalExtractor 唤醒注册 → IS/OOS 双窗（SOP-C §8）→ 衰减与正交化 → 门槛不过则**就地封矿留痕**
3. **P2 因子卡登记+挂轴**（0.5 天）：策略库 STR 条目 + TDM 事件传导轴 + 消费文档
4. **P3（可选）**：衍生候选 002/003 立项评审

## 5. 长尾矿脉清单（未挖，登记排下批）

- CNKI 中文文献深挖（台风×干散货运价中文学术界可能有现成实证）
- GARCH 波动率口径（台风×运价波动率而非均值）
- 保险板块映射（财险赔付逻辑）
- 港口拥堵高频代理（marine_forecast 作业窗口 × AIS 类数据，当前无 AIS 源）
- 强度权重细化（track 表 2017+ 的风圈/气压构建连续强度分）

## 6. 引文清单（来源可溯闸）

- Zhang et al., 2026, *Sustainability* 18(7):3418（MDPI）——台风对全球航运网络威胁：<https://www.mdpi.com/2071-1050/18/7/3418>
- Chang et al., 2023, *Sustainability* 15(14):11367（MDPI）——外生冲击×BDI 事件分析：<https://www.mdpi.com/2071-1050/15/14/11367>
- Kim, 2025, PMC12279113——BDI 金融数据预测：<https://pmc.ncbi.nlm.nih.gov/articles/PMC12279113/>
- U. Arkansas Walton College——飓风×卡车运价不显著（反例基准）：<https://walton.uark.edu/insights/posts/do_hurricanes_cause_freight_price_spikes_new_evidence_from_us_trucking_markets.php>
- AXS Marine, 2020——台风 Bavi 上海港船舶活动 -50%：<https://public.axsmarine.com/blog/super-typhoon-bavi-puts-china-ports-commodity-flows-and-pacific-vessel-supply-at-risk>
- 交通运输部《中国沿海（散货）运输市场分析报告》2026-09：<https://www.mot.gov.cn/shuju/yunjiazhishu/yanhaisanhuoyjzs/202609/t20260903_4223761.html>
- 国盛证券"量价淘金"（四）事件→因子，2023-12：<https://www.fxbaogao.com/detail/4065977>；（十三）事件簇：<https://www.sdyanbao.com/detail/905045>
- 中金《十问十答：A 股事件驱动的影响解析》：<https://zhuanlan.zhihu.com/p/1936076000350953657>
- Marsh《港口堵塞与航运延误》：<https://www.marsh.com/cn/zh/industries/marine/insights/port-congestion-risk-impact-on-shipping-delays-in-the-marine-market.html>
