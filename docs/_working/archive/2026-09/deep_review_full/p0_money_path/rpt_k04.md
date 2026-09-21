---
ttl: task_bound
title: 深度审查作业簿——风控否决引擎
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：风控否决引擎（K04）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（目标文件基线后零漂移；本文件仅 3 个 commit=新而稳定）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/risk/core/risk_veto_engine.py:111`（内置规则 :138-217；判定核心 :351-391）
- 生产调用方（实测 grep）: 唯一构造点 `src/zephyr/ex_core/pre_execution_checker.py:173`；唯一接线 `trading_session.py:490,773`（`_is_blocked_by_pre_execution` 逐单硬拦，submit 流程真实消费=**已接线非孤儿**）
- 测试文件: tests/risk/core/test_risk_veto_engine.py + test_risk_data_pipeline.py（38 passed）
- 运行结果: `python -m pytest tests/risk/core/test_risk_veto_engine.py tests/risk/core/test_risk_data_pipeline.py -q` → 38 passed（Python 3.12.8）

## 1 对象快照

- **范围**：veto 引擎本体（7 内置规则+纯函数判定核心）+ 上游 RiskSnapshot 装配（risk_data_pipeline.assemble_risk_snapshot）+ 下游消费面（pre_execution_checker 四级闸+trading_session 提交流程）。
- **排除项**：RiskLimits 契约定义、C-004 合规闸（K08 相关）、cancel_rate_guard。
- **材料缺项声明**：运行时证据包未取；数据画像（快照缺价率/停牌频率）未取。
- **测试覆盖概况**：引擎 7 规则+异常 Fail-Closed+排序+边界覆盖好（信任）；**测试喂了 sellable_quantities 而生产从不喂**——接线缺口测试无法暴露（见 P1-1）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **P35 T+1 可卖规则生产空转（装饰性规则）**：规则实现正确（sellable=None 跳过不臆测），但生产快照装配 `_pre_exec_snapshot_builder` 调 `build_risk_snapshot()` 从不传 sellable_quantities，且全仓无任何 sellable 产源（grep 仅接口位）→ P35 恒 skip，T+1 卖出约束在执行前闸门 0 覆盖 | risk_veto_engine.py:216-246（skip 语义 :229）；trading_session.py:451-455（不传）；grep sellable_quantity 产源=仅 live_portfolio.py:69 接口与 pipeline 透传 | **P1** | 走一次 build_risk_snapshot()→所有 view.sellable_quantity is None；构造当日买入+全量卖出订单过 pre-exec 闸→放行 |
| A | 数学审查（限额规则）：post_weight=(current_mv+order_value)/nav 量纲正确（mv+订单额 ÷ nav）；杠杆规则 post=(Σmv+order)/nav 对纯多头=B-018 口径正确；买入不改 nav（现金转持仓）假设成立；nav≤0 上游已 Fail-Closed（RiskDataPipelineError） | risk_veto_engine.py:249-317；risk_data_pipeline.py:262-267 | 已查无 | 手算对拍测试用例 |
| A | fail-open 链条排查（该拦没拦）：市价单缺 last_price → _order_value=None → P40/P50 skip——但缺价标的必入 missing_price_symbols → P10 已双向否决，链条闭合；market_value=None 仅在缺价分支出现，同被 P10 兜住。**标准管道下不可达**（自定义 rules 注入时需自证） | risk_veto_engine.py:249-256,268-269,302-303；risk_data_pipeline.py:237-247 | 已查无（附条件） | 构造 quote 缺失快照断言 P10 命中 |
| A | 边界：quantity≤0/负价→InvalidVetoRequestError（调用方 `_is_blocked_by_pre_execution` 全异常捕获→Fail-Closed 拒该单）；规则异常→RULE_ERROR 否决；空持仓 SELL→held=0 否决；nav=0→上游拒绝出快照 | risk_veto_engine.py:338-348,368-379；trading_session.py:890-911；risk_data_pipeline.py:262-267 | 已查无 | 已有测试+调包装函数验证 |
| B | 上游=本引擎最大风险面已由 pipeline 分级兜住：持仓真源失败→拒出快照（Fail-Closed）；行情缺→P10 否决；限额缺→P15 拒买放卖；停牌→P20 双向否决。上游隐式契约（quotes 为 {symbol: quote} 映射、quote.close 为收盘/最新价）未文档化单位（元 vs 千分元）——量纲契约靠全仓一致习惯 | risk_data_pipeline.py:210-306 | P3 | 看 quote 生产方单位注释（data 域） |
| C | 下游消费链完整且方向正确：blocks→PreExecutionReport.allowed=False→拒单入 _blocked_orders；异常不牵连整批（逐单 Fail-Closed）；快照批内缓存+批间失效（trading_session.py:739-742）设计正确 | pre_execution_checker.py:176-262；trading_session.py:739-742,773,890-911 | 已查无 | 读码+集成测试存在 |
| C | Kill switch 探针未接线时仅 DEBUG 日志放行（`KILL_SWITCH_PROBE_UNWIRED`）——"未注入=不拦"哲学下，熔断闸静默缺位只有 debug 级留痕，运维不可见 | pre_execution_checker.py:186-188 | P2 | 构造无 probe 的 checker→闸 1 静默通过，日志级别=debug |
| D | 单仓限额双承载漂移：DefaultRiskValidator.validate_order 用 `post > effective*1.05`（5% 容差），veto 引擎 P40 用严格 `>`——同一概念两处判定两阈值（容差未在任何真源文档化）；顺序上 validator 先行（1.05 放行）引擎后置（严格拦）→ 无放水洞但口径漂移在案（模式 #4） | default_risk_validator.py:234-244 vs risk_veto_engine.py:277-278 | P3 | 构造 post_weight=limit*1.03 订单→validator 放行+P40 拦截，对拍输出 |
| D | SELL 遇快照缺标的→P30 否决（held=0）：fail-closed 方向但与 P15"SELL=风险收敛放行"哲学相反——快照漏标的时阻断的是减仓。现实概率低（_SessionPositionProvider 直连 broker） | risk_veto_engine.py:193-213 vs 159-168 | P3 | 构造 positions 缺标的的快照发 SELL |
| E | 假阳性过关：P1-1（T+1 空转）即本问答案；探针未接线（C 轴）；其余规则 Fail-Closed 方向正确 | 全文 | （P1/P2 已计） | — |
| E | 静默失败：规则异常有 ERROR 日志+结构化 RULE_ERROR 否决（不静默）；唯探针缺位是 debug 级（C 轴 P2） | risk_veto_engine.py:371-379 | （已计） | — |
| E | 重复触发：纯函数无状态，重放幂等；request_id uuid12 可碰撞（同 K02 口径 P3 级） | risk_veto_engine.py:85 | 已查无 | — |
| E | 时序攻击：批内快照复用=批内行情不刷新（设计取舍已注释"同一时点真相"）；批间失效在 submit 入口重置——乱序/迟到事件无死角 | trading_session.py:738-742 | 已查无 | 读码 |

## 3 SOTA 对照

- **Pre-trade risk check 清单式设计**（数据完整性→交易约束→限额分层+全量评估不短路+fail-closed）：与 MiFID II RTS 6 前置风控要求、FIA 建议的 pre-trade risk check 顺序同构；**对等已有**（无需外部检索即可确认结构同构性；本对象未做独立 WebSearch，检索预算用于 K02 监管阈值与 K05 VaR，如实记录）。
- **T+1 可卖数量**：A 股特有口径，规则设计（无真源不臆测+接口位）正确但缺产源——属立卡候选（接 QMT 持仓明细的 `m_strPositionAccount` 可卖字段/冻结数量字段即可点亮，改造点=position provider 一处）。

## 4 缺陷清单（按严重级排序）

1. **[P1] P35 T+1 规则生产空转**：现状→规则在但产源为零，生产快照恒 None→恒 skip。影响→当日买入份额可在执行前闸门全量卖出→券商拒单（error 53/54 类）→订单失败重试噪音，极端时触发撤单率保护误伤；与 K01 清算链 T+1 缺口同根（该卖的被拒/该拦的没拦）。爆炸半径=单订单级。建议修法→_SessionPositionProvider 或 broker 适配器补 sellable 产源（QMT 持仓明细可卖字段），build_risk_snapshot 传入。验证法→当日买入后发 SELL 全量断言 P35 命中（现在不命中）。
2. **[P2] 熔断探针未接线仅 DEBUG 留痕**：建议升级 WARNING+启动自检（assembly 时 probe=None 直接 CRITICAL）。验证法→无 probe 会话跑一单看日志级别。
3. **[P3] 四条低危打包**：单仓限额双承载阈值漂移（1.05 容差 vs 严格）；SELL 缺标的反直觉否决；request_id 12hex 碰撞；quote 价格单位契约未文档化。

## 5 挂起疑问

1. sellable 产源缺失是"尚未施工"还是"QMT 接口未探明"（模式 #13：外部 API 契约未实测）？建议登记 tracker 后按 K06/执行域排期。
2. DefaultRiskValidator（K01 链）与 RiskVetoEngine（本链）对同一订单串行判定，两套限额口径是否有意并存（双保险）还是迁移中间态？若后者，按规范预算净零应登记合并计划。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学四问逐规则过；E 轴五问逐条。
- 长尾清单：① 自定义 rules 注入（OCP）路径无生产使用，其 fail-open 组合空间未穷举；② fills_summary（日内成交汇总）口径未深审（属 pipeline 非本闸）；③ quote.is_suspended 的判定真源（停牌数据源准确性）未审——上游数据域。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 P35 T+1规则因全仓无sellable产源生产空转: 挂起登记(sellable产源立卡)。引擎本体最扎实。
