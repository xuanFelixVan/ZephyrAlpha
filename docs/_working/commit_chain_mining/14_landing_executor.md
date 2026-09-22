---
ttl: task_bound
---

# 环节4：落地执行体（commit_queue_landing + 网关门禁链）

> 挖矿：主会话亲挖（子代理 1302 限流阵亡）+ 环节2/3 子代理交叉证据。别名：LANDING=scripts/governance/commit_queue_landing.py｜GW=src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py。

## A 职责与输入输出

drain 每项调 `WorktreeLanding.__call__(item, queue_root) -> LandingResult`（LANDING:801）：幂等短路（_already_landed，崩溃重放不双落）→ ensure_worktree → 【CAS 重试环】_sync_worktree → 基底冲突判定 → gateway.claim_files（净树基线）→ _apply_snapshot（blob 袋写盘）→ _prestage_snapshot（预暂存，修 q-0013/0014 暂存依赖型 gate 读空 diff 的病）→ gateway.commit（FORGED-GW-MARKER env + allow_non_worktree 诚实记录）→ CAS update-ref dev → 主区收敛。瞬态 git 错误（索引锁/句柄占用）→ LandingEnvironmentError→项退回 pending 整轮终止，绝不死信。

## B 门禁链顺序机制（R3 挂点）

- 网关门禁注册：GW:957-958 `auto_register_gates`（YAML 驱动自动注册，82 个显式 import 已迁移）；执行 `check_all` 按 **priority 升序**（commit_gate_registry.py:8/317-329，同 priority 按注册序；priority 撞号 fail-closed 阻断注册）。
- **GATE-PRECOMMIT-RUN 是链条中的一环**（GW:3169-3337，非独立 pre-commit）：flag `gate_precommit_run_enabled`（裁定#341 方案②）开时在 own-scope 临时索引（GIT_INDEX_FILE）上跑 `pre-commit run --files <本项文件>`；重跑检测 hook 改写文件（mutation）二次阻断。
- 死信力学实证：workclean 0091（111 文件）死因 CREATE-GUARD 但耗时 116 分钟 → 时空分配=pre-commit 全套 hook（含 ruff-format 全量改写）先磨掉绝大部分时间并 PASS，随后廉价 token 检查 CREATE-GUARD 一秒内杀——**失败暴露位=链条最末端，成本付在最前端**。taskcards 0032 死 RULING-REFERENCE 仅 1 分钟（小批+链条前的便宜 gate 杀）反向印证。
- pre-commit hooks 内部顺序=.pre-commit-config.yaml 文件序且 fail-fast：61 conflict-marker→68 private-key→83 protected-paths→94/101/108 dangerous 系→123 worktree-required→134 algo-flow→142 pytest-drift→**151 ruff→157 ruff-format**→171 arch→189 naming→…→45+ hook（blueprint/frontmatter/vocab/directory-contract 等在后段）。violation 在后段的批次，前面 20-30 个 hook（含全量 ruff/ruff-format）全部白跑。

## C 大批慢的力学（111 文件=116 分钟）

1. pre-commit hooks 逐 hook 全 staged 面执行：Windows 每 hook 子进程 spawn 开销 ×45+ hook；ruff-format 对 111 文件改写+复暂存。
2. own-scope 临时索引构建（GIT_INDEX_FILE）：每项重建。
3. 全仓扫描型 gate（CloneGuard/CAPABILITY-OVERLAP、部分 registry 校验）随 staged 面放大。
4. CAS 重试环：冲突时整环重来（sync→snapshot→gates）。
→ 治本组合：入队面预检拦 T0 违规（防"磨完才死"）+拆批上限（压单链时长）+hook 重排（便宜前置）。

## D 升级机会

1. 【快】hook 重排：把纯文本确定性 gate（algo-flow/naming/blueprint-format/frontmatter/vocab/doc-node-id 等）整体挪到 ruff/ruff-format **之前**（R3 主手术，改 config 顺序+每 hook 成本档表为据）。
2. 【快】门禁 priority 复盘：GATE-PRECOMMIT-RUN 与 T0 级 commit_gates（CREATE-GUARD/TRANSLATION/RULING-REF）的 priority 相对位次——T0 gate 若排在 precommit-run 后，提到前面（改 priority 数字，fail-closed 撞号检测会拦重号）。
3. 【快】CAS 环内 sync/snapshot 结果复用（同项重试时跳过未变步骤）——低风险缓存，需指纹校验。
4. 🌑 checkpoint 断点续落（单批中断恢复）：拆批上限落地后必要性大降——挂起。

## E 挖矿日志表

LANDING __call__ 全文精读 / GW gate 执行序与 auto_register / precommit_run_scoped 实现 / .pre-commit-config hook 全序提取 / 死信时空分配反推（0091 vs 0032 对照）。

## F 自审闸三态裁定

- 施工：D1 hook 重排 + D2 priority 复盘（=Owner R3 原文落地）。
- 挂起：D3 CAS 复用、D4 checkpoint（拆批后重评）。
- 封矿：无。
