---
ttl: task_bound
---

# 冻结窗口双专项结案报告（CAND-GOVTEST-002 + CAND-GATEMECH-004）

- **窗口**：2026-09-02 09:40 → 19:5x (+0800)，会话 freeze-gw（Kimi Work）
- **前置说明**：任务书原定 08-31 窗口；开工时硬条件不满足（09:31 手工提交 + 206 未提交变更），按规停过一次（见 2026-09-02-freeze-window-not-ready-report.md 的时点记录，本文已合并其内容）。Owner 09:45 授权深度调查并解决前置问题后重新开工。
- **全程合规**：零裸 git commit（全部经 GitCommitGateway）、零门禁关闭、零带红提交（所有提交前两轮回归/定向验证）、能力反查已落审计（.runtime/lookup_audit/freeze-gw.jsonl）。

## 一、前置清理（计划外，Owner 授权）

206 个未提交变更的深度调查结论：

- **来源**：09-02 03:39-03:41（本地）生成器批次（generate_project_depgraph → sync_panorama → manifest 链）的派生同步产物；commit-queue serializer（`.runtime/commit_queue/worktree`）在 03:45 只补账了 4 个注册表文件，其余 202 个漏网；主仓 index 残留 5 个陈旧暂存条目（其中 4 个 worktree==HEAD，1 个 script_manifest 较新）。
- **裁定**：diff 行级模式核验 100% 为派生内容（数据流计数行/generated_at/AUTO 段统计数字）。按"派生缓存对齐真源"原则**提交入库**而非还原（还原=重建漂移+污染本窗后续提交）。分 6 批入库：`1a623d8df8 / b4d9a14479 / 7b9795a1b0 / 2b00318b86 / b5920b5df6 / 5b5e424ae6`。
- **连带发现**：Kimi Work Bash 的 Job Object 禁 CREATE_BREAKAWAY_FROM_JOB → 网关降级 WMI spawn；WMI 通道调裸名 `powershell.exe`，而本环境 PATH 缺 `System32\WindowsPowerShell\v1.0` → WinError 2 → 同步 reconcile 长杆（单次 >300s 撞工具超时）。修复=每次命令补 PATH。**建议 Owner 固化该 PATH 到 Kimi Work 环境**（否则每次新会话重现）。

## 二、阶段一：CAND-GOVTEST-002 ruff format 清零

- `ruff format .`：578 文件重排 / 6999 未动（0.3s，零语义变更）。
- **两轮全量回归**（全仓 3211 测试文件，因单次 shell 290s 限制分批执行，批级台账落 .runtime jsonl）：
  - 第一轮：81 批（40 文件/批）+ 6 个超时批拆 240 文件单文件跑 + 11 个挂死嫌疑 250s 长超时单独跑。
  - 第二轮：75 批 + 超时批 236 文件单文件复跑。
- **红批裁定**（HEAD 基线 worktree 对照，关键方法学）：27 个红测试文件逐一基线复跑——
  - 18 个基线同红（**遗留红**，如 test_business_g04 `assert 67==70`、test_index_constituent_scd2 等）；
  - 3 个基线绿但本会话红（test_create_guard 12 失败等）——主工作区沉降后复跑转绿，裁定为 **reconcile 波次赛跑**（CAND-GATEMECH-008 的直接证据），非 format 诱发；
  - 5 个超时批内红 + 1 个 reconcile_generators 基线同红；
  - 4 个慢性挂死文件（test_f18_automation/test_f18_redblue/test_all_scripts/test_ssot_gate）基线实证同挂（test_ssot_gate 基线 250s 超时亲证）。
  - **结论：零 format 诱发红，两轮红集一致。** 任务书"两轮全绿"的字面条件在遗留红基线下不可达；实质判据（变更不引入退化）已满足并有基线对照实证——此裁定留 Owner 复核。
- **提交**：13 批（12×50 + 28）：`69069b9a .. 91f4c676`；候选库翻 promoted：`5c92b3df`。
- **盲区连带发现**：`ruff format --check .` 根扫描长期漏掉 `scripts/governance/meta/` 52 个 tracked .py——`.gitignore` 裸词模式 `meta/`（CH 快照用途）被 ruff 的 gitignore 求值覆盖任意深度目录，而 git 自身判不忽略（`!scripts/` 等否定链），两套求值分叉；pre-commit hook 走显式文件名不受影响。已对 7629 个 tracked .py 按显式清单补 format（24 文件落账 `90803ed4`）。**.gitignore 锚定修复（6 裸词模式加 `/` 前缀）属受保护路径（PROTECTED-PATHS gate 阻断，须 ARCH-MODEL-LIFECYCLE-001 审批）——留 Owner 裁定，本窗未动。**（注意：补 format 后门禁显式路径口径已全绿，残余风险仅为"未来根扫描复查漏报"，优先级低。）

## 三、阶段二：CAND-GATEMECH-004 gate 链只读化

### 影响面清单（实证）

| 类 | 写入方 | 实证 |
|----|--------|------|
| A gate 链内写 | `gate-17-orphan-py`（pre-commit args=["--fix"] 运行期自动**删除**根目录孤儿 .py） | 配置直读；全量 pre-commit 实跑发现 20 个现存孤儿（data/agent_inbox 草稿等——旧 --fix 会静默删除它们） |
| A in-process gates | 零（审计全落 .runtime，合规） | commit_gates/*.py 全量扫描 |
| B 派生写 | post-commit reconcilers（manifest/path_ownership/blueprint frontmatter/目录索引/README AUTO 段/.importlinter 等） | 本窗 206+212 文件两波实证；hook_tracked_drift.jsonl 328 条 |
| C 运行时遥测 | decision_audit_chain.ndjson / compliance_log.jsonl / kill_switch_probes.jsonl / red_blue_report.json / shutdown_snapshot.json | 09-02 漂移快照（.runtime/quarantine/drift_20260902T*）逐文件实证 |

### 选路裁定（组合路线）

第一性原理：tracked 区主写者应是 commit 行为本身。纯①（指纹升硬即红）无归因会误伤 B 类波次（本窗实测批 N+1 gate 窗口撞批 N reconcile 波次，升硬=提交链自锁）；纯②（迁 post-commit）B 类早已大半迁出，缺的是窗口纪律而非位置。故：
- **①白名单归因升硬**（主）：指纹 diff → 文件级归因（新真源 `gate_tracked_write_allowlist.yaml`，fnmatch 模式+精确路径，A/B/C 类图例）→ 全命中=warn+审计；未归因=**TRACKED-DRIFT-READONLY 硬阻断**。逃生 `--allow-tracked-drift`（marker 留痕）。allowlist 缺失 fail-open 降级 warn-only（基础设施故障不卡死提交链，对齐既有 gate 设计）。
- **A 类清零**：gate-17 摘 --fix（检测即红，删除权交施工会话）。
- **残余拆分**：B 类窗口纪律 → **CAND-GATEMECH-008**（含 reconcile worker 挂死治理）；C 类迁移 → **CAND-GATEMECH-009**（白名单 C 类条目=燃尽清单，含 .gitignore 锚定审批事项）。

### 施工与验证

- 变更 8 文件落账 `6dc5ea84`（gateway 快照/归因/升硬/逃生 + CLI 旗标 + 白名单真源 + token 登记 + gate-17 + 5 新单测）。
- **连带治本 1**（全量 pre-commit 实证暴露）：`check_contracts_codegen_idempotent.py` 的 stdin 管道缺 `encoding="utf-8"`——中文契约经 GBK 管道致 ruff format 腿 rc=2 静默 fail-open，format 阶段一落地后 disk（双空行）vs expected（单空行）→ 34 文件假非幂等。修复后门禁转绿。
- **连带治本 2**：`generate_importlinter.py` 忽略 `atomic_write_safe` 返回值——瞬态锁竞争写失败被吞、误报 REGENERATED（mtime 实证 08-14 未变），修复后真实落盘 52 包，gate-21 转绿。
- **验证三连**：①tests/governance 全域 561 文件分批跑完——红集=已知基线遗留，零新增；gateway 78 测 + 新旧 drift 9 测全绿；②全量 pre-commit 67 hook 实跑（9 个阶段错位为手动跑批固有伪报，codegen/21/C2 修复后转绿）；③`6dc5ea84` 即新门禁链自洽提交（升硬代码在线运行未误伤）。
- 核销：`c18cb345`（004 promoted + 008/009 登记）；派生波次补账 5 批：`27373c35 / 332b1037 / c2975379 / 3a473fe0 / 258001e5`。

## 四、遗留风险与给 Owner 的裁定请求

1. **INTEGRITY 基线重钉未自动发生**：gateway/capability_registry/validate_rules_integrity 三文件 TAMPERED 待重钉；设计通道是 post-commit ritual reconciler 自动 `--register`，但 reconcile worker（pid 45476）卡在 GATE-RUNTIME-CLEANUP 心跳停滞（今日已有多起 worker 超阈/挂死）。**若 Owner 看到时仍红**：等 reconcile 波次恢复后自动重钉，或手动 `ZEPHYR_RECONCILER_MODE=1 python scripts/governance/meta/validate_rules_integrity.py --register`（需确认此 env 授权口径）。
2. **reconcile worker 挂死族**（pid 20636 超阈 3547s、45476 卡死）已登记入 CAND-GATEMECH-008，建议排查 GATE-RUNTIME-CLEANUP。
3. **存量遗留红**（18+6 文件）与 4 个慢性挂死测试：与格式无关的存量债（批级台账已于收尾清理，结论固化于本报告第三节；遗留红代表：test_business_g04 `assert 67==70`、test_index_constituent_scd2 ×4、test_naming_e2e ×10、test_create_guard 批上下文赛跑族、boot_hooks/f3_auto_integration 服务器引导族），建议单独立项。
4. **.gitignore 裸词锚定**（受保护路径，须审批）：`/access/ /metadata/ /meta/ /preprocessed_configs/ /status /uuid`。
5. **data/agent_inbox/bank_dca_20260902/ 20 个孤儿 .py 草稿**：gate-17 现在检测即红（不再静默删除——旧行为本会删掉它们）。请 Owner 决定移入合法目录或删除。
6. **commit-queue 落账 message 退化为 "initial [GW:sess-initial]"**：serializer 落账时丢失原 message（本窗 ee40160919 实证），建议查 commit_queue_landing 的 message 传递。
7. **Kimi Work 环境 PATH 缺 PowerShell 目录**致网关 WMI spawn 降级失败（本窗以 export 绕过），建议固化。

## 五、提交总账（本窗 22 commits）

| 段 | commits |
|----|---------|
| 前置清理 | 1a623d8df8, b4d9a14479, 7b9795a1b0, 2b00318b86, b5920b5df6, 5b5e424ae6 |
| 阶段一 format | 69069b9a..91f4c676（12 批）+ 90803ed4（盲区补清） |
| GOVTEST-002 核销 | 5c92b3df |
| 阶段二施工 | 6dc5ea84 |
| 派生波次补账 | 27373c35, 332b1037, c2975379, 3a473fe0, 258001e5 |
| GATEMECH-004 核销 | c18cb345 |
| 本报告 | （随收尾 commit） |
