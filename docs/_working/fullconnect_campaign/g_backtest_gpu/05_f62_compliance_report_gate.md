---
ttl: task_bound
title: "F62 合规门与程序化交易报告——ReportGate C-002 拒单+FeatureGate 硬边界（码成闸空）"
session: zc-l07-20260927
updated: 2026-09-29
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F62 · 合规门与程序化交易报告（总册状态 built（M7：码成闸空零注入=P0 接线前置）/P0；本卷复核=红态维持，broker_ack 6/6 false 本日复测）（已过时，见刷新批注——四袋施工后红态部分翻面）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | 监管真源：43_compliance_discipline.md（§7.4 先报告后交易/§8 日申报笔数/§7.3 盘中操纵；**居 docs/_working/archive/ 归档态**，M7-06 B4 张力在案）+程序化新规两文（programmatic_trading_guard.py:12-14、cancel_rate_guard.py:33 引）+trae_044 |
| 下游消费 | C-002 拦截=order_manager._check_compliance_gates（order_manager.py:356-418，ComplianceGateBlockError ZA-EX-0011）；C-004 拦截=trading_session._is_blocked_by_compliance_gates（trading_session.py:979-1041）；Owner 人工报送动作（外部券商渠道） |
| 自动化触发 | 盘中操纵流=事件驱动零定时器（on_order/on_cancel/on_trade 喂入，stream_driver:8）；批扫=intraday_manipulation_detector 落 MANIPULATION_BATCH_SCAN 痕；报送确认位=人工编辑 YAML 回填 |
| 真源与注册表 | REG-CMP-REPORT-001=docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml（6 项义务，tier_2，safety H）；**本日复测 broker_ack: false ×6 全数**（6 项 reported_at 全 null=报告从未报送）；代码出口=compliance/api/__init__.py |
| 门禁与质量尺 | 全闸 Fail-Closed：登记表不可读=BLOCK；检测引擎失效=拒单（trading_session:995/1022/1070 三处）；检测器与上下文成对注入否则 fail-fast（:326-329）；日申报计数同实例防护（:342-346）；冻结须人工复解释放；tests/compliance 21+ex_core 闸面 54 件在册（M7-06 实测口径） |
| 当前运行状态 | **红（生产装配零注入）**：闸家族 12 件码成闸空——6 处 OrderManager() 裸构造三参全 None（M7-06 穷尽：qmt_trading_session.py:115/qmt_file_bridge_integration.py:52/app_panel.py:524/start_paper_session.py:492/construction 两处）；assemble_session 零 C-004 注入；programmatic_trading_guard 零生产实例化；操纵监测族 5 件零装配；不构成在险违规的唯一原因=未实盘（S-1 锁着） |

## 二、子模块三级枚举（compliance 域 27 件，M7-06 全景三层+本日复核点）

- **C-002 订单级三门**：ReportGate（compliance_report_registry.py:133，先报告后交易）；CancelRateGuard 日申报硬计数（:98-108 阈值 5000/10000，**兜底实例只查不计数=1 万笔防线未激活**）；盘中操纵冻结闸（order_manager.py:401-418，monitor 零装配→静默跳过）
- **C-004 会话级三闸**：KillSwitchLite（discipline_prohibition_checker.py:124-140，默认 state_path 写主仓 data/compliance_log/=M7-06 B5）；四项严禁纪律闸（Hard Block 3+WARNING 1）；trading_compliance_detector（MOD-CMP-007）
- **程序化报告面**：compliance_report_registry（6 项义务+order_min_dwell_us=50 记录性参数）；programmatic_trading_guard（五项登记+启动/下单双校验 :514/:551+配置漂移检测 :584，PAPER/SIM 豁免）
- **操纵监测族 5 件**：trading_compliance_detector（判定核心）+manipulation_stream_driver+intraday_manipulation_detector+manipulation_realtime_monitor（is_frozen 供第三闸）+info_asymmetry_manipulation_detector——族内零重实现、全零装配
- **配套**：compliance_log（production，6 消费）/policy_engine/rule_engine/hard_boundary_adjudicator/evidence_chain_generator/regulatory_change_tracker 等（治理面归 M3 引用）

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| C-002 三门码面 | built（注入即生效/None 跳过） | M7-06 装配点 6 处穷尽在案；本卷维持红判 |
| C-004 三闸 | 码 built/装配缺位 | assemble_session 仅注入 risk_layer+pre_execution_gate（start_paper_session.py:563-565） |
| 报告义务面 | **登记 built/报送 missing** | broker_ack false ×6 本日复测；门禁校验入口就绪待数据 |
| 执行前四级闸 | 已接线 | 闸 1.5 S-1 已闭（M7-02 复证）；本环节不含但为拒单链前置 |

### 骨架勘误
- 总册锚点列"FeatureGate"——M7-06 全景中该名未见于合规闸三层（硬边界=hard_boundary_adjudicator/hard_boundary 面归 M3）；疑总册笔误，建议核正为 hard_boundary_adjudicator（登记级勘误，不动锚点主文件）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 12 件零生产装配+None 静默跳过 | **接线顺序强约束**：Owner 先券商报送→人工回填 YAML→再注入三门三闸+monitor（同批编排，否则 paper 也全拒）——Owner 门位+G5 前置（裁定-4 保持 fail-closed） | P0（Owner+工程 1-2 天） |
| 2 | 1 万笔日申报防线未激活（兜底只查不计数） | 并入缺口 1 注入批（B2 子症防漏读） | P0（随 1） |
| 3 | 冻结闸依赖倒挂（monitor 失效=全拒可用性反噬） | 装配+健康探针（心跳进 premarket_checker 清单，+0.5 天） | P1 |
| 4 | 43 号真源居归档目录却为 MODIFY-GUARD 指针真源 | 升迁正式位或登记降级声明（0.5h，待裁） | P2（待裁） |
| 5 | KillSwitchLite 默认 state_path 写生产路径 | 头注声明+env 化（0.5h） | P2 |

## 五、自审闸三态
**挖干可施工（红→绿路径清晰但含 Owner 人工动作，非纯工程可闭）**——本卷纯引用+复测加深，不重挖 M7-06；勘误 1 条（FeatureGate 名）。

## 六、复跑命令
```bash
grep -c "broker_ack: false" docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml   # =6
grep -rn "OrderManager(" src/zephyr scripts --include="*.py" | grep -v test   # 6 处裸构造
grep -rn "ProgrammaticTradingGuard(" src/zephyr scripts --include="*.py" | grep -v test   # 唯一自身:278
sed -n '356,418p' src/zephyr/ex_core/order_manager.py          # C-002 三门全文
grep -rn "FeatureGate\|feature_gate" src/zephyr/compliance --include="*.py" | grep -v __pycache__ | head -3   # 勘误取证
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更（本卷=四段中施工面最重的卷，四袋落地）
- `fa9ae36533`（09-28，Agent-L 死信复苏重投）：G07 程序化报备闸+G09 信息空窗回避闸接入 OrderManager C-002 链（None=skip，fail-closed）；scripts/start_paper_session.py（+21）paper 会话装配注入两件；W140 接线表 12 行落 docs/_working/qoder_legacy_closeout/；test_order_manager_sim_compliance_wiring.py（222 行）8 项红绿。
- `5acdd1ef85`（09-28，F62 清单闸写侧）：**C-004 ChecklistCompletionChecker 生产写侧三腿+装配接线**——compliance/checklist_evidence.py（354 行新件）+algo_flow/checklist_evidence.yaml（commit 注记自证真源=本卷 C-004 处方与 F62 排雷案卷雷三）。
- `ced0f780bf`（09-29，清单证据时区锚）：trading_session._validate_and_submit 取证日由 datetime.now(UTC) 改经 today_shanghai(Asia/Shanghai) 显式锚——修复北京 00:00-08:00 窗读证（UTC 日）与写证（北京日）差一天致三腿误判陈旧整批拒的生产缺陷（修读写对齐非放宽，Hard Block 裁定值原样）。
- `35ca1d69cd`（09-29，SW5 卡2）：SettlementReconciler 违宪整改——post_settlement_pipeline 事件触发腿+幂等日终 sweep（宪法 §9.3，详见 F82 卷批注）。
- 登记面：compliance_report_registry 6 项义务 broker_ack 已回填 **true×6**（reported_at="2025-12"，Owner 口述 QMT 开通时报送，2026-09-27 回填注记）——本卷"broker_ack: false ×6 全数（从未报送）"**已过时**。

### 缺口清单状态修订
- 缺口 1（12 件零生产装配）：**部分翻面**——paper 腿已注入（G07/G09 经 start_paper_session 装配；HEAD 复测裸构造 6→5 处：start_paper_session.py:727 现带参注入，余 qmt_trading_session.py:123／qmt_file_bridge_integration.py:88／app_panel.py:524／construction 两处维持）；Owner 前置半边（先报送→回填 YAML）已由 broker_ack 回填兑现。
- 缺口 2（1 万笔日申报防线未激活）：未见施工证据，维持。
- 缺口 3/4/5：维持。
- 清单外新增已闭面：C-004 清单闸生产写侧三腿（5acdd1ef85）+清单证据时区锚统一（ced0f780bf）——挖矿时点未立案的施工，现已落地。

### 自审闸三态
- **挖干可施工（维持）**；标题红判与 §一/§三"生产装配零注入/红（码成闸空）"**已过时**——红→黄偏绿（paper 腿注入+清单闸写侧建成+报送面回填；实盘腿与 qmt 链装配仍缺位），缺口 1 的"Owner 先报送"前置已解除半边。
