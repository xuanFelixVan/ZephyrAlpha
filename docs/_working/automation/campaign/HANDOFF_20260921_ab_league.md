---
ttl: task_bound
completes_when: A/B 联赛四件套施工落地且卖出测试归档，或被新交接令替代
---

# 交接总簿：A/B 联赛开工 + 卖出测试 + RL 解禁（第四棒→第五棒，2026-09-21 00:5x）

> 会话世系：st-autolnk-20260917（六线交付+拍板批）→ b 班（L1.1+车道G）→ 本班（挖矿树封矿+QMT 桥实测+R1/R2）→ **下一棒（本文件交接）**。
> 前会话 sessionId=sess_526a209c-3f12-4535-95c6-25cc197ab05e（ReadSessionContext 可读）。

## 1. 本班核实过的战场状态（2026-09-21 00:4x 实测）

- 时间 09-21 00:41；距上棒已 3 天，**大量平行施工已落地**（intake 挖矿班/unified PLAN v1.0/data-fix 班/git-gov N-5 处置/裁定#385 等——git log 09-20~21 密集可见）。
- residual 战役**已收工归档**：docs/_working/archive/2026-09/residual_construction/（E3 ✅ 32431d66 等；其 C1 三共享文件独占**随收工解除**，但 tasks.yaml 仍属多车道共用热文件，改前照旧 acquire）。
- **本战役资产健在**：mining/ 十工段作业簿+总谱完好（st-mine 线加了 index.md+coordination 文件，工单已被各车道认领施工中=生态闭环）；六线测试 50/50 绿；fx 表 69 行/最新 09-18（Windows 任务 23:30 自动班持续打卡，周末自动跳过=正确）；R1 已达成（daily_alt_fx 在 22 jobs 内）。
- **QMT 模拟户实测**：E:\qmt_bridge_sim\Stock\PositionStatics.csv 显示持仓 **510300 沪深300ETF 1100 股**（"零售10测试"备注，早前测试买入，T+1 早已过期=卖出测试原料充足）；大 QMT 模拟端 XtItClient 需在运行（上次实测 18901 LISTENING=文件桥 HTTP 快路径活）。**MiniQMT 09-18 下线——一切走大 QMT 文件桥（MOD-L06-001-QMTFB），禁拉 XtMiniQmt**。

## 2. 下一棒开工清单（Owner 已裁定"全部可做，实盘除外"）

### 件 1：A/B 联赛（Owner 明令"现在就要跑起来"，支持 A~G 任意扩展，核心=百分百复原）

新文件（全部新建，无共享热文件冲突）：
- docs/_working/automation/campaign/mining/11_联赛/工段作业簿.md（先挖矿封矿：十节结构，同 mining/00_总环节谱.md §三）
- config/league_registry.yaml — 联赛注册表（组 ID A/B/C…；参赛日；状态 champion|challenger|retired；档案路径；判定窗）
- scripts/backtest/league_registry.py — 加载/登记 API（学 standards_lib 风格）
- scripts/backtest/league_archive.py — 参赛档案打包器：manifest.yaml（git commit hash+因子清单+数据指纹 trade_date 截止+配置快照+整装回测产物指针 fw-auto/latest.json+模块依赖链接）→ archive/<GROUP>-<date>/。复原口径=三指纹（代码 git hash+因子定义+数据截止日），数据本体不可复原但 CH 可按截止日重查——边界如实写进 manifest
- scripts/backtest/league_restore.py — 复原器：读 manifest→核对当前 git/因子/数据截止日差异→输出可复原性判定+执行 git checkout 指纹
- scripts/backtest/league_monthly_snapshot.py — 月度对比快照：sim_pocket_daily 按组拉 equity→对比表→data/backtest_artifacts/league/snapshot-YYYYMM.md（只留档不判胜负）
- tests/backtest/test_league_*.py — 上述全部纯函数测试
- 判定器（6 个月终审）：复用 promotion_combo_gate+STD-SWITCH-001(#305)口径，挂单至首组满窗

接口（只读复用，勿改）：src/zephyr/strategy_pipeline/promotion_advisory.py（MOD-BT-199）、sim_governance/sim_deviation_report 月度链、promotion_combo_gate.py（L2 已建）。

### 件 2：卖出测试（Owner 明令"买测过卖没测，按理买行卖也行"）

- 走大 QMT 文件桥（同 100 股买入协议）：QmtFileBridgeBroker(env="sim")，标的=**已有持仓 510300 卖 100 股**（T+1 已过可卖），限价=市价附近（ETF ~4.66 元）
- 流程：connect→读 PositionStatics 镜像持仓→submit SELL 100→轮询状态（夜间=已报，成交腿等开盘）→撤单或留单→证据 yaml 至 docs/_working/full-auto-chain/evidence/qmt-bridge-sell-20260921-c4.yaml
- 禁区：QMT_REAL_*/enable_real/ZEPHYR_ENV=live 全禁；勿拉 XtMiniQmt（已下线）；勿动 kill_switch 持久态

### 件 3：RL 训练器（Owner 解禁——大白话：给"执行训练场"搭教练）

- 现状：src/zephyr/ex_sor/rl_exec_env.py 骨架（reset/step+负 implementation shortfall 奖励）无 torch 无训练器
- 工单：trainer（建议 TD3 起步）+历史 replay 数据预热+checkpoint 纪律；产物只进模拟盘对拍
- 前置：torch 环境（Kronos 微调曾实测 torch 2.13+3090 可用）；training 是离线 GPU 活不碰钱

### 件 4：数据源转正（Owner 裁定"不用等 7 天，自动+报警即可"）

- fx 表实测已自动打卡 4 天（69 行/09-18）→H-06（AltFxECB Windows 任务退役）维持挂单等 L1.1 正门班次观察，不阻塞任何事
- intel_harvester/ECB 源全部维持自动；异常报警=已有 ops 告警桥承接

## 3. 红线与坑（全量，前四棒血泪浓缩）

1. 禁写 docs/03_modules/**、TDM、AGENTS.md；新模块蓝图暂存 campaign/blueprints（H-01）
2. 提交走 GitCommitGateway；TRAE-079 allow_overlap 24h 限 5 次（热文件用 lock_files.py acquire 正道）；SESSION-REQUIRED=pid=0 会话 90s 过期——注册+提交同一命令
3. **改后即 add**（网关失败清理链+共享区回滚链会吃未 add 新文件）；队列 serializer 隔离暂存区（staged 外来内容连坐时入队是唯一解）；队列 serializer 世界读快照内 catalog——CREATE-GUARD 引用的 token 所在 catalog 必须同批入袋
4. 新 .py：REPO_ROOT 用 zephyr.shared.io.paths、时间用 now_utc()（禁 datetime.now）、[BLUEPRINT] MOD-ID 禁括号、m11/m10 豁免格式=noqa+理由≥10 字、禁 §N.N 引用写法（DANGLING-REFERENCE 拦，写"第N节"）
5. ch_reader.query 返回 TSV 字符串非 dict；count() 助手在手；papersession/交易禁区见 campaign/qmt_e2e_runbook.md
6. 测试命令模板：python -m pytest <files> -q -o cache_dir=.runtime/tmp/pytest_cache_autolnk

## 4. 挂单与依赖门（全量，有主有触发）

- H-01 蓝图晋升（docs/03_modules 解冻）/H-02 fx 表名进 TableRegistry/H-03 GPU-01/02（backtest 收针）/H-04 RL 真训练 Owner 门（训练器施工已解禁，真训练后模型上实盘仍 Owner 门）/H-05 CH register ps1/H-06 AltFxECB 退役（等正门观察）/H-07 standards.yaml 进 ROOR
- L7 判定窗：首组参赛起 6 个月（月度快照留档、终审一次性）；裁决#306 组合门 v2 draft 待重考；#305 切换判据 STD-SWITCH-001 已登记 draft_upgrade_eligible
- R2 打卡：Windows 任务日 23:30 自动（现已 4+ 天绿），无需人工
