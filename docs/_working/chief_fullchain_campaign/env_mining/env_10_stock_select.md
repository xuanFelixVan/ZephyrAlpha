---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_10_stock_select.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-10 个股选择 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[layer=L3]（26）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：从板块传导到"今天买哪几只"的漏斗——Universe 剔除→九阶段选票→双池 5 分制评分→负面否决→顺位排序→策略专属链→候选池分层→可交易性预检→日内动态补充
- **节点代表（26，代表非穷举）**：L3 个股选择(structural)｜L3-01 Universe构建与剔除｜L3-02 九阶段选票主链｜L3-03 双池评分(structural)｜L3-03-1 短线池5分制｜L3-03-2 波段池5分制｜L3-03-3 双策略合流体检｜L3-04 负面否决器｜L3-05 顺位排序｜L3-06 环境开关｜L3-07 策略专属链(structural)｜L3-07-1 打板选股链｜L3-07-3 其余sleeve选股链(verified)｜L3-08 候选池输出｜L3-09 股票池分层维护｜L3-10 可交易性预检｜L3-11 竞价选股+涨速扫描(structural)｜L3-12 资金面/龙虎榜/筹码/缠论四验证(structural)｜TDM-C-L3 币对选择(not_built)
- **图面状态**：confidence proposed=19 / untested=6 / verified=1（L3-07-3）；activation postmarket18 为主；red_reason：L3/L3-03/L3-07/L3-11/L3-12 structural、C-L3 not_built

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 11 边：L2-06-3 强度传导→L3 主链/L3-02、L2-05-1 水温→L3-06 环境开关、L2-06-2 龙头→L3-07-1 打板链、L2-09-2 冲击标的→L3-04 否决、L0→L3-06、L9-G1 产业链→L3-01 Universe、L9-G3 股权穿透→L3-12-2 龙虎榜 | 九阶段漏斗+负面否决+双池评分与业界多经理选股管线（funnel+veto）同构 | signal |
| ②下游 | 图内 OUT 4 边：L3→L4、L3-10 预检→L4、L3-08 候选池→F-C3-01 归因回喂。grep 消费方：src/zephyr/signal_ashare/strategy_signal/signal_factory.py、screening/tiered_screening_filter.py、screening/selection_funnel_skeleton.py、core/candidate_pool_snapshot.py（候选池留照面）、tests/pf_core/test_selection_result_contract.py（选股结果契约测试=下游消费的合同面） | — | signal |
| ③算法机制 | 九阶段漏斗（signal_fundamental/selection_funnel.py）；双池 5 分制（signal_ashare/fine_scoring_engine.py+quant_short_term_strength_engine.py）；合流冲突消解（signal_fundamental/router/signal_conflict_resolver）；负面否决（signal_fundamental/negative_veto.py）；顺位置信（selection_confidence.py）；环境开关（signal_ashare/core/environment_switch.py）；竞价微观结构（auction_microstructure_analyzer.py）；缠论结构（chanlun_structure.py）；筹码（regime/features/chip_distribution_engine.py） | — | signal |
| ④后端代码 | 20/26 有码全在盘（无码=5 个 structural 父节点+币圈）。tests/：tests/pf_core/test_selection_result_contract.py、tests/data/data/test_internal_compute_provider_daban_load.py（打板数据腿）；**已查无 signal_fundamental 专属测试目录**（negative_veto/selection_confidence/capital_allocator 无直接测试命中）——选股主链测试缺口在册 | — | 半实现 |
| ⑤前端呈现（只登记） | dashboard/components/warroom.py+api_server.py（候选池/选股结果读出）；web/features/tdm.js | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-150（行情主表）/DS-082/DS-181；龙虎榜（L3-12-2）、股东/限售（L3-01 剔除源经 instrument_master） | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。消费方轮以契约测试收口（selection_result_contract 是选股→下游的正式接口证据），此后无新增。
- **未挖长尾**：(a) 九阶段逐阶段通过率/漏斗损耗台账（无运行读数，实查待施工批）；(b) L3-12 四验证件（资金面/席位/筹码/缠论）逐件输入表核验；(c) candidate_pool_snapshot 留照频率与 TTL。
- **🌑不可得**：①双池 5 分制的历史区分度回测证据（评分引擎无留痕台账）；②L3-07-3 全场唯一 verified 的证据底稿（图面标 verified 但考试链归档未见——待验证）。

## §3 挖后自审闸三态裁定

**挂起排期（整层）——图语义→代码施工令缺口 + 测试伴生缺口**

- 理由：20/26 有码、漏斗/评分/否决/预检件件在盘，但 confidence 19 proposed+6 untested，无生产激活证据；signal_fundamental 主链无专属测试（已查无）=施工伴生义务未履行；上游 L2 水温/传导未激活（ENV-09 挂起），本层单独施工会成为无上游语义的空转。按纪律挂起排期。
- 施工令候选排序（解锁后）：signal_fundamental 主链单测补齐（selection_funnel/negative_veto/selection_confidence 三件优先）> L3-06 环境开关×水温闭合 > L3-11 日内动态（竞价+涨速）激活。
- 解锁条件：ENV-08/ENV-09 激活到位 + Owner 个股选择层施工令 + L3-07-3 verified 底稿补登记。
- C-L3 币对=not_built 外域封存。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：26 节点切片，verified=L3-07-3 单点确认 | signal | structural5 分型；双池/九阶段/四验证机制族谱 |
| 2 | 代码轮：20 module_ref 存在性+tests 反查 | signal | 零失踪；signal_fundamental 无测试目录=缺口登记 |
| 3 | 消费方轮：candidate_pool/selection_funnel 全仓反查 | signal | signal_factory/tiered_filter/snapshot/契约测试四处消费锚 |
