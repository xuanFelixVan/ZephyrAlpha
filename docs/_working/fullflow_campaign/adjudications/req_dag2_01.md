---
ttl: task_bound
completes_when: 总包对三条申请逐条给出裁定（或转交 Owner 门位）并回写 COORDINATION_LEDGER
---

# 裁定申请书 req_dag2_01 · 车道 st-ff-dag2-20260918

> 按台账 §4：车道不自行取裁定号，只交申请书。三条均附本车道实测证据与 file:line。

## ① 过期死信批 q-20260918-st-ff-dag-20260918-0001/0002 的余件归属

- **背景**：两件死信的 files 清单含 11 个路径，其中 `tasks.yaml`（blob `a11bc4fc…`）与推导器已由本车道
  在真基线上重放落地；但 `src/zephyr/data/config/schedule.yaml`（blob `1d2f0d7a…`）、
  `known_data_gaps.yaml`（两代 blob `218f28a0…`/`72ebab5f…`）、`data_supply_sentinel.yaml`（blob `a6f26e2c…`）
  的在途改动**从未进过 HEAD**（`git log --all -S` 与 `git status` 双测）。
- **为何要总包裁**：`schedule.yaml` 在本车道任务书里是禁写面；`data_supply_sentinel.yaml` 真源属 z-sentinel
  （R-041 刚落地 `85ef0962d0`），旧 blob 极可能已被其新版覆盖 ⇒ 重放=回退他人成果。
- **选项**：A 逐 blob 与现 HEAD 三方比对后由 owner 车道各取所需（建议）；B 整体作废该批 blob；
  C 指派某条车道统一重放。
- **本车道未做**：一个字节都没碰这三件，只登记。

## ② 推导器产物措辞的账实不符（需批准才改）

- **实测**（判据函数=`scripts/derive_task_dependencies.py::render_markdown`）：
  `landed = DERIVED_TAG in tasks_yaml.read_text()`（**文件级 substring**，不是本轮 apply 结果），
  且高置信行写的是 `len(applied)`=**任务数**而非边数。
  本车道在含 tag 的输入上复现：`tasks_touched: 0` 却输出"（本次 --apply 已写入 tasks.yaml）"，
  并逐字节重出 19:31 那份失真文档（sha `fb8990d1…`）。这就是 R-026 第 9 型的实体来源。
- **建议修法（等批）**：`render_markdown` 接 `apply_high_confidence` 的返回值，
  文案改为"本批写入 N 任务 / M 条边"；`touched=0` 时写"本轮零写入（历史边不变）"；
  并把 §1 标题"高置信（已落地）"改成"高置信（建议）"。
- **为何不自改**：这是**产数面的语义**（文档=机生真源），单方面改措辞等于改口径，
  且会与已落地引用该文档数字的案卷冲突 ⇒ 要总包签字。

## ③ R-042 同签名新事件：过期队列快照被推进主工作区的 tracked 热配置

- **观测**：本会话内 `src/zephyr/data/config/tasks.yaml` 工作区字节被替换为 19:30 死信快照
  （sha `a11bc4fc…`，266 任务：比当时 HEAD 多 4 个外来未落地任务块、少 2 个 HEAD 在册任务）。
  替换发生在车道两次实测之间（前一次与 HEAD 全等、`git status` 干净），文件 mtime 显示 19:47
  但写入时刻更晚 ⇒ **写方保留了源 mtime（copy2 语义）**。
  `.runtime/commit_queue/{pending,processing,done}` 中无任何项引用该 blob ⇒ 不是正常队列路径。
- **后果若未拦**：按当时工作区提交 = 净删 2 个在册任务 + 塞入 4 个外来任务（触发注册表净删门/Owner 位，
  或在门下游静默改排班）。
- **请求**：①并入 R-042 未结案卷；②立一条机械护栏——**任何恢复/prestage 脚本对 tracked 热配置写入前，
  MUST 先与 `git show HEAD:<path>` 比对，落后于 HEAD 一律拒写并留痕**（与 R-038 判据④"归档早于破坏性操作"同族）；
  ③给出该事件的排查责任人（本车道无权限也无证据指认主体，不编造归因）。
