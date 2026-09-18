---
ttl: task_bound
doc_type: report
title: 深度审查报告——日度决策编排器（T03）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：日度决策编排器（T03）

- 状态: **已审**
- 级别: P1｜类型: 决策链编排
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:582(run_daily_decision)/:654(_run_inner)/:405(compute_position_cap)`
- 生产调用方: pipeline_events.maybe_run_daily_decision（daily_kline SUCCESS 唤醒链末棒）+ `__main__` 手工补跑；下游=decision_daily 表（warroom 面板消费；v1 零实盘执行，裁定#305 第 6 点）
- 测试文件: tests/strategy_pipeline/test_decision_orchestrator.py（31 用例）
- 材料包缺项: daily_gate_snapshot/collect_gate_snapshot 内部未深审（依赖对象）；decision_daily 近 N 天实跑行未取样（v1 刚接电）

## 1 对象快照

- 范围：S1 日历三层解析/S2 regime 腿/S3 门腿/S4 包选择/S5 仓位合成/S6 落库/S7 播报 + marker 幂等 + 唤醒挂点。排除：daily_gate_snapshot.py（上游采集）、ch_writer（写通道）、schemas/categories/decision_daily.py（列真源）。
- 变更热力：2026-09-16 蓝图→2026-09-18 基线当日接电（BT-P1-031 刀 3），极速成型区。
- 测试覆盖概况：31 用例覆盖 D1-D7 降级矩阵/幂等/marker 陷阱/wake 过滤/包选择三态——覆盖质量高（含 test_d7_sink_fail_fail_open 显式断言 marker 先占语义）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **regime confidence=NULL → TypeError → 全日拍板 error**：reader 侧 `float(row["confidence"])` 无 NULL 防御且在 query try 块之外（daily_gate_snapshot.py:127），编排器 `float(regime.get("confidence") or 0.0)`（:538）把 None 与 0.0 混写——NULL 行炸整腿，D7 折 error+告警，当日无快照行需人工 force 补拍 | daily_gate_snapshot.py:119-131; orchestrator :538, :600-606 | **P2** | 造一行 confidence=NULL 的 regime_snapshot_history 跑 run_daily_decision → action=error |
| A | 预算带线性插值 `cap=low+(high-low)*conf`：隐含假设=conf 是 HMM 后验隶属度且在 [0,1] 均匀可用（:416 clamp）；conf 缺失与 conf=0 同判过渡带×0.5（expansion 带下 conf=0 仍给 25% 总仓）——"零置信仍给四分之一仓"的边界语义未在蓝图声明 | orchestrator :405-423 | P3 | compute_position_cap("expansion", 0.0) → 0.25 |
| A | euphoria "只卖不买"仅存在于 cap_calc dict 与 note 文本（:548-549），**未持久化为结构化列**——decision_daily 行无 sell_only 字段，未来 S7 执行面无法机读该语义（总仓上限 30% 与禁新开并存，语义靠注释承载） | orchestrator :423, :548-549, :683-703 | **P2** | 读 schemas/categories/decision_daily.py INSERT_COLUMNS 无 sell_only 列 |
| A | `_s2_regime_leg` 新鲜度：source_date 用字符串 ISO 比较（:532）——接受 source_date==day（比"昨收 PIT"更新）与==prev_day，仅拒更老；"接受当日 regime"是否 PIT 安全未声明 | orchestrator :530-536 | P3 | source_date=day 构造跑 S2 观察不判陈旧 |
| A.3 | 测试无日期漂移（固定 D 常量），FakeReader/FakeSink 断言强度足（行数/告警文本/动作三重断言）；31 用例对 D1-D7 全矩阵——信任 | test_decision_orchestrator.py:168-403 | 已查无 | — |
| B | TDM 配置裸 `yaml.safe_load`（:340-350）绕过 decision_map.load schema 校验=旁系双加载路径：YAML 结构损坏→None→"格空"安全侧+warning，但与 gate 校验的图谱真源可能静默不一致（T01 报告已登记同源发现） | orchestrator :340-350 | P3 | 对照 decision_map.load_decision_map 校验输出 |
| B | `_resolve_kline_day` 异常→""→proven=False→（无日历行时）sleep：行情实证断供=休眠安全侧，误休眠风险由 D4 data_proven 分叉对冲——方向正确 | orchestrator :479-487, :242-252 | 已查无（正面） | — |
| B | kill_switch 读态失败→按熔断保守侧（:560-563）、门缺席层→依赖包禁用不阻断（D2）、预算 run 缺席→no_trade（D3）——三输入断供行为全部显式降级有账 | orchestrator :553-571 | 已查无（正面） | — |
| C | 写侧 fail-closed：缺声明列 raise（:457）、disposition 非 committed/durable raise（:461-462）——"算了但没落地"禁；下游 warroom 读表，v1 无执行面=爆炸半径当前为零（裁定#305 第 6 点） | orchestrator :445-463 | 已查无（正面） | — |
| C | marker 先拍板先占+写失败不回滚（:681）：瞬时写库故障→marker 已占→同日重唤醒全 skip→当日决策缺失（无行=无新开仓令，安全侧但机会成本单向）；**有显式测试+force 逃生口**——已裁定权衡非盲区 | orchestrator :194-205, :658-681; test :343-353 | P3 | 见 test_d7_sink_fail_fail_open 复演 |
| D | 并列拍板体 daily_warroom_pipeline（MOD-PLAN-018）"复用其两段编排/幂等/次交易日解析口径"——语义复用非代码复用，两套实现漂移风险（checklist #4 同族）：次交易日解析两处各写一份 | orchestrator :36-37 vs daily_warroom_pipeline 实现 | P3 | diff 两模块日历 SQL 模板 |
| D | P2b 场景 SQL 硬编码表名 c1_market.judgment_daily_plan/judgment_plan_verification（:169-174）vs 本模块自declared不变量"表名经 TableRegistry 真源解析"（:156-158）——同模块内自相矛盾 | orchestrator :156-174 | P3 | 查两表是否在 TableRegistry |
| E | `maybe_run_daily_decision` 唤醒条件 fail-open：SIM_DAILY_WAKE_TASKS 导入失败→`wake = success`→任意成功任务触发拍板（:731-736）；marker 幂等兜底使多触发塌缩为一次，但触发面意外扩大无告警 | orchestrator :730-738 | P3 | monkeypatch import 失败复演 |
| E | marker TOCTOU 并发窗：两路同日并发拍板→双 read-pass→双行双 run_id（:658-681）；safe_write_text 未带 expected sha=非 CAS 写；当前事件链串行使窗口实际关闭 | orchestrator :186-205 | P3 | 两线程同 marker_dir 并发跑 |
| E | force 重拍=新 run_id 追加（快照只增不改）：同 trade_date 多行时下游取数口径（max run_id? 最新 ingest_ts?）未在本模块声明——留痕语义依赖消费方自觉 | orchestrator :680, test :364-371 | P3 | 查 warroom 取数 SQL |
| E | A 股口径：决策生效日=次交易日（is_open=1 查表）自动跳周末/节假日；"禁新开仓≠清仓"与 T+1 兼容（存量卖出不受闸）；分红/停牌面不在本层 | orchestrator :39, :162-163 | 已查无 | — |

## 3 SOTA 对照

1. **regime 驱动仓位管理（对等已有）**：HMM 状态+置信度定仓位是量化实践成法——QuantInsti《Market Regime using Hidden Markov Model》（博客，2021 起持续更新，https://blog.quantinsti.com/regime-adaptive-trading-python/，position sizing based on model confidence）；arXiv 2402.05272《Downside Risk Reduction Using Regime-Switching Signals》（arXiv，2024，https://arxiv.org/html/2402.05272v2）同口径按 regime 信号调 exposure。本模块在业界做法上加了过渡带折减+60% 硬顶+六段封闭带，保守性更高。
2. **情绪六段预算带（驳回外部对标）**：六段制（capitulation→distribution）是本仓 TDM 情绪周期自定义分层，无业界同名口径；业界对应物=波动率状态过滤（QSTrader《Market Regime Detection with HMMs》，QuantStart，2016，https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/）。中文情绪周期语境按政策不算盲区；判"自研分层、业界无直接对等"，参数全 proposed 待 Owner 终裁（代码已声明）。
3. 结论：核心机制**对等已有**；六段带为自研扩展，无立卡即改项。

## 4 缺陷清单

1. **[P2] regime confidence NULL 炸腿致全日拍板 error**——现状：reader 解包无 NULL 防御（daily_gate_snapshot.py:127）+编排器 `or 0.0` 混淆 None/0（:538）；影响：坏行→当日无决策快照+需人工 force（visible 但单点脆）；建议：reader 侧 NULL→status=absent 带原因，编排器侧显式区分"缺失"与"零置信"；验证法：注入 NULL 行复演。
2. **[P2] euphoria sell_only 未结构化落列**——现状：语义只在 note 文本与内存 dict（:423/:548/:683-703）；影响：S7 执行面接电后"只卖不买"无法从 decision_daily 机读，靠翻 note=口径漂移温床；建议：INSERT_COLUMNS 增 sell_only 列（schema v1.1）或 package_set_json 内结构化；验证法：读 schemas/categories/decision_daily.py 列清单。
3. **[P3] marker 先占+写失败不回滚=当日决策缺失需人工 force**（已测已裁定，:681+test:343）——建议：告警文案加"需 force 补拍"行动项；验证法：见测试。
4. **[P3] 唤醒条件 import 失败 fail-open**（:731-736）——建议：except 分支留痕计数；验证法：monkeypatch。
5. **[P3] TDM 裸读绕过 schema 校验**（:340-350）——建议：复用 decision_map.load_decision_map；验证法：喂坏 YAML 对比两路行为。
6. **[P3] 场景 SQL 硬编码表名 vs 自declared不变量**（:156-174）——建议：两表入 TableRegistry 或修订注释豁免留痕；验证法：查注册表。
7. **[P3] marker TOCTOU/非 CAS 写**（:186-205）——建议：safe_write_text 带 expected sha；验证法：并发复演。
8. **[P3] conf=0 仍给带下限×0.5 仓位**（:405-423）——建议：Owner 确认零置信语义；验证法：compute_position_cap("expansion",0.0)。
9. **[P3] 与 daily_warroom_pipeline 双实现漂移面**（:36-37）——建议：口径对账清单登记（align 体系）；验证法：diff 两模块日历解析。

## 5 挂起疑问

1. source_date==day（当日 regime）被新鲜度检查接受——PIT 口径上"盘后拍板用当日 regime"是否越"昨收 PIT"蓝图语义？（:39 说 regime=昨收 PIT，:532 却放行当日。）
2. REGIME_TO_SEGMENT 缺 r 状态（如未来新增 r5-r9）→"不可映射"no_trade 保守侧——映射表与 HMM 状态集的同步机制归谁管？
3. GRADUATED_PACKAGES 接电来源（工厂考试台账）未定接口——与 T06 promotion_advisory 的衔接契约需收口。

## 6 完备性自评

- 六轴全查：是。A（插值/新鲜度/NULL 三边界+测试审查）、B（TDM/regime/门快照/日历四输入断供行为逐条）、C（写侧 fail-closed+warroom 消费+v1 零执行面）、D（并列拍板体+TableRegistry 矛盾+裸读旁路）、E（幂等/并发/重拍/wake 五问）。
- 长尾：①collect_gate_snapshot L2-L5 内部未深审（依赖件）；②warroom 面板取数口径未追（前端域）；③ch_writer 投递语义信任 error contract 未实测。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
