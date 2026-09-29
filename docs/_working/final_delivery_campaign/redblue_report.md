---
ttl: task_bound
title: 最终交付战役四改动红蓝极限对抗报告（st-finaldel-redblue-20260929）
session: st-finaldel-redblue-20260929
---

# 红蓝极限对抗报告 — 提交链战役四改动（Rx-1/Rx-2/Rx-3+4/morning_digest）

> 对抗日期 2026-09-29；对象=60d7bdda（Rx-3/4）、280d40d5fc 系（Rx-1）、Rx-2 锁等待账本、morning_digest 收编链（工作树版）。
> 全部攻击场景在 `.runtime/tmp/st-finaldel-redblue-20260929/` 与系统临时目录构造，零生产写。
> 判定口径：蓝胜=防线按宣称语义成立；红胜=真缺陷。红胜小缺陷当场修+回归钉子+正门提交；大缺陷/在飞竞态登记。

## 逐场景判定表

### Rx-1 入队 ruff 预清（git_commit._ruff_preclean_gate + enqueue_preflight.ruff_preclean）

| # | 红攻手法 | 预期防线 | 实测结果 | 判定 |
|---|---------|---------|---------|------|
| R1a-1 | 250 个 .py 清单（>200 限流） | 限流 skip 不挂死 | 0.01s skip 记原因 | 蓝胜 |
| R1a-2 | 恰 200 文件满批 | 预算内跑完 | 0.11s 通过 | 蓝胜 |
| R1a-3 | 单个 10-20MB 大文件 | 秒级快败 | **ruff format --check 咬满 60s 撞超时**（10MB 文件后台实测 >90s 被 timeout 硬杀）；限流原按数不按体积，最坏 2×60s/次 | **红胜→已修** |
| R1b | 绝对路径/不存在件/空清单/.py 后缀目录 | 全部不触发不炸 | 全部放行（不存在件无法提交，放行无害） | 蓝胜 |
| R1c | --skip-preflight 逃逸 + 落地权威对照 | 诊断逃生不豁免落地 | gate 放行后 tmp 仓真 pre_commit run 同文件 rc=1——语义守恒 | 蓝胜 |
| R1d | 注入面：CJK/空格/`&%;@` 怪名 + 20 万字符超长行 + 900 连坏行 | 800 字截断处方不炸 | 处方 606 字符、无异常逃逸；concise 格式不回显文件内容=不可伪造报告段 | 蓝胜 |
| R1e | env=0/false/off 关闸 + 变体 | 等同旧路径 | 坏文件放行、enabled 判定全对 | 蓝胜 |
| R1f | ruff 包缺失机器（`-m ruff` rc=1 "No module named"） | 设施故障 fail-open | **rc≠0 被当违规命中=好文件假红硬拦**，违反模块自身 fail-open 不变量 | **红胜→已修** |
| R1g（加测） | `..` 相对路径坏文件 | 照拦 | 放行——根因=ruff respect_gitignore+仓 .gitignore `.runtime/`（攻击树在 .runtime 下被忽略）；gitignored 文件本就进不了正常提交面，非防线缺口 | 蓝胜（备注登记） |

### Rx-2 锁等待账本（_GlobalCommitLock + lock_wait_events.jsonl）

| # | 红攻手法 | 预期防线 | 实测结果 | 判定 |
|---|---------|---------|---------|------|
| R2a | `.runtime/audit` 位点是文件（mkdir 必炸） | 写入器静默、提交照常 | `_append_lock_wait_event` 静默不上抛；全局锁正常获取 | 蓝胜 |
| R2b | 账本注入畸形行（非法 JSON/NUL 字节）+ 注入含换行引号 NUL 的 session_id | 写方转义、无读取方炸面 | json.dumps 正确转义、注入行合法可解析、畸形行共存；全仓 grep 读取方仅 gateway+tests（生产无读取方=无炸面） | 蓝胜 |
| R2c-1 | 双线程真实持锁/等待归因 | holder 指真实持锁 pid、waited_ms>0 | holder='pid=<持锁进程>' waited_ms=1203ms（≈释放延迟 1.2s） | 蓝胜 |
| R2c-2 | 10 进程并发抢锁 | 字段完整、归因不张冠李戴 | 0 错误、9/9 waited_rows 全字段、holder 全部指向真实竞争者集合内 pid | 蓝胜 |
| R2c-3 | 僵尸锁（不存在 pid 4194304） | 收割且 holder 可观测 | 0.00s 收割、holder='pid=4194304' 留痕、waited_ms 在账 | 蓝胜 |

### Rx-3/4 fail_fast + Phase-B 收窄（60d7bdda）

| # | 红攻手法 | 预期防线 | 实测结果 | 判定 |
|---|---------|---------|---------|------|
| R3-1 | `_precommit_config_hook_ids` 11 例对抗样本（缺失/broken yaml/空文档/顶层 list/repos null/repos 为字符串/hooks 空项/id null/id 整数/重复 id/混合好坏） | 解析失败→空元组回全量，永不外抛 | 11/11 全部安全降级或取合法 id，零异常逃逸 | 蓝胜 |
| R3-2 | ZEPHYR_PRECOMMIT_PHASEB_FULL 语义变体（"1"/" 1 "/"true"/"0"/缺省） | =1 回全量 | "1" 含带空格全回；"true" 不识别（文档口径=仅"1"，登记备注非缺陷） | 蓝胜 |
| R3-3 | 变异侦测实弹：快段 hook 改文件但 exit 0 | pre-commit 内建侦测必 rc!=0 | tmp 仓真跑：文件已变异且 hook exit 0，pre_commit rc=1 "files were modified by this hook"——Phase-A 必红，无"绿但变异"逃逸 | 蓝胜 |
| R3-4 | 快段红 + 慢尾红共存（per-hook fail_fast 短路） | 红还是红，不白跑 | 真跑：首败即停（慢尾 0 执行）、rc=1 阻断——红=必然 own（--files own 结构面），短路与全局 fail_fast 掩蔽风险无关 | 蓝胜 |
| R3-5 | SKIP 反选慢尾续跑（SKIP=快段 id） | 慢尾红必被 Phase-B 捕获 | 真跑：快段 Skipped、慢尾 Failed、rc=1 | 蓝胜 |
| R3-6 | 既有 29 例战役测试+账本 8 例回归 | 全绿 | 37 passed | 蓝胜 |

### morning_digest 收编链（工作树版，HEAD 未落袋）

| # | 红攻手法 | 预期防线 | 实测结果 | 判定 |
|---|---------|---------|---------|------|
| R4a | ALGO-FLOW-LINK 判据绕过：yaml 节点 name_en/code 引用不存在函数 | 有层拦截 | check_algo_flow_links blocked=False 直接通过；check_algo_flow.py 也只验标记存在——**双层均不验符号实存**。属判据范围外（gate 不变量从未承诺符号校验），扩展=结构级，登记不修 | 红胜（范围外，登记） |
| R4b | initial_state 非法值注入 11 例（大小写/空格/SQL 注入串/int/None） | 回退 candidate 不炸 | 10/11 回退 candidate 起步正常；`lifecycle_now='shelved'` 直调 `_transition_lifecycle` 抛 InvalidTransitionError——经查 decide() 有 `_OBSERVING_LIFECYCLES=("sim","paper")` 前置闸，该路径经 decide() 不可达（我的探针绕闸直调私有函数，非产品缺陷） | 蓝胜 |
| R4c | 毒 ADV 包（顶层 list/标量 JSON）打 collect_pending_advisories | 坏包跳过不抛（docstring 自宣称） | **顶层 list 包 → AttributeError: 'list' object has no attribute .get 逃逸出 collect**；refresh 兜底接住但=一个毒包打死整份晨报（全部待办对 Owner 不可见） | **红胜（修复受阻，登记+补丁）** |
| R4d | markdown 注入（strategy_id 含链接/加粗） | —（晨报为本地渲染面） | 依赖 R4c 修复后才可达渲染面；本地 Owner 报告、写面已有权限边界，L 级登记 | 登记不修 |
| R4e | 蓝验：pytest tests/strategy_pipeline + check_algo_flow | 全绿+PASS | check_algo_flow rc=0 PASS；morning_digest/promotion 既有测试绿。套件整体 2 失败+1 收集错均为外来漂移（见下） | 蓝胜（附外来登记） |

## 红胜缺陷处置

### 已修（本轮提交，正门 git_commit.py，落地 hash=81eb4a1e，git log -1 核实恰 2 文件无连坐；报告本体因 capability registry 正被他会在飞 converge 未随批，留工作树待后续批次收口）

1. **R1a 体积 DoS**：`scripts/governance/enqueue_preflight.py` 增 `_RUFF_PRECLEAN_MAX_FILE_BYTES=1_000_000`，`_ruff_preclean_py_files` 超限 skip 记原因（与 M2.2 max_bytes 同款保守判据；落地侧权威兜底不缺席）。修复后 1.2MB 坏文件 0.00s skip（修复前 60s+ 撞超时）。回归钉=TestRuffPrecleanRedblue 2 例。
2. **R1f 工具缺失假红**：`_ruff_findings` 无 ruff exe 时先探测 `python -m ruff --version`，rc≠0/超时=设施故障 fail-open 返回空 findings——修复前 rc=1 被当违规命中=全量假红。回归钉=1 例（断言只探测一次、坏文件放行）。

### 登记（不修，附处置处方）

3. **R4c morning_digest 毒包**：修复被在飞竞态阻断——`morning_digest.py`/`test_morning_digest.py` 在死会话 st-finaldel-carch-20260929 的 processing 态队列袋内（blob 快照语义，我改工作树版会被袋落地覆盖、抢提交=双版本竞态）。**处方**：袋落地后由收编会话合入以下补丁（`collect_pending_advisories` 内 `adv = json.loads(...)` 之后）：
   ```python
           if not isinstance(adv, dict):
               logger.warning("建议包顶层非对象（晨报跳过）: %s", path.name)
               continue
   ```
   配套测试：tmp_path 建 ADV-001（合法 dict）+ ADV-002（`[1,2,3]`），断言 `collect_pending_advisories` 返回恰 1 条且 `refresh_morning_digest` ok=True。
4. **R4a 幽灵函数节点**：ALGO-FLOW-LINK 与 check_algo_flow 双层均不验 yaml 节点 `name_en/code` 符号实存——全景图可含指向不存在函数的节点且全绿。判据扩展（对 AST 符号表交叉验证）=结构级改动，留 Owner 决策；本登记即发现记录。
5. **R4d 晨报 markdown 注入**：strategy_id/advisory_id 原样进 markdown 模板。写面=advisory 目录（管线自有权限边界），触达面=本地晨报，L 级；若未来晨报进前端渲染需先加转义。

## 发现的无关问题（只登记不顺手修）

- `tests/strategy_pipeline/test_daily_gate_snapshot_l5.py` 收集错：`cannot import name '_read_external_kill_switch_state' from daily_gate_snapshot`——他会话改符号未同步测试，非四对象。
- `tests/strategy_pipeline/test_decision_orchestrator.py::TestCalendarDormancy` 2 例失败——日历休眠域，非四对象。
- `tests/governance/test_enqueue_preflight_bypass_canary.py` 4 例失败：`HEAD 注册表不可读 module_translation_registry.yaml`——SW18 救援批（e8bc336d65 等）挪注册表致 HEAD 读取失败，与本轮改动零交集（stash 验证被在飞 index.lock 阻断，改经失败点+依赖面定位：canary 不 import ruff preclean，炸点在 commit_preflight 读 HEAD 注册表）。
- 仓内 ruff 对 `.runtime/` 生效 respect_gitignore（.gitignore:111）：`.runtime` 下文件被 ruff 静默跳过——对本 gate 无害（gitignored 件进不了正常提交面），但任何"拿 .runtime 文件当 ruff 判据样本"的测试都会假绿，登记防后来者踩坑。

## 总判定

- **红胜 3**：R1a（体积 DoS，已修）、R1f（工具缺失假红，已修）、R4c（毒包打死晨报，竞态转登记+补丁）。
- **登记 3**：R4a（幽灵函数双层盲区）、R4d（markdown 注入 L 级）、外加 4 项无关发现。
- **蓝胜 19 场景**：Rx-1 路径/逃逸/注入/env、Rx-2 全部、Rx-3/4 全部（含两处真 pre-commit 实弹）、R4b/R4e。
- **修复验证**：test_ruff_preclean_enqueue 17 passed（含 3 例新钉）；回归 test_commit_chain_campaign+test_lock_wait_ledger 37 passed；ruff check/format 自检过；两处红胜场景复打翻蓝。
