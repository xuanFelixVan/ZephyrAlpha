---
ttl: task_bound
---

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

## 3. preflight/cache 灰度观察计划（R4）

- **窗口**：2026-09-12 起 7 天（至 2026-09-19）。
- **起始域**：docs 域提交优先观察（本文档提交即首个样本）；src 域自然混入后一并统计。
- **指标**（均可从 `.runtime/gate_cache/` 与 `.runtime/gate_audit/` 回溯，无新增埋点）：
  1. `gate_result_cache` 命中率：cache-hit detail 计数 / 白名单 gate 调用计数（TTL 10min 内同指纹重提交流）；
  2. `gate_preflight` 指纹采信率：F′==F 采信次数 / 预跑次数（采信率低=锁内全量重跑频发，需排查写入方）；
  3. **零漏检红线**：观察期内任何"预跑/缓存放行后本应阻断的违规"（以 post-commit reconciler critical_warn 与人工复核为准）出现 → 立即 flag OFF 回滚。
- **扩面条件**：7 天零漏检 + 命中/采信数据正常 → 维持 ON 进常态化；异常 → flag OFF（回滚零残留：缓存目录可整删，预跑代码保留不拆）。
- **回滚命令**：`config/flags.yaml` 两 flag 翻回 false + 删 `.runtime/gate_cache/`。

## 4. L1 检测面补偿说明（Tier2 缺位期）

Tier2 全层暂下线（等 R3）期间的补偿防线：Tier1 AST 哈希经 L2 周期审计保留、ast_grep 结构规则（本夜全部实证拦截来源）、L0 MCP advisory（check_before_write）、acknowledged 白名单纪律（resolve_finding 双 verdict）。
