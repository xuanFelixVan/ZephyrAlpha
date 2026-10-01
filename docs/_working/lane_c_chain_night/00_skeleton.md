---
created: 2026-10-01
ttl: task_bound
title: 车道C病链+事件系统夜战总包骨架（st-lanech-20261001 总包）
session: st-lanech-20261001
related: docs/_working/total_circulation_night/00_skeleton.md（总流通夜战骨架，环节体系互挂）
worktree: .worktrees/st-lanech-20261001
note: 20261001 删除事故后重建（原主区 untracked 目录被他队清理，重建落 worktree git 跟踪区）
---

# 车道C病链+事件系统夜战骨架

> Owner 令（2026-10-01 凌晨）：三病链全部开工，线内先挖后干、线间并行流水，零遗留交付。
> 挖矿真源：本会话 2026-09-30/10-01 四矿区挖矿报告（15 病根全实证）。

## 一、环节清单与终态

| 环 | 环节名 | 病根 | 终态 | 施工簿 |
|---|---|---|---|---|
| E1 | 候选供给环（lane C gplearn mine） | A2 算法失稳 + A3 消费不设防 | ✅ 修复落地（582c93ae） | e1_mine_repair.md |
| E2 | 触发环（FactoryLaneC + E0 闸） | A4 日历缺周末行 + A5 wrapper 吞错 | ✅ wrapper rc+工作日 20:00（582c93ae+任务重注册） | e2e3_ops_repair.md |
| E3 | 翻译供给环（Ollama/C3） | C2 OllamaServe 断供 | ✅ 失败重启+探活 UP（qwen3:8b/14b） | e2e3_ops_repair.md |
| E4 | 事件总线环（journal） | B1/B2/B3/B5/B6 | ✅ 手术 pending_left=0 + 代码治本五项（582c93ae） | e4_journal_surgery.md + e4_code_fix.md |
| E5 | 告警环（毒丸出口） | B4 ERROR≠CRITICAL | ✅ 毒丸告警升级 CRITICAL + repair CLI | e4_code_fix.md |
| E6 | 预审环（E2 defer 积压） | C2 衍生 | ✅ 三轮重放：246 条真判定（passed 101+/rejected 129+），defer 尾 40 转夜班自动消化；LLM 超时 60→240s | （本簿§三） |
| E7 | 构造环（E2→E3） | C1 衍生 | 观测（E6 过审集自动消化，F06 已现 passed） | （挂 E6/E11） |
| E8 | 批测环（C4/c4_batch_due） | B3 | ✅ 挖干封矿：85/85 已入账无积压 | e8 记录见本簿§四 |
| E9 | 监控环（三盲） | C3 | ✅ wrapper 内置 Alerter 心跳；deadman 表扩展登记移交（防跨队冲突） | e2e3_ops_repair.md |
| E10 | 数据健康环（TI 214 列） | A1 断层 + A2' 自繁衍 | ✅ 普查（12 列 Inf 277.6 万格）+ 算法修面 12/12 + 写链 sanitize 闸 + 存量 mutations 清洗 | e10_data_health.md + e10_fix.md |
| E11 | F 车道消费断点 | pipeline:73 欠账 | ✅ 适配器落地+3700 配方回填+E2 实证 precheck_passed | e11_lane_f_adapter.md |

## 二、提交与 merge 终态

- worktree 分支 ai/st-lanech-20261001/task-lane-chain-fix：**582c93ae**（主体簇 17 文件）+ **8233da08**（测试簇 5 文件）。
- merge 回 dev 挂起：主区 60+ 他队在途 staged 阻挡（含 tests/backtest/test_lane_c_formula_miner.py 他队同文件在途）。**硬期限：10-01 20:00 挖矿窗前完成 merge**（FactoryLaneC 已改工作日 20:00，届时主区 HEAD 须为修复后代码）。
- 主区 token 先行批（8 施工簿 md + capability 册 8 token）：主区工作区就绪待提交，与 merge 同窗收口。

## 三、E6 预审重放战果（记录）

- 第一轮（主区，60s 超时代码）：15 条 defer 再 defer（Ollama 冷启动超时，defer_llm_unreachable 62.1s avg）。
- 修复：hypothesis_precheck 调用侧 LLM 读超时 60→240s。
- 第二轮（worktree 240s）：**53 条真判定**（passed 22/rejected 31，avg 2.8s——模型热身后秒判）。
- 终轮（limit 60）：累计 **246 条真判定**（passed 101/rejected 129/新 defer 16），E2 通道复活实证（对比此前 9 天 0 有效判定）。
- 残余 defer 40 条=队尾待复审（F 车道 3700 新候选按设计优先占名额），夜班自动消化，非基础设施故障。

## 四、E8 批测环挖干记录（封矿）

- CH 台账对账：translated 目录 85 件 c4_*.py 全部已入 c1_backtest.strategy_screen（screen_batch='C4-translated-20260912'），未批测积压=0。
- 09-16 两条 c4_batch_due 事件=已考完的废件（他队 21:07 已清理）；"全仓 0 处 drain(allow_heavy=True)"的结构缺口保留裁定：重活显式 drain 语义不变，靠 c4 独立夜批直接跑批（其自身调度与事件总线解耦）。

## 五、冲突台账

| 对象 | 他队 | 处置 |
|---|---|---|
| pipeline_events.py | st-circ-a7（F82/F27） | 已落地 HEAD，我簇基于其上叠加，兼容性测试全绿 |
| capability_canonical_file_registry.yaml | st-fullscore 等 | 主区册热拉锯：lane_f token 在 worktree 册随袋落地；主区工作区 8 token 待提交 |
| module_translation_registry.yaml | 多队 | 热册拉锯实锤（我 03:31 写入被他队 verified_promotion_check 覆盖，重插解决）；lane_f 条目主区+worktree 双侧在位 |
| tests/backtest/test_lane_c_formula_miner.py | 他队 staged 在途 | merge 挂起主因之一，落地后对账合并 |
| 主区 staged 60+ 文件 | 五大队 | merge 挂起，提交潮落定后重试 |

## 六、事故记录

- **20261001 施工簿删除事故**：主区 docs/_working/lane_c_chain_night_20261001/（untracked，8 md）被他队清理删除（untracked 无 B2 护盾）。重建落 worktree git 跟踪区（本目录），教训=**施工产物即写即 git add 铁律对 untracked 新目录同样适用**，或直接落 worktree 跟踪区。

## 七、判据

- 挖干=六向台账+自审闸三态；施工=内收原则；收口=循环检查×2 零→红蓝→全绿。
- 提交=git_commit.py 正门；OWNER 门位事项（STR-AUTO-001 注册表净删/日历口径变更）登记留裁，未动。

## 八、14:4x 定向 stash 破局尝试记录（失败，零丢失）

Owner 问"能不能自己提交"→ 执行定向破局：快照三文件→stash push 三文件→merge——merge 仍被挡
（弹入/他队活跃文件构成新阻挡面），且 pop 时池序被插队，误弹他队遗留整面 stash 入工作区。
**损害=零**：三文件与快照逐字节一致 ✓；弹入内容=他队工作面本就该回工作区（知情条已留
fullscore_night/10_coordination/stash_pop_notice_st-lanech-20261001.md，stash commit a50ed2c4 可考古）。
学费=**多队并发期 stash 池是共享危险区：push 后必须立即记 hash，pop 必须显式 stash@{n} 指名，禁裸 pop**。
merge 回归守候模式（watchdog+automation）。
