---
ttl: task_bound
---

# 车道 10_d1_d2 — 落地池两缺陷·手术单总览（一屏版）

> 立档：2026-09-24 ｜ 性质：设计-only（本目录只出手术单，不改码、不提交、不碰 `.runtime/commit_queue/`）
> 索引：`00_commit_speedup_master_plan.md` 车道表 L2/L3 两行即本目录交付物

| 缺陷 | 一句话机理 | 我实测到的数字 | 修复的最大风险 |
|------|-----------|---------------|----------------|
| **D1 `stats_lock` 停世界**（`d1_stats_lock.md`） | 四工共享的池级锁 `stats_lock`（`commit_queue_landing.py:2096`）在落账段 `:2196-2216` 内包住 `_mark_cascade_stale`（`commit_queue.py:1025`）——后者每次落地把**全部 pending 文件**读一遍、命中件各写一次（写=`fsync`+`replace`），于是每落一件其余三工全停 | 生产形态只读勘察：pending 实有 **83 件**、`base_head` 只有 **5 个值**、**同值最多 77 件**；抛袋根实测 `_mark_cascade_stale` 首次调用（N=83 全命中）**132.8/144.3/151.9 ms**（min/med/max，6 个新鲜根），已全部 stale 的二次调用仅 **6.8/8.0/8.8 ms**；单件重写 **1.74 ms**、单件扫描 **0.096 ms**；四工争用模拟 **overlap ratio = 1.00**（Σ412.3 ms vs wall 412.8 ms，零重叠） | 级联 stale 旗延迟落盘后，「盘上旗」不再及时驱动认领时的基底重校验 → 基底已被本波越过的件**未经重校验即落 dev = 无声覆写兄弟件内容**（热册驱逐同型的字段级净损）。缓解=手术第 4 条强制把判定入参改为「盘旗 ∪ 本波内存 landed_index」，并以 12 例逐字段差分矩阵（含专门的交错认领例）自证 |
| **D2 env 旗跨线程泄漏**（`d2_env_flag_leak.md`） | 落盘与网关都直接改**进程全局** `os.environ`（`commit_queue_landing.py:1577-1578`/`:1641-1645`；网关 `git_commit_gateway.py:3510` 置位、`:3557` **无条件 pop**、`:3973`/`:4025` 置位后**永不还原**）——四工同进程即互相摘旗/串旗，而这枚旗是 POST-COMMIT-GUARD 防伪与 `git_guard` 破坏性操作放行的**凭据** | 消费者 **9 类**全分类（表 A）：commit 自身的子进程（post-commit/reference-transaction/pre-commit 通道）其实**已由 per-spawn 显式注入**拿到旗（`:3243-3246`、`:4276-4277`、`session_worktree.py:3859`）→ 全局写点多为**冗余且有害**；暴露窗口 = 一次完整 `gateway.commit`（分钟级）→ k=4 下「任一时刻某线程持旗」概率≈1，故 `:3557` 的抹旗是**结构常态**而非偶发；进程内读点 6 处（`git_guard.py:140`、`ops_guard.py:583`、`install_inprocess_enforcement` 由 `commit_queue.py:2281` 装配） | 删全局置位后若某个仍靠「继承全局字典」的子进程拿不到旗 → POST-COMMIT-GUARD 把**合法网关 commit 判为伪造并 `git reset --soft HEAD~1`**，把已落地件吃掉（安全边界翻向最坏一侧）。缓解=不可颠倒的四段顺序：先修 `:3973/:4025` 永久留旗（与池无关、现在就在漏）→ 补齐/确认 per-spawn 注入覆盖 → 真钩子端到端＋双线程红测转绿 → **最后**删全局写；plumbing 侧 `_trusted_git_env()`（`:714-719`）必须显式决定旗值，不许「继承看运气」 |

## 建单顺序（推荐）

**先 D2，后 D1。** 理由：

1. **性质不同**：D2 是**安全边界**（防伪凭据 + 破坏性操作授权位，错向即「误删/误回退已落地 commit」），
   D1 是**吞吐卫生**（不改任何判定，只改临界区宽度）。凭据类缺陷不与性能抢窗口。
2. **可达性不同**：D2 的 W4（`_commit_auto` 置位永不还原）**池化前即可达**，是今天守护进程里的常驻过授权面；
   D2 的跨线程摘旗（W3）才需要池——两者都该在下一轮 k>1 实验前关闭。
3. **改动面积**：D2 全在 `commit_queue_landing.py:1577-1645` + 网关 4 个写点，零数据、零 schema；
   D1 需要新写 12 例逐字段差分 harness，是本项目里重的一件，且它的收益本身要靠新插桩复测（见下）。
4. **D1 的验收不押吞吐**：按实测，D1 的停世界是 **~0.15 s/件**（首件最贵，稳态退化为 ~8 ms 纯扫描），
   而单件落地是分钟级 → **D1 单独不足以解释并发度恰为 1.000**（本单已在 D1 §2.4 明写此边界，
   不把收益记在没测到的账上）。残余嫌疑移交勘察 lane：`_converge_main_workspace`
   （`commit_queue_landing.py:1390-1424`，每件对**共享主工作区**逐件 git 操作 = 天然串行点）
   与 `PermissionError` 退避风暴（`commit_queue.py:406-420`，现含于锁内）。
5. **不互相挡**：两单函数面不重叠（D1 在 `:2196-2216`，D2 在 `:1577-1645`），
   但要求**不同 commit**，避免 gate 连坐时归属混淆。

## 交付纪律备注（施工 lane 须知）

- 三文件均为新建 .md → 提交侧 CREATE-GUARD 需登记 creation_token（本车道未登记，按主计划合同由施工侧处理）。
- 本目录**零 .json**（文档约定）；实测原始件在 `.runtime/tmp/cs-tbl/d1_probe/`（TTL 临时件，非交付物）。
- 两份手术单均含「不许动」清单：任何 gate 判据、阈值、测试断言一律零改动；
  其中 `tests/git/test_git_commit_gateway.py:431 test_commit_sets_gateway_env` 现为**空断言**
  （语句尾 `or True`），属**加严**对象，不许反向删除。
