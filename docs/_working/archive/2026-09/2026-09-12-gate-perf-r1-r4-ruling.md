---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：治理档案（裁定/对质记录），长期保留。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# echo_guard 分层归位裁定（R1-R4）+ preflight/cache 灰度观察计划

- **task_bound**：运维裁定记录；R3 回位条件满足后销项归档；会话 st-encfix-20260911 单写手
- **创建**：2026-09-12；creation_token=`gate-perf-r1-r4-ruling-20260912`（capability_canonical_file_registry.yaml creation_tokens 段）
- **裁定依据**：Owner 2026-09-12 批准"从 R1-4 全部开工"；上游证据链五组（见 §1）

## 0. 一句话裁定

"卸载 onnxscript"与"升级 CLI"不是二选一，是同一治本方案（分层归位）的两个时点：
语义检测从 L1 提交拦截位（30s 预算）归位到 L2 周期审计位（分钟预算）；
上游修复+索引压实后按回位条件复活 Tier2。

## 1. 证据链（2026-09-11/12 取证）

1. embeddings.npy 5.57GB 服务 28,236 函数（理论 ~116MB，膨胀 48×）；全量重建后 5,570,994,176B→5,575,188,480B **只增不减**（append-only 不压实）。
2. 驱逐实验：删 npy 后 check 绕过 HF_HUB_OFFLINE 联网拉模型，475.7s rc=15 失败且不重建——npy 驱逐不可行。
3. 内存无罪：64GB 余 21GB，(32,1024,1024) 128MiB 批分配失败为 CLI 内部缺陷。
4. 升级无门：PyPI 最新即 0.4.1（已装）。
5. 配置无 Tier 开关：yml/CLI 均无；蓝图钦定唯一 Tier2 关闭机制=onnxscript 缺席。

## 2. 执行状态

| 项 | 动作 | 状态 |
|---|---|---|
| R1 | `pip uninstall onnxscript`（可逆）；L1 归位确定性引擎（ast_grep+token 检查；echo_guard 快速失败降级） | ✅ 已执行；实测 CAPABILITY-OVERLAP 0.76s（原 32s/30s 烧预算态） |
| R2a | RECONCILER-HEALTH 2.6 探针：rescan.signal 残留>7 天 / embeddings.npy>2GB 双告警（warn 不阻断） | ✅ 已落码（+4 测试） |
| R2b | embeddings.npy 保留原地（Tier2 唯一工作状态；探针监控；压实重建并入 R3 窗口） | ✅ 裁定保留 |
| R3 | 上游三缺陷+回位条件登记 clone_guard.yml echo_guard 段 | ✅ 已登记；回位=上游修复版 + onnxscript 重装 + 联网窗口压实重建 + check<30s 验证 |
| R4 | preflight/cache 灰度观察计划（§3） | ✅ 本文档即计划 |
| R5 | commit_queue dead=821 按 66 号 §6.4 取回流程批处理（队列运营收尾，不新增机制） | 移交排期 |

## 3. preflight/cache 灰度观察计划（R4）——已提前结项转正

- **2026-09-12 Owner 裁定提前转正**（原定 7 天窗口缩至 0）：依据=7 笔实弹提交零异常
  +红蓝#2 缓存投毒/失效攻击 4/4 全防住+reconciler 永久对账兜底（漏检检测不依赖灰度期，
  每次提交自动跑）。转正操作=flags.yaml 两 flag 描述去除灰度语言+implementation_status
  升 production。**回滚通道永久有效**：`config/flags.yaml` 两 flag 翻回 false +
  删 `.runtime/gate_cache/`——任何时候发现漏检照此执行，无需等窗口。
- 观察指标（命中率/采信率）仍可持续从 `.runtime/gate_cache/` 与 gate 审计回溯（被动留痕）。

## 3a. R3 处置——不等作者了，echo_guard 退役（2026-09-12 Owner 裁定）

- 原案"等上游发版后回位四步"**取消**：等时间表未知的外部作者=永悬活账；redup 已实测
  接管核心职责（T1/T2/T3 红蓝#3 全抓获+L2 语义全语料）；其独门能力（全函数索引 vs
  变更文件）由 redup L2 周期审计兜底（W3 缺口=新文件克隆旧仓未变更函数，提交时漏检、
  周期审计补获）。
- 退役动作：clone_guard.yml echo_guard enabled:false 长期保持+注释改退役语义；
  死缓存已删（embeddings.npy 5.2GB/index.duckdb 826MB/wal，可再生的派生缓存）；
  RECONCILER-HEALTH 2.6 探针保留（防误启用复发）；重启条件留档备查（非承诺）。

## 4. L1 检测面补偿说明（echo_guard 退役后）

退役后 L1 阵容=ast_grep（结构规则，本夜全部实证拦截来源）+ redup（T1/T2/T3 结构克隆，
changed-only 增量 ~2s）+ 能力反查/token 检查 + L0 MCP advisory + acknowledged 白名单纪律。
已知残余缺口（红蓝#3 唯一真红旗）：新文件克隆旧仓**未变更**函数在提交时漏检——
由 redup L2 周期审计（全语料语义模式）补获，属分层设计内的时间延迟而非覆盖缺失。
