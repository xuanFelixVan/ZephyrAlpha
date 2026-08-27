---
ttl: task_bound
title: 2026-08-27 三起 3500+ 文件误删专项取证报告（定凶+治本闭环）
owner: ZephyrAlpha-Owner
language: zh
status: final
version: "1.0.0"
date: 2026-08-27
---

# 2026-08-27 三起 3500+ 文件误删专项取证报告

## 一、结论（定凶）

**三起误删全部同源定凶：pytest 运行红队删除测试时，进程环境泄漏授权变量（ZEPHYR_COMMIT_GATEWAY=1 / ZEPHYR_FORCE_DELETE=1），`guard_rmtree('src/zephyr')` 判定"授权放行"后真实执行了 `shutil.rmtree('src/zephyr', ignore_errors=True)`。**

不是外来攻击、不是未仪表化通道、不是护栏失效——是**护栏的"授权放行"语义在测试上下文中变成了真删执行器**。

## 二、证据链（ops_guard_delete.jsonl，时间=CST）

### 1. 三起 ALLOWED 真删记录与三次误删一一对应

| 时间 | pid | 记录 | verdict/reason | 对应误删事件 |
|---|---|---|---|---|
| 03:27:37 | 36432 | `guard_rmtree shutil.rmtree('src/zephyr')` + `inprocess_allow delete('src/zephyr')` | ALLOWED / 授权放行（命中保护区但有授权标记）、授权通过（FORCE/GATEWAY） | 事件1：3537 文件（src/zephyr/shared 整包等） |
| 08:24:39 | 25408 | 同上两条 | 同上 | 事件2：3526 文件 |
| 12:27:02 | 23812 | 同上两条 | 同上 | 事件3：3513 文件（含外来会话 5 个已暂存 QMT 新文件被误伤，经 index 恢复） |

### 2. 对照组：干净环境的同类调用全部 BLOCKED

| 时间 | pid | verdict |
|---|---|---|
| 05:42:07 | 38768 | BLOCKED（递归删除命中保护区） |
| 07:47:20 | 46264 | BLOCKED |
| 10:35:32 | 8448 | BLOCKED |
| 12:26:34 | 43696 | BLOCKED |
| 12:29:52 | 41100（本会话验证） | BLOCKED |

### 3. 事故机理四环闭合

1. **触发**：pytest 运行 `tests/governance/test_ops_guard_red_team.py`（含 `TestPythonAPI::test_guard_rmtree_blocks_src` 直接以真路径 `guard_rmtree('src/zephyr')` 调用，期望 DeleteBlockedError）。
2. **泄漏**：`ZEPHYR_COMMIT_GATEWAY=1` 经 gateway 链路置位（src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:3940）并随 `os.environ.copy()` 全量子进程继承（ops_guard.py:548-551 注释实证）——任何子进程都变成"授权方"。
3. **误判**：`guard_rmtree` → `analyze_delete_command` → `_is_authorized()=True` → verdict=ALLOWED（授权放行）。
4. **真删**：`guard_rmtree` 语义=「分析+执行」（scripts/ops_guard.py:679 `shutil.rmtree(path_str, ignore_errors=True)`）——授权放行即真删。整包 wipe 在数秒内完成（ignore_errors 静默）。

### 4. 旁证（假阴性读数同源）

- 大盘 sweep 中 `TestPythonAPI::test_guard_rmtree_blocks_protected` 报 "DID NOT RAISE DeleteBlockedError"——与 ALLOWED 记录互证：投毒环境下测试测不到拦截。
- 本会话实测：投毒环境（ZEPHYR_COMMIT_GATEWAY=1）跑红队 49 failed/38 passed；干净环境 87/87 全绿。

## 三、治本闭环（已落地三件套）

| # | 措施 | 落点 | 状态 |
|---|---|---|---|
| 1 | **pytest 上下文保护区浅层递归永不真删不变量**——先于一切授权判定、不受观测模式软化、仅递归+浅层触发（深层 fixture/白名单/单文件分级规则不受影响） | scripts/ops_guard.py `_enforce_pytest_never_delete_protected` 接入 `_inprocess_judge`/`guard_rmtree`/`guard_remove` 三处 | ✅ b4629e81 |
| 2 | **红队测试卫生**——autouse fixture 模块级剔除两个授权变量，红队结果不再依赖宿主环境 | tests/governance/test_ops_guard_red_team.py `_scrub_auth_env` | ✅ db417d1a |
| 3 | **回归测试**——投毒环境 `guard_rmtree('src/zephyr')` 必拦 + 深层路径/白名单不误伤 + `test_guard_rmtree_authorized` 语义更新 | 同文件 3 新测 | ✅ 126+投毒89+guard族156 全绿 |

## 四、恢复留痕

三起均按 #ARCH-257 判例 `git restore --source=HEAD --pathspec-from-file=-` 精准恢复（仅还原删除路径，不动并发会话 2148 处修改）；事件3 中外来会话 5 个已暂存未提交新文件（QMT 桥接族）经 `git checkout-index` 从索引恢复，零损失。

## 五、残留建议（报 Owner）

1. **授权面收窄**：ZEPHYR_COMMIT_GATEWAY 的全量子进程继承面过大，建议改为「仅 commit 执行瞬间+指定 PID」或一次性令牌（裁定五c，待办）。
2. **同类普查**：其他以真路径调用 guard_* 的测试已普查（仅 test_ops_guard_red_team.py 与 test_file_ops_enforcement.py 两处，均被不变量覆盖）；后续新增测试若再以真路径调用，不变量天然拦截。
3. **WriteAudit PID 级审计**（#ARCH-264 O3）维持原计划推进——本次不变量已覆盖"pytest 上下文真删保护区"主通道，WriteAudit 解决的是更广的"未仪表化写删"残留面。
