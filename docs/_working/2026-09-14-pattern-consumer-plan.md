---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/2026-09-14-pattern-consumer-plan.md |
<!-- [MODULE] MOD-SIG-145 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] M -->

# 图形库消费端方案（st-patmine-20260914 消费班，2026-09-14）

> 状态：**v1.0 冻结待施工**（v0.9 草案经挖矿 SOP 六向完善后定稿，挖矿日志=§四；
> 双噪音未触发，时间盒封批收敛）。方法论序：方案→挖矿完善→施工 SOP。
> 纪律真源：AGENTS.md + construction_workflow_policy.md（施工前必读+前置登记）。

## 一、内部反查证据（断点盘点，2026-09-14 实测）

生产件已备齐，管线未通电：

| 组件 | 模块 | 状态 | 断点 |
|------|------|------|------|
| PatternEvent（含 historical_win_rate 注入契约） | MOD-SIG-091 引擎 | production | **全仓仅回填脚本构造引擎——信号管线无引擎宿主**，胜率注入参数无人传 |
| 胜率只读出口 | pattern_win_rate_provider | production | 消费方仅 evidence 回填器 |
| 形态→信号映射（方向/强度=置信度×胜率/止损=点位外扩，CTR-002 Fail-Closed） | MOD-SIG-115 mapper | production 头 | **除 provider 外零调用方**；[AI_AUTONOMY]=human_gated（本方案不改其代码） |
| 信号权重调节（滚动 IC/胜率/回撤→权重，限幅±20%+版本化回滚+审计回调） | MOD-SIG-131 adjuster | production 头 | 未装配 |
| 证据机（事件→胜率物化→evidence 回填） | MOD-SIG-145 | 闭环 | 胜率表日期驱动=天然前瞻结算（见 C3 简化） |
| 信号总线（signal_factory/双引擎融合/交叉投票漏斗/三维矩阵/投票积分） | strategy_signal 域 | 在产 | **MappedSignal 无出口接线** |
| regime 基建 | regime_snapshot_history 表+market_state_sensor+胜率表 regime_tag 切片 | 在产 | 信号侧未消费 |
| 前端 | dashboard | — | **图形库零端点零页面** |
| 回测/筛选消费 | 回测域 | — | 形态条件未接入 screen |

**结论**：消费班核心工程=①通电（装配）②接入（总线+meta 门）③调权（131 消费物化表）
④呈现（API+页）⑤边界登记（回测/TDM/因子域）。

## 二、消费端分层设计（v1.0，含挖矿修正）

### C1 运行时装配批（通电）
- 新建装配点 `pattern_signal_runtime.py`（模块级组合根，纯装配无业务逻辑，新建 .py 走
  scaffold+翻译登记）：
  - engine 构造注入 `win_rate_provider=PatternWinRateProvider(...)` 的查询函数；
  - `PatternToSignalMapper` 实例化（validator=CTR-002 校验器，stop_buffer/default_win_rate
    取 blueprint 值）；
  - `SignalWeightAdjuster` 注入时钟/审计/告警回调；
  - 输出 `PatternSignalRuntime` 接口：`on_events(symbol, events) -> list[MappedSignal]`。
- 装配宿主=信号管线运行时（signal_factory 档）启动导入，不另起进程（四要素：无 cron/无
  sleep-loop）。宿主接续点在施工批 W-C1 现场确认（tasks.yaml 信号档）。

### C2 信号管线接入（含 meta-gating 门）
- MappedSignal → signal_factory/交叉投票漏斗，形态信号作为一路加权投票源
  （业界对照：加权投票优于简单多数，buildalpha/TradingView 集成实践）；
- **meta 门**（Lopez de Prado 式 meta-labeling/gating：门坐在信号之上过滤/调权，不替换
  信号逻辑——Medium 多层投票框架+arXiv 2501.10709 对照）：
  - **regime 门**：接胜率表 regime_tag 切片口径+regime_snapshot_history/market_state_sensor，
    门=是否准入+权重调节，不新造检测器（净零）；弱证据族（治理报告 §七 头肩/三重）不亮绿灯；
  - **PIT 铁律**：confirmed_at=收盘完成时刻（DDL 已编码），信号 T+1 可执行（复用回测批
    P0 前视断言套件做管线级硬断言）；
- **小样本稳健化（挖矿 M1 修正）**：provider 输出改为 **Wilson 95% 下界**（z=1.96）作为
  historical_win_rate 保守估计（raw+n_events 并出；low_sample n<30→None 已由 DDL 编码，
  消费方按无统计处理）——**mapper 不改**（human_gated），改动落在 145 线 provider
  （依据：TradingView winrate 脚本实照+statisticsfundamentals/metricgate 小样本口径，
  20 笔 55% 真胜率可显示 40~70% 的噪声带）。
- **审计决策链快照（挖矿 M6 修正，VCP v1.1 signal→order→execution 可追溯思路的个人化
  裁剪）**：信号落库审计带四元组快照=（所用 win_rate 值+low_sample 标记+当期 regime_tag
  +131 权重版本号），不新增 DDL（走既有审计通道）。
- KillSwitch/限流：接入现有信号安全设施。

### C3 调权反馈（挖矿内部反查后大幅简化）
- ~~原 v0.9：前瞻验证新表+与回扫口径分离~~ **过度设计，撤销**。胜率物化表本就日期驱动
  （事件×日K 自动结算，JOB-108 日链已自动化重物化）——昨天信号的对错今天自动进表。
- C3=纯消费：131 adjuster 经 provider 读滚动胜率（Wilson 口径）→ 限幅调权+版本化+
  审计回调；触发=物化任务完成事件钩子（事件触发，禁 cron）；权重持久化目标在 W-C3
  现场定（既有权重配置 or 小表+business_data_categories 登记）。
- evidence 回填仍以 145 物化为唯一真源不变（只读消费纪律）。

### C4 查询/前端面
- api_server 增 3 端点：形态事件查询（symbol/日期窗）、胜率表查询（四窗×regime 切片）、
  证据查询（registry evidence 直读）；
- dashboard 图形库页：照抄 TDM/策略工厂交互（表+热力+证据徽章）；
- **展示口径（挖矿 M5 吸收）**：胜率=百分比+样本数双格式并列+low_sample 徽章（TradesViz
  count/% 双口径+Avark 概率双格式惯例）；信号卡=方向+置信度+入场/止损同卡（MappedSignal
  字段天然齐备）；暗色主题=既有房规。

### C5 边界登记（不越界）
- 回测域：形态条件接入 screen/lane_c——登记接口需求，归属回测域；
- TDM 域：形态→信号边+图形域节点 payload——归属 TDM 前后端会话；
- 因子域：形态宽度/丰度因子（pattern breadth）候选 F 槽位——归属因子/altdata 域。

### C6 明确不做
- 不做自动交易执行（只到信号层）；不做组合层消费；不改 145 证据机口径；不改
  MOD-SIG-115 mapper 代码（human_gated，其契约经由 provider 侧 Wilson 化满足）。

## 三、纪律锚（硬约束清单）
1. 弱证据族不绿灯（治理报告 §七）；2. PIT=收盘确认；3. CTR-002 Fail-Closed；
4. 装配/调权=事件触发，禁 cron/Timer/sleep-loop；5. DatabaseService 唯一 DB 入口；
6. 测试隔离 tmp_path；7. 热文件 safe_write；8. 前端照抄既有页不发明新范式；
9. 施工前置三件：construction_workflow_policy.md 必读+RULE-DEPGRAPH 登记+
   RULE-CAPABILITY-LOOKUP 审计。

## 四、挖矿增补（SOP §6 日志）

| 轮 | 矿脉 | 内部半边 | 全网半边 | 判定 | 吸收进方案 |
|---|------|---------|---------|------|-----------|
| M1 | ③算法：小样本胜率加权 | mapper 现公式的 default_win_rate 空转风险 | Wilson 下界=小样本标准解（TradingView 实照+统计口径 4 源） | **signal** | C2：provider 输出 Wilson 95% LB，mapper 不动 |
| M2 | ①上游：regime 喂入 | regime_snapshot_history+market_state_sensor+regime_tag 切片全在产 | regime gate=准入路由标准实践（arongroups/PyQuantLab/TradingView） | **signal** | C2：门=复用既有切片口径，不新造检测器 |
| M3 | ②下游：信号汇入 | 投票漏斗/融合引擎/积分器契约盘点 | 加权投票+meta-gating（门在信号之上）+聚合前 regime 感知（Medium/arXiv/BuildAlpha） | **signal** | C2 结构获术语锚与方法论背书，映射到既有投票总线 |
| M4 | ④后端：装配宿主 | 全仓仅回填脚本构造引擎=宿主真空 | （§7 豁免：内部足够） | signal(内部) | C1 宿主接续点列为 W-C1 现场确认项 |
| M5 | ⑤前端：呈现惯例 | TDM/工厂页两先例=房规 | 胜率双格式并列+信号卡四要素+暗色主题（TradesViz/Avark/DataArt） | 弱signal | C4 展示口径两条吸收 |
| M6 | ⑥数据字段：审计口径 | 事件表审计字段齐（#ARCH-CH-025）+low_sample 已编码 | 信号→执行可追溯链（SFC DS-OL/VCP v1.1） | 弱signal | C2：审计四元组快照（win_rate/low_sample/regime_tag/权重版本） |

终止判定：六向全覆盖，signal 3+弱 signal 2+内部 signal 1，noise 0——**双噪音未触发，
时间盒封批收敛**（6 轮全 signal 产出率=每轮都改了方案，继续挖边际收益已转入施工细节，
按 SOP §4 封批）。四闸结论：M1/M2/M3 关键结论均 ≥2 独立来源；A股适配=regime 门复用
自有切片、Wilson 无市场结构假设、meta 门不改执行语义；可回测性=C2 断言套件+C3 滚动
指标天然闭环；字段全既有（零新 DDL 需求，唯 C3 权重持久化目标待现场定）。

## 五、施工批切分（按 construction SOP 15 步，每批独立 commit 正门）

- **W-C1 通电批**：pattern_signal_runtime.py（scaffold 新建+翻译登记+depgraph 设计节点）
  +engine→provider→mapper 链路单测（tmp_path）
- **W-C2 接线批**：signal_factory 档接入+meta 门（regime+弱证据）+PIT 管线断言+审计快照
  +provider Wilson 化（145 线自治）
- **W-C3 调权批**：131 装配+物化完成事件钩子+权重持久化落地
- **W-C4 呈现批**：3 端点+前端图形库页
- 边界登记（C5）随各批 commit message 交底；每批 commit 后 git log -1 --name-only 核实
