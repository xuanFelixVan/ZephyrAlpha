---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——GitCommitGateway+提交队列
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：GitCommitGateway+提交队列（I29）

- 状态: **已审**
- 级别: P1｜类型: 基础设施
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df，**审查目标修复 3c853303da 已在基线后/工作区前落地并含于 HEAD**）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（全局锁/门禁注册/step3a :1614）+ `scripts/commit_queue.py:715`（SerializerLease）/:1014-1160（drain 主循环）
- 生产调用方: scripts/git_commit.py（唯一合法 commit 入口）、scripts/commit_queue.py CLI、scheduler/reconciler 派生批（machine 车道）、规则链路 flush batcher
- 测试文件: tests/governance/test_commit_queue.py（修复批 +57 行）、tests/governance/test_commit_queue_landing.py（+167 行）
- 备注: **专项=审 3c853303da（lease 活体不抢+renew 续租）修复质量 + 近期高速化施工（F1 fe47296db5 / F4 025df945e0）是否引入新洞**；两文件合计 5646 行，本次按"修复面+主循环+全局锁契约"深读，非全文件逐行（长尾见 §6）

## 1 对象快照

- 审查范围：SerializerLease 全实现（:715-870，acquire/活体不抢/renew/__exit__）、drain 主循环（车道化 FIFO/原子取项/逐项续租 :1124-1133）、F1 `_fold_rules_integrity_into_batch`（gateway :1802+，折入时序与 fail-open 语义）、gateway 头注不变式（全局锁 TTL=1800s/`_in_commit_flow` 守卫/rename fallback/adopt_prior_work）、step3a `os.path.isfile` 撤暂存路径（:1614）。
- 排除项：~60 个 gate 的逐一实现（I30）；commit gate registry 装配；git_commit.py CLI 层；F4 arch-diagram 并发化（reconciler 侧，只看其与队列的交互面）。
- 测试覆盖概况：修复批带 3 条回归（skipped/replayed 反斜杠移除+混合分隔符——此为 local_replay 的；队列侧 +224 行测试覆盖 lease/landing）；落地侧容忍衍生漂移已有测试。
- 材料包缺项：11 条 pathspec 死信的原始死信文件未调阅（以 commit message 取证段为准）；近 7 天死信率统计未取。
- 变更热力：gateway=150 次提交（全仓最高热区之一）、commit_queue=18 次；近期密度显著升高（st-flashspeed/st-commitspeed 两波提速战役）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗 | **修复残余洞：__exit__ 无属主校验删租约**：renew() 有 pid 校验防易主误覆盖（:831-841），但 __exit__（:808-815）无条件 `os.remove(self._lease_file)`——若本进程租约曾被「损坏回收分支」删除而他进程已建新租约，本进程退出时会把**新持有者的租约**删掉→第三方趁虚再入→双 drain 复发（与刚治本的死信同构，入口从"抢锁"换成"误删"） | commit_queue.py:808-815 vs :826-843（renew 有校验的对照） | P2 | 两进程演练：A 持锁→手工破坏租约内容触发损坏分支被 B 重建→A 退出→观察 B 的租约被删且 C 可入 |
| E 对抗 | PID 复用误判活体（Windows PID 复用）：is_pid_alive 对已死持有者的复用 PID 误判活→僵尸租约最长滞留 TTL(300s)内不可回收→可用性延迟（自举 5s 放弃语义下表现为"这轮排不了"）——非正确性洞，登记可接受 | commit_queue.py:765-772（依赖 is_pid_alive 单真源） | P3 | 模拟 PID 复用观察回收延迟 |
| A 深度 | 修复质量正面确认：①活体不抢（:782-795 超TTL+活PID=慢项在途，不抢）②renew 逐项心跳（:1124-1133 每项处理前刷新，原子写 tmp+os.replace+fsync）③易主防 clobber（:831-841）④fail-open 不入排空主循环——三层防抢互为冗余，取证叙事（tracked 文件 reset 后仍在/只有新文件死）与代码路径一致 | commit_queue.py:738-795, 826-868, 1124-1133 | — | 复跑 tests/governance/test_commit_queue*.py |
| A 深度 | F1 折入时序依赖「flush 只 git-add 现盘字节」：折入用工作树混合态算最终 DB——若 flush 失败（批未落地）而 DB 已写入折叠基线，DB 将**超前于现实**（登记了未提交内容的 hash）→后续 check() 对回滚后的工作树误报 TAMPERED，直至下一次成功 register 自愈；fail-open 只覆盖异常不覆盖"flush 失败"半态 | git_commit_gateway.py:_fold_rules_integrity_into_batch（fail-open 注释 vs flush 失败路径） | P3 | 构造 flush 失败（断仓/锁）后核对 rules_integrity_db 与 HEAD 偏差及 check() 行为 |
| B 上游 | F1 加长单项时长→正是 lease TTL 撞线的诱因源：衍生并入后 machine 车道单项承载更多文件（reconciler ~180s 级）——renew 心跳恰好治此；两笔提速改动形成"病因加深+药方加固"耦合，任何一方单独回滚都复发 | fe47296db5 message（24h 31 笔尾笔）+ commit_queue.py:1124-1131 | P3 | 回滚演练任一侧观察死信复发 |
| E 对抗 | F4 并发化（025df945e0，reconciler 侧）：波次拓扑+cap 钳位+byte-identical 双实证+4 文件 DIFF 归因生成器非确定性（serial×2 对照实验）——方法论严谨；残余=非确定性生成器使 byte-identical 验收永久带 4 文件豁免面，未来真回归可藏身同面 | 025df945e0 message（对照组设计） | P3 | 检查该 4 文件是否有非确定性归因记录可追溯 |
| A 深度 | 车道化 FIFO（interactive 优先/machine 让路+30min 防饿死）：优先级反转防护有兜底；qid 字典序==FIFO 依赖 qid 单调（enqueue 侧时戳+序号）——跨天/时钟回拨时字典序可能乱（长尾） | commit_queue.py:1138-1148 | P3 | 拨钟构造乱序 qid 观察 _pick_head |
| E 对抗 | 原子取项 rename 竞态处理完备：FileNotFoundError=并发 compaction 跳过、PermissionError=重试收敛不跳项（:1160-1168）——「保 FIFO 不冤枉慢写入者」语义明确 | commit_queue.py:1160-1168 | — | — |
| D 旁系 | gateway 全局锁（TTL=1800s）与 SerializerLease（TTL=300s+renew）双锁体系：全局锁无 renew（1800s 覆盖 commit 时长富余），lease 有 renew——同一作者批内两种 TTL 策略，全局锁若遇 >30min 单 commit 会被抢（现网无此场景） | gateway.py:8 头注 vs commit_queue.py:169-171 | P3 | code review 登记 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 分布式租约（lease + renewal heartbeat + fencing token） | **对等已有偏强**：业界租约标准=TTL+心跳续期+属主校验（etcd lease/Chubby）；本修复补齐心跳与属主校验，达业界形态；缺 fencing token（租约世代号），残余洞（__exit__ 误删）正是无 fencing 的经典后果 | etcd lease 文档（lease keep-alive 语义）, etcd.io, 2025（检索受限流批次影响，URL=官方文档域）；Chubby lease 论文域（research.google.com 存档） |
| 提交队列死信自愈（DLQ + requeue + 取证签名） | **对等已有偏强**：dead/dead_reason/requeue + 死信取证（"只有新文件死"签名）+ 落地侧容忍衍生漂移，超出一般队列实践 | 受限流批次口径（Kafka DLQ 惯例参照，kafka.apache.org, 2025） |
| 原子目录作业（rename-based claim、pending→processing 状态机） | 对等已有：与 maildir/磁盘队列惯例一致（rename 原子性+孤儿回收 _recover_orphans） | 受限流口径 |

## 4 缺陷清单

1. **D-1（P2）__exit__ 删租约无属主校验（3c853303da 残余洞）**
   - 现状→证据：renew 有 pid 校验（:831-841），__exit__ 裸 os.remove（:808-815）。触发链=损坏回收分支或他进程陈锁强破后重建租约的窗口内，旧持有者退出删新租约。
   - 影响：低概率但后果=双 drain 复发（与 11 条死信同构），且更隐蔽（无人"抢"，是"让"出来的竞态）。
   - 建议修法：__exit__ 读租约内容校验 pid==os.getpid() 再删（与 renew 同款守卫）；不匹配则只清 _acquired 标志。
   - 验证法：轴 E 两进程演练；修复批补一条回归测试。
2. **D-2（P3）F1 折入的 flush 失败半态**：DB 超前注册致 TAMPERED 假警（自愈可达）；建议 flush 失败路径回滚/重 register 折叠 DB。
3. **D-3（P3）全局锁 1800s 无续租**：登记；遇超长 commit 场景前先补 renew。
4. **D-4（P3）F4 的 4 文件非确定性豁免面**：归因记录应随件保留，防真回归藏身。
5. **D-5（P3）qid 字典序 FIFO 的时钟回拨长尾**。

## 5 挂起疑问

- 11 条死信的后续：requeue 后是否全部落地（需读 .runtime/commit_queue/dead/ 实况，审查环境只读未取）。
- Mode B 自愈重放竞态（commit message 提到"Mode B 自愈重放期竞态窗口仍在故亦败"）——该窗口是否已有独立工单/裁定跟踪，未在仓内 grep 到登记。
- gateway 3715 行中 ~50 个 _check_* 与 GateSpec 的映射完整性（属 I30 交叉项）。

## 6 完备性自评

- 六轴全查：A（lease 算法逐分支+F1 时序）、B（git 环境竞态源）、C（消费方=git_commit.py/调度派生批/reconciler）、D（双锁体系+F1/F4 耦合）、E（五问：静默失败=死信 dead_reason 有、假阳性=is_pid_alive 复用、重放=adopt-prior-work 契约在、时序=本报告核心）、F（etcd/Chubby/Kafka 口径，限流批次如实记）。
- 长尾：gateway 150 commits 的其余 140 次未逐一考古（以头注不变式+近期三批为准）；_recover_orphans 实现未逐行；commit_queue 侧测试断言强度抽查 5 例正常。
- 专项结论（任务问句）：**3c853303da 修复质量=高**（三层防抢+取证叙事与代码一致+带回归测试），残余一个同构级小洞（__exit__ 无属主校验，P2）；**F1/F4 未发现正确性级新洞**（各有一个 P3 级半态/豁免面登记）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- 3c853303da 修复质量复核=高（三层防抢+带回归）。残余同构洞 __exit__ 属主校验: 挂起登记（提交链提速车道在途，防冲突）。F1/F4 未发现正确性新洞。
