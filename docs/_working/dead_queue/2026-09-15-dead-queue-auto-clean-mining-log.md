---
ttl: task_bound
---

# 方案挖矿日志 — dead/ 死信自动清理（guard_recycle 通道）

> 任务：owner_cleanable_qids 能否自动清理？能否识别该清/不该清？是否走挖矿 SOP？
> 日期：2026-09-15 · 执行：solo_agent · 方法=mining_sop_policy v1.0.1（六向寻路，内部反查优先+外部校验）

## 候补母节点

「dead/ 死信处置自动化」——拆两轴：①清理动作的合规通道 ②识别语义（该清/不该清）。

## 六向寻路

### 向1 · 制度内先例（内部反查）

- **git grep "永不清理"** → 7 处命中，全部指向同一不变量：`scripts/commit_queue.py` L914/L1022/L1127/L1186/L1634/L1697/L1711 ——「dead/ 永不清理」是 66 号设计文档 §8 队列腐蚀口径的**代码级钉死不变量**。
- **TestDoneTtlCleanup.test_dead_never_cleaned_invariant**（tests/governance/test_commit_queue.py）钉死断言：超龄死信 + TTL=0 极端值也不动。done/ 有 7 天 TTL 自动清理，dead/ **永不自动清理**。
- **commit 989e3af3a9（B4 死信处置定案入档）**：clean 死信 5 条定性（1 already-landed+4 MIXED 属主已推进），均不再 requeue 防 stale 快照回退——**"dead/ 永不清理字节永可取"是 Owner 既有裁定**。
- **§9 主工作区纪律（ARCH-311 事故教训，2026-09-15 增补）**：任何"删除"一律走 `ops_guard.guard_recycle`（统一回收站，永不物理删除，30 天可恢复）；未接 guard 的删除工具/脚本禁止对 tracked 或他人未跟踪工作文件使用。
- **guard_recycle 真源**（scripts/ops_guard.py）：`guard_recycle(path, *, cwd, reason, repo_root)` → move 进 `.runtime/recycle_bin/<epoch_ts>/<原相对路径>`，保留层级，30 天恢复窗。
- **architecture_issue_registry L6428 先例**：stash_lifecycle_reconciler 曾设计"自动清理过期 AI stash"，实测发现 reconciler 清了不该清的（_is_ai_generated 同形虚设 bug）——**reconciler 自动清理有前科**，需护栏。
- **L5701 反例**：14 项"增量机械性清理治理已失效（无机械触发保证=永不清理）"曾被判失效转 EXECUTE 分批治理——治理动作本身也曾踩"只声明不执行"坑。

**挖干判定**：内部反查已命中设计文档、代码不变量、钉死测试、Owner 裁定、事故先例五层——制度面已饱和。

### 向2 · 谁是消费方（下游反查）

- retirement_audit.json/yaml 的 `owner_cleanable_qids`：消费方=Owner（现状）。若自动化，消费方变为 reconciler 自身+Owner 审计。
- dead/ 目录其他消费者：`commit_queue.py requeue`（读原项留痕）、仲裁/debug 场景（blob 取回）。

### 向3 · 替代方案对照（外部校验）

- **etcd/ZooKeeper 语义**：ephemeral/lease 过期=节点消失，但**审计日志永不自动删**（etcd 历史 compaction 有 revision 窗口，ZK 无）——业界对"审计证据类数据"默认不物理删。
- **GitHub Actions/CI 死信**：失败 job 日志 90 天自动过期（有 retention 策略=显式配置而非默认），且**归档先于删除**。
- **Kafka log compaction**：保留每个 key 最新值，删除墓碑——但墓碑本身保留 interval 可配，语义="先标记后清"。
- 共性收敛：**审计/死信类数据的业界默认=保留或先归档后清，且删除必须有显式 retention 配置**，无"识别到即可删"的先例。

### 向4 · 风险反查

- 自动清理最坏情形：blob_ref 指向的 blobs/ 是内容寻址共享存储（多队列项可共享同一 blob）——删 dead 项 JSON 不删 blob 无碍，但若连带清 blob 会破坏他项。识别逻辑必须**只动 dead/*.json 的"可清标记"，不动 blobs/**。
- "该清"误判面：判定链（blob_sha256==worktree 字节 / git --since）是**概率性证据**（mtime/时钟/工作区漂移），非死信语义终判——与 test_dead_never_cleaned_invariant 的"极端值也不动"哲学冲突。

### 向5 · 成本

- 实现成本：低（在现有 reconciler 报告后加 guard_recycle 调用，~50 行）。
- 但需新增"二次确认窗"（报告先出 → 24h 冷静期 → 下轮自动 recycle）= 中成本，且引入跨轮状态。

### 向6 · 谁做过同样的事（仓库内）

- `runtime_cleanup_reconciler` / `tmp_cleanup_reconciler` / `stash_lifecycle_reconciler`：三者都是"自动清理"先例，但清理对象都是 **.runtime 临时区**（TTL 明确、内容可再生），且 stash 清理出过误删事故。
- dead/ 不同：内容=**决策证据**（谁提交失败、为何失败、blob 快照），不可再生。

## 收敛判断（signal/noise）

| 发现 | 判定 |
|------|------|
| dead/ 永不清理=代码不变量+钉死测试+Owner 裁定三层钉死 | **signal（强）** |
| guard_recycle 是唯一合规删除通道（§9 纪律 3） | **signal（强）** |
| 三分类判定是概率性证据，非终判 | **signal（强）** |
| 业界审计数据默认保留/先归档 | signal（中） |
| stash 清理误删前科 | signal（中） |
| "识别到即删"无业界先例 | noise |
| blobs/ 共享存储连带风险 | noise（只动 JSON 即可规避） |

**连续两轮 noise 封矿判定**：需要新信息的点只剩"Owner 是否愿意修订 dead/ 永不清理裁定"——这是决策不是挖矿，封矿转方案。

## 方案结论

**问题一（能不能自动清理）**：能，但不能动 `commit_queue.py` 的 cleanup_done 通道（不变量钉死），唯一合规路径=**独立 reconciler 调 guard_recycle（move 进回收站，永不物理删）**——与 §9 纪律 3、"dead/ 永不清理"不变量（字节永可取，回收站 30 天）语义兼容的前提是**先修钉死测试与不变量表述**（"dead/ 永不自动清理"→"dead/ 项永不物理删除；guard_recycle 归档属治理动作非清理"）。

**问题二（能不能识别）**：三分类已识别"已收敛"（content_landed/landed_elsewhere），但这是概率性证据；真正"不该清"的判定=superseded_or_dropped + requeued 标注项 + blob 被他项共享——可识别但需要保守白名单（只清"连续两轮审计均判 landed 且非 requeued"的项）。

**问题三（要不要走挖矿 SOP）**：已走完（本日志即产出）。挖掘结论：这不是纯施工任务，是**裁定级变更**（动 Owner 既有定案+钉死测试）——SOP 的价值正是把"拍脑袋自动清理"拦住，先把裁定改了再施工。
