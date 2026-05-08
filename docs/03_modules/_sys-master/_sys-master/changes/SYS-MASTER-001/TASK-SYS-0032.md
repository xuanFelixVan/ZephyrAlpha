---
task_id: "TASK-SYS-0032"
source_blueprint: "SYS-MASTER-001"
source_section: "§50 多策略组合与容量管理 + §51 经纪商容灾与应急平仓 + §59 运维基础保障 + §62 日运营节奏与交易会话协议"

title: "多策略组合四构造法(1/N静态/RiskPari/Kelly Criterion/MaxDD限制) + 容量估计(C_max/退役触发器) + 经纪商三级容灾(主P0→备P1→应急P2)+四类故障+四步应急平仓 + 运维基础保障(四层备份/四类日志/配置漂移/检查点/环境版本化) + 日运营五阶段ET(08:00-18:00)+四快捷指令 四合一骨架"
description: |
  将 §50 多策略组合 + §51 经纪商容灾 + §59 运维基础保障 + §62 日运营节奏四合一落地为交易操作完整性锚点。
  §50 定义：
  （1）四种策略组合构造方法——1/N 静态权重（均值诊断）· Risk Parity × 每日 rebalance（波动率反比）· Kelly Criterion f* = (bp-q)/b（概率盈亏率）· Max DD 限制（任何策略DD>20%→底部位置砍半）。
  （2）策略退役触发——Sharpe 12个月 < 0.0→退役· Calmar 12个月 < 0.3→12个月观察· 连续6个月负回报→自动退役。
  （3）容量估计——C_max = min(Signal Decay 开始衰减 × 流动性利用率 × 冲击模型)· MAX(10M USD, C_max)→ 标量容量。
  §51 定义：
  （1）三级经纪商灾备——主P0(主要API Primary)· 备P1(自动故障转移到备用+continue open orders+sync positions)· 应急P2(手工/第三方broker，仅平仓减少风险)。
  （2）四类经纪商故障——API连接丢失（P0 dead→自动P1 resuscitation + 5min circuit breaker）· 错误拒绝（error_rate>20%→human review→临时P1）· 间隙成交(Gap Fill)（大滑点>5×spread→暂停+劣频调查）· 市场异常中断（Exchange-wide halt→全部shift to emergency monitor）。
  （3）四步应急平仓——①检测P0故障>容忍（P0 90s+P1 120s）→ ②简报 Owner（new pending in L0+唯一 brief）→③P2 20% Exposure→每15min再降20%→④P0恢复继续→ 5min后转P0 / P0未恢复→Owner dec 3x Go/No-go。
  §59 定义：
  （1）运维基础保障——四层备份（Git/Cloud Zip Daily/ Db Dump Twice/ Secrets Vault）· 四类日志（System/Order/Market/AI Decision, ISO8601Z,single log daily<100MB per module）· 配置漂移（每24h config.yml vs last-good→diff→告警+last-good覆盖）· Pipeline检查点（每步写入 restartable 状态 + 24h+残差清理）· Dev环境版本化（freeze.txt md5 hash→ ≥每周更新）。
  （2）一键环境重建——git clone + pip install + python setup_check.py（5秒完成）。
  §62 定义：
  （1）日运营5阶段 ET P1 08:00-09:30 启动+盘前检查//P2 09:30-16:00 主交易时段//P3 16:00-16:30 收市核实//P4 16:30-17:30 盘后系统维护//P5 17:30-18:00 日终总结。
  （2）四个快捷指令——/crisis（立刻Pause所有策略仅Emergency defense·内存Only）· /status（实时关键指标 clean dashboard）· /notes（所有今天关键事件 markdown saved to daily_notes.md）· /publish（将今天稳定变更发布到MOD-MASTER-001 + bump版本号）。
  本卡搭建 strategy_portfolio.py + broker_resilience.py + ops_foundation.py + daily_ops.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\strategy_portfolio.py"
    description: "§50 4构造法(1/N/RiskParity/Kelly/MaxDD) + 退役(Sharpe<0/Calmar<0.3/6m负) + C_max容量"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\broker_resilience.py"
    description: "§51 3级(P0主/P1备/P2应急) + 4故障(API/拒绝/间隙/中断) + 4步应急平仓"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ops_foundation.py"
    description: "§59 4备份+4日志+配置漂移+检查点+环境版本化+1键重建"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\daily_ops.py"
    description: "§62 5阶段ET(P1 08:00→P5 18:00) + 4快捷指令(crisis/status/notes/publish)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\strategy_portfolio.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\broker_resilience.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ops_foundation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\daily_ops.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§50 4方法+退役+C_max + §51 3级+4故障+4步平仓 + §59 备份/日志/漂移/检查点/版本化 + §62 5阶段+4快捷指令"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 80

acceptance_criteria:
  - "strategy_portfolio.py 实现 PortfolioConstructor——4 methods(1/N: equal_weight diagnose mean· RiskParity: 1/σ²_i→daily rebalance L2· Kelly: f*=(bp-q)/b clamp 0.25×cf_resk· MaxDD: any strat DD>20%→halve allocation)· Retirement(Sharpe_12m<0 → RETIRE· Calmar_12m<0.3→12m WATCH· consecutive_6m_negative → AUTO_RETIRE)· CapacityEstimator(C_max=min(signal_decay_start,liq_util,impact)· MAX(10M,C_max))"
  - "broker_resilience.py 实现 BrokerTier 枚举（PRIMARY_P0/BACKUP_P1/EMERGENCY_P2）——故障自动切换 P0→P1（API dead→resuscitate within 5min）· error_rate>20%→human review→temp P1 · large_slippage>5×spread→pause+latent investigation · ExchangeHalt→EMERGENCY monitor"
  - "broker_resilience.py 实现 EmergencyLiquidation——Step1 detect P0 fail>tolerance(90s P0+120s P1)→Step2 brief Owner(L0 notify+unique brief)→Step3 P2 reduce 20% Exposure per 15min till 0→Step4 P0 recovered→resume 5min+revert to P0 / P0 not recovered→Owner 3×Go/No-go decision"
  - "ops_foundation.py 实现 BackupManager——4 layers(Git/daily cloud zip/SQL dump twice/vault)· Logger(4 types:System/Order/Market/AI_Decision ISO8601Z <100MB/day per module)· ConfigDriftGuard(24h config.yml vs last-good→diff→alert+override)· Checkpoint(step→write restartable state + >24h stale cleanup)· EnvVersion(freeze.txt md5+hash ≥weekly→audit check)"
  - "ops_foundation.py 实现 OneClickSetup——git clone + pip install + python setup_check.py→verify within 5s"
  - "daily_ops.py 实现 DailyRhythm——5 Phase ET(P1 08:00-09:30 pre-flight checks/P2 09:30-16:00 primary trading/P3 16:00-16:30 settlement verify/P4 16:30-17:30 daily maintenance/P5 17:30-18:00 eod recap)· 4 QuickCommands(/crisis pause all strategies emergency defense M→RAM· /status real-time dashboard· /notes save critical events markdown· /publish publish stable changes MOD-MASTER-001 bump version)"
  - "script_manifest.yaml 注册全部 4 个 .py"

rollback_instructions: |
  1. 删除 strategy_portfolio.py / broker_resilience.py / ops_foundation.py / daily_ops.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0029"
blocked_by: []
status: "done"
tags_fn:
  - "trading"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
