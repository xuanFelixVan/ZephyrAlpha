---
ttl: task_bound
rule_form: data
verifiability: manual
title: F4 作业簿——架构图生成器波次并发化（GATE-ARCH-DIAGRAM 15 生成器 DAG 分组并发）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: active
---

# F4 作业簿 — 架构图生成器波次并发化（GATE-ARCH-DIAGRAM）

> 施工包：F4（免签）｜真源：`docs/_working/kimi_audit/S18_Flash施工包判据.md` F4 + `S18_提交链路根因表.md` R-08
> 会话：st-flashspeed-20260918｜lock 持有：`src/zephyr/governance/audit/reconciliation_registry.py`
> 靶点：`make_arch_diagram_reconciler._reconcile`（priority=630），15 个生成器串联循环。

## 0. 病灶（第一性原理）

GATE-ARCH-DIAGRAM 的 `_reconcile` 原以 `for gen_name in _GENERATORS` **串联**跑 15 个生成器，
每个 `_run_subprocess(timeout=180)`。实测串联墙钟 **57.41s**（worktree 隔离实证）。这 15 个生成器
之间**绝大多数无依赖**（各写各的 .md），串联等于把 11 个独立任务排成一条队 → 墙钟 = Σ 单生成器耗时，
而非 max。post-commit reconcile worker 因此被这段无谓的串联拖长。

**但须诚实定性 F4 的实际杠杆**：F1 施工期观测（见 F1 作业簿 §6 观测1）记录 detached worker 跑满
39 个 reconciler 耗时 **~6 分钟**，主导项是 **GATE-REGENERATE（卡 180s，疑命中 timeout）+
GATE-DELETE-AUDIT（卡 120s）**，架构图 15 生成器（57s）**并非** 6min 的主瓶颈。故 F4 优化的是
worker 总时长中约 57s 的那一段（→ ~28s），对 6min 主导项（REGENERATE/DELETE-AUDIT）无触及——
后者是否"命中 timeout 的空转病灶"应由 **F6 堵点总账**排查，不在 F4 作用域（F4 判据明确限定
"reconciliation_registry.py 15 generators"）。

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|----|------|------|
| ①上游 | 谁触发 _reconcile | `_trigger`：commit 命中 `_PG_WRITE_SCRIPTS`（apply_depgraph 等 6 个）或 `_YAML_SOURCES`（10 个架构 YAML）→ post-commit 异步 worker 调 GATE-ARCH-DIAGRAM(630) |
| ②下游 | 产物落到哪 | 15 生成器写 16 个 `_OUTPUTS`（00/01/03/05/06 目录下 .md + `src/zephyr/data/config/policies.yaml`）；`git diff -- _OUTPUTS` 检测漂移 → `_commit_auto` 批提交 |
| ③算法机制 | 生成器间依赖 | 静态 DAG 核验：navigation_index 读 5 张 wave0 图；align_panoramas 读 capacity_report；panorama_registry 聚合全部 14；data_acquisition_flow 与 dataflow_diagram 共享 `05_/_zoomable_html`（后者 blanket glob 清目录）；其余 11 个互不读对方产物 |
| ④后端 | DB 读写 | **15 个生成器全部 DB-只读**（scan 确认零 INSERT/DELETE/DROP/CREATE/UPDATE）：panorama_registry/navigation_index 走 `SELECT COUNT(*)`（depgraph PG），data_inventory 走 ClickHouse 实时扫描。故并发无 DB 写竞争 |
| ⑤前端 | 无 | 纯后端 reconcile 链路（产物 .md 供人查阅，无前端渲染耦合） |
| ⑥数据字段 | 非确定性来源 | 4 个生成器输出含**易变内容**：align_panoramas L853 `now_utc()` wall-clock 时间戳；navigation_index/panorama_registry 嵌入实时 PG `COUNT(*)`；data_inventory 嵌入实时 CH 扫描行数。这 4 个 serial 连跑两遍亦逐字节 DIFF（见 §3 实证）——**非并发引入** |

## 2. 治本设计（依赖拓扑分 3 波，波内并发、波间串行屏障）

**核心洞察**：15 生成器的依赖图是浅 DAG（深度 3）。按拓扑分波，波内用 `ThreadPoolExecutor`
并发，波间靠 `ex.map` 的阻塞语义形成串行屏障（上一波全部结束、产物落盘后才提交下一波）。

```
wave0 (11 独立):  decision_diagram, dataflow_diagram, integration_topology,
                  design_vs_production, cross_domain_matrix, constraint_violations,
                  capacity_report, capability_heatmap, asset_catalog, policies, data_inventory
wave1 (3):        align_panoramas(←capacity_report), navigation_index(←5图),
                  data_acquisition_flow(←dataflow_diagram 的 05_HTML 清目录之后)
wave2 (1):        panorama_registry(←聚合 wave0+wave1 全部)
```

**关键排序裁定**：`data_acquisition_flow` 本可入 wave0（不读任何 .md 产物），但它与
`dataflow_diagram` 共写 `05_dataflow_architecture/_zoomable_html`，而 dataflow_diagram 对该子目录做
**blanket `glob("*.html").unlink()` 清除**（L1436-1441）。若二者同波并发，dataflow 的清除可能删掉
data_acquisition_flow 刚写的 HTML。故把 data_acquisition_flow 下沉到 wave1（dataflow 在 wave0 先清先写），
**精确保留串联原序**（原 #2 清、#15 写）→ HTML 产物亦 byte-identical。decision_diagram 写的是
`06_/_zoomable_html`（且用 `cleanup_stale_files` 而非 blanket glob），与 dataflow 的 05_ 子目录互斥，无竞争。

**落地改动**（`reconciliation_registry.py`，`make_arch_diagram_reconciler` 闭包内）：
1. 工厂级新增 `from concurrent.futures import ThreadPoolExecutor`。
2. `_OUTPUTS` 后新增 `_WAVES`（3 波元组）+ **partition guard**：
   `if sorted(flatten(_WAVES)) != sorted(_GENERATORS): raise ValueError(...)`——防新增/删除生成器
   漏排波次导致**静默跳过**（构造期硬失败，优于运行期漏跑）。
3. 新增 `_MAX_GEN_WORKERS`：默认 **4**，env `ZEPHYR_ARCH_GEN_WORKERS` 可调，**硬钳 [1,20]**
   （本机压测红线 worker≤20；多个 post-commit reconcile 叠加时限制单 reconciler 子进程爆炸半径）。
4. 串联 `for` 循环 → `with ThreadPoolExecutor(max_workers=_MAX_GEN_WORKERS) as _ex:` 外层遍历
   `_WAVES`，内层 `_ex.map(_run_one, wave)`。`_run_one` 封装原 `_run_subprocess` 调用，
   **新增捕获 `subprocess.TimeoutExpired`（降级 rc=-1）与 `Exception`（降级 rc=-1）**——原串联版
   单生成器超时会 raise 中断整轮，现降级为计入 failed_gens 继续（部分漂移修复优于全跳过，语义一致但更健壮）。
5. `failed_gens` continue-on-failure 语义、all-failed→warn 短路、drift-gate、auto-commit 全部**零改动**。

## 3. 安全性 / byte-identical 等价证明（红蓝自审 + 双实证）

**判据②要求"输出与串联版逐字节相同"。两道实证（worktree 隔离，主仓零触碰，与 altdata 零碰撞）：**

**实证 A — serial vs wave-parallel（cap=11）**：16 产物 sha256 比对 → 12 逐字节相同，4 处 DIFF
（navigation_index / panorama_registry / panorama_alignment_report / data_inventory）。

**实证 B — serial × 2（确定性核验，判 DIFF 归因）**：同一 worktree 连跑两遍**纯串联**，16 产物比对
→ **同样这 4 个文件 DIFF，同样 12 个逐字节相同**。

**结论**：4 处 DIFF 是生成器**自身非确定性**（§1⑥ 的 wall-clock 时间戳 + 实时 DB 行数），
**与并发无关**——纯串联重复跑也一样变。波次并发对**确定性产物（12/16）零改变**，对易变产物
引入的偏差**不超过串联自身重复运行的偏差**。byte-identical 判据在"并发不额外引入偏差"的语义下 **PASS**。

| 场景 | 串联版 | 波次并发版 | 等价? |
|------|--------|-----------|-------|
| 12 个确定性生成器产物 | 基准 | 逐字节相同（实证 A+B） | ✓ |
| 4 个易变生成器产物 | 每次跑都变（时间戳/实时行数） | 变化幅度 ≤ 串联自身重复（实证 B） | ✓ 并发无额外偏差 |
| navigation_index 读 5 图 | #4-#7 写，#9 读 | wave0 写，wave1 读（屏障保证） | ✓ 单测 test_dag_dependency_barriers |
| data_acquisition_flow 的 05_HTML | #2 清，#15 写 | wave0 清，wave1 写（下沉保序） | ✓ 设计裁定 + 屏障 |
| panorama_registry 聚合全部 | #1-#14 后 #10... 实为最后写 | wave2 最后（读 wave0+1 全产物） | ✓ 屏障 |
| 单生成器超时 | raise 中断整轮 | 降级 rc=-1 计入 failed_gens 继续 | ✓ 更健壮，语义不降 |
| 单生成器 rc!=0 | 记入 failed_gens 继续 | 同 | ✓ 单测 test_single_generator_failure |
| 全部失败 | all-failed→warn 短路 | 同 | ✓ 单测 test_all_generators_fail |
| 生成器漏排波次 | N/A（串联遍历全集） | partition guard 构造期 raise | ✓ 新增防护，优于静默跳过 |

## 4. 判据映射（S18_Flash施工包判据 F4）

| 判据 | 验法 | 结果 |
|------|------|------|
| 总墙钟 <180s | worktree 实证：parallel(cap=11)=**17.86s**；生产默认 cap=4 仿真 **~28.3s**；serial 基准 57.41s | ✓ PASS（cap=4 留 6.4x 余量） |
| 输出与串联版逐字节相同（抽样 5） | 全 16 抽样（超判据要求）：12 逐字节同；4 易变经 serial×2 证明非并发引入 | ✓ PASS（模 volatility，见 §3） |

**cap 选型裁定**：生产默认 **cap=4**（非实测最快的 11）。理由：①<180s 判据 cap=4 已 6.4x 达标；
②cap=11 虽 3.2x（17.9s）但 11 个并发 Python 生成器进程 CPU/内存爆炸半径大，且 post-commit worker
可多笔叠加（3 笔并发 reconcile × 11 = 33 进程 > 20 红线）；cap=4 时 4 笔叠加才 16 < 20。
③reconcile 是**后台异步**，18s vs 28s 的差对 CLI commit 返回延迟无影响（commit 不等 worker）。
故取保守 cap=4，env 可调至 ≤20 供 Owner 按宿主负载 tuning。

## 5. 挖后自审闸（三态）

**裁定 = 施工**。理由：①设计闭环（浅 DAG 分波，屏障保序）；②byte-identical 经 serial×2 双实证，
并发零额外偏差；③判据可机验（墙钟 + hash 比对 + 7 例结构单测）；④**不碰任何门禁语义/判据**——
drift-gate、auto-commit、failed_gens、all-failed 短路、_OUTPUTS、_trigger 全零改动，仅改"15 个生成器
按什么调度跑"（性能参数，非检测/提交语义）；⑤不动 serializer 通道数、不碰 POST-COMMIT-GUARD /
RULING-REFERENCE / risk_tier 门位。符合 R4 不可放宽白名单（纯性能重构，检测面与提交面语义不变）。
新增 partition guard 是**加固**（防漏排），非放宽。

## 6. 施工日志

- [x] 静态 DAG 核验：15 生成器读/写 16 产物全扫描 → 确认 wave0 内 11 个互不读对方产物（dataflow_diagram
      对 decision_index.md 的 2 处引用经查为注释 + 嵌入文档串，非文件读）；HTML 子目录 06_/05_ 互斥
- [x] DB 写扫描：15 生成器零 INSERT/DELETE/DROP/CREATE/UPDATE（全 DB-只读）→ 并发无 DB 写竞争
- [x] worktree 隔离实证（`.worktrees/f4-exp`，ZEPHYR_WORKTREE_ROOT 注入使 REPO_ROOT=worktree、
      DB_PATH 锚主仓只读）：serial 57.41s / parallel(cap=11) 17.86s / 3.21x；byte 12 同 4 易变
- [x] serial×2 确定性核验：同 4 文件 DIFF、同 12 文件 stable → 证明 4 处 DIFF 是生成器非确定性非并发
- [x] 落地 reconciliation_registry.py：ThreadPoolExecutor 导入 + _WAVES + partition guard +
      _MAX_GEN_WORKERS(cap=4,env 可调,钳[1,20]) + 串联循环→波次并发 + _run_one 超时/异常降级
- [x] py_compile OK；reconciler 构造 OK（partition guard 通过，priority=630）
- [x] 新增 `tests/governance/audit/test_arch_diagram_wave_concurrency.py` 7 例（mocked subprocess，零真实
      生成器运行）→ **7 passed**：15 各一次 / DAG 屏障 / 波内并发峰值≥2 / clean / 单失败不阻断 /
      超时降级不抛 / 全失败 warn 短路
- [x] 回归 `pytest tests/governance/audit/` → **1794 passed, 1 skipped**（0 fail，含 F1 fold 4 例）
- [x] worktree 清理：`git worktree remove --force` + prune；复制入 worktree 的 5 个 gitignored
      连接配置（.env.postgres/clickhouse/redis/qmt/ch_backup）随 worktree 删除一并清除；主仓 config 完好
- [x] 主仓隔离核实：5 个产物目录 + policies.yaml `git status` 零改动（仅 altdata 的 04_ 文件 dirty，未触碰）

### 验收结论：判据全过

| 判据 | 结果 |
|------|------|
| 总墙钟 <180s | ✓ parallel 17.86s@cap11 / ~28.3s@生产 cap4 / serial 基准 57.41s |
| 输出逐字节相同（抽样 5） | ✓ 全 16 抽样：12 逐字节同，4 易变经 serial×2 证明非并发引入 |
| 结构正确性 | ✓ 7 例单测 + 1794 回归全绿 |

### 施工期观测（留给 F6 的实证）

1. **6min worker 主导项非架构图**：F1 观测 + 本次实测共同表明——架构图 15 生成器仅 57s（F4 已优化到
   ~28s），而 detached worker ~6min 的主导是 **GATE-REGENERATE（卡 180s，=其 timeout 值，疑命中超时
   空转）+ GATE-DELETE-AUDIT（卡 120s，=其 timeout 值）**。二者"恰好卡满 timeout"高度可疑——可能是
   子进程 hang 到超时被 kill 的**空转病灶**（白等 180s/120s 无产出）。**F6 须排查**：这两个 reconciler
   是真跑满还是命中 timeout；若命中，是死信/病灶（治本）还是正常长任务（记账）。
2. **4 个生成器的非确定性 = 永续 diff churn 病灶**：navigation_index/panorama_registry/data_inventory
   嵌实时 DB 行数、align_panoramas 嵌 `now_utc()` wall-clock（**违反 RULE-SCHEMA-TZ「生成器禁
   datetime.now()/time.time()」**）。后果：每次 GATE-ARCH-DIAGRAM 跑完，这 4 个产物必然 diff →
   `_commit_auto` 每轮产生一笔 `chore(arch)` 尾笔（即便架构无实质变化）。这与 F1 消除的 integrity
   尾笔是**同族 churn**（不同源）。**F6 须登记**：align_panoramas 的 now_utc 是明确违规（可治本改
   idempotent_timestamp）；3 个实时行数嵌入需裁定是否改幂等口径（涉产物语义，可能需 Owner 门位）。
   **F4 不修**（超作用域 + 禁动生成器语义），仅登记移交。
