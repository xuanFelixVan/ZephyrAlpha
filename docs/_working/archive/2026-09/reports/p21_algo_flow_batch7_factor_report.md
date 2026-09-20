---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓 批7 报告：factor 域（st-btfix-p15-20260915）

## 概要

| 项 | 值 |
|----|----|
| 域 | factor → `docs/03_modules/_domain_factor/algo_flow/` |
| 出仓文件 | 82 src（内联块 → 单行 external 锚点），3910 行机器块外迁 |
| yaml 产物 | 82 本批新建 |
| 测试 | tests/factor = **825 passed**（100.8s，隔离 cache_dir） |
| 提交 | `88d9ee5b`（166 文件，零吸收已核实） |
| 幂等 | 复扫 0 待出仓（72 skipped + 15 already） |

## 配套登记

- **创建令牌**：+91 条（capability `btfix_p1p2`，created_by st-btfix-p15-20260915）——**已由他会话吸收落库**：kimi 挖矿会话提交 `cbd9bb40cc` 落库注册表时连带吸收了我方 91 条 token（+368 行），批7 主提交因此不含注册表（REGISTRY-MASS-DELETION gate 拦截暴露：我方暂存版落后 HEAD 4 行/1 条目）。token 均已入库，无重复义务。
- **TDM 注解**：2 节点（TDM-E-L3-07-2 多因子打分链 / TDM-F-C3-02 升降级管线与退役评审，note_confirmed 2026-09-15 紧贴 node_id + algo_note_zh 出仓注记）。
- **CloneGuard**：6 对既有克隆暴露（配置加载/默认参数/因子校验/状态清空等样板同构），均核实 HEAD 既有，echo-guard.yml acknowledged（25 条累计）。

## 过程发现（多会话并发高峰实录）

1. **watchdog 第三次抢先 adopt**：以 `st-circmv-synthcw-20260915` 合成会话持有 79 个 factor src（批5 为 task:SRC-081）。同法处置：gateway.release_files 精准释放 → 秒级重 claim 全成。
2. **会话 TTL 过期**：claim 时自动注册的会话 1 小时 TTL 到期 → 提交被 SESSION-REQUIRED 拦截 → claim 一次即自动重注册，但存在重注册后个别文件 claim 丢失（reversal.yaml）需补 claim。
3. **REGISTRY-MASS-DELETION gate 拦截**：他会话先落库注册表后，我方暂存版相对 HEAD 成净删——登记表提交必须以"提交前重读 HEAD"为前置，多会话并发下暂存版保质期极短。
4. **git add / index.lock 竞态**：staging 循环遇 index.lock 128 失败需重试；daemon 在纯化后会再次 auto-stage 外来文件，提交前必须最后一步再纯化。

## 战役进度

- 已出仓累计：批1-2（72）+ 批3 regime（42）+ 批4 ex_core（59）+ 批5 ml_train（43）+ 批6 risk（76）+ 批7 factor（82）= **374 文件（11.3% / 3302）**
- 剩余大域：feedback_loop(340) / infrastructure(336) / governance(296) / shared(243) / gov_enforcement(188) / security(188) 需独立立项；中小域：autonomy_core(138) / signal_ashare(128) / data(116) / trading(92) / orchestrator(75) 等可继续逐批。
- 遗留（非本批义务）：pytest_min.ini markers bug；TDM note 归因窗口重设计；GATE-PANORAMA-ALIGNMENT 检测器失效。
