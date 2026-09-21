---
ttl: task_bound
completes_when: Owner 对门清单逐门点单后转 archived
session: st-live-readiness-20260922
date: '2026-09-22'
---

# 实盘准入门禁设计 — 小资金实盘准入准备班 · 件4

> 班次：st-live-readiness-20260922（通宵令 §3 分包1）
> 定位：**哪些门全绿才许挂实盘旗**——供 Owner 拍板的门清单+检查器设计。本班只设计，不施工、不翻转、不连接。
> 设计原则：①判定优先**机械可证**（Owner 机械判定门铁律：文件存在/flag 值/注册表行数/报告数字直接查）②门与门独立，单门绿≠整体绿 ③`promote_ready≠决定`——全绿后仍须 Owner 门位签发（promotion_combo_gate.py:15 同语义）④禁跳门、禁 AI 自动升档（B-007）。

---

## §1 门清单（G1–G12）

| 门 | 名称 | 判据（机械可证口径） | 当前状态 | 卡在哪 |
|----|------|----------------------|----------|--------|
| G1 | 密钥轮换闭环 | tc_10 步骤5 核对通过：OKX（只读+IP 白名单+禁提币）/iFind/百度盘 token 已换；AI 复核=只报键名/格式零打印值 | 红 | **等 Owner**（曝光 09-18 后超 3 天未轮换） |
| G2 | 整装回测达标 | L2 组合门四阈值全过（`promotion_combo_gate.py:56-61`）：OOS Sharpe≥1.5 / 最大回撤≤15% / 纸面成交≥30 笔 / DSR>0；红蓝两轮 0 | 红 | **等指令 A**（st-integrated-bt-20260922：协议 v1 已冻结 01:05，W_IS 首跑在飞，红蓝未做）+等指令 B（30 笔纸面成交） |
| G3 | 策略包毕业 | `GRADUATED_PACKAGES` 非空，且条目可溯源到 S-OWNER 考试链产出（禁手填，裁定#305 语境） | 红 | **等考试链**（80 条 E4 及格者卡 E7；卡1/卡2 FAIL 且 OOS 已烧禁重跑） |
| G4 | 模拟盘连续绿 | 模拟盘 E2E 圈连续 **N 日**全 ok+零 error+验证环日更。N 本班建议=**20 个交易日**（约一个自然月，覆盖月末/月末效应与至少一次完整周循环）；N 为建议档，**待 Owner 确认** | 红 | **等指令 B**（st-sim-launch-20260922 实测进度=0，worktree 刚建未落盘）+等模拟终端 GUI 登录（Owner 四类事） |
| G5 | 熔断链实弹验证 | sim 环境完成一次 HALT 拒单演练：pre_execution_checker 闸门1 注入后实跑，验证拒全部新单+fail-closed（探针拔掉=拒单）。同批满足 real_channel_locked 解锁前置"纸面≥3 次演练"中的演练计数 | 红 | **等指令 B**（sim 部署后可做；代码面已就绪 `pre_execution_checker.py:176-206`） |
| G6 | blocks_live_trading 接线 | 下单路径存在对该 flag 的代码断言（下单前查 live 档 blocks_live_trading=true → 拒单）；现状=配置声明零消费方（本班 grep 复核） | 红 | **施工项**（小改，本班红线禁施工，另行立项） |
| G7 | 仓位参数 confirmed | 60% 硬顶+六段预算带+过渡带 0.5-0.7 从 proposed→confirmed（daily-orchestrator-blueprint.md:187 口径），Owner 签字 | 红 | **等 Owner** |
| G8 | 交易级告警补齐 | alert_threshold_registry 增加行情价格/仓位级专条：位置超限（POSITION_LIMIT 阈值）/日亏 -3% AUM/断连/心跳丢≥3——与五级熔断阈值一一对应 | 红 | **施工项**（登记册增补，须走注册表流程，本班禁施工） |
| G9 | 熔断态持久化或守护 | R3 缺口闭环：五级熔断触发态落盘（state 文件）或交易进程有守护+重启后状态重建 | 红 | **施工项**（本班禁施工，另行立项） |
| G10 | live 参数填入 | qmt_environments.yaml live 档 account 填入+资金规模定案+单笔止损百分比定案（Owner 门位） | 红 | **等 Owner** |
| G11 | 换档审批 | B-007 阶梯 paper→pilot 的 Owner 签发记录在册（pilot=小资金实盘档位） | 红 | **等 Owner**（前置=G1-G10 全绿） |
| G12 | 外部合规确认 | 程序化交易报备/券商 QMT 实盘开通条件/税负口径，Owner 书面确认结果登记 | 白 | **等 Owner**（超出仓库知识） |

**门依赖拓扑**：G1/G6/G7/G8/G9 相互独立可并行；G2=G2a（回测指标，等指令A）+G2b（30 笔纸面，等指令B）；G4/G5 依赖指令B 部署；G3 依赖考试链；G11 依赖其余全绿；G12 独立但须尽早启动（券商流程周期不受我方控制）。

## §2 依赖项清单（收官分列）

### 等 Owner（7 项）
| # | 事项 | 对应门 |
|---|------|--------|
| O-1 | 密钥轮换执行+叫核对（必换 OKX/iFind/百度盘；建议换 LLM key+TUSHARE_TOKEN） | G1 |
| O-2 | 仓位参数 confirmed（60% 硬顶/六段预算带/过渡带） | G7 |
| O-3 | 资金规模定案+单笔止损百分比定案 | G10 |
| O-4 | 模拟盘绿天数 N 确认（本班建议 20 交易日） | G4 |
| O-5 | crisis θ 校准（0.5 起步，月度演练回看误报率） | 面1-R4 |
| O-6 | 换档签发 paper→pilot | G11 |
| O-7 | 外部合规确认（程序化报备/券商条件） | G12 |

### 等指令 A 产物（整装回测，st-integrated-bt-20260922 在飞）
| # | 事项 | 对应门 |
|---|------|--------|
| A-1 | 首跑报告（W_IS→W_OOS→W_HOLDOUT 单次→红蓝两轮 0） | G2a |

### 等指令 B 产物（模拟盘，st-sim-launch-20260922 实测进度 0）
| # | 事项 | 对应门 |
|---|------|--------|
| B-1 | 模拟盘部署+首圈 | G2b/G4/G5 |
| B-2 | 纸面成交≥30 笔积累 | G2b |
| B-3 | 模拟终端 GUI 登录（Owner 四类事：密码） | G4 前置 |

### 等考试链
| # | 事项 | 对应门 |
|---|------|--------|
| X-1 | ≥1 个策略包经 S-OWNER 考试链毕业（GRADUATED_PACKAGES 首条） | G3 |

### 本班禁施工、建议另行立项的施工项（3 项，均小改）
| # | 事项 | 对应门 | 说明 |
|---|------|--------|------|
| S-1 | blocks_live_trading 代码断言接线 | G6 | 下单前查 live 档 flag，拒单+告警；预计 <50 行 |
| S-2 | 交易级告警专条入 alert_threshold_registry | G8 | 4 条（位置/日亏/断连/心跳），走注册表流程 |
| S-3 | 五级熔断态持久化 | G9 | state 文件落盘（paper_hedge state_path 同款纪律）或进程守护+重建 |

## §3 检查器设计（check_live_readiness，只读探针稿）

**形态**：一个只读检查器（建议 `scripts/governance/check_live_readiness.py`，本班不建，仅设计），零网络、零下单、输出 JSON 到 `.runtime/tmp/`（测试隔离纪律：禁写生产路径）。

**判定矩阵**（每门一个纯函数，机械可证优先）：

```
G1: 读 tc_10 步骤5 行状态==已做 AND 核对回执文件存在            → PASS/FAIL
G2: 读 promotion_combo_gate 最新输出 JSON（data/strategy_intake/
    promotion_advisories + docs/_working/pipeline-research/promotion-reports）
    四键 ≥阈值 AND verdict==promote_ready                        → PASS/FAIL/BLOCKED(无报告)
G3: 读 GRADUATED_PACKAGES 注册态非空 AND 每条含 exam_chain 溯源字段 → PASS/FAIL
G4: 读模拟盘 E2E 台账最近 N 日行，全 ok 且 error=0               → PASS/FAIL/BLOCKED(N 未定或台账缺)
G5: 读演练留痕 data/backtest_artifacts/paper_hedge/ 演练次数≥1
    且含 HALT 拒单演练记录                                        → PASS/FAIL/BLOCKED(等 sim)
G6: grep 下单路径文件含 blocks_live_trading 消费方（AST 级更佳）   → PASS/FAIL
G7: 读仓位参数状态字段==confirmed                                 → PASS/FAIL
G8: 读 alert_threshold_registry 含交易级专条≥4 条                 → PASS/FAIL
G9: 读熔断 state 文件存在或守护任务注册                           → PASS/FAIL
G10: 读 qmt_environments live.account!="" AND 资金参数册存在       → PASS/FAIL
G11: 读换档签发记录存在                                            → PASS/FAIL
G12: 读外部合规确认登记存在                                        → PASS/FAIL/BLOCKED
```

**输出契约**：`{"gate_id": "...", "verdict": "PASS|FAIL|BLOCKED", "evidence": "文件:行号或键值", "checked_at": "..."}` 逐门一行 + 顶部 `all_green: bool`。**all_green=true 也只产出"建议 Owner 签发"提示，不触发任何实盘动作**（promote_ready≠决定 同语义）。

**跑法**：手动触发或挂晨审车辆；每次输出为只读快照，禁止写生产路径（宪法 §9.6）。

## §4 反面清单（挂旗前最后一次核对）

1. 禁区四条全程有效：`QMT_REAL_*`／`enable_real`／`ZEPHYR_ENV=live`／`LiveSimulationSwitcher.switch_to_live` 全禁（qmt_e2e_runbook.md:28-30；本班通宵令 §4 同口径）。
2. real_channel_locked=true 恒真；解锁=纸面≥3 次演练+Owner 批准，且**解锁当日必须同步把 paper_auto_confirm 置 false**（paper_hedge.yaml 注释原文：真实通道解锁后人工确认回到 Owner）——两个 flag 联动，禁只翻一个。
3. kill_switch 复位属 Owner（qmt_e2e_runbook.md:30 附条；系统级 kill_switch reset 语义 :300-318）。
4. 禁跳门：任何"情况特殊先上实盘"=违宪（§5 门位），唯一通道=Owner 裁定登记。
5. 双终端在线时辨机唯一权威=TCP 配对法，LISTEN 端口法禁用（qmt_environments.yaml disambiguation 节，2026-08-03 实测二义）。
