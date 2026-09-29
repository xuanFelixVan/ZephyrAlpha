---
created: 2026-09-30
ttl: task_bound
title: E2 gateway锁外锁内前置挖矿簿
session: st-gate-rationalize-20260929
---

# E2 gateway 锁外/锁内前置 挖矿簿（02）

> 环节定义（00_skeleton §一）：pg_probe/横幅/worktree 检测/tracked 快照/itA 清扫。
> 范围=GitCommitGateway.commit()（git_commit_gateway.py:2518-2841）从入口到 _GlobalCommitLock 临界区内、
> gate 链（E3）开跑之前的全部固定前置；行号 2026-09-30 实测，种子行号漂移处已重定位。

## 0 自审闸：【挖干】

理由：commit() 前置全序 22 件逐件读毕（锁外 10 件/锁内 7 件/收尾 5 件），每件有 file:line 锚；git 子进程逐笔账=锁外 2-4 个+锁内 4 个（tracked 前后快照）+清扫 2-4 个，与 adjudication:29「每笔固定杂税」清单对账一致；Rx-2 落账已落有双点位实证；三横幅（critical_warn/block/bottleneck）真源与消费方闭合。缺口一处（§4）：gate_preflight flag 出厂 OFF 的 compute_fingerprint 内部成本未实测（零开销路径不阻塞）。

## 1 组件全清单

### 1.1 锁外前置（_GlobalCommitLock 进入前）

| # | 组件 | 功能 | 代码锚点 | 触发时机 | 耗时账 | 自动化属性 |
|---|------|------|---------|---------|--------|-----------|
| 1 | 入口归一化+existing 过滤 | abspath 归一；_filter_existing_files：不存在文件逐个 is_git_tracked（1 ls-files 子进程/件，:(icase) 大小写兼容 :2843-2855）或 _is_staged_delete | git_commit_gateway.py:2564-2571, 1918-1928 | 每笔必经 | 正常笔≈0 子进程（文件都在）；删除笔 1 子进程/删除件 | 必经 |
| 2 | worktree 归属检测 | _get_worktree_manager 惰性单例 → get_current_worktree；异常降 wt_session=None | git_commit_gateway.py:2573-2578, 1282-1288 | 每笔必经 | 1 次（惰性后进程内缓存） | 必经 |
| 3 | 非 worktree 提交警告 | list_active 排除 worker-{sha8}-{pid}（:1312-1321）后有他会话→WARN 并发风险；不阻断 | git_commit_gateway.py:1290-1342 | wt_session=None 时 | 1 次整表 registry 读+判活 | 条件 |
| 4 | MERGE_HEAD 盲检测（锁外） | _is_merge_in_progress：git rev-parse --git-path MERGE_HEAD（worktree 感知，AI-R1-003）；命中且无 merge_finalize→拒绝（B2① AI-FILL-14 截胡治本） | git_commit_gateway.py:2581-2586, 4423-4457 | 每笔必经 | 1 git 子进程 | 必经 |
| 5 | _WORKTREE_SKIP_GATES 装载 | worktree 内跳过搭便车三 gate（单一真源 session_worktree，tracker #92） | git_commit_gateway.py:2593-2599 | wt_session 非 None | 进程内 import | 条件 |
| 6 | pg_probe 前置 | refresh_pg_probe_state：TCP 探测 PG（_PROBE_TIMEOUT_SECONDS=1.0s，不认证不查询 :155-165）→ 读 prev 状态合并双锚点（first_offline_at/last_reachable_at）→ tmp+replace 原子写 .runtime/pg_probe_state.json；endpoint 真源=depgraph_schema._load_pg_config；任何失败不阻断 | git_commit_gateway.py:2601-2612; pg_probe.py:103-109, 143-152, 181-216 | 每笔必经（锁外） | ≤1s（在线亚毫秒连库口）；+1 状态文件写；**无缓存——每笔全价探测**（pg_probe.py:181 无 freshness 短路，_PROBE_FRESH_SECONDS=600 仅消费侧 :219-230） | 必经 |
| 7 | critical_warn 横幅 | 查 governance.db（SQLite）reconcile_execution_log 近 24h action=critical_warn（未 ack 且无后续 clean）→ 有则打印横幅；不阻断 | git_commit_gateway.py:2617; reconciliation_registry.py:1544, 1604-1644 | 每笔必经 | 1 次 SQLite 连接+查询（timeout=10s 池 :1687） | 必经 |
| 8 | block_next 横幅 | 查同表近 24h block_next → 有则打印+**返回 error 硬阻断**（resolve_blocks() 才能清） | git_commit_gateway.py:2623-2628; reconciliation_registry.py:1647-1768, 1771+ | 每笔必经 | 1 次 SQLite 连接+查询 | 必经（阻断型） |
| 9 | message 构造+逃生旗标记 | gw_marker=[GW:sid] 锁外构造；merge/overlap/multi-domain/tracked-drift 尾标记 | git_commit_gateway.py:2630-2654 | 每笔必经 | 进程内 | 必经 |
| 10 | O2 热文件 overlap 升级阻断+计量 | allow_overlap 时先 _check_hot_overlap_escalation（24h 滚动窗热文件≥阈→阻断）再放行并 _log_allow_overlap_usage（含 is_hot_file 逐件判定）落 allow_overlap_usage.jsonl | git_commit_gateway.py:2636-2650, 820-849 | --allow-overlap 时 | 逐件热文件表读 | 条件 |
| 11 | gate_preflight 锁外预跑 | flag gate_preflight 出厂 OFF（:2659「OFF 时零开销」）；ON 时 compute_fingerprint+白名单内容 gate 预跑记指纹，锁内 F′==F 才采信 | git_commit_gateway.py:2659-2703 | flag ON 时 | OFF=0 | 条件（默认关） |

### 1.2 锁内前置（_GlobalCommitLock 临界区内，gate 链前）

| # | 组件 | 功能 | 代码锚点 | 触发时机 | 耗时账 | 自动化属性 |
|---|------|------|---------|---------|--------|-----------|
| 12 | 进锁+Rx-2 成功落账 | _GlobalCommitLock(timeout=lock_wait_timeout 默认 60s) 进入；立即写 lock_wait 行（waited_ms/holder/timeout，含无竞争 ≈0 行——覆盖率判据要求全量） | git_commit_gateway.py:2704-2720 | 每笔必经 | append 1 行 | 必经 |
| 13 | 锁内 merge 二次校验 | 晾置可发生在锁外检测后——TOCTOU 根治复检 | git_commit_gateway.py:2721-2723 | 每笔必经 | 1 git 子进程（**每笔第 2 次 merge 检测**） | 必经 |
| 14 | ita 清扫 | _list_intent_to_add_paths：git ls-files --debug 解析 flags 0x20000000 位（回退 --stage 空 blob+cat-file，旧 git 每件 1 子进程）→ 命中且非目标件→git reset -q（只动 index）；MERGE_HEAD 期全禁；审计 gateway_index_hygiene.jsonl | git_commit_gateway.py:2724-2726, 4463-4527, 746-766 | 每笔必经 | 1 git 子进程保底（ls-files --debug 全索引）+有残留 +1 | 必经 |
| 15 | 幻影 AD 清扫 | git status --porcelain=v1 扫 AD 条目（staged-add+worktree-deleted=确定性垃圾）→ _unquote_git_path（#353③ 中文路径引号转义逃逸治本）→ git reset -q；MERGE_HEAD 期全禁；同册审计 | git_commit_gateway.py:2727-2728, 4530-4573 | 每笔必经 | 1 git 子进程保底（status 全量）+有残留 +1 | 必经 |
| 16 | 锁内指纹重验 | preflight ON 时重算 F′ 比对；OFF=零开销 | git_commit_gateway.py:2729-2739 | flag ON 时 | OFF=0 | 条件 |
| 17 | tracked 区前后快照 | _tracked_area_snapshot×2（gate 链前 :3194/链后 :3225）：每次 git diff-files + git diff-index --cached HEAD **2 个子进程**，拼原始输出 sha256 指纹+路径映射；**共 4 子进程/笔** | git_commit_gateway.py:3194, 3225, 2974-3013 | 每笔必经（gate 链包裹） | 4 git 子进程/笔（adjudication:29 杂税清单同名项） | 必经 |
| 18 | tracked 漂移归因+白名单 | 指纹 diff→文件级归因 _attribute_tracked_writes；白名单 SSoT=gate_tracked_write_allowlist.yaml（mtime 缓存，失败 fail-open 降级 warn-only）；清单外漂移降级 warn 不连坐（F3 治本），清单内未归因→TRACKED-DRIFT-READONLY 硬阻断（allow_tracked_drift 逃生留痕） | git_commit_gateway.py:3015-3059, 3226-3274 | 前后指纹不等时 | 1 次 YAML 读（有 mtime 缓存） | 条件（漂移才走） |
| 19 | gate 链入口+own-tree 视图 | _check_gates_with_drift_watch：A1 读缓存开窗（:3198）+S1 不可变树 CommitTreeView 接线（flag immutable_tree，:3213）→ 交 E3（本簿不展开） | git_commit_gateway.py:3172-3224 | 每笔必经 | 见 E3 册 | 必经（边界件） |

### 1.3 出口/异常路径（前置收尾）

| # | 组件 | 功能 | 代码锚点 | 触发时机 | 耗时账 | 自动化属性 |
|---|------|------|---------|---------|--------|-----------|
| 20 | 阻断审计+bottleneck 横幅 | gate 阻断→_audit_commit_block_event（status 映射>正则提 gate_id，UNKNOWN×6 治本 :1972-1984）写 commit_block_events.jsonl + _print_bottleneck_banner 整读该 jsonl 取 24h TOP | git_commit_gateway.py:2758-2762, 1964-1994, 769-817 | 阻断时 | 2×append/写 + **整读 jsonl 逐行 parse ×1** | 条件 |
| 21 | 锁超时/fail-open 双路 | GatewayError→Rx-2 lock_timeout 落账（:2767-2778）；OSError→_audit_commit_lock_fallback 无锁降级重跑 merge 检测+双清扫+gate 链（:2781-2815） | git_commit_gateway.py:2764-2815, 726-743 | 异常时 | 同主链一套 | 条件 |
| 22 | 慢提交+GAP-1 采样 | 全程墙钟>60s（_SLOW_COMMIT_THRESHOLD_S :347）→commit_slow 行；成功笔 sha 尾≥0xE 12.5% 采样 commit_ok_sample | git_commit_gateway.py:2817-2836, 1996-2012 | 每笔成功 | append ≤1 行 | 条件 |
| 23 | _snapshot_worktree_status | 成功笔 git status --porcelain=v1 --branch 全量 → branch_header+dirty 前 200 条 append worktree_status_snapshots.jsonl（best-effort） | git_commit_gateway.py:2837, 2115-2150 | 每笔成功 | 1 git 子进程+1 append；实测现册 2464 行（2026-09-30 wc 实测；**种子称曾有 449 万行膨胀史，现状已收敛**） | 成功笔必经 |
| 24 | 成功路径 bottleneck 横幅 | D5 推模式：成功也打近 24h 堵点（Owner 裁定"每次交付都提醒"）→**整读 jsonl 第 2 次/笔** | git_commit_gateway.py:2840, 769-817 | 每笔成功 | 整读 jsonl 逐行 parse ×1 | 成功笔必经 |

## 2 六向台账

- **上游触发源**：①git_commit.py CLI `_commit_with_claim_lifecycle`→gw.commit（git_commit.py:754-772）②commit_queue 落地器（E7，worktree 内）③reconciler auto-commit 批（E8 BatchedAutoCommitter，gateway:1122）④session_worktree merge 预演链（pg_probe CONSUMERS 列 pre_merge_topo_check，pg_probe.py:5）。
- **下游消费方**：①pg_probe_state.json→E3 四台 depgraph gate 降级判定+DEPGRAPH-FRESHNESS 24h 豁免（pg_probe.py:30-33）②critical_warn/block→AI 修复环（resolve_blocks reconciliation_registry.py:1771）③commit_block_events.jsonl→commit_perf_report.py --hours 24（横幅 :812 自述）+E9 遥测④worktree_status_snapshots.jsonl→worktree wipe 事故追查（:2118-2120 S3 裁定）⑤lock_wait_events.jsonl→gates 相位四合一定案（:561-563 Rx-2）⑥tracked 快照→TRACKED-DRIFT-READONLY gate 结果进 E3 链。
- **输入面**：files 清单/message/session_id、allow_* 五逃生旗+merge_finalize+lock_wait_timeout（:2538-2546）、config/flags.yaml（gate_preflight/immutable_tree 两旗）、governance.db、pg 端点配置（DATABASE_URL > config/.env.postgres）、gate_tracked_write_allowlist.yaml。
- **输出面**：.runtime/pg_probe_state.json；stdout 三横幅；.runtime/audit/{commit_block_events.jsonl, lock_wait_events.jsonl, gateway_index_hygiene.jsonl, worktree_status_snapshots.jsonl, hook_tracked_drift.jsonl, allow_overlap_usage.jsonl, commit_lock_fallback.jsonl}；index 清扫副作用（git reset）。
- **真源锚**：pg 端点唯一真源=depgraph_schema._load_pg_config（pg_probe.py:144-152 禁复制）；merge 判定唯一原语=_is_merge_in_progress（gateway:4423-4441，禁 .git/MERGE_HEAD 硬编码 :4425-4430）；tracked 白名单 SSoT=catalog YAML（:3015, 3018）；skip 集合单一真源=session_worktree._WORKTREE_SKIP_GATES（:2591-2592）；整链顺序真源=本册 §1（commit() :2558-2841 单体函数）。
- **耗时账汇总**：锁外固定≈pg_probe(≤1s 无缓存)+2×SQLite 横幅查询+2 git 子进程（merge+worktree）；锁内固定≈4 git 子进程（tracked 快照）+2 git 子进程（双清扫）+1 git（merge 复检）+1 append（Rx-2）；成功收尾≈1 git status+jsonl 整读×1+快照 append。合计每笔固定 git 子进程≈10、jsonl 整读 1-2 次、SQLite 查询 2 次、TCP 探测 1 次无缓存——与 adjudication:29/285/293/344 四条杂税定性完全对上。

## 3 现状缺陷与已修记录

已修（勿重做）：
1. B2① MERGE_HEAD 盲（AI-FILL-14 截胡张冠李戴）→ 锁外+锁内双检+merge_finalize 显式通道（gateway:2581-2586, 2721-2723；adjudication:381 载 M3/T6 同包非 dev 早退与钩链 git 子进程 5→1 已落）。
2. B2② ita 盲区（diff --cached 不可见致 merge 误报，09 分支两文件实证）→ ls-files --debug flags 位清扫（gateway:4464-4471）。
3. P3-2 幻影 AD（被拦提交预暂存残留）→ porcelain AD 清扫（gateway:4531-4539）。
4. #353③ 中文路径幻影逃逸（porcelain 引号转义恒假判断）→ _unquote_git_path 统一解析（gateway:4552-4556）。
5. F3 连坐降级（清单外漂移整链白跑 19-58s×4-6 重试放大）→ own/foreign 分道，foreign 降级 warn（gateway:3231-3248）。
6. UNKNOWN×6 阻断归因失效 → status 映射链（gateway:1972-1984）。
7. Rx-2 锁等待落账已落（成功+超时双点位；处方=02_prescriptions.md:25，docs/_working/final_delivery_campaign/mining_commit_chain/02_prescriptions.md；adjudication:362 列「已执行勿重做」）。
8. #ARCH-119 pg_probe 立项（B2 主体）：探针不阻断+状态文件跨进程单真源+双锚点（pg_probe.py:23-55）。
9. AI-R1-003 worktree 感知 merge 检测（.git/MERGE_HEAD 硬编码治本，gateway:4425-4434）。
10. T4-1/CAND-GATEMECH-004 tracked 漂移审计化+文件级归因升硬（gateway:3061-3103, 3182-3188）。

现存缺陷（未修）：
- D1 pg_probe 每笔全价 TCP 探测无缓存（pg_probe.py:181-216 无新鲜度短路；消费侧 _PROBE_FRESH_SECONDS=600 形同虚设于生产侧）——处方已在案。
- D2 bottleneck 横幅整读 commit_block_events.jsonl 逐行 parse，成功+阻断双路径最多 ×2/笔，随账本线性涨（gateway:788；adjudication:293 处方=尾读 N 行/ts 二分）。
- D3 tracked 前后快照 4 git 子进程/笔（gateway:3194+3225×2；adjudication:29 杂税同名项，本总包 A2/「快照并1」施工点）。
- D4 双清扫每笔 2 个保底全量 git 子进程（ls-files --debug 全索引 + status --porcelain 全量），即便零残留也付（gateway:4515, 4544）。
- D5 锁外/锁内 merge 双检、锁内 worktree 检测复用锁外结果——两次 rev-parse 中锁外一次理论上可并入锁内（现状保持双检是有意 TOCTOU 加固，动前须红队复评）。
- D6 _filter_existing_files 删除场景逐件 ls-files 无批量（gateway:1920-1927 对比 lock_files._tracked_paths_batch 已有分片先例 :646-671）。

## 4 待办与移交

1. 【st-gate-rationalize-20260929 认领】盲轮询退避（归属 E1 锁本体，施工点 gateway:704；本环节锁内段依赖其节奏，验收联动）。
2. 【st-gate-rationalize-20260929 认领】pg_probe 缓存：生产侧加 ≤600s 新鲜度短路（adjudication:344 待办清单同名项；施工点 gateway:2601-2612/pg_probe.py:181）。
3. 【st-gate-rationalize-20260929 认领】横幅尾读：bottleneck 改尾读 N 行或 ts 二分（adjudication:293；施工点 gateway:769-817）。
4. 【st-gate-rationalize-20260929 认领】快照并1：tracked 前后快照 4 子进程并 1（skeleton:34「B gateway 杂税四件」；施工点 gateway:3194, 3225, 2986-2997）。
5. 移交 E3：gate 链本体 104 台与 preflight 白名单 CONTENT_SCAN_CACHE_WHITELIST 语义。
6. 移交 E4：pre-commit 通道 hook 链（T6 已修成果核验口径=adjudication:381）。
7. 移交 E9/E10：六本 jsonl 册的轮转策略（worktree_status_snapshots 现状 2464 行健康，历史 449 万行膨胀复盘归档于 adjudication:344 轮转待办）。
8. 未挖缺口（不阻塞）：gate_preflight=ON 路径 compute_fingerprint 实测成本（flag 出厂 OFF，零开销路径；翻转属 Owner 窗口，实弹时补测）；_check_hot_overlap_escalation 内部阈值表（O2，:2636-2641，仅逃生旗触发）。
