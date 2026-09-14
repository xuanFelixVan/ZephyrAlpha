---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L157: | R7 | 长尾·扩展V+倒扇贝 | **signal** | vtopbot.html See-also 证实 Extended V 独立章；aiscallop/idscallops 双页核实（伞形右半，牛熊双市均佳）→ CHART-079/080/081，扇贝族 4 型收官 |
>
> **⚠️ 未完成（5 条，逐条摘录）**
> - L70: | PAT-STRUCT-042 | Market Profile 结构（未完成拍卖） | Dalton《Mind Over Markets》+ CBOT；GoCharting/LuxAlgo/Vtrender 交叉 | SR-006 静态量价分布的结构事件语义扩展（Virgin POC 磁吸/端部
> - L119: - **P3（重依赖）**：FIB-018 Nen Star——谐波引擎整体未建（FIB-007~018 全族
> - L161: （Top-5 已采，其余 15 条低价值挂起）、Busted 族（已采）、岛形族（Long Island
> - L162: 驳回终态）、扇贝族（收官）、扩展V（已采）；仍然挂起：量廓形状（判据未定）、
> - L196: pattern_catalog_sync 扩展为常设校验器（登记为待施工项，防字段漂移）。
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 2 个，其中判废弃 0、路径漂移 0）+ commit 提及 1 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# [BLUEPRINT] | docs/_working/2026-09-14-chart-pattern-mining-report.md |
<!-- [MODULE] MOD-SIG-145 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# 图形库"病菌寻路"全网挖矿报告（st-patmine-20260914，2026-09-14）

> 任务：挖掘现有 256 条目录之外的技术图形入库候选。方法论=挖矿 SOP
> （docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md）六向寻路+防噪音四闸
> +双噪音终止。上会话遗留（治理报告 §四 9 条 Bulkowski 候选因 thepatternsite 超时+Wiley 403
> 停在"待核对"）由本批网络窗口补核对。产出：**19 条新登记（256→275）**+驳回 2+长尾清单。

## 一、冷启动与通道自证

- Python 3.12.8 ✓ / process_reaper 存活（last_run 2026-09-14 07:37）✓ / 挖矿 SOP 全文已读 ✓
- 网络通道：WebFetch 直连 thepatternsite.com 与 web.archive.org 双双超时（与上会话同病）；
  **web_reader MCP 通道可直连 thepatternsite**（本批关键基建发现）——Pattern Index 全目录
  与 Roof 页全文均经此通道取得；WebSearch（服务端代理）可用，限流 429 按 SOP 60-130s
  单发节律穿行，全程 3 次超时 2 次自愈。

## 二、挖矿日志表（SOP §6 必载）

| 轮 | 矿脉 | 动作 | 判定 | 关键产出 |
|---|------|------|------|---------|
| R1 | ①连通性 | WebFetch 直连×2 | 受阻→换道 | web_reader 通道突破（受阻≠查无，记档） |
| R2 | ①量度移动 | 搜 mmu/mmd | **signal** | 第二腿≈第一腿(幅度+时长)，失败率 23%；MMD 约束=D 低于 C（修正过深失败率升） |
| R3 | ①直角扩散 | 搜 rabfa/rabfd | **signal** | 平底+上升高点=熊反（切片 159% 涨/64% 败）；平顶+下降低点=牛反；partial rise 预警 |
| R4 | ①Eve&Adam | 搜 aadb/aedb/eedt 族 | **signal** | 双底/双顶各 4 变体（Adam=尖刺/Eve=圆阔），EOC3 p.398/419/438 独立章 |
| R5 | ①反死猫跳 | 搜 idcb | **signal** | 单日暴涨 5-20%+ 后缓幅回落，事件形态，dcb.html 镜像页互证 |
| R6 | ①直线运行 | 搜 straight-line run | **noise→驳回** | 无独立条目页，仅旗杆属性/overlap 突破统计条件 |
| R7 | ①财报旗形 | 搜 earnflag | **signal** | 事件形态=业绩公告跳空+旗面持续；A股锚=c3_fundamental.announce_date(PIT) |
| R8 | ①双沟 | 搜 gutters×2（1 超时重试） | **signal(更名)** | Gutters 非标准名，实名=**Inverted Roof**（iroof.html），Roof 族一体登记 |
| R9 | ①全量差额 | web_reader 读 Pattern Index 全文 | **signal 爆发** | 权威全目录到手（含 2025-02 新增 5 条小形态）；逐项 diff 我方 256 条 |
| R10 | ①新候选逐核 | 搜 abw/dbw/udb/FlatBase/InsideDays/2B | **signal** | 扩散楔形×2、丑陋双底(两谷差≥5%)、平台基底(O'Neil+IBD 双源)、内包日、2B(Sperandeo 三源) |
| R11 | ②谐波 | 搜 Carney 全集 | **signal(1 条)** | 核心 11 条已在册；唯一缺标准项=Nen Star（12 型扫描器集成员）；Anti 系/黑白天鹅→长尾 |
| R12 | ③量价/订单流 | 搜 Market Profile 结构 | **signal** | Virgin POC/Poor High-Low/Single Print/Excess 结构族（Dalton《Mind Over Markets》多源） |
| R13 | ④A股技术派 | 搜 量学黄金柱 | **signal** | 黄金柱判定可量化（基柱实顶线+后三日站稳+价升量缩），张得一《量柱擒涨停》2009 多源 |
| R14 | ⑤波浪/缠论 | 搜 chan.py 中枢生长 | 登记级 noise | 中枢新生/延伸/扩张/扩展+小转大=现有 PAT-CLL-006 行为细化→实现细化清单，不新增条目 |
| R15 | ⑥学术 | 搜 motif 挖矿论文 | 登记级 noise | 方法论指针存档：Martiny2012/Hu2019(Applied Soft Computing)/Cremona2025(SSRN)/JPM 无监督；STRUCT-017/018 已锚方法族 |

终止判定：15 轮 signal 矿脉 11 个、noise 2 个、受阻 1 次换道后转 signal；**双噪音未触发**
（长尾矿脉仍在，按 SOP §4 时间盒封批，长尾见 §五）。候选总量 19（<20 上限），未触
"候选堆积不落地"红线。

## 三、登记批：19 条（chart_pattern_registry.yaml v2.15.0→v2.16.0，256→275）

| 新 ID | 形态 | 来源（doc_ref 摘要） | 差额论证 | direction |
|-------|------|---------------------|---------|-----------|
| PAT-CHART-063 | Measured Move Up 量度上涨 | thepatternsite.com/mmu.html + EOC3 | 目录 62 条无数值目标投影类形态；与箱体/旗形量度联动 | long |
| PAT-CHART-064 | Measured Move Down 量度下跌 | thepatternsite.com/mmd.html + EOC3 | 镜像缺口；D 低于 C 约束独有 | short |
| PAT-CHART-065 | 直角上升扩散 RABF-A | thepatternsite.com/rabfa.html + EOC3 Ch.9 | 021 只有对称扩散；本条平底熊反 | short |
| PAT-CHART-066 | 直角下降扩散 RABF-D | thepatternsite.com/rabfd.html + EOC3 Ch.10 | 平顶牛向镜像 | long |
| PAT-CHART-067 | 上升扩散楔形 ABW | thepatternsite.com/abw.html + EOC3 | 与 065 区分=双边界同向上升；牛市多发熊市罕见 | short |
| PAT-CHART-068 | 下降扩散楔形 DBW | thepatternsite.com/dbw.html + EOC3 | 镜像；ppBWD busted 配对交易法 | long |
| PAT-CHART-069 | 亚当夏娃双底四变体族 | aadb/aedb/eedb 8 页族 + EOC3 p.398/419/438 | 004 双底的形态学细分（尖刺/圆阔组合决定胜率档位） | long |
| PAT-CHART-070 | 亚当夏娃双顶四变体族 | aadt/aedt/eedt 族 + EOC3 | 001 的细分视图 | short |
| PAT-CHART-071 | Ugly Double Bottom 丑陋双底 | thepatternsite.com/udb.html + EOC3 | 两谷差≥5%；Bulkowski：股价翻倍前出现频率最高形态 | long |
| PAT-CHART-072 | Inverted Dead Cat Bounce 反死猫跳 | thepatternsite.com/idcb.html | 026 死猫跳镜像；A股=利好出尽/炸板见顶语境 | short |
| PAT-CHART-073 | Earnings Flag 财报旗形 | thepatternsite.com/earnflag.html | 事件形态；A股业绩公告 PIT 锚适配 | long |
| PAT-CHART-074 | Roof 屋顶 | thepatternsite.com/roof.html（发现者原典） | Bulkowski 2005 自创，EOC3 新增 23 形态之一；似头肩顶但无双肩谷 | short |
| PAT-CHART-075 | Inverted Roof 倒屋顶（天沟） | thepatternsite.com/iroof.html | 任务书"Gutters"实名勘定；074 镜像；似复杂头肩底 | long |
| PAT-CHART-076 | 2B 假突破反转 | Sperandeo《Trader Vic》1991 p.91 + Schwager + Duddella 三源 | SR-001 突破失败的摆动级精细化；1-2-3 反转字形② | both |
| PAT-CHART-077 | Flat Base 平台基底 | O'Neil《HTMMIS》+ IBD + FlatBase.html 三源 | O'Neil 基底族第 4 型（杯柄/双底/VCP/高紧旗之外）；与 031 低位箱体位置语义区分 | long |
| PAT-CANDLE-078 | Inside Days 内包日 | thepatternsite.com/InsideDays.html | 蜡烛 77 条无全区间内包（与孕线=实体包含相区分）；NR7 近亲 | neutral |
| PAT-FIB-018 | Nen Star 奈恩星 | Carney HarmonicTrader + 12 型标准扫描器集 | 谐波族自称完备的最后缺口；登记后 12 型集完备成立 | both |
| PAT-STRUCT-042 | Market Profile 结构（未完成拍卖） | Dalton《Mind Over Markets》+ CBOT；GoCharting/LuxAlgo/Vtrender 交叉 | SR-006 静态量价分布的结构事件语义扩展（Virgin POC 磁吸/端部未完成/单印带） | neutral |
| PAT-STRUCT-043 | 黄金柱（量学） | 张得一《量柱擒涨停》川人社 2009（百度百科词条+知乎专栏交叉） | A 股原生量价体系唯一缺席的主流门派（缠论/波浪/江恩/威科夫均在册） | long |

四闸结论：来源可溯全过（URL/书名+出版社+年份）；交叉验证 10 条 ≥2 独立源、9 条
=发现者原典 site+EOC3 双载体；A股适配逐条写进 algorithm_variant（涨跌停剔除/
announce_date 锚/利好出尽语义）；可回测性=全部 OHLCV 日线（STRUCT-042 分钟轮廓，
分钟 K 已在产）。regime_valid/invalid 留空=诚实态（无实证不预填），实现后经
pattern_event_store→胜率物化→机生 evidence 回填，与 JFQA regime 依赖纪律一致。

## 四、驳回与去重存档（防后人重复挖）

1. **Straight-Line Run**：驳回。thepatternsite 无独立条目页，仅作为旗杆属性与
   overlap-breakout 统计条件出现（PatternReview6/Overlap 页）；登记即通胀。
2. **Three Drives**：已在册 PAT-FIB-016，任务书候选清单去重，不重复登记。
3. **美国特有事件形态族**（Earnings Surprise/FDA 审批/Same-store sales/评级升降/
   Dutch auction tender）：A股语境无对应事件源，驳回；Earnings Flag 因财报公告可
   PIT 锚定而独获适配。
4. **Anti 系谐波**（Anti-Gartley/Bat/Crab/Shark/Cypher/Nen）与 White/Black Swan：
   长尾不登记（族内变体密度已够，Carney 原著优先级排序待谐波引擎立项时再裁）。
5. **Ex-dividend gaps**：驳回——我方 K 线为复权口径，除权缺口被复权抹除，数据不可得。

## 五、长尾矿脉清单（下批候选，封批未登记）

| 矿脉 | 内容 | 备注 |
|------|------|------|
| Bulkowski 小形态族 | 2-Close/2-step(2025 新)/3-bar/3DC/3L-R/Fakey/Gap2H/Hook reversal/Open-close reversal/Pivot point reversal/Shark-32/Turn-key(2025 新)/Weekly reversals/Elevator stop/Cloud banks/Diving board/Knots/Pothole/Carl V/Cat's ears | thepatternsite 有 Small Patterns 专页+绩效表；单条价值密度低，宜按绩效榜Top-N批量核 |
| Busted 形态族 | 10 章统计（busted 三角/双顶底/头肩/矩形等 1-3 级 bust） | 与 active 的 PAT-SR-001 语义近邻，登记前先做合并论证 |
| 岛形族扩展 | Long Island / Island tops/bottoms 细分 | 现有 025 岛反的细分视图 |
| 扇贝反转变体 | Ascending/Descending and inverted scallops | 罕见形态，样本薄 |
| Extended V / Multi-peaks / Three-peaks-and-spike | EOC3 章级形态 | 待原书统计核对 |
| 量廓形状族 | U-shaped/Dome-shaped volume（量廓形状与突破质量相关性） | 上下文特征语义，登记形态需先定判据 |
| Elliott 细化 | Truncation/Running flat/Triple three/波性 | ELW-002/003 细化视图，随波浪引擎批 |
| 缠论细化 | 中枢延伸/扩张/扩展/新生、小转大、同级别分解 | chanlun-pro 配置文档+chan.py 多级别联立可锚 |
| 游资新词 | 涨停回马枪/N 字反包/凹口淘金（量学姊妹战法） | 回马枪暂无书源=来源可溯闸未过，凹口淘金有《量柱擒涨停》书源可下批核 |

## 六、实现候选清单（交接图形库会话/本会话线）

全部实现纪律：事件走 pattern_event_store（pattern_class 封闭集）、确认=收盘完成时刻
（PIT 铁律）、evidence 禁手填由 pattern_evidence_backfill 生成器回填。

- **P1（近亲复用，工时低）**：CANDLE-078 Inside Days（OHLC 区间比较）；
  CHART-071 Ugly DB（双底检测器+谷差参数）；CHART-069/070 Adam&Eve 族
  （双底/顶检测器+峰谷形态分类器：尖刺/圆阔二值化）；CHART-072 iDCB（DCB 镜像）；
  CHART-073 Earnings Flag（旗形+announce_date 事件锚）；CHART-043 黄金柱
  （日线量价三规则）；CHART-076 2B（SR-001 加摆动级确认）。
- **P2（新几何检测器）**：CHART-063/064 MMU/MMD（三段等幅投影）；CHART-065~068
  扩散族四条（一个参数化发散边界线检测器覆盖：flat_side×slope 组合）；
  CHART-077 Flat Base（周线基底扫描，可与 VCP 检测器同框架）；
  CHART-074/075 Roof 族（脊/檐线触线≥3 次检测器）。
- **P3（重依赖）**：FIB-018 Nen Star——谐波引擎整体未建（FIB-007~018 全族
  pending），建议整族立项一次到位；STRUCT-042 MP 结构——分钟轮廓构建器+
  涨跌停日端部剔除，依赖分钟 K 在产管道。

## 七、净零预算声明（宪法 §4）

- 目录 256→275（+7.4%）。19 条中 11 条显式声明 variant_of 归属（065/066/067/068→021，
  069→004，070→001，071→004，072→026，073→010，076→SR-001，042→SR-006），即对
  既有条目做细化/扩展而非平行新增；驳回 2+美国事件族 6 条不入册；长尾 9 矿脉挂账
  不登记。下批净删候选：若 Busted 族立项，须同步论证 SR-001 的合并或降级。

## 八、纪律执行留痕

- 热文件 claim：chart_pattern_registry.yaml / capability_canonical_file_registry.yaml
  均 `lock_files.py acquire st-patmine-20260914`；注册表写入两度走
  `safe_write_text`（CAS base 校验，写后进程外 yaml 重解析核数 275/275）。
- 并发事实交底：暂存区原持有他会话 stale 快照（REG-PAT-001 暂存版缺今日
  6df8b2d4f7 批的 547 处字段更新），本次提交以工作区版（=HEAD+本批 19 条）为准，
  对 HEAD 逐字段对账**存量 256 条零内容差异**；capability 登记册暂存区含
  st-chinfra-20260914 / st-mktfix-20260914 两条 append-only token，随本 commit
  连坐吸收（归属交底，append-only 无互斥风险）。
- 提交：git_commit.py 正门，commit 后 git log -1 --name-only 核实归属。

## 九、第二批挖矿增补（2026-09-14 续班，Owner"开下一批挖矿"指令）

按 §五 长尾清单+上批交代的③支脉盲区续挖。登记 12 条（275→287，v2.17.0），
驳回清账 2 件，长尾矿脉大面积清偿。

### 挖矿日志表（批二）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|------|------|---------|
| R1 | ③支脉A 吸收 | **signal** | 订单级定义成立（被动限价单承接主动攻击+价格停滞→反向），OrderFlowLabs/NinjaTrader/TraderDale/ATAS 5 源；与 VSA 停止量分层=bar 代理 vs 订单直测，五档数据可得 → STRUCT-044 |
| R2 | ③支脉B Delta 背离 | **signal** | CVD 背离定义完备（价新高+CVD 次高=顶背离），Bookmap/LuxAlgo/ZitaPlus 4 源；=OFI(035) 的累计化+摆动级语义 → STRUCT-045 |
| R3 | ④凹口淘金 | **signal** | 书源《伏击涨停》清华社 2014+知乎量学第14讲+口诀"凹口去淘金报四三涨停"；凹口线+凹底倍量(伸缩)+回踩不破可量化 → STRUCT-046；倍量伸缩并入其注记不单列 |
| R4 | 长尾·小形态绩效榜 | **signal** | SmallPatterns.html 全榜拉平（2024-10 口径，7% 止盈止损）；Top-10 去重（已册 NR4/NR7/WRB/关键反转/内包日+ OutsideDays 并 072 注记）后登记 5 条；Bulkowski 自结论"小形态均利微薄+做空全亏"如实入档 |
| R5 | 长尾·Busted 族 | **signal** | BustedPatterns.html 全文：bust=突破≤10% 失败+反向穿出；busted 双顶反超非 busted 双底（52/51/54% vs 43/42/50%）；与 SR-001 合并论证完成=互补分工（瞬时失败事件 vs 摆动级反向穿越），登记族锚 1 条 → CHART-078 |
| R6 | 长尾·长岛反转 | **驳回（清账）** | longisland.html 全文：**Bulkowski 本人 2020-09-11 宣布"不再视为有效形态"**（非对齐缺口界定，续延型 rank 43/56）——发现者自撤，登记即逆权威 |
| R7 | 长尾·扩展V+倒扇贝 | **signal** | vtopbot.html See-also 证实 Extended V 独立章；aiscallop/idscallops 双页核实（伞形右半，牛熊双市均佳）→ CHART-079/080/081，扇贝族 4 型收官 |
| R8 | 长尾·回马枪书源 | **noise→维持挂账** | 民间战法无明确书籍出处/单一作者（雪球/凤凰/新浪/知乎多源一致），来源可溯闸不过；操作条件虽清晰，纪律优先；找到书源再立卡 |

批二 8 轮：signal 6、noise 1、驳回清账 1。**长尾清单 §五 清偿状态**：小形态族
（Top-5 已采，其余 15 条低价值挂起）、Busted 族（已采）、岛形族（Long Island
驳回终态）、扇贝族（收官）、扩展V（已采）；仍然挂起：量廓形状（判据未定）、
Elliott 细化、缠论中枢生长（实现细化清单）、游资新词（无书源族）。

### 批二登记清单（12 条）

| 新 ID | 形态 | 来源要点 | variant_of |
|-------|------|---------|-----------|
| PAT-STRUCT-044 | 订单流吸收 | OrderFlowLabs Glossary 等 5 源；五档+方向分类可测 | STRUCT-023 |
| PAT-STRUCT-045 | 累计量 Delta 背离 | Bookmap/LuxAlgo/ZitaPlus/TradingView 4 源 | STRUCT-035 |
| PAT-STRUCT-046 | 凹口淘金（量学） | 《伏击涨停》2014+知乎第14讲+口诀 | null（043 姊妹） |
| PAT-CHART-078 | 失效形态族（bust） | BustedPatterns.html+《GSiCP》2e p.225（18 种细目） | PAT-SR-001 |
| PAT-CHART-079 | 扩展V形（顶/底） | vtopbot See-also+EOC3 章 | CHART-023 |
| PAT-CHART-080 | 倒置上升扇贝 | aiscallop.html（伞形右半，双市均佳） | CHART-041 |
| PAT-CHART-081 | 倒置下降扇贝 | idscallops.html | CHART-042 |
| PAT-CANDLE-079 | 周线反转（上/下向） | WeeklyRevsDownside/Upside+绩效榜（第1/8名） | null |
| PAT-CANDLE-080 | 开收反转（升/降势） | OCRU.html 全量 ID 核对（25% 区间规则，第2/5名） | null |
| PAT-CANDLE-081 | 钩形反转（升/降势） | HRD/HRU+绩效榜（第9/13名） | null |
| PAT-CANDLE-082 | 枢轴点反转（升/降势） | PPRU/PPRD+绩效榜（第15/17名） | CANDLE-072 |
| PAT-CANDLE-083 | 鲨鱼 32 | Shark32.html（Chesler 原创）+绩效榜（第18名） | null |

净零声明：12 条中 8 条显式 variant_of/并入注记归属；1 条驳回（长岛）+1 维持挂账
（回马枪）+2 注记并入（OutsideDays→072、倍量伸缩→046）——目录 287 条，扩张速率
较批一收敛（+4.4% vs +7.4%）。实现交接：批二 P1 追加=小形态 5 条（纯 bar 比较，
最低成本）+凹口淘金/黄金柱同批（量学规则族）；P2 追加=Busted 族检测器+吸收/CVD
（依赖 tick 主动方向分类，与 tick_depth_5 管道对齐）。

## 十、schema v2.2：refinements 细化分支字段（Owner 咨询"需不需要加字段"后裁定，2026-09-14）

**裁定：加字段**。动因：先期散文挂账（中枢生长方式/Elliott 细化等）只活在挖矿报告里，
看注册表条目本身不可见；且 variant_of 是单向子→父指针，父→子分支无法反查。

- **字段**：`refinements: list[obj]|null`，每项 `{name, name_zh, registered_as, source}`。
- **双向闭环**：已立卡分支 `registered_as=子条目 pattern_id`，与子条目 `variant_of`
  构成父子互指——本批内置校验 PASS（17 父条目全部子存在+回指一致）；未来
  pattern_catalog_sync 扩展为常设校验器（登记为待施工项，防字段漂移）。
- **未立卡细化**：`registered_as=null`+来源，实现批照单施工禁凭空新编（例：
  中枢四种生长=新生/延伸/扩张/扩展，源 chanlun-pro 配置文档+知乎《中枢的四种
  生长方式》；Elliott 锯齿双重三重/平台三型/三角四变体/三重三/truncation，源
  Frost & Prechter 1978）。
- **净零声明**：本字段替代报告散文挂账（§五 的细化类条目由此结构化归位），不新增
  规则/gate；维护纪律=矿批/设计批填写+生成器校验，非手工维护计数清单（不触 §9.5）。
- **首批回填 17 父条目**：CHART-001/004/010/015/021/023/026/041/042、SR-001、
  CANDLE-072、STRUCT-023/035（已册子分支归位）+ CLL-006、ELW-001/002/003/004/005
  （未立卡细化入册）。
- **边界澄清**：量廓形状（U型/穹顶量）不属"细化"——它是无父条目的独立候选族，
  维持长尾挂账（判据未定），待有权威判据来源时独立立卡。
- 落库注记：写盘两度撞 Windows 文件锁（WinError 32，提交后杀毒/索引扫描窗口），
  退避重试第三次成功；写前写后 yaml 重解析+双向闭环校验自证。
