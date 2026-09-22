---
ttl: task_bound
---

# 环节1：入队链（enqueue）挖矿

> 挖矿：子代理 2026-09-22 凌晨，全程只读。锚定实证=workclean 0091 死信（111 文件 116 分钟死于 CREATE-GUARD）。

## A 职责与输入输出

把提交意图变成"内容寻址快照袋+pending 项"，入袋即安全（66号§4 裁定2）；入队后自举排空。队列核心层**零 git/零注册表依赖**（commit_queue.py:1012 明文不变量），门禁判断延迟到落地侧。输入 `enqueue_item(session_id, message, files=[(path,bytes)], options)`；输出落袋 qid；轻检拒绝 DENIED exit2；预检阻断 exit8。两条通道：git_commit.py --enqueue（主门，含预检+自举）；commit_queue.py enqueue/requeue CLI（**均无预检**）。

## B 代码地图

- commit_queue.py：resolve_queue_root:326 / _ensure_dirs:351 / 轻检四件（session 白名单/路径穿越+密钥/空 message/10MB 上限）:395-442 / _store_blob（sha256+exists 去重+tmp/fsync/replace）:450 / qid 分配:469-502 / 同键去重 compaction:509-567 / **enqueue_item**:593-706 / try_bootstrap_drain:1237 / requeue:1320-1395（**无预检**）/ CLI:1693-1738。
- git_commit.py --enqueue：入口分流（显式/锁忙探针/LOCK_TIMEOUT 改道）→ _git_tracked_subset 删除分区:547 → **入队预校验 :800-814（建临时网关+run_preflight(mode="enqueue")）** → 读快照入袋:849 → 自举排空:863。
- **预检引擎已存在**：src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py——PREFLIGHT_GATES 白名单:105-135（现 16 道）；准入判据（禁依赖共享暂存区）:42-54；run_preflight:230-295（审计落 .runtime/audit/preflight_events.jsonl）。

## C 六向台账（关键发现）

- **① 三触发口**全汇入 _enqueue_mode；reconciler 自动批走 landing 侧 reroute（:1100）不经预检——同语义两张皮（缺口）。
- **③ 机制对标**：DIRECTORY-CONTRACT 已完成"diff 依赖型 gate→files 内联清单校验后准入白名单"完整先例（commit_preflight.py:126-133；directory_contract_gate.py:80 _MAX_INLINE_FILES=500）。**杀手榜前三不在白名单的原因**=输入面锚 staged diff：CREATE-GUARD（priority=61）、TRANSLATION-COVERAGE（git diff --cached --diff-filter=A）、RULING-REFERENCE——入队语义下"清单∪dev HEAD 跟踪态∪注册表"可等价判定（git_commit.py:797-799 注释已论证磁盘内容=快照内容）。
- **④ 测试覆盖**：enqueue 核心密集（1209 行测试）；**--enqueue 接线 0 直测、enqueue 预检 0 测**（缺口实锤）；git_commit.py 头部 [TESTS] 指针漂移（指向不存在的 tests/test_git_commit_gateway.py）。
- **⑤ 观测**：enqueue_item 无分步计时；入队→死信之间无进度事件。
- **⑥ 状态数据**：pending 3/processing 1/done 849/dead 385/**blobs 16218 个共 2.31GB 无界增长**（cleanup_done 明文不管 blobs，done TTL 清理不连带 GC）。

## D 成本模型

入队本体最贵步=冷 blob 逐文件 fsync（111 个≈1-3s）；调用方墙钟绝对主导=自举排空的落地全链——**落地侧遥测：单项均值 79s/P90 189s/max 988s**。经济账：预检 3-5s vs 落地死刑 79s+排队 116min——失败前移的动机就在这。

## E 升级机会清单

1. 【快】**CREATE-GUARD 前移入队预检**（=R1 主件）：按 DIRECTORY-CONTRACT 同款改造为"清单内联判定新文件（path∉dev HEAD ls-tree 批量）∩ path∉creation_tokens"→预检快败+登记指引；准入 PREFLIGHT_GATES。风险：入队后他人抢先落同路径→误红（罕见，提示重试）。
2. 【快】**入队批次条数硬顶 40+逃生旗 --allow-oversize-batch**（=R2，SC-3）：_enqueue_mode 快败提示拆批；旗写 meta_extra 留痕；enqueue_item 加同判兜 requeue 通道（约 30 行+3-5 测试）。先例：_MAX_INLINE_FILES=500（语义=降级阈值，此处为拒绝阈值，跨域不并）。
3. 【快】requeue 面补同款预检（死信重取回不再原样再死）。
4. 【快→半挂】RULING-REFERENCE 同型前移（逐文件 HEAD 内容对比提裁定#NNN 新增引用，纯文本）；TRANSLATION-COVERAGE 改造面大先挂牌，待病灶前移后按死信率复测定优先级。
5. 【快】enqueue_item 分步计时落审计（+10 行）。
6. 【快】NO-BARE-SQL/ALGO-FLOW 类文本扫门禁同型评估（待环节5 清单定输入面后定）。
7. 🌑 blobs GC（2.31GB 无界）：跨域+Owner 门位——挂起登记。
8. 【快】git_commit.py 头部 [TESTS] 指针修正。
9. 【快】_enqueue_mode 端到端+预检接线测试补齐（随施工同批）。
10. 封矿：enqueue_item 核心内嵌门禁检查（破坏零依赖不变量）；解耦自举排空（协议变更）；死信改同步报错整体重构。

## F 挖矿日志表

enqueue 函数族全文/三触发口/预检引擎/三 gate 输入面/0091 死信实物（101md+9yaml+1csv）/运行态统计/_enqueue_mode 测试检索（查无）/集成测试 preflight 检索（查无）/条数上限检索（查无，唯一先例 500 降级阈值）/[TESTS] 指针（查无=漂移）。

## G 自审闸三态裁定（主会话融合）

施工：E1+E2+E3+E5+E8+E9（+E6 视环节5 结论）。挂起：E4 半（TRANSLATION）、E7（blobs GC，Owner）。封矿：E10 三项。
