---
ttl: task_bound
session: st-circ-a6-20260930
batch: 第4批/A6 挖矿簿 4/6
---

# S4-D 手术单 — SessionRegistry 增量写（整表重写竞态 → 每会话分片）

> 立档：2026-09-30 ｜ 车道：A6（design-only，不附代码）
> 真源文件：`src/zephyr/security/access_control/session_concurrency.py`（SessionRegistry 真身在 security/access_control，非 ops_governance——挂账指引的 grep 已纠偏；ops_governance 侧仅 phase_manager 消费 shutdown 钩子）
> 消费面：`commit_gates/session_required_gate.py`、`rule_bridge/heartbeat_daemon.py`、`rule_bridge/session_worktree.py`、`library/lookup.py`

## 1. 现象量级（遥测实证）

- 本夜 SESSION-REQUIRED 过期坑与本案同源（骨架 §22 挂账原文）：会话明明活着，gate 报「session 未注册」。
- 活表现状：`.runtime/session_registry.json` **11 条 / 5.5KB**（本会话只读量取）——表小，病不在体量，在**写法**。
- 历史实证三连（模块 docstring 自证）：AI-NORTH-001 心跳 daemon 与 commit 进程并发写互踩→心跳丢失→假性过期反复重注册（:783-789）；WinError5 读方持锁连锁→注册表保存失败→watchdog 活跃集为空→#ARCH-304 自动认领不触发→漂移误报 critical+claim 基线失效（:791-798，factory-gate-b2-20260913 实弹 5 连）；#ARCH-324 双 registry 分裂（:314-321）。

## 2. 机理锚点（整表重写竞态）

| 位置 | 内容 |
|------|------|
| `session_concurrency.py:770-779` | `_load()`：读**整表** JSON；损坏→**整表退 {}**（:776-779 一损俱损） |
| `:781-812` | `_save()`：**整表重写**（per-pid tmp+os.replace+WinError5 三次退避）；per-pid tmp 只治「共享 tmp 名竞态」，**不治读-改-写窗口** |
| `:330` | 进程内 `RLock` 只串行化本进程；**跨进程零互斥**——docstring 自认「跨进程并发由 gateway 全局锁+原子 os.replace 兜底」（:328-329），但 heartbeat daemon（独立 DETACHED 进程）不走 gateway 锁 |
| `:340-385 / :387-400 / :502 / :513 / :635-768` | register/mark_logical/unregister/heartbeat/claim/release 全部走 `_load→改→_save` 同一窗口 |
| `heartbeat_daemon.py:39,524` | 每会话独立 daemon **每 30s** heartbeat 一次——夜战 10+ 会话=每 30s 十余次整表重写并发 |
| `session_required_gate.py:90-101` | SESSION-REQUIRED 读链：`gateway.registry.get_session(sid)` → None 即阻断；**条目被他人 last-writer-wins 覆盖 = gate 假红** |
| `:302-330` | anchor_main_root 锚定主仓（#ARCH-324 治本），写点唯一、竞态面唯一 |

**竞态窗口**：A 进程 `_load`（读到 X,Y）→ B 进程 `_load`+`_save`（写回 X,Y,Z′）→ A 进程 `_save`（写回 X′,Y——**Z′ 丢失**）。Z 若是心跳/注册，即「活会话被抹」→ SESSION-REQUIRED 假红或心跳假死。窗口毫秒级×夜战高频写，命中是时间问题。

## 3. 设计（意图，不附码）

**原则：把「共享可变面」拆没——写只碰自己的片，竞态对象消失，而不是给竞态加锁。**

1. **表拆片**：`.runtime/session_registry/`（目录）+ 每会话一片 `<sid>.json`。写路径（register/heartbeat/claim/...）只读改写**本会话片**（保留 per-pid tmp+os.replace+WinError5 退避原语义）；跨会话操作（如 depends_on 登记）改写两张片，各自原子。
2. **读侧聚合**：`_load` 变为「glob 读片、逐片 json.loads、损坏/缺失片跳过+审计落账」（对齐现 ：777 容错语义，但损失半径从整表缩到单片）。`get_session` 热路径只读单片（O(1)，比现在整表还快）。
3. **TTL 清扫**：孤儿片收割（片 mtime 超 `_SESSION_TTL_SECONDS` 或 pid 探活失败）并入既有清理路径；清扫与写入同片原子，不碰他片。
4. **迁移双写窗口**：过渡期 `_save` 同时写片+旧单文件（旧表降级为只读兼容副本）；读侧优先片目录、片目录不存在回退旧表。两个 flag 周期后退役旧表写。
5. **不动面**：SessionInfo schema、判活矩阵（:282-299）、anchor_main_root、SESSION-REQUIRED/worktree gate 判定语义、lock_files.py 文件级锁（不同层，不合并）。

## 4. 红测两针

- **R-D1 交错写竞态判别**：两线程（或双进程）复现「A load → B load → B save → A save」交错——断言 B 的新增/心跳**不得**被 A 的写回抹除。**现码必红**（last-writer-wins 结构性丢失）；分片后各自写自己片，天然绿。
- **R-D2 损伤半径断言**：写 A 片不得改 B 片字节（mtime+内容断言）；人为损坏 B 片 JSON → A 的 register/heartbeat/get_session 必须正常（**现码单表一损俱损整表退 {}，必红**）。

## 5. 差分矩阵

1. register/heartbeat/unregister 逐 API 行为全等；2. claim/release/批量（:635-768）持面语义全等；3. depends_on 登记跨片写一致性；4. get_session 三态（在册/不在册→阻断/异常→降级放行 :91-94）；5. 片损坏（跳过+审计，其余片可用）；6. 片缺失（读侧视作未注册）；7. 目录不存在→回退读旧表；8. 迁移双写窗口（旧表+片并存，两侧读一致）；9. TTL 清扫不误杀活片（mtime 新鲜/pid 活）；10. 清扫死片后 gate 立即可见；11. anchor_main_root 路径下目录布局（主仓锚定不变）；12. 高并发 10 daemon×30s 心跳 soak（断言零丢失）；13. worktree 内构造锚主仓（#ARCH-324 回归）。

## 6. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | 迁移期两真源漂移（片有旧表无） | 双写窗口内旧表为冗余副本非真源；读侧以片为准；红测例 8 锁一致性 | 双写期 crash→旧表落后→但读侧已优先片，无感 |
| 2 | glob 读放大（会话数多时） | 现实 11 片×毫秒级；get_session O(1) 单片反优 | 百级会话才需索引片（不做，YAGNI） |
| 3 | 清扫误杀（时钟回拨/TTL 边界） | 清扫判据复用 ：282-299 判活矩阵+pid 探活，双条件；红测例 9 | 低 |
| 4 | 他消费者直读旧单文件路径 | grep 全消费面走 SessionRegistry API（已核实 gate/daemon/worktree/lookup 均经 API）；迁移期旧表持续写 | 外部脚本裸读路径——退役公告随 flag 周期发 |

回滚：片目录为纯新增；`ZEPHYR_SESSION_REGISTRY_SHARDS=0` 停用分片（回退旧表单文件，双写保证零丢失）；单 commit revert 净退。

## 7. 估时

| 步 | 内容 | 估时 |
|---|------|-----|
| 1 | R-D1/R-D2 红测先跑现码取红证 | 0.5 h |
| 2 | 分片读写+读侧聚合+回退读 | 1.0 h |
| 3 | 迁移双写+TTL 清扫 | 0.5 h |
| 4 | 差分矩阵 13 例+soak 全绿 | 1.0 h |
| 合计 | | **3.0 h**（+旧表退役另一 flag 周期，零工时） |

## 8. 执行留痕（G2 施工班 st-circ-g2-20260930，2026-10-01）

- **施工完成**：§3 全部五件——①表拆片：主真源=.runtime/session_registry/<sid>.json 每会话一片，全部写路径（register/heartbeat/mark_logical/register_dependency/clear_dependency/unregister/claim_file(s)_batch/release_file(s)_batch/get_session）只碰本会话片（per-pid tmp+os.replace+WinError5 退避原语义保留），get_session O(1)；②读侧聚合：损坏/缺失片跳过+审计（损失半径=单片），片目录缺席回退旧表，迁移窗旧表底座片优先（部署前条目不漏看）；③迁移双写：片写同步镜像 upsert 旧单表（watchdog/write_audit_daemon/commit_queue/check_commit_message 直读路径不受扰）；④语义收敛：公共 save()=merge-upsert 永不删（整表替换删条目正是 R-D1 病根），删除只走 unregister/reap 显式意图；⑤回退手柄 ZEPHYR_SESSION_REGISTRY_SHARDS=0。退役 _ensure_registered_locked（零调用方）。§3.5 不动面零触碰（SessionInfo schema/判活矩阵/anchor_main_root/TTL 常数/gate 语义/lock_files.py）。
- **红测先行**：R-D1 交错写（现码 last-writer-wins 抹条目红证）+R-D2a 损伤半径（现码整表退 {}）+R-D2b 写隔离字节断言。差分矩阵 13 例全映射+10 写者×30 轮 soak+跨进程 20 轮注册竞态零丢失+unregister 幂等双侧。测试读数：session 70/70+消费面 172/172（e2e session_concurrency/heartbeat_daemon/claim_files/stash 红蓝/import_integrity）+session_worktree 7/7；ruff 双净。
- **运维留痕**：直投两次死于 GATE-PRECOMMIT-RUN debt-ratchet（净增键全为他会话在途树面债：vendor/Kronos examples、py.ini、directory_contract.yaml——与本袋两件零交集，两次同签名复现=环境漂移形态）——按门处方改走队列正门（serializer 干净暂存区结构性免疫连坐），未动全局基线未翻全局手柄；维护班治本建议=基线吸收或树面收敛后复归。
- **落地**：队列袋 q-20261001-st-circ-g2-20260930-0003。旧表退役=另一 flag 周期（零工时），直读消费者退役公告随 flag 周期发。
