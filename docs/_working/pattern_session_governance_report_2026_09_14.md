---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/pattern_session_governance_report_2026_09_14.md |
<!-- [MODULE] MOD-SIG-145 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# 图形库会话治理上报（st-pattern-20260914，2026-09-14 深夜班）

> 背景：图形库全链施工批（MOD-SIG-145/146，P1+P2 共 11 commit）。本报告上报施工中
> 发现的基础设施问题五件 + JOB-108 接线规格书。详尽过程记忆在会话 st-pattern-20260914。

## 一、上报五件（按危害排序）

### 1. capability_canonical_file_registry.yaml 并发死区插入 → YAML 炸全仓【已修标，需治本】
- 现象：c4 会话把 creation_token 条目 EOF 追加到 `di_seam_exemptions: []` 之后
  （12250 行处），整个文件 parse 失败——**所有新文件创建（scaffold 重复检测）
  即报错**，阻断面是全仓级。
- 已做：悬挂块上移回 creation_tokens 序列尾（st-pattern-20260914 修复，CAS 留痕）。
- 治本建议：所有向该 registry 插入的工具（scaffold.py / batch_creation_tokens.py /
  其他会话自写脚本）统一加**写后 `yaml.safe_load` 校验，失败即回滚**；
  写路径全部收口 safe_write_text CAS。
- 相关：altdata 会话 2026-09-13 曾上报同文件"并发损坏（12112 行）"挂账——同一根因复发。

### 2. scaffold.py 嵌套包斜杠 bug【四连发，未修】
- 现象：`scaffold.py module signal_ashare/strategy_signal <name>` 时
  `_register_to_init` 用 package 原文（含斜杠）拼 import 行
  → `from zephyr.signal_ashare/strategy_signal.x import Y`（SyntaxError），
  且 `__all__.append(...)` 偶发多参数。本会话手工修复 4 次。
- 修法建议：`package.replace('/', '.')` + 写入前后 `ast.parse` 自检 + 追加式
  `__all__` 注册改幂等集合语义。

### 3. data_asset_registry.yaml 双 `datasets:` 根键【历史遗留，未修】
- 现象：752/755 行两个 `datasets:` 键，PyYAML 静默取后者；人工/工具插条目到
  前段会被解析层忽略。
- 修法建议：合并两段（一次性脚本+parse 对账），并在 verify 门禁加"根键唯一"检查。

### 4. registry v1 老条目缺 schema v2.1 字段行【已兼容，未回填】
- 现象：部分 PAT-CANDLE 条目（如 PAT-CANDLE-003）无 `code_symbol:` 字段行，
  生成器"null→值"替换打不中。
- 已做：pattern_catalog_sync.py 加"无则插入"兼容分支。
- 修法建议：一次性回填脚本给全部 v1 条目补齐 v2.1 占位字段（null 化），
  之后生成器可回归纯替换语义。

### 5. 幽灵锚点 anchor_id=674【已按门禁指令清理，留痕】
- 现象：battle_map_anchors 存在 02:07 创建的锚点（BM-SEL-01→MOD-L02-028，
  target_id_not_found），GATE-BATTLE-MAP-ALIGNMENT 全仓扫描连坐阻断无辜提交。
- 已做：`apply_battle_map.py --remove-anchor --anchor-id 674`（门禁指令的指定动作）。
- 建议：①create-anchor 时校验 target 存在；②GATE-BATTLE-MAP-ALIGNMENT 按 §3
  改造 own-scope 或降 warn（幽灵锚点非提交人过错）。

## 二、JOB-108 接线规格书（数据域会话可直接施工）

目标：pattern_event 增量扫描接入 IntegratorScheduler 声明式 DAG。
当时未直接施工原因：两处落点文件（tasks.yaml / internal_compute_provider.py）
在本会话窗口内有他会话在途未提交改动（' M'），按共享文件纪律不硬闯。

### 落点 1：`src/zephyr/data/config/tasks.yaml` 追加任务块

```yaml
- task_id: pattern_event_incremental
  table: c1_market.market_pattern_event
  source: internal
  schedule: daily_kline
  incremental: true
  date_col: anchor_trade_date
  dependencies: ["kline_daily_incremental"]   # 日K线落地后事件触发
  capability: pattern_event
  symbols:
  fallback_sources: []
  extra:
    description: "图形形态事件增量（MOD-SIG-145/JOB-108：引擎扫描器滚动回看 400 日上下文、
      只产出近 15 日确认事件；确定性 event_id+ReplacingMergeTree 幂等）"
```

### 落点 2：`src/zephyr/data/implementations/internal_compute_provider.py`

1. `meta.capabilities` 追加 `CapabilityContract("pattern_event", supports_symbols_null=True)`。
2. `fetch()` 增加 capability 分支：`pattern_event` → 调用
   `scripts/data/pattern_event_incremental.py` 主流程（建议抽为
   `zephyr.signal_ashare.strategy_signal.pattern_event_job.run_incremental()` 薄适配），
   扫描器自行经 pattern_event_store 落库，返回空 FetchResult 即可。

### 落点 3（接线后一次性）
- 手动跑一轮 `scripts/data/pattern_win_rate_materialize.py`，
  之后每次增量事件落库后由同一 DAG 尾部触发重物化。

## 三、本会话施工台账（自证留痕）

- commit：84f4679a（设计）→ 7057d15c49（W1 表+store）→ 9ca0f62b95（W2 回填器
  +canonical YAML 修复）→ 59544e35cb（W3 统计+provider）→ 1190e235b9（W4 引擎
  注入物+evidence+DS/JOB）→ a1b5c7f525（P2-a 蜡烛）→ 271c62d27f68（P2-c 变换层）
  → ac52af85f6c4（目录同步 77/77）→ c963b928aa（classic2 头肩三重）→ 7ea45c09281b
  （classic3 三角矩形楔形）→ d95e290421（治理报告）→ 2d65147cf10c（类目补登）。
- 形态实现：15 → 102（77 蜡烛+15 原有+4 头肩三重+6 三角矩形楔形）。
- 事件表约 2340 万（重扫扩容后）；胜率统计 4309 行；机生 evidence 12 条。

## 四、P3 Bulkowski 差额候选清单（EOC3 75 vs 目录 62，待原书核对后登记，禁自编）

目录 PAT-CHART 62 条已覆盖 Bulkowski 经典族的绝大部分（双顶底/头肩/三重/三角×3/
楔形×2/矩形/旗形×3/杯柄×2/圆弧×2/扩散/钻石/岛反/扇贝×2/牛角×2/管道×2/冲回×2/
V×2/死猫跳/三峰穹顶/三升谷三降峰/BigW BigM/高紧旗/复合头肩/Wolfe/Quasimodo/VCP/
Ross Hook/1-2-3 等）。逐条比对后疑似差额候选（**候选≠登记**，须 EOC3 原书或权威
来源核对定义与统计后再走 CREATE 流程）：

| 候选 | 说明 | 优先级 |
|---|---|---|
| Measured Move Up / Down（量度涨跌） | 最经典缺口，与箱体/旗形目标价直接联动 | 高 |
| Broadening Right-angled Ascending / Descending（直角扩散×2） | 目录 021 只有对称扩散 | 高 |
| Eve & Adam Double Bottom / Top（亚当夏娃双底/顶变体） | Bulkowski 双底顶细分族 | 中 |
| Three Drives（三驱） | 谐波族近亲，fib 类已有铺垫 | 中 |
| Inverted Dead Cat Bounce（反死猫跳） | 事件形态族 | 中 |
| Straight-Line Run（直线运行） | 事件形态族 | 中 |
| Earnings Flag（财报旗形） | 事件形态族，A股语境=业绩缺口形态 | 低（依赖财报事件层） |
| Gutters（双沟） | 罕见，统计样本薄 | 低 |

## 五、IND-REV-001 退役协调（Owner 倾向 B；消费清查已完，B 的最大成本归零）

- Owner 倾向（2026-09-14）：**方案 B 直接退役**（最彻底最治本）。
- 消费清查结果（st-pattern-20260914，2026-09-14）：**零下游消费方**——
  src/tests/scripts 全量 grep `candle_pattern` 列与 `IND-REV-001` 引用，
  除 reversal.py 自身+其测试外无任何读取者；前端/配置零引用。
  CH technical_indicator 表确有 candle_pattern 列（Nullable Float64）。
- 结论：B 的"查名单、迁消费方"成本实测=零，可直接进入退役执行。
- 执行清单（指标队会话执行，退役 commit 走 ruling_registry 同 commit）：
  1. reversal.py 删 CandlestickPattern 类 + 对应测试断言；
  2. schemas/categories/market_technical_indicator.py：INSERT_COLUMNS 去掉
     candle_pattern（列物理保留、停产为全 NULL，观察一季度后 ALTER DROP）；
  3. technical_indicator_registry：IND-REV-001 标 deprecated → 下季删除
     （注册表净删，本条即 Owner 批准依据）；
  4. 可选：在 REG-PAT-001 头部注记"蜡烛实现唯一真源=candlestick_scanner"。
- 现状安全说明：退役前两管道并存互不干扰（旧产指标表列/新产事件表），无时效压力。

## 六、applicable_series 标注批（已完成，2026-09-14）

REG-PAT-001 全部 256 条中 162 条已标注：
- 几何类（chart_pattern 62 + trendline_channel 13 + support_resistance 10）=85 条：
  `["time_bars", "renko", "pnf", "kagi"]`——既有几何形态在替代序列上同样成立，
  适配器由 MOD-SIG-146 series_transform 提供；
- 蜡烛类 77 条：`["time_bars"]`——蜡烛依赖 OHLC 影线，替代序列无此语义；
- 其余 94 条（缠论/波浪/fib/structure/DL 等）本批不动，待各域语义裁定后补。
生成器：pattern_catalog_sync.py --annotate-series（幂等，禁手填）。

## 五-附、原方案 A/B 对照（提案原文存档，2026-09-14 早版）

- 现状：P2-a 后 77 条蜡烛实现已全在 `candlestick_scanner.py`（目录 code_path
  77/77 已迁移）；指标域 `factor/technical_indicators/reversal.py` 的
  CandlestickPattern（5 形态 pandas 版）与指标注册表 IND-REV-001 仍在，
  且指标 CH 表 technical_indicator 的 CDL 输出列仍由指标队增量任务生产。
- 提案（二选一，Owner 拍板后由指标队会话执行，退役走 ruling_registry 同 commit）：
  - 方案 A（推荐）：IND-REV-001 改薄视图——保留指标表既有 CDL 列的消费兼容，
    计算内部转发 candlestick_scanner（单一实现真源），注册表标注 view_of=MOD-SIG-145；
  - 方案 B：IND-REV-001 直接退役——需同步评估 technical_indicator 表 CDL 列的
    下游消费（编译消费清单→迁移或公告断供），涉及注册表净删+表结构变更，流程更重。
- 无论 A/B：reversal.py 旧实现代码的删除/保留属指标域文件操作，由指标队执行。
