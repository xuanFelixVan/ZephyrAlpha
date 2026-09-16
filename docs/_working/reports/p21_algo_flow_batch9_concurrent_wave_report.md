---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓 批9 报告：三域并发 wave（autonomy_core / signal_ashare / data）（st-btfix-p15-20260915）

## 概要

批9 形态变更（Owner 拍板）：**3 个子代理并发搬迁+测试，主会话统一收口**（TDM 注解/创建令牌/claim/串行提交/报告）。提交通道串行是宪法设计（全局锁防搭便车），搬迁侧并发安全（三域文件完全不相交）。

| 域 | src 出仓 | yaml 新建 | 外迁行数 | 域测试 | 提交 |
|----|----|----|----|----|----|
| autonomy_core | 136 | 136 | 4666 | 49 passed | `a1322846` |
| signal_ashare | 102 | 102 | 4960 | 2777 passed（38s；较 wave 时 2758 多 19 例=他会话新增测试） | `a68a71ff` |
| data | 116 | 116 | 4888 | 449 passed / 1 skipped | `9a36c094` |
| 合计 | **354** | **354** | **14514** | 3272 passed / 1 skipped / 0 failed | — |

三个域 round-trip 断言全过、幂等复扫 0 待出仓（除下述 2 个工具 bug 文件）。

## 配套登记

- **创建令牌**：+354 条（autonomy_core 136 / signal 102 / data 116，capability `btfix_p1p2`，created_by st-btfix-p15-20260915）——登记后即被他会话（kimi 挖矿 `06c372bc76`）连带落库（批7/8 同款吸收），三域提交均不含注册表。token 均已入库。
- **TDM 注解**：27 节点（signal_ashare 24 + data 3；autonomy_core 在 TDM 零引用），note_confirmed 2026-09-15 紧贴 node_id + algo_note_zh 出仓注记（yaml 路径取自源文件真实 external 锚点），其中 26 节点既有日期按口径更新为改动确认日。yaml 解析验证 138 节点完整。
- **CloneGuard**：批9 提交期间零新增暴露（echo-guard 累计 31 条不变）。

## 工具 bug（本批新发现，留待修复后补迁）

`externalize_algo_flow.py` 对 **docstring 内嵌块 + `[/ALGO_FLOW]` 后尾部边注释** 模式（块整体嵌在模块级 docstring 内）锚点替换后 ast 校验失败：裸 CJK 字符（`。` U+3002 / `—` U+2014）泄漏到字符串/注释上下文之外。工具自动 .bak 回滚零残留：

1. `src/zephyr/autonomy_core/context/memory_bank.py`（block_lines 65 > 标记跨度 51）
2. `src/zephyr/autonomy_core/skills/skill_attention.py`（block_lines 63 > 标记跨度 48）

共性：块尾部"边:"注释段超出 `[/ALGO_FLOW]` 标记跨度，替换窗口计算未覆盖。修工具后对两文件单独补迁。

## 他会话改动归属隔离（子代理识别 + 主会话核实）

- signal_ashare 6 个子包 `__init__.py`（intraday_t0/limit_up/ml_forecast/screening/sector/sentiment）`__all__` 补充——他会话，不属本批提交
- `src/zephyr/data/config/tasks.yaml`（kline_sector_880 错峰调度注释）、`docs/03_modules/_domain_data/boot_autostart_architecture.md`（CRLF 级）——他会话
- 4 个 signal_ashare 既有 span-not-found 文件（pattern_evidence_certifier 等）保持原状

## 过程观察（并发 wave 实录）

1. **子代理边界纪律有效**：3 代理零 git 操作、零共享文件触碰、零 token 登记，全部由主会话统一收口——并发无冲突。
2. **lock_files 双重 claim 耗时**：476 文件逐个 acquire 约 10 分钟（每文件一个 python 子进程）；建议后续给 lock_files.py 加批量接口。
3. **注册表第三次被吸**：354 token 登记后数分钟即被他会话提交连带入库——多会话风暴下注册表工作区改动保质期以分钟计，"登记后立即被吸收"已是常态且无害（净增）。
4. 域测试均未触发 80MB 审计日志分片策略（本批三域测试目录不含 feedback_loop scheduler 审计链校验）。

## 战役进度

- 本批后累计：批1-8（462）+ 批9（354）= **816 文件（24.7% / 3302）**
- 剩余大域：feedback_loop(340) / infrastructure(336) / governance(296) / shared(243) / gov_enforcement(188) / security(188) 需独立立项；中小域：orchestrator(75) 等可继续按并发 wave 推进。
- 遗留（非本批义务）：externalize 工具 docstring 内嵌块 bug（2 文件待补迁）；pytest_min.ini markers bug；TDM note 归因窗口重设计；GATE-PANORAMA-ALIGNMENT 检测器失效；events.jsonl 80MB 瘦身。

## 收尾补记（2026-09-16，st-btfix-p15-20260916 会话——三哈希实际落库批）

**总包预审计修正证实**：wave 当晚只完成 yaml 落盘（票A），源码锚替换（票B）从未执行（三域 external 锚计数 0/0/1）。收尾批补票 B：136/102/115 文件锚替换全绿，三域锚终态 136/102/116（含既有 capability_symbol_gate），354/354 达成。孤儿 yaml 普查三域全零（A5 四模块删除不波及）。

**yaml 与源码零漂移实证**：69069b9ab4 ruff format 对三域 docstring 块零触碰——CRLF 归一化后 yaml 块与当前源码逐字节一致 354/354 identical。tool 重写 yaml 为幂等覆盖（`_existing_yaml_for` 既有 yaml 优先补丁随 9a 入库：yaml 先落盘场景下 `_yaml_rel_for` 盘存在性碰撞检测会把映射整体改道 `parent__stem` 新路径产生重复 yaml+锚错位——收尾批 dry-run 实证 137 处改道并治本）。

**TDM 注解归属事故与处置**：27 节点出仓注记（yaml 路径取自真实 external 锚）写盘后被他会话裁定#257② 提交（d285958cc4）连带吸收入库——单文件并发编辑后提交方整体拿走，内容零丢失归属随该提交。收尾批按 ALGO-NOTE-SYNC 门官方机制（"加 note_confirmed"=代码触碰+口径未变显式确认）将 27 节点 note_confirmed 推进 2026-09-16 并随 9c 提交（9a36c094）落地。

**门禁会战实录（收尾批 9b/9c 过闸路径）**：DECISION-MAP 基线红（STR-VREV-027/STR-MULTIFACTOR-097 悬空，登记不追归属 automount/btfix 管线自清）一度硬阻 TDM 提交——总包 GW4 注册表补全批落工作区后转绿（收尾批实测 HEAD 9 fails→0）；ALGO-NOTE-SYNC 需 staged diff 先行（门禁链先于网关暂存运行+`_unstage_non_target_files` 会清非清单暂存）——TDM 必须入 --files 且预暂存；CAPABILITY-LOOKUP-REQUIRED 补 `CapabilityLookup.find` 审计后放行。他会话在途件零吸收处置：data/config/tasks.yaml、akshare_provider.py（混有 LUE-2 未提交改动）剔除出 9c，后者 yaml 照常入库、源锚随他会话提交落地。

**claim 体系双轨教训**：lock_files（.ailocks）与 GitCommitGateway claim_files（SessionRegistry.held_files）是两套账——前者不满足提交门检，重试前必须 `git_commit.py --claim-only` 重建 held_files（失败提交 finally 会释放 claim）；会话保活（裁定#252 锁存活=会话存活）需常驻心跳进程，保活进程被杀窗口期 .ailocks 条目会被他会话清理。

## GW11 遗留清偿批（2026-09-16，st-btfix-p17-20260916 会话）

### ① events.jsonl 80MB 瘦身——查证后「登记不执行」（三步验证留痕）

**必要性**：data/audit_trail/events.jsonl 实测 84.6MB / 112,975+ 事件（多会话活跃期 ~100 事件/20 分钟增速），无界增长属实。但交接包所称 verify_chain >120s 未能复现：独立实测 4.8s（112,975 事件全链校验，含 HMAC/内容哈希重算）——>120s 疑为 12 会话并发负载下测量，非文件体积单变量结论。

**真实性**：该文件是活跃追加式哈希链（gate_engine 当日在写）。且链已带历史损伤（先于本会话）：verify_chain 报 37,845 issues——HMAC 失配 26,909 条（自事件 #26810 起）、prev 链断裂 5,595 条（自 #35156 起）、内容哈希失配 5,343 条（自 #53721 起）。疑似密钥轮换/多写方互踩事故现场，瘦身=销毁取证现场。

**可逆性**：两方案均不可逆受损——
1. **截头保尾（保留近 30 天）**：合成链实证（AuditWriter 建 5 事件链→截头保尾 3 事件）：verify_chain 从 valid 翻 compromised，报 `event #1: genesis prev_hash must be '' or '0'*64`。integrity.py L207-213 genesis 哨兵要求首行 prev 为空/全零，截头必破，代码层无解（修 verify_chain 需改 gov_audit，越车道）。
2. **整链分段轮转（LogRotationManager 式）**：违反已登记不变量（retention.py INVARIANTS"不碰核心不可变链data/audit_trail/events.jsonl"+paths.py SSoT 注+AuditChainVerifier 同声明）；跨段防篡改证明永久弱化（删归档段不可检）；merkle_hourly/全史查询消费方（query/anomaly/indexer/drift_bridge/forensic）静默丢史；文件活跃写入窗口内备份-轮转-恢复链路有丢事件窗口；且 ~4 个月即复长回 80MB，无车道内常治机制。

**决定**：登记不执行。附新发现移交 Owner：事件 #26810 起的 HMAC 大面积失配 + #35156/#53721 起的链断裂需专项取证（多写方并发 append 互踩嫌疑：两 writer 各持 _last_hash 交错落盘即致 prev 链断），any 轮转/瘦身动作在取证完成前冻结。

### ② GATE-PANORAMA-ALIGNMENT 检测器失效——GW11 复现实证（修复与回归测试已随晨班 6aee30f70b 在库）

失效形态：reconcile_execution_log 留痕 2026-09-14 17:57（st-mktfix-202609）`run_alignment 异常(UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd6...)`。GW11 独立复现：构造含 GBK 孤立 0xd6 的蓝图 fixture——修复前读取方式必抛 UnicodeDecodeError（同事故签名）；现行 B3 硬化（`_fetch_blueprint_nodes` errors="replace"+U+FFFD 检出跳过、`_load_exempt_list` 前置捕获）下检测器存活、坏文件跳过留 WARNING、好文件正常采集（正例抓到/反例放行）。既有回归测试 TestBadEncodingFailOpen 全绿（test_align_panoramas 43/43）。GW11 结论：无新增改动（晨班已闭环），本节为独立复核证据。

### ③ ALGO-NOTE-SYNC 超窗归因漂移治本——GW11 落地实录（cc386251）

修复：`_collect_node_block_changes_by_linenos`——staged/HEAD 全文建行号→node_id 索引，按 hunk 头双侧行号游标精确归属（+新文锚/-旧文锚/上下文双推进，EOF 钳位继承末行锚）；门闭包经 `git show :map`/`git show HEAD:map` 供料，全文不可得回退窗内锚扫描（回退方向=fail-closed，宁误报不放漂移）。测试 8 例（超窗形态钉死/旧缺陷存档/治本放行/删除行旧锚/无尾换行钳位/无锚空归因/闭包布线/回退阻断），单文件 13/13，全量 tests/governance/commit_gates **2452 passed（2444 基线+8 新增，零回归）**。实弹：本节提交即新门代码在真实网关管线首跑（git show 供料布线实测）；归因逻辑实弹以 FakeGateway 闭包级用例覆盖——真实 TDM（config/**）在 GW11 禁碰车道内，未做真实地图修订实弹，如实留痕。
